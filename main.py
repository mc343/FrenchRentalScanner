"""
French Rental Scanner - Main Application

Scans Bien'ici for rental apartments and houses in the current target locations,
stores them in a database, and provides a dashboard for review and analysis.
"""
import argparse
import logging
import os
import re
import subprocess
import sys
import time
from typing import Dict, List

from scraper import BieniciScraper, LogicImmoScraper, PAPScraper
from scraper.parallel_scanner import ParallelScanner
from database import DatabaseManager

SCRAPER_REGISTRY = {
    "Bienici": BieniciScraper,
    "LogicImmo": LogicImmoScraper,
    "PAP": PAPScraper,
}

ACTIVE_SOURCES = ["Bienici", "LogicImmo", "PAP"]
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "rental_listings.db")


def default_filters() -> dict:
    """Return the default search filters."""
    return {
        "location": "Huningue",
        "min_price": 500,
        "max_price": 2500,
        "min_area": 20,
        "max_area": 100,
        "property_type": "all",
    }


def _normalize_title(value: str) -> str:
    """Create a lightweight comparable title token."""
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower())
    return " ".join(cleaned.split())[:80]


def _listing_signature(listing: Dict) -> str:
    """Build a source-agnostic signature to suppress duplicate listings."""
    city = str(listing.get("city") or listing.get("location") or "").strip().lower()
    property_type = str(listing.get("property_type") or "").strip().lower()
    price = int(round(float(listing.get("price") or 0) / 100.0) * 100)
    area = int(round(float(listing.get("area") or 0)))
    title = _normalize_title(listing.get("title"))
    return "|".join([city, property_type, str(price), str(area), title])


def dedupe_listings(listings: List[Dict]) -> List[Dict]:
    """Collapse obviously duplicated listings across websites."""
    by_direct_key: Dict[str, Dict] = {}
    deduped: Dict[str, Dict] = {}

    for listing in listings:
        direct_parts = [
            str(listing.get("source") or "").strip().lower(),
            str(listing.get("listing_id") or "").strip(),
            str(listing.get("url") or "").strip().lower(),
        ]
        direct_key = "|".join(direct_parts)
        existing_direct = by_direct_key.get(direct_key)
        if direct_key.strip("|") and existing_direct:
            current_images = len(existing_direct.get("images") or [])
            new_images = len(listing.get("images") or [])
            current_features = len(existing_direct.get("features") or [])
            new_features = len(listing.get("features") or [])
            if (new_images, new_features) > (current_images, current_features):
                by_direct_key[direct_key] = listing
            continue
        if direct_key.strip("|"):
            by_direct_key[direct_key] = listing

    for listing in by_direct_key.values():
        signature = _listing_signature(listing)
        current = deduped.get(signature)
        if not current:
            deduped[signature] = listing
            continue

        current_images = len(current.get("images") or [])
        new_images = len(listing.get("images") or [])
        current_features = len(current.get("features") or [])
        new_features = len(listing.get("features") or [])

        if (new_images, new_features) > (current_images, current_features):
            primary = listing
            secondary = current
        else:
            primary = current
            secondary = listing

        merged_sources = set(primary.get("contact_info", {}).get("duplicate_sources", []))
        merged_sources.add(primary.get("source", ""))
        merged_sources.add(secondary.get("source", ""))
        merged_sources.discard("")

        merged_urls = set(primary.get("contact_info", {}).get("duplicate_urls", []))
        if primary.get("url"):
            merged_urls.add(primary["url"])
        if secondary.get("url"):
            merged_urls.add(secondary["url"])

        primary_contact = dict(primary.get("contact_info") or {})
        primary_contact["duplicate_sources"] = sorted(merged_sources)
        primary_contact["duplicate_urls"] = sorted(merged_urls)
        primary["contact_info"] = primary_contact
        deduped[signature] = primary

    return list(deduped.values())


def run_scan(filters: dict = None, sources: list = None) -> dict:
    """Run scans for the selected websites and persist results."""
    # Configure logging to capture ParallelScanner output
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    filters = filters or default_filters()
    selected_sources = sources or ACTIVE_SOURCES

    start_time = time.time()

    # Use ParallelScanner for concurrent scraping
    parallel_scanner = ParallelScanner(
        timeout=150,
        max_workers=3,
        scraper_registry=SCRAPER_REGISTRY
    )
    scan_result = parallel_scanner.scan(filters, selected_sources)
    raw_listings = scan_result["raw_listings"]
    per_source_results = scan_result["per_source_results"]

    scan_duration = time.time() - start_time

    db = DatabaseManager(DEFAULT_DB_PATH)
    deduped_listings = dedupe_listings(raw_listings)
    if deduped_listings:
        store_summary = db.add_listings_batch(deduped_listings, return_summary=True)
    else:
        store_summary = {"stored_count": 0, "new_count": 0, "updated_count": 0, "error_count": 0}
    stored_count = store_summary["stored_count"]

    scan_city = str(filters.get("location") or "").strip()
    if scan_city:
        for source in selected_sources:
            source_result = per_source_results.get(source, {})
            if source_result.get("error") or int(source_result.get("count") or 0) == 0:
                continue
            source_ids = [
                listing.get("listing_id")
                for listing in raw_listings
                if listing.get("source") == source
            ]
            db.reconcile_source_city_inventory(source, scan_city, source_ids)

    return {
        "filters": filters,
        "sources": selected_sources,
        "raw_listings": raw_listings,
        "listings": deduped_listings,
        "stored_count": stored_count,
        "new_count": store_summary.get("new_count", 0),
        "updated_count": store_summary.get("updated_count", 0),
        "batch_duplicate_count": store_summary.get("batch_duplicate_count", 0),
        "store_error_count": store_summary.get("error_count", 0),
        "per_source_results": per_source_results,
        "stats": db.get_stats(),
        "scan_duration": scan_duration,
    }


def scan_listings(filters: dict = None, sources: list = None):
    """Scan all configured websites for listings."""
    filters = filters or default_filters()
    sources = sources or ACTIVE_SOURCES

    print("French Rental Scanner - Bien'ici")
    print("=" * 50)
    print()
    print("Scanning with filters:")
    for key, value in filters.items():
        print(f"  {key}: {value}")
    print(f"  sources: {', '.join(sources)}")
    print()

    result = run_scan(filters, sources=sources)

    # Display scan timing
    scan_duration = result.get("scan_duration", 0)
    print(f"Scan completed in {scan_duration:.1f} seconds")
    print()

    for source in result["sources"]:
        source_result = result["per_source_results"].get(source, {})
        print(f"Scanning {source}...")
        if source_result.get("error"):
            print(f"  Error: {source_result['error']}")
        else:
            print(f"  Found {source_result.get('count', 0)} listings")
        print()

    if result["listings"]:
        print(f"Persisting {len(result['listings'])} de-duplicated listings...")
        print(
            f"  Added/updated {result['stored_count']} listings "
            f"(new {result.get('new_count', 0)}, updated {result.get('updated_count', 0)})"
        )
        if result.get("batch_duplicate_count", 0):
            print(f"  Collapsed {result['batch_duplicate_count']} duplicate row(s) inside the same scan batch")
        if len(result["raw_listings"]) != len(result["listings"]):
            print(f"  Suppressed {len(result['raw_listings']) - len(result['listings'])} duplicate listing(s)")
        print()
        print("Database Statistics:")
        print(f"  Total listings: {result['stats']['total_listings']}")
        print(f"  Available: {result['stats']['available']}")
        print(f"  Favorites: {result['stats']['favorites']}")
        print(f"  Sources: {result['stats'].get('sources', {})}")
    else:
        print("No listings found")

    print()
    print("Scan complete!")


def show_stats():
    """Show database statistics."""
    db = DatabaseManager(DEFAULT_DB_PATH)
    stats = db.get_stats()

    print("Database Statistics")
    print("=" * 50)
    print(f"Total listings: {stats['total_listings']}")
    print(f"Available: {stats['available']}")
    print(f"Favorites: {stats['favorites']}")
    print(f"Listings with availability date: {stats.get('with_available_date', 0)}")
    print()
    print("Sources:")
    for source, count in stats.get("sources", {}).items():
        print(f"  {source}: {count}")


def launch_dashboard():
    """Launch the Streamlit dashboard."""
    print("Launching dashboard...")
    print("Opening browser at http://127.0.0.1:8501")
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard/app.py",
        "--server.address",
        "127.0.0.1",
        "--browser.gatherUsageStats",
        "false",
    ])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="French Rental Scanner - Scan Bien'ici rental listings for Huningue and Mulhouse"
    )

    parser.add_argument(
        "action",
        choices=["scan", "dashboard", "stats"],
        help="Action to perform",
    )

    parser.add_argument("--location", type=str, default="Huningue", help="Location to search (default: Huningue)")
    parser.add_argument("--min-price", type=int, default=500, help="Minimum price in EUR (default: 500)")
    parser.add_argument("--max-price", type=int, default=2500, help="Maximum price in EUR (default: 2500)")
    parser.add_argument("--min-area", type=int, default=20, help="Minimum area in m2 (default: 20)")
    parser.add_argument("--max-area", type=int, default=100, help="Maximum area in m2 (default: 100)")
    parser.add_argument(
        "--type",
        type=str,
        default="all",
        choices=["all", "apartment", "house"],
        help="Property type (default: all)",
    )
    parser.add_argument(
        "--available-within",
        type=int,
        default=None,
        help="Only include listings available within N days (e.g., 90 for 3 months, 120 for 4 months)",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=ACTIVE_SOURCES,
        choices=ACTIVE_SOURCES,
        help="Websites to scan",
    )

    args = parser.parse_args()

    if args.action == "scan":
        filters = {
            "location": args.location,
            "min_price": args.min_price,
            "max_price": args.max_price,
            "min_area": args.min_area,
            "max_area": args.max_area,
            "property_type": args.type,
        }
        scan_listings(filters, sources=args.sources)
    elif args.action == "stats":
        show_stats()
    elif args.action == "dashboard":
        launch_dashboard()


if __name__ == "__main__":
    main()

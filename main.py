"""
French Rental Scanner - Main Application

Scans Bien'ici for rental apartments and houses in the current target locations,
stores them in a database, and provides a dashboard for review and analysis.
"""
import argparse
import subprocess
import sys

from scraper import BieniciScraper
from database import DatabaseManager

SCRAPER_REGISTRY = {
    "Bienici": BieniciScraper,
}

ACTIVE_SOURCES = ["Bienici"]


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


def run_scan(filters: dict = None, sources: list = None) -> dict:
    """Run scans for the selected websites and persist results."""
    filters = filters or default_filters()
    selected_sources = sources or ACTIVE_SOURCES

    db = DatabaseManager("rental_listings.db")
    all_listings = []
    per_source_results = {}

    for source in selected_sources:
        scraper_cls = SCRAPER_REGISTRY.get(source)
        if not scraper_cls:
            per_source_results[source] = {"count": 0, "error": f"Unknown source: {source}"}
            continue

        try:
            scraper = scraper_cls()
            source_listings = scraper.search(filters)
            all_listings.extend(source_listings)
            source_error = getattr(scraper, "last_error", None)
            per_source_results[source] = {"count": len(source_listings), "error": source_error}
        except Exception as exc:
            per_source_results[source] = {"count": 0, "error": str(exc)}

    stored_count = db.add_listings_batch(all_listings) if all_listings else 0

    scan_city = str(filters.get("location") or "").strip()
    if scan_city:
        for source in selected_sources:
            source_ids = [
                listing.get("listing_id")
                for listing in all_listings
                if listing.get("source") == source
            ]
            db.reconcile_source_city_inventory(source, scan_city, source_ids)

    return {
        "filters": filters,
        "sources": selected_sources,
        "listings": all_listings,
        "stored_count": stored_count,
        "per_source_results": per_source_results,
        "stats": db.get_stats(),
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

    for source in result["sources"]:
        source_result = result["per_source_results"].get(source, {})
        print(f"Scanning {source}...")
        if source_result.get("error"):
            print(f"  Error: {source_result['error']}")
        else:
            print(f"  Found {source_result.get('count', 0)} listings")
        print()

    if result["listings"]:
        print(f"Storing {len(result['listings'])} listings in database...")
        print(f"  Added/updated {result['stored_count']} listings")
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
    db = DatabaseManager("rental_listings.db")
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

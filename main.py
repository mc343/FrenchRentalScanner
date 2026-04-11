"""
French Rental Scanner - Main Application

Scans French rental websites (SeLoger, LeBonCoin) for apartment/house listings,
stores them in a database, and provides a dashboard for filtering and analysis.
"""
import argparse
import sys
from datetime import datetime
from scraper import SeLogerScraper, LeBonCoinScraper
from database import DatabaseManager


def scan_listings(filters: dict = None):
    """Scan all configured websites for listings

    Args:
        filters: Dictionary of search filters
    """
    print("🏠 French Rental Scanner")
    print("=" * 50)
    print()

    if filters is None:
        # Default filters
        filters = {
            'location': 'Paris',
            'min_price': 500,
            'max_price': 2500,
            'min_area': 20,
            'max_area': 100,
            'property_type': 'all'
        }

    print(f"🔍 Scanning with filters:")
    for key, value in filters.items():
        print(f"  {key}: {value}")
    print()

    # Initialize database
    db = DatabaseManager("rental_listings.db")

    all_listings = []

    # Scan SeLoger
    print("📡 Scanning SeLoger.fr...")
    try:
        seloger = SeLogerScraper()
        seloger_listings = seloger.search(filters)
        print(f"  ✓ Found {len(seloger_listings)} listings")
        all_listings.extend(seloger_listings)
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print()

    # Scan LeBonCoin
    print("📡 Scanning LeBonCoin.fr...")
    try:
        leboncoin = LeBonCoinScraper()
        leboncoin_listings = leboncoin.search(filters)
        print(f"  ✓ Found {len(leboncoin_listings)} listings")
        all_listings.extend(leboncoin_listings)
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print()

    # Store in database
    if all_listings:
        print(f"💾 Storing {len(all_listings)} listings in database...")
        count = db.add_listings_batch(all_listings)
        print(f"  ✓ Added/updated {count} listings")

        # Show stats
        stats = db.get_stats()
        print()
        print("📊 Database Statistics:")
        print(f"  Total listings: {stats['total_listings']}")
        print(f"  Available: {stats['available']}")
        print(f"  Favorites: {stats['favorites']}")
        print(f"  Sources: {stats.get('sources', {})}")
    else:
        print("⚠ No listings found")

    print()
    print("✅ Scan complete!")


def show_stats():
    """Show database statistics"""
    db = DatabaseManager("rental_listings.db")
    stats = db.get_stats()

    print("📊 Database Statistics")
    print("=" * 50)
    print(f"Total listings: {stats['total_listings']}")
    print(f"Available: {stats['available']}")
    print(f"Favorites: {stats['favorites']}")
    print()
    print("Sources:")
    for source, count in stats.get('sources', {}).items():
        print(f"  {source}: {count}")


def launch_dashboard():
    """Launch the Streamlit dashboard"""
    import subprocess
    print("🚀 Launching dashboard...")
    print("Opening browser at http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"])


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="French Rental Scanner - Scan French rental websites"
    )

    parser.add_argument(
        'action',
        choices=['scan', 'dashboard', 'stats'],
        help='Action to perform'
    )

    parser.add_argument('--location', type=str, default='Paris',
                       help='Location to search (default: Paris)')
    parser.add_argument('--min-price', type=int, default=500,
                       help='Minimum price in € (default: 500)')
    parser.add_argument('--max-price', type=int, default=2500,
                       help='Maximum price in € (default: 2500)')
    parser.add_argument('--min-area', type=int, default=20,
                       help='Minimum area in m² (default: 20)')
    parser.add_argument('--max-area', type=int, default=100,
                       help='Maximum area in m² (default: 100)')
    parser.add_argument('--type', type=str, default='all',
                       choices=['all', 'apartment', 'house'],
                       help='Property type (default: all)')

    args = parser.parse_args()

    if args.action == 'scan':
        filters = {
            'location': args.location,
            'min_price': args.min_price,
            'max_price': args.max_price,
            'min_area': args.min_area,
            'max_area': args.max_area,
            'property_type': args.type
        }
        scan_listings(filters)

    elif args.action == 'stats':
        show_stats()

    elif args.action == 'dashboard':
        launch_dashboard()


if __name__ == "__main__":
    main()

"""
French Rental Scanner - Interactive Interface
A menu-driven application for managing rental listings
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseManager
from database.models import Listing
from datetime import datetime
from quick_add import quick_add, batch_add, extract_listing_info
from url_scraper import URLScraper


class Colors:
    """ANSI color codes for terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class RentalScannerApp:
    """Interactive application for French Rental Scanner"""

    def __init__(self):
        self.db = DatabaseManager("rental_listings.db")
        self.running = True

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """Print formatted header"""
        print(Colors.HEADER + "=" * 70 + Colors.ENDC)
        print(Colors.BOLD + Colors.OKBLUE + f"  {title:^66}" + Colors.ENDC)
        print(Colors.HEADER + "=" * 70 + Colors.ENDC)
        print()

    def print_menu(self, options):
        """Print menu options"""
        for i, (key, desc) in enumerate(options.items(), 1):
            print(f"  [{key}] {desc}")
        print()
        print(Colors.WARNING + "  [0] Exit" + Colors.ENDC)
        print(Colors.HEADER + "-" * 70 + Colors.ENDC)

    def get_input(self, prompt):
        """Get user input"""
        try:
            return input(Colors.OKCYAN + prompt + Colors.ENDC).strip()
        except EOFError:
            return "0"

    def print_success(self, message):
        """Print success message"""
        print(Colors.OKGREEN + f"  [OK] {message}" + Colors.ENDC)

    def print_error(self, message):
        """Print error message"""
        print(Colors.FAIL + f"  [ERROR] {message}" + Colors.ENDC)

    def print_info(self, message):
        """Print info message"""
        print(Colors.OKCYAN + f"  [INFO] {message}" + Colors.ENDC)

    def show_listing(self, listing, show_id=False):
        """Display a single listing"""
        if show_id:
            print(f"\n{Colors.BOLD}ID: {listing.id}{Colors.ENDC}")
        print(f"  {Colors.BOLD}{Colors.OKBLUE}{listing.title}{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}{listing.price} EUR/month{Colors.ENDC} | "
              f"{listing.area} m2 | {listing.location}")
        print(f"  Source: {listing.source}")

        if listing.description:
            desc = listing.description[:100] + "..." if len(listing.description) > 100 else listing.description
            print(f"  {desc}")

        if listing.features:
            print(f"  Features: {', '.join(listing.features[:5])}")

        status = []
        if listing.is_favorite:
            status.append(Colors.OKGREEN + "FAVORITE" + Colors.ENDC)
        if listing.contacted:
            status.append(Colors.OKCYAN + "CONTACTED" + Colors.ENDC)
        if listing.viewing_scheduled:
            status.append(Colors.WARNING + "VIEWING SCHEDULED" + Colors.ENDC)

        if status:
            print(f"  Status: {' | '.join(str(s) for s in status)}")

    def show_listings(self, listings):
        """Display multiple listings"""
        if not listings:
            self.print_error("No listings found")
            return

        print(f"\n{Colors.BOLD}Found {len(listings)} listing(s):{Colors.ENDC}")
        print(Colors.HEADER + "-" * 70 + Colors.ENDC)

        for i, listing in enumerate(listings, 1):
            print(f"\n  [{i}] {listing.title}")
            print(f"      {listing.price} EUR | {listing.area} m2 | {listing.location}")
            if listing.is_favorite:
                print(f"      {Colors.OKGREEN}[FAVORITE]{Colors.ENDC}")
        print()

    # ==================== MENU HANDLERS ====================

    def main_menu(self):
        """Main application menu"""
        while self.running:
            self.clear_screen()
            self.print_header("FRENCH RENTAL SCANNER")

            # Show stats
            stats = self.db.get_stats()
            print(f"  Total Listings: {Colors.BOLD}{stats['total_listings']}{Colors.ENDC} | "
                  f"Favorites: {Colors.BOLD}{stats['favorites']}{Colors.ENDC} | "
                  f"Available: {Colors.BOLD}{stats['available']}{Colors.ENDC}")
            print()

            options = {
                '1': 'View all listings',
                '2': 'Search listings',
                '3': 'Quick add (paste from website)',
                '4': 'URL scraper (auto-extract from URL)',
                '5': 'Add listing manually',
                '6': 'Manage favorites',
                '7': 'View statistics',
                '8': 'Database operations',
            }

            self.print_menu(options)
            choice = self.get_input("Select option: ")

            handlers = {
                '1': self.view_listings,
                '2': self.search_listings,
                '3': self.quick_add_mode,
                '4': self.url_scraper_mode,
                '5': self.add_listing_manual,
                '6': self.manage_favorites,
                '7': self.view_statistics,
                '8': self.database_ops,
                '0': self.exit_app
            }

            if choice in handlers:
                handlers[choice]()
                if choice != '0':
                    input(Colors.WARNING + "\nPress Enter to continue..." + Colors.ENDC)
            else:
                self.print_error("Invalid option")

    def view_listings(self):
        """View all listings with pagination"""
        self.clear_screen()
        self.print_header("VIEW ALL LISTINGS")

        listings = self.db.get_listings(limit=50)
        self.show_listings(listings)

        if listings:
            choice = self.get_input("\nView details (number) or Enter to return: ")
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(listings):
                    self.clear_screen()
                    self.print_header("LISTING DETAILS")
                    self.show_listing(listings[idx], show_id=True)
                    self.show_listing_actions(listings[idx])

    def search_listings(self):
        """Search listings with filters"""
        self.clear_screen()
        self.print_header("SEARCH LISTINGS")

        filters = {}

        # Location
        location = self.get_input("Location (press Enter to skip): ")
        if location:
            filters['city'] = location

        # Price range
        min_price = self.get_input("Minimum price (press Enter to skip): ")
        if min_price.isdigit():
            filters['min_price'] = int(min_price)

        max_price = self.get_input("Maximum price (press Enter to skip): ")
        if max_price.isdigit():
            filters['max_price'] = int(max_price)

        # Area range
        min_area = self.get_input("Minimum area m2 (press Enter to skip): ")
        if min_area.isdigit():
            filters['min_area'] = int(min_area)

        max_area = self.get_input("Maximum area m2 (press Enter to skip): ")
        if max_area.isdigit():
            filters['max_area'] = int(max_area)

        # Favorites only
        fav_only = self.get_input("Show favorites only? (y/N): ")
        if fav_only.lower() == 'y':
            filters['is_favorite'] = True

        # Search
        listings = self.db.get_listings(filters=filters, limit=50)
        self.show_listings(listings)

        if listings:
            choice = self.get_input("\nView details (number) or Enter to return: ")
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(listings):
                    self.clear_screen()
                    self.print_header("LISTING DETAILS")
                    self.show_listing(listings[idx], show_id=True)
                    self.show_listing_actions(listings[idx])

    def add_listing_manual(self):
        """Add a listing manually"""
        self.clear_screen()
        self.print_header("ADD LISTING MANUALLY")

        listing = {
            'listing_id': f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'source': 'Manual',
            'url': '',
            'title': '',
            'description': '',
            'price': 0,
            'area': 0,
            'location': '',
            'city': '',
            'property_type': 'apartment',
            'features': [],
            'images': []
        }

        # Get listing details
        listing['title'] = self.get_input("Title: ")
        listing['location'] = self.get_input("Location: ")
        listing['city'] = self.get_input("City: ")

        price = self.get_input("Price (EUR): ")
        if price.replace('.', '').isdigit():
            listing['price'] = float(price)

        area = self.get_input("Area (m2): ")
        if area.isdigit():
            listing['area'] = float(area)

        listing['description'] = self.get_input("Description: ")

        # Features
        features_input = self.get_input("Features (comma-separated): ")
        if features_input:
            listing['features'] = [f.strip() for f in features_input.split(',')]

        # Save
        result = self.db.add_listing(listing)
        if result:
            self.print_success("Listing added successfully!")
        else:
            self.print_error("Failed to add listing")

    def manage_favorites(self):
        """Manage favorite listings"""
        self.clear_screen()
        self.print_header("MANAGE FAVORITES")

        favorites = self.db.get_favorites()
        if not favorites:
            self.print_info("No favorites yet")
            return

        self.show_listings(favorites)

        choice = self.get_input("\nSelect action: [V]iew details, [R]emove favorite, Enter to return: ")
        choice = choice.lower()

        if choice == 'v':
            num = self.get_input("Enter listing number: ")
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(favorites):
                    self.clear_screen()
                    self.print_header("FAVORITE DETAILS")
                    self.show_listing(favorites[idx], show_id=True)

        elif choice == 'r':
            num = self.get_input("Enter listing number to remove: ")
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(favorites):
                    listing_id = favorites[idx].id
                    if self.db.toggle_favorite(listing_id):
                        self.print_success("Removed from favorites")

    def view_statistics(self):
        """View database statistics"""
        self.clear_screen()
        self.print_header("STATISTICS")

        stats = self.db.get_stats()

        print(f"\n  Total Listings: {Colors.BOLD}{stats['total_listings']}{Colors.ENDC}")
        print(f"  Available: {Colors.BOLD}{stats['available']}{Colors.ENDC}")
        print(f"  Favorites: {Colors.BOLD}{stats['favorites']}{Colors.ENDC}")
        print()

        print("  By Source:")
        for source, count in stats.get('sources', {}).items():
            print(f"    {source}: {count}")

        print()
        print("  Property Types:")
        # Would need to add this query to db.get_stats()
        print("    Apartment: -")
        print("    House: -")
        print("    Studio: -")

    def quick_add_mode(self):
        """Quick add mode - paste rental information"""
        self.clear_screen()
        self.print_header("QUICK ADD MODE")

        print("\n  Instructions:")
        print("    1. Visit a rental website (SeLoger, LeBonCoin, etc.)")
        print("    2. Copy information from the listing")
        print("    3. Paste it below - the app will extract details")
        print()
        print("  Example format: '2BR Paris 11eme, 1500 EUR, 45m2'")
        print(Colors.HEADER + "-" * 70 + Colors.ENDC)

        while True:
            print()
            data = self.get_input("Paste rental information (or 'menu' to return): ")

            if data.lower() in ['menu', 'exit', 'quit', 'back', 'return']:
                break

            if not data:
                continue

            # Try to extract information
            listing = extract_listing_info(data)

            if listing:
                print()
                print(f"  {Colors.OKGREEN}[FOUND]{Colors.ENDC} {listing['title']}")
                print(f"    Price: {listing['price']} EUR")
                print(f"    Area: {listing['area']} m2")
                print(f"    Location: {listing['location']}")

                # Ask to confirm
                confirm = self.get_input("\n  Add this listing? (Y/n): ").lower()

                if confirm == 'y':
                    result = self.db.add_listing(listing)
                    if result:
                        self.print_success("Listing added!")
                    else:
                        self.print_error("Failed to add")
                else:
                    self.print_info("Not added")
            else:
                self.print_info("Could not extract details. Please try manual entry")

    def url_scraper_mode(self):
        """URL scraper mode - extract data from URLs"""
        self.clear_screen()
        self.print_header("URL SCRAPER MODE")

        print("\n  Paste rental listing URLs and I'll extract the data!")
        print()
        print("  Supported:")
        print("    - SeLoger.fr")
        print("    - LeBonCoin.fr")
        print("    - Most French rental websites")
        print(Colors.HEADER + "-" * 70 + Colors.ENDC)

        scraper = URLScraper()

        while True:
            print()
            url = self.get_input("Paste URL (or 'menu' to return): ")

            if url.lower() in ['menu', 'exit', 'quit', 'back', 'return']:
                break

            if not url:
                continue

            if not url.startswith('http'):
                self.print_error("Invalid URL. Must start with http:// or https://")
                continue

            # Scrape the URL
            self.print_info("Fetching URL...")
            listing = scraper.scrape_url(url)

            if listing and listing['price'] > 0:
                print()
                print(f"  {Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Found listing!")
                print(f"    Title: {listing['title']}")
                print(f"    Price: {listing['price']} EUR")
                print(f"    Area: {listing['area']} m2")
                print(f"    Location: {listing['location']}")

                # Show features
                if listing['features']:
                    print("    Features:")
                    for feature in listing['features'][:5]:
                        print(f"      - {feature}")

                # Ask to confirm
                confirm = self.get_input("\n  Add to database? (Y/n): ").lower()

                if confirm == 'y':
                    result = self.db.add_listing(listing)
                    if result:
                        self.print_success("Listing added to database!")
                    else:
                        self.print_error("Failed to add")
                else:
                    self.print_info("Not added")
            else:
                self.print_info("Could not extract data. Website may be blocking scrapers")
                self.print_info("Try manual entry instead")

    def database_ops(self):
        """Database operations"""
        self.clear_screen()
        self.print_header("DATABASE OPERATIONS")

        options = {
            '1': 'Export listings to CSV',
            '2': 'Import listings from CSV',
            '3': 'Clear all listings',
            '4': 'Reset database',
        }

        self.print_menu(options)
        choice = self.get_input("Select option: ")

        if choice == '1':
            self.export_to_csv()
        elif choice == '3':
            confirm = self.get_input("Are you sure? This will delete all listings! (yes/NO): ")
            if confirm == 'yes':
                self.print_info("Database clear not implemented yet")
                self.print_error("Operation cancelled")

    def export_to_csv(self):
        """Export listings to CSV"""
        import csv

        self.clear_screen()
        self.print_header("EXPORT TO CSV")

        listings = self.db.get_listings(limit=1000)
        if not listings:
            self.print_error("No listings to export")
            return

        filename = self.get_input("Filename (default: listings.csv): ") or "listings.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Title', 'Price', 'Area', 'Location', 'City',
                               'Property Type', 'Source', 'Favorite', 'Contacted'])

                for lst in listings:
                    writer.writerow([
                        lst.id, lst.title, lst.price, lst.area,
                        lst.location, lst.city, lst.property_type,
                        lst.source, lst.is_favorite, lst.contacted
                    ])

            self.print_success(f"Exported {len(listings)} listings to {filename}")

        except Exception as e:
            self.print_error(f"Export failed: {e}")

    def show_listing_actions(self, listing):
        """Show actions for a specific listing"""
        print(f"\n{Colors.HEADER + '-' * 70 + Colors.ENDC}")
        print("Actions:")
        print("  [F] Toggle favorite")
        print("  [C] Mark as contacted")
        print("  [D] Delete listing")
        print("  [Enter] Return")

        choice = self.get_input("\nSelect action: ").lower()

        if choice == 'f':
            new_status = self.db.toggle_favorite(listing.id)
            status = "added to" if new_status else "removed from"
            self.print_success(f"Listing {status} favorites")

        elif choice == 'c':
            if self.db.mark_viewed(listing.id):
                self.print_success("Marked as contacted")

        elif choice == 'd':
            confirm = self.get_input("Delete this listing? (yes/NO): ")
            if confirm == 'yes':
                self.print_info("Delete not implemented yet")
                self.print_error("Operation cancelled")

    def exit_app(self):
        """Exit application"""
        self.clear_screen()
        print(Colors.OKGREEN + "Thank you for using French Rental Scanner!" + Colors.ENDC)
        print(Colors.OKCYAN + "Your data is saved in rental_listings.db" + Colors.ENDC)
        print()
        self.running = False


def main():
    """Main entry point"""
    try:
        app = RentalScannerApp()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

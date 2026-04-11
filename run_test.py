"""
Simple test runner for French Rental Scanner
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("French Rental Scanner - Quick Test")
    print("=" * 60)

    # Test imports
    print("\n1. Testing imports...")
    try:
        from scraper.seloger import SeLogerScraper
        from scraper.leboncoin import LeBonCoinScraper
        from database.connection import DatabaseManager
        print("   [OK] All imports successful")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    # Test database
    print("\n2. Testing database...")
    try:
        db = DatabaseManager("rental_listings.db")

        # Add test listing
        test_listing = {
            'listing_id': f'test_{os.getpid()}',
            'source': 'Test',
            'url': 'https://test.com',
            'title': 'Test Apartment',
            'description': 'Test',
            'price': 1000.0,
            'area': 50.0,
            'location': 'Paris',
            'city': 'Paris',
            'property_type': 'apartment'
        }

        result = db.add_listing(test_listing)
        if result:
            print("   [OK] Database operations work")
        else:
            print("   [FAIL] Could not add listing")
            return False

        # Get stats
        stats = db.get_stats()
        print(f"   [OK] Database has {stats['total_listings']} listings")

    except Exception as e:
        print(f"   [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test scrapers
    print("\n3. Testing scrapers...")
    try:
        seloger = SeLogerScraper()
        leboncoin = LeBonCoinScraper()
        print(f"   [OK] SeLoger: {seloger.BASE_URL}")
        print(f"   [OK] LeBonCoin: {leboncoin.BASE_URL}")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] All core tests passed!")
    print("\nThe tool is ready to use!")
    print("\nTo try it out:")
    print("1. View sample data in database")
    print("2. Launch dashboard (requires Streamlit)")
    print("3. Try scanning (note: websites may block scrapers)")
    print("\nCommands:")
    print("  py -3 main.py stats        - View database stats")
    print("  py -3 main.py dashboard    - Launch dashboard")
    print("  py -3 main.py scan         - Scan for listings")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)

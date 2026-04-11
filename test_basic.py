"""
Basic test for French Rental Scanner - without actual web scraping
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules import correctly"""
    print("[*] Testing imports...")
    try:
        from scraper.base import BaseScraper
        from scraper.seloger import SeLogerScraper
        from scraper.leboncoin import LeBonCoinScraper
        from database.models import Base, Listing
        from database.connection import DatabaseManager
        print("    [OK] All imports successful")
        return True
    except Exception as e:
        print(f"    [FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database functionality"""
    print("\n[*] Testing database...")
    try:
        from database.connection import DatabaseManager

        # Create test database
        db = DatabaseManager("test_rental.db")
        print("    [OK] Database initialized")

        # Test adding a listing
        test_listing = {
            'listing_id': 'test_001',
            'source': 'SeLoger',
            'url': 'https://example.com/listing/1',
            'title': 'Beautiful Apartment in Paris',
            'description': 'A lovely 2BR apartment in the heart of Paris',
            'price': 1500.0,
            'area': 65.0,
            'location': 'Paris 11eme',
            'city': 'Paris',
            'property_type': 'apartment',
            'features': ['Elevator', 'Balcony', 'Near Metro'],
            'images': ['https://example.com/image1.jpg']
        }

        listing = db.add_listing(test_listing)
        if listing:
            print("    [OK] Test listing added to database")
        else:
            print("    [FAIL] Failed to add test listing")
            return False

        # Test getting listings
        listings = db.get_listings(limit=5)
        if listings:
            print(f"    [OK] Retrieved {len(listings)} listings from database")
            for lst in listings:
                print(f"       - {lst.title}: {lst.price}EUR in {lst.location}")
        else:
            print("    [WARN] No listings found in database")

        # Test stats
        stats = db.get_stats()
        print(f"    [OK] Database stats: {stats['total_listings']} total listings")

        return True

    except Exception as e:
        print(f"    [FAIL] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scraper_init():
    """Test scraper initialization"""
    print("\n[*] Testing scrapers...")
    try:
        from scraper.seloger import SeLogerScraper
        from scraper.leboncoin import LeBonCoinScraper

        seloger = SeLogerScraper()
        print("    [OK] SeLoger scraper initialized")
        print(f"       Name: {seloger.name}")
        print(f"       Base URL: {seloger.BASE_URL}")

        leboncoin = LeBonCoinScraper()
        print("    [OK] LeBonCoin scraper initialized")
        print(f"       Name: {leboncoin.name}")
        print(f"       Base URL: {leboncoin.BASE_URL}")

        return True

    except Exception as e:
        print(f"    [FAIL] Scraper init failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_module():
    """Test main module"""
    print("\n[*] Testing main module...")
    try:
        import main
        print("    [OK] Main module loaded")
        print(f"       Module file: {main.__file__}")
        return True
    except Exception as e:
        print(f"    [FAIL] Main module failed: {e}")
        return False

def main_test():
    """Run all tests"""
    print("=" * 60)
    print("French Rental Scanner - Basic Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Scrapers", test_scraper_init()))
    results.append(("Main Module", test_main_module()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:20s} {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\nThe tool is ready to use!")
        print("\nNext steps:")
        print("1. Test with real data: py -3 main.py scan --location Paris")
        print("2. Launch dashboard: py -3 main.py dashboard")
        return True
    else:
        print("\n[WARNING] Some tests failed. Please fix the errors above.")
        return False

if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)

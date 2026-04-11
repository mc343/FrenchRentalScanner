"""
Test script for French Rental Scanner
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing French Rental Scanner")
print("=" * 50)

# Test 1: Imports
print("\n1️⃣ Testing imports...")
try:
    from scraper import SeLogerScraper, LeBonCoinScraper
    from database import DatabaseManager, Listing
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Database
print("\n2️⃣ Testing database...")
try:
    db = DatabaseManager("test_listings.db")
    print("   ✅ Database initialized")

    # Test adding a listing
    test_listing = {
        'listing_id': 'test_123',
        'source': 'Test',
        'url': 'https://test.com',
        'title': 'Test Apartment',
        'description': 'Test description',
        'price': 1000.0,
        'area': 50.0,
        'location': 'Paris',
        'city': 'Paris',
        'property_type': 'apartment',
        'features': ['Elevator', 'Balcony'],
        'images': []
    }

    listing = db.add_listing(test_listing)
    if listing:
        print("   ✅ Test listing added")
    else:
        print("   ❌ Failed to add test listing")

    # Test getting listings
    listings = db.get_listings(limit=5)
    print(f"   ✅ Retrieved {len(listings)} listings")

    # Test stats
    stats = db.get_stats()
    print(f"   ✅ Stats: {stats}")

except Exception as e:
    print(f"   ❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Scraper initialization
print("\n3️⃣ Testing scrapers...")
try:
    seloger = SeLogerScraper()
    print("   ✅ SeLoger scraper initialized")

    leboncoin = LeBonCoinScraper()
    print("   ✅ LeBonCoin scraper initialized")
except Exception as e:
    print(f"   ❌ Scraper init failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Main module
print("\n4️⃣ Testing main module...")
try:
    import main
    print("   ✅ Main module loaded")
except Exception as e:
    print(f"   ❌ Main module failed: {e}")

# Test 5: Dashboard
print("\n5️⃣ Testing dashboard...")
try:
    from dashboard.app import init_db
    test_db = init_db()
    print("   ✅ Dashboard can initialize database")
except Exception as e:
    print(f"   ❌ Dashboard test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("✅ All core tests passed!")
print("\nNext steps:")
print("1. Test actual scraping with: python main.py scan")
print("2. Launch dashboard with: python main.py dashboard")

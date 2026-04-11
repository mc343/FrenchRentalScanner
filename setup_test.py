"""
French Rental Scanner - Quick Start Guide
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_data():
    """Create sample rental data for testing"""
    from database.connection import DatabaseManager

    print("Creating sample rental data...")
    db = DatabaseManager("rental_listings.db")

    # Sample listings
    listings = [
        {
            'listing_id': 'seloger_001',
            'source': 'SeLoger',
            'url': 'https://www.seloger.com/loc/paris-75/apartment/test1',
            'title': 'Beautiful 2BR in Marais',
            'description': 'Charming apartment in historic Marais district',
            'price': 1800.0,
            'area': 65.0,
            'location': 'Paris 4eme, Marais',
            'city': 'Paris',
            'property_type': 'apartment',
            'features': ['Elevator', 'Balcony', 'Near Metro', 'Renovated'],
            'images': []
        },
        {
            'listing_id': 'leboncoin_001',
            'source': 'LeBonCoin',
            'url': 'https://www.leboncoin.fr/locations/paris/test2',
            'title': 'Modern Studio - Canal Saint-Martin',
            'description': 'Bright studio near Canal Saint-Martin',
            'price': 950.0,
            'area': 28.0,
            'location': 'Paris 10eme, Canal Saint-Martin',
            'city': 'Paris',
            'property_type': 'apartment',
            'features': ['Furnished', 'Near Metro', 'Quiet'],
            'images': []
        },
        {
            'listing_id': 'seloger_002',
            'source': 'SeLoger',
            'url': 'https://www.seloger.com/loc/paris-75/house/test3',
            'title': 'House with Garden - Belleville',
            'description': 'Rare house with private garden in Paris',
            'price': 3200.0,
            'area': 120.0,
            'location': 'Paris 20eme, Belleville',
            'city': 'Paris',
            'property_type': 'house',
            'features': ['Garden', '2 Floors', 'Parking', 'Terrace'],
            'images': []
        }
    ]

    for listing in listings:
        db.add_listing(listing)

    print(f"Created {len(listings)} sample listings")

    # Show stats
    stats = db.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total listings: {stats['total_listings']}")
    print(f"  By source: {stats.get('sources', {})}")

def view_listings():
    """View all listings"""
    from database.connection import DatabaseManager

    db = DatabaseManager("rental_listings.db")
    listings = db.get_listings(limit=20)

    print(f"\nFound {len(listings)} listings:")
    print("-" * 60)

    for lst in listings:
        # Use to_dict method if available
        if hasattr(lst, 'to_dict'):
            data = lst.to_dict()
            print(f"\n{data['title']}")
            print(f"  Source: {data['source']}")
            print(f"  Price: {data['price']} EUR/month")
            print(f"  Area: {data['area']} m2")
            print(f"  Location: {data['location']}")
        else:
            # Access attributes directly within try/except
            try:
                print(f"\n{lst.title}")
                print(f"  Source: {lst.source}")
                print(f"  Price: {lst.price} EUR/month")
                print(f"  Area: {lst.area} m2")
                print(f"  Location: {lst.location}")
            except Exception as e:
                print(f"  Error accessing listing: {e}")

def main():
    print("=" * 60)
    print("French Rental Scanner - Setup & Test")
    print("=" * 60)
    print("\nThis will:")
    print("1. Create sample rental data")
    print("2. Display all listings")
    print("3. Test the dashboard (if Streamlit is installed)")
    print("\nPress Ctrl+C to cancel at any time")
    print("-" * 60)

    try:
        # Create sample data
        create_sample_data()

        # View listings
        view_listings()

        print("\n" + "=" * 60)
        print("Setup complete!")
        print("\nNext steps:")
        print("1. Launch dashboard:")
        print("   py -3 main.py dashboard")
        print("\n2. Or scan for real listings:")
        print("   py -3 main.py scan --location Paris --min-price 500")
        print("\n3. View statistics:")
        print("   py -3 main.py stats")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

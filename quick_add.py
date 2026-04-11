"""
Quick Add Module - Paste rental details from websites
"""
from database.connection import DatabaseManager
import sys


def quick_add():
    """Quick add mode for pasting website data"""
    db = DatabaseManager("rental_listings.db")

    print("\n" + "=" * 60)
    print("QUICK ADD - Paste from Rental Website")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Visit a rental website (SeLoger, LeBonCoin, etc.)")
    print("2. Copy information from the listing")
    print("3. Paste it below")
    print("4. The app will try to extract details")
    print()
    print("-" * 60)

    while True:
        print("\nPaste rental information (or 'menu' to return):")
        print("Example format: '2BR Paris 11eme, 1500 EUR, 45m2'")
        print()

        data = input("Paste here: ").strip()

        if data.lower() in ['menu', 'exit', 'quit', 'back', 'return']:
            print("\nReturning to menu...")
            break

        if not data:
            continue

        # Try to extract information
        listing = extract_listing_info(data)

        if listing:
            print(f"\n[FOUND] {listing['title']}")
            print(f"  Price: {listing['price']} EUR")
            print(f"  Area: {listing['area']} m2")
            print(f"  Location: {listing['location']}")
            print()

            # Ask to confirm
            confirm = input("Add this listing? (Y/n): ").lower()

            if confirm == 'y':
                result = db.add_listing(listing)
                if result:
                    print("\n[SUCCESS] Listing added!")
                else:
                    print("\n[ERROR] Failed to add")
            else:
                print("\n[CANCELLED] Not added")
        else:
            print("\n[INFO] Could not extract details. Please try manual entry.")


def extract_listing_info(text):
    """Extract listing information from pasted text"""
    import re

    listing = {
        'listing_id': f"quick_{hash(text)}",
        'source': 'Manual',
        'url': '',
        'title': '',
        'description': '',
        'price': 0,
        'area': 0,
        'location': '',
        'city': 'Paris',  # Default
        'property_type': 'apartment',
        'features': [],
        'images': []
    }

    # Extract price
    price_patterns = [
        r'(\d+[\s,]?\d*)\s*(?:€|EUR|euros?)',
        r'(\d+)\s*(?:€|EUR)',
        r'price[:\s]*(\d+)',
        r'prix[:\s]*(\d+)',
        r'loyer[:\s]*(\d+)'
    ]

    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(' ', '').replace(',', '.')
            try:
                listing['price'] = float(price_str)
                break
            except:
                continue

    # Extract area
    area_patterns = [
        r'(\d+[\s,]?\d*)\s*(?:m²|m2|sq\.?m)',
        r'(\d+)\s*(?:m²|m2)',
        r'surface[:\s]*(\d+)',
        r'surface[:\s]*(\d+)'
    ]

    for pattern in area_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                listing['area'] = float(match.group(1))
                break
            except:
                continue

    # Extract city/location
    cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice',
              'Nantes', 'Strasbourg', 'Montpellier', 'Bordeaux', 'Lille']

    for city in cities:
        if city.lower() in text.lower():
            listing['city'] = city
            listing['location'] = f"{city} (extracted)"
            break

    # Try to extract title from first 100 characters
    lines = text.split('\n')
    if lines:
        first_line = lines[0][:100]
        # Remove common words
        title_candidates = first_line.replace('€', '').replace('EUR', '').replace('m²', '').replace('m2', '')
        if len(title_candidates) > 10:
            listing['title'] = title_candidates.strip()
        else:
            listing['title'] = "Listing from website"

    # Validate we have minimum info
    if listing['price'] > 0:
        return listing
    else:
        return None


def batch_add():
    """Batch add multiple listings quickly"""
    from database.connection import DatabaseManager

    db = DatabaseManager("rental_listings.db")

    print("\n" + "=" * 60)
    print("BATCH ADD MODE")
    print("=" * 60)
    print()
    print("Add multiple listings quickly")
    print("Format: Title | Price | Area | Location")
    print()
    print("Enter listings one per line, empty line to finish")
    print()

    listings = []

    while True:
        line = input(f"Listing #{len(listings) + 1} (or Enter to finish): ").strip()

        if not line:
            break

        # Try to parse pipe-separated format
        parts = [p.strip() for p in line.split('|')]

        if len(parts) >= 3:
            try:
                listing = {
                    'listing_id': f"batch_{len(listings)}",
                    'source': 'Batch',
                    'url': '',
                    'title': parts[0] if parts[0] else 'Apartment',
                    'description': '',
                    'price': float(parts[1]) if len(parts) > 1 and parts[1].replace('.', '').isdigit() else 1000,
                    'area': float(parts[2]) if len(parts) > 2 and parts[2].replace('.', '').isdigit() else 50,
                    'location': parts[3] if len(parts) > 3 else 'Paris',
                    'city': 'Paris',
                    'property_type': 'apartment',
                    'features': [],
                    'images': []
                }

                listings.append(listing)
                print(f"  [ADDED] {listing['title']} - {listing['price']} EUR")

            except Exception as e:
                print(f"  [ERROR] Invalid format. Use: Title | Price | Area | Location")

    if listings:
        print(f"\n[INFO] Adding {len(listings)} listings to database...")
        count = db.add_listings_batch(listings)
        print(f"[SUCCESS] {count} listings added!")


def format_listing_for_display(listing):
    """Format listing for display"""
    return f"""
Title: {listing['title']}
Price: {listing['price']} EUR/month
Area: {listing['area']} m²
Location: {listing['location']}
Source: {listing['source']}

Paste the listing details from any website and I'll extract the information automatically.
"""


if __name__ == "__main__":
    quick_add()

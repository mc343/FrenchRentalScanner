"""
URL Scraper - Paste rental URLs and extract data automatically
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseManager
import requests
from bs4 import BeautifulSoup
import re


class URLScraper:
    """Scrapes rental data from URLs"""

    def __init__(self):
        self.db = DatabaseManager("rental_listings.db")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_url(self, url):
        """Scrape data from a rental listing URL"""
        try:
            print(f"\nFetching: {url}")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data based on common patterns
            listing = {
                'listing_id': f"url_{hash(url)}",
                'source': self.detect_source(url),
                'url': url,
                'title': self.extract_title(soup, url),
                'description': self.extract_description(soup),
                'price': self.extract_price(soup),
                'area': self.extract_area(soup),
                'location': self.extract_location(soup),
                'city': 'Paris',  # Will try to detect
                'property_type': 'apartment',
                'features': self.extract_features(soup),
                'images': self.extract_images(soup)
            }

            return listing

        except Exception as e:
            print(f"[ERROR] Failed to scrape URL: {e}")
            return None

    def detect_source(self, url):
        """Detect the source website from URL"""
        if 'seloger' in url.lower():
            return 'SeLoger'
        elif 'leboncoin' in url.lower():
            return 'LeBonCoin'
        elif 'logic-immo' in url.lower():
            return 'LogicImmo'
        elif 'pap.fr' in url.lower():
            return 'PAP'
        else:
            return 'Web'

    def extract_title(self, soup, url):
        """Extract title from page"""
        # Try multiple selectors
        selectors = [
            'h1[property="og:title"]',
            'h1.title',
            '.listing-title',
            '.ad-title',
            'h1'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)

        return "Rental Listing"

    def extract_price(self, soup):
        """Extract price from page"""
        price = 0

        # Try different price selectors
        selectors = [
            '.price',
            '.amount',
            '[itemprop="price"]',
            '.price-value'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                # Extract numbers
                match = re.search(r'(\d+[\s,]?\d*)', text)
                if match:
                    try:
                        price = float(match.group(1).replace(' ', '').replace(',', '.'))
                        break
                    except:
                        continue

        return price

    def extract_area(self, soup):
        """Extract area from page"""
        area = 0

        selectors = [
            '.area',
            '.surface',
            '[itemprop="floorSize"]',
            '.surface-area'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    try:
                        area = float(match.group(1))
                        break
                    except:
                        continue

        return area

    def extract_location(self, soup):
        """Extract location from page"""
        # Try meta tags
        city_elem = soup.select_one('[itemprop="addressLocality"]')
        if city_elem:
            return city_elem.get_text(strip=True)

        # Try common patterns
        location_elem = soup.select_one('.location')
        if location_elem:
            return location_elem.get_text(strip=True)

        return "Paris (detect from URL)"

    def extract_description(self, soup):
        """Extract description"""
        selectors = [
            '[itemprop="description"]',
            '.description',
            '.ad-description',
            '.listing-description'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)[:500]  # First 500 chars

        return ""

    def extract_features(self, soup):
        """Extract features/amenities"""
        features = []

        # Look for feature lists
        feature_selectors = [
            '.features li',
            '.amenities li',
            '.equipment li',
            '[itemprop="amenityFeature"]',
            '.criterion li'
        ]

        for selector in feature_selectors:
            elems = soup.select(selector)
            if elems:
                for elem in elems[:10]:  # Max 10 features
                    feature_text = elem.get_text(strip=True)
                    if feature_text and len(feature_text) < 100:
                        features.append(feature_text)
                break

        return features

    def extract_images(self, soup):
        """Extract image URLs"""
        images = []

        # Try different image selectors
        img_selectors = [
            '.gallery img',
            '.photos img',
            '[itemprop="image"]',
            '.carousel img'
        ]

        for selector in img_selectors:
            imgs = soup.select(selector)
            if imgs:
                for img in imgs[:5]:  # Max 5 images
                    src = img.get('data-src') or img.get('src')
                    if src and src.startswith('http'):
                        images.append(src)
                break

        return images


def url_scraper_interface():
    """Interactive URL scraper interface"""
    scraper = URLScraper()

    print("\n" + "=" * 60)
    print("URL SCRAPER MODE")
    print("=" * 60)
    print()
    print("Paste rental listing URLs and I'll extract the data!")
    print()
    print("Supported:")
    print("  - SeLoger.fr")
    print("  - LeBonCoin.fr")
    print("  - Most French rental websites")
    print()
    print("-" * 60)

    while True:
        url = input("Paste URL (or 'menu' to return): ").strip()

        if url.lower() in ['menu', 'exit', 'quit', 'back', 'return']:
            print("\nReturning to menu...")
            break

        if not url:
            continue

        if not url.startswith('http'):
            print("[ERROR] Invalid URL. Must start with http:// or https://")
            continue

        # Scrape the URL
        listing = scraper.scrape_url(url)

        if listing and listing['price'] > 0:
            print(f"\n[SUCCESS] Found listing!")
            print(f"  Title: {listing['title']}")
            print(f"  Price: {listing['price']} EUR")
            print(f"  Area: {listing['area']} m²")
            print(f"  Location: {listing['location']}")
            print()

            # Show features
            if listing['features']:
                print("  Features:")
                for feature in listing['features'][:5]:
                    print(f"    - {feature}")

            print()

            # Ask to confirm
            confirm = input("Add to database? (Y/n): ").lower()

            if confirm == 'y':
                from database.connection import DatabaseManager
                db = DatabaseManager("rental_listings.db")
                result = db.add_listing(listing)

                if result:
                    print("[SUCCESS] Listing added to database!")
                else:
                    print("[ERROR] Failed to add")
            else:
                print("[CANCELLED] Not added")
        else:
            print("[INFO] Could not extract data. Website may be blocking scrapers.")
            print("       Try manual entry instead.")

        print()


if __name__ == "__main__":
    url_scraper_interface()

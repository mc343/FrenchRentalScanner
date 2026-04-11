"""
Selenium Scraper - Real web scraping with JavaScript rendering
"""
import sys
import os
import time
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SeleniumScraper:
    """Scraper using Selenium for JavaScript rendering"""

    def __init__(self, headless=True):
        self.db = DatabaseManager("rental_listings.db")
        self.driver = None
        self.headless = headless

    def init_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            options = Options()

            if self.headless:
                options.add_argument('--headless')

            # Anti-detection options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

            # Set user agent
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)

            return True

        except Exception as e:
            print(f"[ERROR] Failed to initialize driver: {e}")
            print("       Make sure Chrome and ChromeDriver are installed")
            return False

    def scrape_seloger(self, location="Paris", min_price=500, max_price=2500, limit=10):
        """Scrape SeLoger.fr for listings"""
        listings = []

        if not self.init_driver():
            return listings

        try:
            # Build search URL
            url = f"https://www.seloger.com/locations,{location.lower()}_.html?price={max_price}&price={min_price}"

            print(f"[INFO] Navigating to SeLoger...")
            self.driver.get(url)

            # Wait for listings to load
            time.sleep(3)

            # Find listing cards
            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, ".listing-card, .Card__Card-sc-1l28pht-0")

            print(f"[INFO] Found {len(listing_elements)} potential listings")

            for i, elem in enumerate(listing_elements[:limit]):
                try:
                    listing = self._extract_seloger_listing(elem)
                    if listing:
                        listings.append(listing)
                        print(f"  [{i+1}] {listing['title']} - {listing['price']} EUR")
                except Exception as e:
                    print(f"[ERROR] Failed to extract listing {i+1}: {e}")
                    continue

        except TimeoutException:
            print("[ERROR] Page load timeout")
        except Exception as e:
            print(f"[ERROR] Scrape failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        return listings

    def _extract_seloger_listing(self, element):
        """Extract listing data from SeLoger element"""
        try:
            # Title
            title_elem = element.find_element(By.CSS_SELECTOR, "h2, .title, .Card__Title-sc-")
            title = title_elem.text.strip() if title_elem else "Rental Listing"

            # Price
            price = 0
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, ".price, .Price, .amount")
                price_text = price_elem.text
                match = re.search(r'(\d+[\s,]?\d*)', price_text)
                if match:
                    price = float(match.group(1).replace(' ', '').replace(',', '.'))
            except NoSuchElementException:
                pass

            # Area
            area = 0
            try:
                area_elem = element.find_element(By.CSS_SELECTOR, ".surface, .area, .Surface-sc-")
                area_text = area_elem.text
                match = re.search(r'(\d+)', area_text)
                if match:
                    area = float(match.group(1))
            except NoSuchElementException:
                pass

            # Location
            location = "Paris"
            try:
                loc_elem = element.find_element(By.CSS_SELECTOR, ".location, .city, .Geo-sc-")
                location = loc_elem.text.strip()
            except NoSuchElementException:
                pass

            # URL
            url = ""
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a")
                url = link_elem.get_attribute('href')
            except NoSuchElementException:
                pass

            if price > 0:
                return {
                    'listing_id': f"seloger_{hash(url) if url else hash(title)}",
                    'source': 'SeLoger',
                    'url': url,
                    'title': title,
                    'description': '',
                    'price': price,
                    'area': area,
                    'location': location,
                    'city': 'Paris',
                    'property_type': 'apartment',
                    'features': [],
                    'images': []
                }

        except Exception as e:
            print(f"[DEBUG] Extraction error: {e}")

        return None

    def scrape_leboncoin(self, location="Paris", min_price=500, max_price=2500, limit=10):
        """Scrape LeBonCoin.fr for listings"""
        listings = []

        if not self.init_driver():
            return listings

        try:
            # Build search URL
            url = f"https://www.leboncoin.fr/recherche/?category=locations&location={location}&price={min_price}-{max_price}"

            print(f"[INFO] Navigating to LeBonCoin...")
            self.driver.get(url)

            # Wait for listings to load
            time.sleep(3)

            # Accept cookies if present
            try:
                accept_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='cookie-consent-accept']")
                accept_btn.click()
                time.sleep(1)
            except NoSuchElementException:
                pass

            # Find listing cards
            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='listing-card'], .adCard")

            print(f"[INFO] Found {len(listing_elements)} potential listings")

            for i, elem in enumerate(listing_elements[:limit]):
                try:
                    listing = self._extract_leboncoin_listing(elem)
                    if listing:
                        listings.append(listing)
                        print(f"  [{i+1}] {listing['title']} - {listing['price']} EUR")
                except Exception as e:
                    print(f"[ERROR] Failed to extract listing {i+1}: {e}")
                    continue

        except TimeoutException:
            print("[ERROR] Page load timeout")
        except Exception as e:
            print(f"[ERROR] Scrape failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        return listings

    def _extract_leboncoin_listing(self, element):
        """Extract listing data from LeBonCoin element"""
        try:
            # Title
            title_elem = element.find_element(By.CSS_SELECTOR, "h2, p[data-testid='listing-title']")
            title = title_elem.text.strip() if title_elem else "Rental Listing"

            # Price
            price = 0
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='listing-price'], .price")
                price_text = price_elem.text
                match = re.search(r'(\d+[\s,]?\d*)', price_text)
                if match:
                    price = float(match.group(1).replace(' ', '').replace(',', '.'))
            except NoSuchElementException:
                pass

            # Location
            location = "Paris"
            try:
                loc_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='listing-location'], .location")
                location = loc_elem.text.strip()
            except NoSuchElementException:
                pass

            # URL
            url = ""
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a")
                url = link_elem.get_attribute('href')
            except NoSuchElementException:
                pass

            if price > 0:
                return {
                    'listing_id': f"leboncoin_{hash(url) if url else hash(title)}",
                    'source': 'LeBonCoin',
                    'url': url,
                    'title': title,
                    'description': '',
                    'price': price,
                    'area': 0,
                    'location': location,
                    'city': 'Paris',
                    'property_type': 'apartment',
                    'features': [],
                    'images': []
                }

        except Exception as e:
            print(f"[DEBUG] Extraction error: {e}")

        return None

    def scrape_url(self, url):
        """Scrape a specific rental listing URL"""
        if not self.init_driver():
            return None

        try:
            print(f"[INFO] Fetching: {url}")
            self.driver.get(url)

            # Wait for page to load
            time.sleep(3)

            # Detect source
            if 'seloger' in url.lower():
                return self._scrape_seloger_detail()
            elif 'leboncoin' in url.lower():
                return self._scrape_leboncoin_detail()
            else:
                return self._scrape_generic(url)

        except Exception as e:
            print(f"[ERROR] Failed to scrape URL: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def _scrape_seloger_detail(self):
        """Scrape SeLoger detail page"""
        try:
            # Title
            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1, .title")
            title = title_elem.text.strip()

            # Price
            price = 0
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, ".price, .amount, [itemprop='price']")
                price_text = price_elem.text
                match = re.search(r'(\d+[\s,]?\d*)', price_text)
                if match:
                    price = float(match.group(1).replace(' ', '').replace(',', '.'))
            except NoSuchElementException:
                pass

            # Area
            area = 0
            try:
                area_elem = self.driver.find_element(By.CSS_SELECTOR, ".surface, [itemprop='floorSize']")
                area_text = area_elem.text
                match = re.search(r'(\d+)', area_text)
                if match:
                    area = float(match.group(1))
            except NoSuchElementException:
                pass

            # Location
            location = "Paris"
            try:
                loc_elem = self.driver.find_element(By.CSS_SELECTOR, "[itemprop='addressLocality'], .location")
                location = loc_elem.text.strip()
            except NoSuchElementException:
                pass

            # Description
            description = ""
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, "[itemprop='description'], .description")
                description = desc_elem.text.strip()[:500]
            except NoSuchElementException:
                pass

            return {
                'listing_id': f"seloger_detail_{hash(self.driver.current_url)}",
                'source': 'SeLoger',
                'url': self.driver.current_url,
                'title': title,
                'description': description,
                'price': price,
                'area': area,
                'location': location,
                'city': 'Paris',
                'property_type': 'apartment',
                'features': [],
                'images': []
            }

        except Exception as e:
            print(f"[ERROR] Failed to extract SeLoger details: {e}")
            return None

    def _scrape_leboncoin_detail(self):
        """Scrape LeBonCoin detail page"""
        try:
            # Title
            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1, [data-testid='listing-title']")
            title = title_elem.text.strip()

            # Price
            price = 0
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='listing-price'], .price")
                price_text = price_elem.text
                match = re.search(r'(\d+[\s,]?\d*)', price_text)
                if match:
                    price = float(match.group(1).replace(' ', '').replace(',', '.'))
            except NoSuchElementException:
                pass

            # Location
            location = "Paris"
            try:
                loc_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='listing-location'], .location")
                location = loc_elem.text.strip()
            except NoSuchElementException:
                pass

            # Description
            description = ""
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='listing-description'], .description")
                description = desc_elem.text.strip()[:500]
            except NoSuchElementException:
                pass

            return {
                'listing_id': f"leboncoin_detail_{hash(self.driver.current_url)}",
                'source': 'LeBonCoin',
                'url': self.driver.current_url,
                'title': title,
                'description': description,
                'price': price,
                'area': 0,
                'location': location,
                'city': 'Paris',
                'property_type': 'apartment',
                'features': [],
                'images': []
            }

        except Exception as e:
            print(f"[ERROR] Failed to extract LeBonCoin details: {e}")
            return None

    def _scrape_generic(self, url):
        """Generic scraper for unknown websites"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Title
            title = "Rental Listing"
            title_elem = soup.select_one("h1")
            if title_elem:
                title = title_elem.get_text(strip=True)

            # Price
            price = 0
            price_patterns = [r'(\d+[\s,]?\d*)\s*(?:€|EUR|euros?)']
            for pattern in price_patterns:
                for elem in soup.find_all(string=re.compile(pattern)):
                    match = re.search(pattern, str(elem))
                    if match:
                        try:
                            price = float(match.group(1).replace(' ', '').replace(',', '.'))
                            break
                        except:
                            continue

            return {
                'listing_id': f"generic_{hash(url)}",
                'source': 'Web',
                'url': url,
                'title': title,
                'description': '',
                'price': price,
                'area': 0,
                'location': 'Paris',
                'city': 'Paris',
                'property_type': 'apartment',
                'features': [],
                'images': []
            }

        except Exception as e:
            print(f"[ERROR] Generic scrape failed: {e}")
            return None


def selenium_interface():
    """Interactive Selenium scraper interface"""
    print("\n" + "=" * 60)
    print("SELENIUM SCRAPER MODE")
    print("=" * 60)
    print()
    print("Real web scraping with JavaScript rendering")
    print()
    print("Options:")
    print("  [1] Scrape SeLoger.fr")
    print("  [2] Scrape LeBonCoin.fr")
    print("  [3] Scrape specific URL")
    print("  [0] Return to menu")
    print()
    print("-" * 60)

    choice = input("Select option: ").strip()

    scraper = SeleniumScraper(headless=False)

    if choice == '1':
        location = input("Location (default: Paris): ").strip() or "Paris"
        min_price = input("Min price (default: 500): ").strip() or "500"
        max_price = input("Max price (default: 2500): ").strip() or "2500"
        limit = input("Max listings (default: 10): ").strip() or "10"

        listings = scraper.scrape_seloger(location, int(min_price), int(max_price), int(limit))

        if listings:
            print(f"\n[SUCCESS] Found {len(listings)} listings")
            for listing in listings:
                print(f"  - {listing['title']}: {listing['price']} EUR")

            confirm = input("\nAdd all to database? (Y/n): ").lower()
            if confirm == 'y':
                db = DatabaseManager("rental_listings.db")
                count = db.add_listings_batch(listings)
                print(f"[SUCCESS] {count} listings added!")
        else:
            print("[INFO] No listings found")

    elif choice == '2':
        location = input("Location (default: Paris): ").strip() or "Paris"
        min_price = input("Min price (default: 500): ").strip() or "500"
        max_price = input("Max price (default: 2500): ").strip() or "2500"
        limit = input("Max listings (default: 10): ").strip() or "10"

        listings = scraper.scrape_leboncoin(location, int(min_price), int(max_price), int(limit))

        if listings:
            print(f"\n[SUCCESS] Found {len(listings)} listings")
            for listing in listings:
                print(f"  - {listing['title']}: {listing['price']} EUR")

            confirm = input("\nAdd all to database? (Y/n): ").lower()
            if confirm == 'y':
                db = DatabaseManager("rental_listings.db")
                count = db.add_listings_batch(listings)
                print(f"[SUCCESS] {count} listings added!")
        else:
            print("[INFO] No listings found")

    elif choice == '3':
        url = input("Enter URL: ").strip()
        if url.startswith('http'):
            listing = scraper.scrape_url(url)
            if listing and listing['price'] > 0:
                print(f"\n[SUCCESS] Found listing!")
                print(f"  Title: {listing['title']}")
                print(f"  Price: {listing['price']} EUR")
                print(f"  Area: {listing['area']} m²")

                confirm = input("\nAdd to database? (Y/n): ").lower()
                if confirm == 'y':
                    db = DatabaseManager("rental_listings.db")
                    result = db.add_listing(listing)
                    if result:
                        print("[SUCCESS] Listing added!")
            else:
                print("[INFO] Could not extract data")
        else:
            print("[ERROR] Invalid URL")


if __name__ == "__main__":
    selenium_interface()

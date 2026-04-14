"""
SeLoger.fr scraper - One of France's largest rental websites
"""
from typing import List, Dict
from urllib.parse import urljoin
from .base import BaseScraper, logger
import re


class SeLogerScraper(BaseScraper):
    """Scraper for SeLoger.fr"""

    BASE_URL = "https://www.seloger.com"

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "SeLoger"

    def search(self, filters: Dict) -> List[Dict]:
        """Search SeLoger with filters

        Filters:
            - location: City or department (e.g., "Paris", "75")
            - min_price: Minimum rent
            - max_price: Maximum rent
            - min_area: Minimum area in m²
            - max_area: Maximum area in m²
            - property_type: "apartment", "house", or "all"
        """
        logger.info(f"Searching SeLoger with filters: {filters}")

        listings = []
        page = 1
        max_pages = 5  # Limit to prevent infinite loops

        while page <= max_pages:
            url = self._build_search_url(filters, page)
            soup = self.get_page(url)

            if not soup:
                break

            page_listings = self._parse_search_results(soup)
            if not page_listings:
                break

            listings.extend(page_listings)
            logger.info(f"Found {len(page_listings)} listings on page {page}")
            page += 1

        return listings

    def _build_search_url(self, filters: Dict, page: int = 1) -> str:
        """Build search URL with filters"""
        # Get location (city code or name)
        location = filters.get('location', 'Paris')
        min_price = filters.get('min_price', 0)
        max_price = filters.get('max_price', 99999)
        min_area = filters.get('min_area', 0)
        max_area = filters.get('max_area', 9999)
        property_type = filters.get('property_type', 'all')

        # Build URL parameters
        params = []
        params.append(f"projects=2")  # 2 = rental

        # Price range
        params.append(f"price={min_price}/{max_price}")

        # Area range
        params.append(f"surface={min_area}/{max_area}")

        # Property type
        if property_type == "apartment":
            params.append("type=1")  # 1 = apartment
        elif property_type == "house":
            params.append("type=2")  # 2 = house

        # Build query string
        query = "/".join(params)
        url = f"{self.BASE_URL}/recherche,{query}?page={page}"

        return url

    def _parse_search_results(self, soup) -> List[Dict]:
        """Parse search results page"""
        listings = []

        # SeLoger listing cards (adjust selectors based on actual HTML)
        listing_cards = soup.select(
            'div.ListingContainer, article[data-testid="listing-card"], article[class*="listing-card"]'
        )

        for card in listing_cards:
            try:
                listing = {
                    'source': self.name,
                    'url': self._extract_url(card),
                    'title': self._extract_title(card),
                    'price': self._extract_price(card),
                    'area': self._extract_area(card),
                    'location': self._extract_location(card),
                    'description': self._extract_description(card),
                    'images': self._extract_images(card),
                    'features': self._extract_features(card)
                }

                availability_text = " ".join(
                    part for part in [listing['title'], listing['description'], " ".join(listing['features'])]
                    if part
                )
                listing['available_date'] = self.extract_available_date(availability_text)

                if listing['url']:
                    listings.append(self.normalize_listing_data(listing))

            except Exception as e:
                logger.warning(f"Error parsing listing card: {e}")
                continue

        return listings

    def _extract_url(self, card) -> str:
        """Extract listing URL"""
        selectors = [
            'a.CartoSummary__link',
            'a[data-testid="sl.explore.coveringLink"]',
            'a[href*="/annonces/"]',
            'a[href*="/locations/"]',
        ]
        for selector in selectors:
            link = card.select_one(selector)
            if link and link.get('href'):
                return urljoin(self.BASE_URL, link.get('href'))
        return ''

    def _extract_title(self, card) -> str:
        """Extract listing title"""
        selectors = [
            'div.ListingContainer__title',
            '[data-testid="sl.title"]',
            'h2',
            'h3',
        ]
        return self._extract_text_by_selectors(card, selectors)

    def _extract_price(self, card) -> float:
        """Extract price"""
        selectors = [
            'div.ListingContainer__price',
            '[data-testid="sl.price"]',
            '[class*="price"]',
        ]
        price_text = self._extract_text_by_selectors(card, selectors)
        return self.extract_price(price_text or card.get_text(" ", strip=True)) or 0.0

    def _extract_area(self, card) -> float:
        """Extract area"""
        selectors = [
            'div.ListingContainer__surface',
            '[data-testid="sl.surface"]',
            '[class*="surface"]',
        ]
        area_text = self._extract_text_by_selectors(card, selectors)
        return self.extract_area(area_text or card.get_text(" ", strip=True)) or 0.0

    def _extract_location(self, card) -> str:
        """Extract location"""
        selectors = [
            'div.ListingContainer__location',
            '[data-testid="sl.location"]',
            '[class*="location"]',
            '[class*="address"]',
        ]
        return self._extract_text_by_selectors(card, selectors)

    def _extract_description(self, card) -> str:
        """Extract description"""
        selectors = [
            'div.ListingContainer__description',
            '[data-testid="sl.description"]',
            '[class*="description"]',
            'p',
        ]
        return self._extract_text_by_selectors(card, selectors)

    def _extract_images(self, card) -> List[str]:
        """Extract image URLs"""
        images = []
        img_elems = card.select('img')
        for img in img_elems:
            src = img.get('data-src') or img.get('src') or img.get('data-lazy')
            if src:
                images.append(urljoin(self.BASE_URL, src))
            srcset = img.get('srcset')
            if srcset:
                for candidate in srcset.split(','):
                    image_url = candidate.strip().split(' ')[0]
                    if image_url:
                        images.append(urljoin(self.BASE_URL, image_url))
        return images

    def _extract_features(self, card) -> List[str]:
        """Extract features/amenities"""
        features = []
        feature_elems = card.select(
            'div.ListingContainer__feature, [data-testid="sl.tags"] *, [class*="feature"], li, span'
        )
        for feat in feature_elems:
            feature_text = self.clean_text(feat.get_text(" ", strip=True))
            if feature_text and len(feature_text) < 80:
                features.append(feature_text)
        return features

    def parse_listing(self, url: str) -> Dict:
        """Parse individual listing page for full details"""
        soup = self.get_page(f"{self.BASE_URL}{url}")
        if not soup:
            return {}

        # Extract detailed information from individual page
        # This would include more features, detailed description, contact info, etc.

        return {
            'url': url,
            'detailed_features': self._parse_detailed_features(soup),
            'contact_info': self._parse_contact_info(soup),
            'full_description': self._parse_full_description(soup)
        }

    def _parse_detailed_features(self, soup) -> Dict:
        """Parse detailed features from listing page"""
        features = {}
        # Implementation would extract all features
        return features

    def _parse_contact_info(self, soup) -> Dict:
        """Parse contact information"""
        contact = {}
        # Implementation would extract phone, email, agency info
        return contact

    def _parse_full_description(self, soup) -> str:
        """Parse full description text"""
        desc_elem = soup.find('div', class_='Description__text')
        return self.clean_text(desc_elem.text) if desc_elem else ''

    def _extract_text_by_selectors(self, node, selectors: List[str]) -> str:
        """Return the first non-empty text found from a selector list."""
        for selector in selectors:
            element = node.select_one(selector)
            if element:
                text = self.clean_text(element.get_text(" ", strip=True))
                if text:
                    return text
        return ''

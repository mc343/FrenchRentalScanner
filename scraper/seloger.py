"""
SeLoger.fr scraper - One of France's largest rental websites
"""
from typing import List, Dict
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
        listing_cards = soup.find_all('div', class_='ListingContainer')

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

                if listing['url']:
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Error parsing listing card: {e}")
                continue

        return listings

    def _extract_url(self, card) -> str:
        """Extract listing URL"""
        link = card.find('a', class_='CartoSummary__link')
        if link:
            return link.get('href', '')
        return ''

    def _extract_title(self, card) -> str:
        """Extract listing title"""
        title_elem = card.find('div', class_='ListingContainer__title')
        return self.clean_text(title_elem.text) if title_elem else ''

    def _extract_price(self, card) -> float:
        """Extract price"""
        price_elem = card.find('div', class_='ListingContainer__price')
        if price_elem:
            return self.extract_price(price_elem.text)
        return 0.0

    def _extract_area(self, card) -> float:
        """Extract area"""
        area_elem = card.find('div', class_='ListingContainer__surface')
        if area_elem:
            return self.extract_area(area_elem.text)
        return 0.0

    def _extract_location(self, card) -> str:
        """Extract location"""
        loc_elem = card.find('div', class_='ListingContainer__location')
        return self.clean_text(loc_elem.text) if loc_elem else ''

    def _extract_description(self, card) -> str:
        """Extract description"""
        desc_elem = card.find('div', class_='ListingContainer__description')
        return self.clean_text(desc_elem.text) if desc_elem else ''

    def _extract_images(self, card) -> List[str]:
        """Extract image URLs"""
        images = []
        img_elems = card.find_all('img', class_='ListingContainer__image')
        for img in img_elems:
            src = img.get('data-src') or img.get('src')
            if src:
                images.append(src)
        return images

    def _extract_features(self, card) -> List[str]:
        """Extract features/amenities"""
        features = []
        feature_elems = card.find_all('div', class_='ListingContainer__feature')
        for feat in feature_elems:
            features.append(self.clean_text(feat.text))
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

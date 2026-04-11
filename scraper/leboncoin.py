"""
LeBonCoin.fr scraper - France's most popular classifieds website
"""
from typing import List, Dict
from .base import BaseScraper, logger
import json


class LeBonCoinScraper(BaseScraper):
    """Scraper for LeBonCoin.fr"""

    BASE_URL = "https://www.leboncoin.fr"

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "LeBonCoin"
        # LeBonCoin uses API for search
        self.api_url = "https://api.leboncoin.fr/finder/classified"

    def search(self, filters: Dict) -> List[Dict]:
        """Search LeBonCoin with filters

        Filters:
            - location: City, department, or region (e.g., "Paris 75", "Île-de-France")
            - min_price: Minimum rent
            - max_price: Maximum rent
            - min_area: Minimum area in m²
            - max_area: Maximum area in m²
            - category: "locations" (rentals)
        """
        logger.info(f"Searching LeBonCoin with filters: {filters}")

        listings = []
        page = 1
        max_pages = 5

        while page <= max_pages:
            # LeBonCoin uses API for search results
            api_data = self._build_api_query(filters, page)
            listings_data = self._fetch_api_results(api_data)

            if not listings_data:
                break

            page_listings = self._parse_api_results(listings_data)
            if not page_listings:
                break

            listings.extend(page_listings)
            logger.info(f"Found {len(page_listings)} listings on page {page}")
            page += 1

        return listings

    def _build_api_query(self, filters: Dict, page: int = 1) -> Dict:
        """Build API query for LeBonCoin"""
        location = filters.get('location', 'Paris')
        min_price = filters.get('min_price', 0)
        max_price = filters.get('max_price', 99999)
        min_area = filters.get('min_area', 0)
        max_area = filters.get('max_area', 9999)

        # Build query parameters
        query = {
            "limit": 35,
            "offset": (page - 1) * 35,
            "filters": {
                "category": {"id": "10"},  # 10 = Locations
                "location": {
                    "city": location,
                    "region": "",
                    "department": ""
                },
                "ranges": {
                    "price": {
                        "min": min_price,
                        "max": max_price
                    },
                    "square": {
                        "min": min_area,
                        "max": max_area
                    }
                },
                "enums": {
                    "ad_type": ["offer"],
                    "real_estate_type": ["flat", "house"]  # Both apartments and houses
                }
            },
            "sort_by": "time_created",  # Sort by newest
            "sort_order": "desc"
        }

        return query

    def _fetch_api_results(self, query: Dict) -> Dict:
        """Fetch results from LeBonCoin API"""
        try:
            response = self.session.post(
                self.api_url,
                json=query,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'api_key': 'ba0c2d52-3c9e-4b34-8b61-3162982b18c5'  # Public API key
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {}

    def _parse_api_results(self, data: Dict) -> List[Dict]:
        """Parse API response data"""
        listings = []

        if not data.get('ads'):
            return listings

        for ad in data['ads']:
            try:
                listing = {
                    'source': self.name,
                    'url': ad.get('url', ''),
                    'title': ad.get('subject', ''),
                    'price': ad.get('price', {}).get('price', [0])[0] if ad.get('price') else 0,
                    'area': self._extract_area_from_dict(ad),
                    'location': self._extract_location_from_dict(ad),
                    'description': ad.get('body', ''),
                    'images': self._extract_images_from_dict(ad),
                    'features': self._extract_features_from_dict(ad),
                    'listing_id': ad.get('list_id', ''),
                    'publication_date': ad.get('publication_date', ''),
                    'is_urgent': ad.get('urgent', False)
                }

                if listing['url']:
                    listings.append(listing)

            except Exception as e:
                logger.warning(f"Error parsing API listing: {e}")
                continue

        return listings

    def _extract_area_from_dict(self, ad: Dict) -> float:
        """Extract area from API data"""
        attributes = ad.get('attributes', {}) or {}
        if isinstance(attributes, list):
            for attr in attributes:
                if attr.get('key') == 'square':
                    return float(attr.get('value', 0))
        return 0.0

    def _extract_location_from_dict(self, ad: Dict) -> str:
        """Extract location from API data"""
        location = ad.get('location', {}) or {}
        city = location.get('city', {})
        if isinstance(city, dict):
            return city.get('name', '')
        return str(city) if city else ''

    def _extract_images_from_dict(self, ad: Dict) -> List[str]:
        """Extract image URLs from API data"""
        images = ad.get('images', {}) or {}
        if isinstance(images, dict):
            urls = images.get('urls', {}) or {}
            if isinstance(urls, dict):
                return list(urls.values())
        return []

    def _extract_features_from_dict(self, ad: Dict) -> List[str]:
        """Extract features from API data"""
        features = []
        attributes = ad.get('attributes', []) or []

        if isinstance(attributes, list):
            for attr in attributes:
                if isinstance(attr, dict):
                    key = attr.get('key', '')
                    value = attr.get('value', '')
                    if key and value:
                        features.append(f"{key}: {value}")

        return features

    def parse_listing(self, url: str) -> Dict:
        """Parse individual listing page"""
        soup = self.get_page(url)
        if not soup:
            return {}

        # Extract data from script tags (LeBonCoin stores data in JSON)
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if 'ad' in data:
                    return self._parse_listing_data(data['ad'])
            except:
                continue

        return {}

    def _parse_listing_data(self, ad_data: Dict) -> Dict:
        """Parse listing data from JSON"""
        return {
            'url': ad_data.get('url', ''),
            'title': ad_data.get('subject', ''),
            'body': ad_data.get('body', ''),
            'price': ad_data.get('price', 0),
            'location': ad_data.get('location', {}),
            'images': ad_data.get('images', {}).get('urls', {}),
            'attributes': ad_data.get('attributes', []),
            'contact_phone': ad_data.get('phone', ''),
            'contact_name': ad_data.get('owner', {}).get('name', '')
        }

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

        self.last_error = None
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
            self.last_error = str(e)
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
                    'price': self._extract_price_from_dict(ad),
                    'area': self._extract_area_from_dict(ad),
                    'location': self._extract_location_from_dict(ad),
                    'description': ad.get('body', ''),
                    'images': self._extract_images_from_dict(ad),
                    'features': self._extract_features_from_dict(ad),
                    'listing_id': ad.get('list_id', ''),
                    'publication_date': ad.get('publication_date', ''),
                    'property_type': self._extract_property_type(ad),
                    'rooms': self._extract_numeric_attribute(ad, {'rooms', 'rooms_number'}),
                    'bedrooms': self._extract_numeric_attribute(ad, {'bedrooms', 'bedrooms_number'}),
                    'furnished': self._extract_boolean_attribute(ad, {'furnished'}),
                    'is_urgent': ad.get('urgent', False)
                }

                availability_text = " ".join(
                    part for part in [listing['title'], listing['description'], " ".join(listing['features'])]
                    if part
                )
                listing['available_date'] = self.extract_available_date(availability_text)

                if listing['url']:
                    listings.append(self.normalize_listing_data(listing))

            except Exception as e:
                logger.warning(f"Error parsing API listing: {e}")
                continue

        return listings

    def _extract_area_from_dict(self, ad: Dict) -> float:
        """Extract area from API data"""
        return self._extract_numeric_attribute(ad, {'square', 'living_area'}) or 0.0

    def _extract_price_from_dict(self, ad: Dict) -> float:
        """Extract price from API data."""
        price = ad.get('price')
        if isinstance(price, dict):
            values = price.get('price', [])
            if isinstance(values, list) and values:
                return float(values[0] or 0)
        if isinstance(price, (int, float)):
            return float(price)
        return 0.0

    def _extract_location_from_dict(self, ad: Dict) -> str:
        """Extract location from API data"""
        location = ad.get('location', {}) or {}
        city = location.get('city', {})
        zipcode = location.get('zipcode') or location.get('zip_code') or ''
        if isinstance(city, dict):
            city_name = city.get('name', '')
        else:
            city_name = str(city) if city else ''
        pieces = [part for part in [city_name, zipcode] if part]
        return " ".join(pieces)

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
                    value = attr.get('value_label') or attr.get('value', '')
                    if key and value:
                        label = attr.get('label') or key.replace('_', ' ')
                        features.append(f"{label}: {value}")

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
            'description': ad_data.get('body', ''),
            'price': self._extract_price_from_dict(ad_data),
            'location': self._extract_location_from_dict(ad_data),
            'images': self._extract_images_from_dict(ad_data),
            'features': self._extract_features_from_dict(ad_data),
            'property_type': self._extract_property_type(ad_data),
            'rooms': self._extract_numeric_attribute(ad_data, {'rooms', 'rooms_number'}),
            'bedrooms': self._extract_numeric_attribute(ad_data, {'bedrooms', 'bedrooms_number'}),
            'furnished': self._extract_boolean_attribute(ad_data, {'furnished'}),
            'contact_info': {
                'phone': ad_data.get('phone', ''),
                'name': ad_data.get('owner', {}).get('name', '')
            }
        }

    def _extract_property_type(self, ad: Dict) -> str:
        """Extract property type from API data."""
        raw = self._extract_attribute_value(ad, {'real_estate_type', 'type'})
        mapping = {
            'flat': 'apartment',
            'appartement': 'apartment',
            'apartment': 'apartment',
            'house': 'house',
            'maison': 'house',
            'studio': 'studio',
        }
        return mapping.get(str(raw).lower(), '')

    def _extract_numeric_attribute(self, ad: Dict, keys: set) -> float:
        """Extract numeric attribute from API data."""
        value = self._extract_attribute_value(ad, keys)
        if value in (None, ''):
            return 0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0

    def _extract_boolean_attribute(self, ad: Dict, keys: set) -> bool:
        """Extract boolean-like attribute from API data."""
        value = self._extract_attribute_value(ad, keys)
        if isinstance(value, bool):
            return value
        return str(value).lower() in {'1', 'true', 'yes', 'oui'}

    def _extract_attribute_value(self, ad: Dict, keys: set):
        """Extract raw attribute value from LeBonCoin API data."""
        attributes = ad.get('attributes', []) or []
        if isinstance(attributes, list):
            for attr in attributes:
                if isinstance(attr, dict) and attr.get('key') in keys:
                    return attr.get('value')
        return None

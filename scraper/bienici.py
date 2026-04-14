"""
Bien'ici scraper - automated rental search via Bien'ici JSON endpoints.
"""
from datetime import datetime
from typing import Dict, List, Optional

from .base import BaseScraper, logger


class BieniciScraper(BaseScraper):
    """Scraper for Bien'ici rental listings."""

    BASE_URL = "https://www.bienici.com"
    SEARCH_URL = f"{BASE_URL}/realEstateAds.json"
    DETAIL_URL = f"{BASE_URL}/realEstateAd.json"
    LOCATION_NAME_MAP = {
        "Huningue": "Huningue-68330",
        "Mulhouse": "Mulhouse-68100",
    }
    LOCATION_RULES = {
        "Huningue": {"city": "Huningue", "postal_codes": {"68330"}},
        "Mulhouse": {"city": "Mulhouse", "postal_codes": {"68100", "68200"}},
    }

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "Bienici"

    def search(self, filters: Dict) -> List[Dict]:
        """Search Bien'ici for rental listings."""
        self.last_error = None
        logger.info(f"Searching Bien'ici with filters: {filters}")

        listings = []
        page_size = 60
        max_pages = 3

        for page_index in range(max_pages):
            payload = self._build_filters_payload(filters, page_index * page_size, page_size)
            data = self._request_json(self.SEARCH_URL, {"filters": self._json_dumps(payload)})
            if not data:
                break

            ads = data.get("realEstateAds") or []
            if not ads:
                break

            page_listings = [self._parse_ad(ad) for ad in ads]
            page_listings = [
                listing for listing in page_listings
                if listing and self._matches_filters(listing, filters)
            ]
            listings.extend(page_listings)

            total = data.get("total") or 0
            if (page_index + 1) * page_size >= total:
                break

        return listings

    def parse_listing(self, url: str) -> Dict:
        """Parse a Bien'ici ad from a detail URL or ad id."""
        ad_id = self._extract_listing_id(url)
        if not ad_id:
            return {}
        return self.fetch_listing_by_id(ad_id) or {}

    def fetch_listing_by_id(self, ad_id: str) -> Optional[Dict]:
        """Fetch a single Bien'ici listing by its ad id."""
        self.last_error = None
        data = self._request_json(self.DETAIL_URL, {"id": ad_id})
        if not data:
            return None
        return self._parse_ad(data)

    def _build_filters_payload(self, filters: Dict, offset: int, size: int) -> Dict:
        """Build the Bien'ici filters payload."""
        property_type = (filters.get("property_type") or "all").lower()
        property_types = ["flat", "house"]
        if property_type == "apartment":
            property_types = ["flat"]
        elif property_type == "house":
            property_types = ["house"]

        location = filters.get("location") or "Huningue"
        location_name = self.LOCATION_NAME_MAP.get(location, location)

        payload = {
            "size": size,
            "from": offset,
            "filterType": "rent",
            "propertyType": property_types,
            "locationNames": [location_name],
            "onTheMarket": [True],
            "minPrice": filters.get("min_price", 0),
            "maxPrice": filters.get("max_price", 99999),
            "minArea": filters.get("min_area", 0),
            "maxArea": filters.get("max_area", 9999),
        }
        return payload

    def _request_json(self, url: str, params: Dict) -> Optional[Dict]:
        """Request a JSON payload from Bien'ici."""
        try:
            response = self.session.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            self.last_error = str(exc)
            logger.error(f"Bien'ici request failed: {exc}")
            return None

    def _parse_ad(self, ad: Dict) -> Optional[Dict]:
        """Normalize a Bien'ici ad into the app listing format."""
        listing_id = ad.get("id")
        if not listing_id:
            return None

        photos = ad.get("photos") or []
        images = [photo.get("url") for photo in photos if photo.get("url")]
        rooms = ad.get("roomsQuantity")
        description = ad.get("description") or ""
        city = ad.get("city") or ""
        postal_code = ad.get("postalCode") or ""
        location = " ".join(part for part in [city, postal_code] if part)

        listing = {
            "listing_id": listing_id,
            "source": self.name,
            "url": f"{self.DETAIL_URL}?id={listing_id}",
            "title": (ad.get("title") or "").strip() or f"{city} rental",
            "description": description,
            "price": float(ad.get("price") or 0),
            "area": float(ad.get("surfaceArea") or 0),
            "location": location,
            "city": city,
            "property_type": self._map_property_type(ad.get("propertyType")),
            "rooms": float(rooms) if rooms is not None else None,
            "features": self._build_features(ad),
            "images": images,
            "publication_date": self._normalize_datetime_like(ad.get("publicationDate")),
            "contact_info": {
                "reference": ad.get("reference"),
                "account_type": ad.get("accountType"),
            },
        }

        listing["available_date"] = self.extract_available_date(
            " ".join([listing["title"], listing["description"], " ".join(listing["features"])])
        )

        return self.normalize_listing_data(listing)

    def _build_features(self, ad: Dict) -> List[str]:
        """Build feature labels from a Bien'ici ad."""
        features = []
        rooms = ad.get("roomsQuantity")
        if rooms:
            features.append(f"Rooms: {rooms}")
        if ad.get("safetyDeposit"):
            features.append(f"Deposit: EUR {ad['safetyDeposit']}")
        if ad.get("agencyRentalFee"):
            features.append(f"Agency fee: EUR {ad['agencyRentalFee']}")
        if ad.get("energyClassification"):
            features.append(f"Energy: {ad['energyClassification']}")
        if ad.get("greenhouseGazClassification"):
            features.append(f"GHG: {ad['greenhouseGazClassification']}")
        if ad.get("newProperty"):
            features.append("New property")
        return features

    def _matches_filters(self, listing: Dict, filters: Dict) -> bool:
        """Apply local safety filters because the remote endpoint can be loose."""
        location = filters.get("location") or "Huningue"
        rule = self.LOCATION_RULES.get(location)
        if rule:
            city = str(listing.get("city") or "").casefold()
            postal = str(listing.get("location") or "").split()[-1] if listing.get("location") else ""
            if city != rule["city"].casefold():
                return False
            if rule["postal_codes"] and postal not in rule["postal_codes"]:
                return False

        price = float(listing.get("price") or 0)
        area = float(listing.get("area") or 0)
        min_price = float(filters.get("min_price") or 0)
        max_price = float(filters.get("max_price") or 999999)
        min_area = float(filters.get("min_area") or 0)
        max_area = float(filters.get("max_area") or 999999)
        if price < min_price or price > max_price:
            return False
        if area and (area < min_area or area > max_area):
            return False

        property_type = (filters.get("property_type") or "all").lower()
        if property_type != "all" and listing.get("property_type") != property_type:
            return False

        return True

    def _map_property_type(self, value: Optional[str]) -> str:
        """Map Bien'ici property type labels to app labels."""
        mapping = {
            "flat": "apartment",
            "house": "house",
            "apartment": "apartment",
            "studio": "studio",
        }
        return mapping.get(str(value or "").lower(), "apartment")

    def _extract_listing_id(self, url: str) -> Optional[str]:
        """Extract a Bien'ici ad id from a detail URL."""
        if not url:
            return None
        if "id=" in url:
            return url.split("id=", 1)[1].split("&", 1)[0]
        return url if url.startswith("ag") else None

    def _json_dumps(self, value: Dict) -> str:
        """Serialize payload to compact JSON."""
        import json

        return json.dumps(value, separators=(",", ":"))

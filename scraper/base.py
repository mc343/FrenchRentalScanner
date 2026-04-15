"""
Base scraper class for French rental websites.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all rental website scrapers."""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.session = requests.Session()
        # Corporate or stale local proxy variables can break direct site access.
        # Default to direct connections unless a scraper is explicitly configured otherwise.
        if not self.config.get("use_env_proxy", False):
            self.session.trust_env = False
            self.session.proxies.clear()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        self.listings = []
        self.last_error = None

    @abstractmethod
    def search(self, filters: Dict) -> List[Dict]:
        """Search for listings with given filters."""

    @abstractmethod
    def parse_listing(self, url: str) -> Dict:
        """Parse individual listing page."""

    def get_page(self, url: str, retry: int = 3) -> Optional[BeautifulSoup]:
        """Fetch page with retry logic."""
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, "html.parser")
            except Exception as exc:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {exc}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {retry} attempts")
                    return None

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text."""
        import re

        match = re.search(r"(\d+[\d\s,.'\"]*)\s*(?:EUR|EUROS?|\\u20ac)", text or "", re.IGNORECASE)
        if match:
            cleaned = (
                match.group(1)
                .replace("'", "")
                .replace(" ", "")
                .replace(",", "")
            )
            return float(cleaned)
        return None

    def extract_area(self, text: str) -> Optional[float]:
        """Extract area in square meters."""
        import re

        match = re.search(r"(\d+[\s,]?\d*)\s*(?:m2|sqm|sq\.?m)", text or "", re.IGNORECASE)
        if match:
            return float(match.group(1).replace(" ", "").replace(",", "."))
        return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        return " ".join((text or "").split())

    def normalize_listing_data(self, listing: Dict) -> Dict:
        """Normalize common listing fields before persistence."""
        listing = dict(listing)

        title = self.clean_text(str(listing.get("title", "") or ""))
        description = self.clean_text(str(listing.get("description", "") or ""))
        location = self.clean_text(str(listing.get("location", "") or ""))
        source = self.clean_text(str(listing.get("source", "") or ""))

        features = listing.get("features") or []
        if isinstance(features, str):
            features = [features]
        features = [self.clean_text(str(feature)) for feature in features if str(feature).strip()]

        images = listing.get("images") or []
        if isinstance(images, str):
            images = [images]
        deduped_images = []
        seen_images = set()
        for image in images:
            image = str(image).strip()
            if image and image not in seen_images:
                deduped_images.append(image)
                seen_images.add(image)

        property_blob = " ".join([title, description, " ".join(features)]).lower()
        property_type = str(listing.get("property_type", "") or "").lower()
        if not property_type or property_type == "all":
            if "studio" in property_blob:
                property_type = "studio"
            elif "house" in property_blob or "maison" in property_blob:
                property_type = "house"
            else:
                property_type = "apartment"

        city = self._infer_city(location, title, description)
        department = self._infer_department(location)

        feature_blob = " ".join(features).lower()
        listing.update(
            {
                "title": title or "Untitled listing",
                "description": description,
                "location": location or city or "",
                "source": source,
                "features": features,
                "images": deduped_images,
                "property_type": property_type,
                "city": listing.get("city") or city or "",
                "department": listing.get("department") or department or "",
                "has_elevator": listing.get("has_elevator", False)
                or any(token in feature_blob for token in ["elevator", "ascenseur", "lift"]),
                "has_parking": listing.get("has_parking", False)
                or any(token in feature_blob for token in ["parking", "garage"]),
                "has_balcony": listing.get("has_balcony", False)
                or any(token in feature_blob for token in ["balcony", "balcon", "terrace", "terrasse"]),
                "has_garden": listing.get("has_garden", False)
                or any(token in feature_blob for token in ["garden", "jardin"]),
                "furnished": listing.get("furnished", False)
                or any(token in feature_blob for token in ["furnished", "meubl", "meuble"]),
            }
        )

        if not listing.get("available_date"):
            listing["available_date"] = self.extract_available_date(
                " ".join([title, description, " ".join(features)])
            )
        else:
            listing["available_date"] = self._normalize_datetime_like(listing.get("available_date"))

        if listing.get("publication_date"):
            listing["publication_date"] = self._normalize_datetime_like(listing.get("publication_date"))

        return listing

    def _infer_city(self, *texts: str) -> str:
        """Infer common city names from listing text."""
        cities = [
            "Paris",
            "Lyon",
            "Marseille",
            "Toulouse",
            "Nice",
            "Nantes",
            "Strasbourg",
            "Montpellier",
            "Bordeaux",
            "Lille",
            "Rennes",
            "Grenoble",
            "Aix-en-Provence",
        ]
        haystack = " ".join(texts).lower()
        for city in cities:
            if city.lower() in haystack:
                return city
        return ""

    def _infer_department(self, text: str) -> str:
        """Infer French department code from text."""
        import re

        if not text:
            return ""
        postal_match = re.search(r"\b((?:0[1-9]|[1-8][0-9]|9[0-5]))\d{3}\b", text)
        if postal_match:
            return postal_match.group(1)
        match = re.search(r"\b(0[1-9]|[1-8][0-9]|9[0-5])\b", text)
        return match.group(1) if match else ""

    def _normalize_datetime_like(self, value):
        """Parse common datetime-like values into datetime objects."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            text = text.replace("Z", "+00:00")
            for parser in (
                lambda item: datetime.fromisoformat(item),
                lambda item: datetime.strptime(item, "%Y-%m-%d"),
                lambda item: datetime.strptime(item, "%d/%m/%Y"),
            ):
                try:
                    return parser(text)
                except ValueError:
                    continue
        return None

    def extract_available_date(self, text: str) -> Optional[datetime]:
        """Extract approximate availability date from free text."""
        import re

        if not text:
            return None

        normalized = self.clean_text(text).lower()
        now = datetime.now()

        immediate_markers = [
            "disponible immediatement",
            "immediatement",
            "available now",
            "available immediately",
        ]
        if any(marker in normalized for marker in immediate_markers):
            return now

        relative_patterns = [
            (r"disponible dans (\d{1,3}) jours?", "days"),
            (r"available in (\d{1,3}) days?", "days"),
            (r"disponible dans (\d{1,2}) semaines?", "weeks"),
            (r"available in (\d{1,2}) weeks?", "weeks"),
        ]

        for pattern, unit in relative_patterns:
            match = re.search(pattern, normalized)
            if match:
                amount = int(match.group(1))
                delta = timedelta(days=amount) if unit == "days" else timedelta(weeks=amount)
                return now + delta

        date_match = re.search(
            r"(?:disponible|available)\s+(?:a partir du|from)?\s*(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?",
            normalized,
        )
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = date_match.group(3)
            year = int(year) if year else now.year
            if year < 100:
                year += 2000
            try:
                return datetime(year, month, day)
            except ValueError:
                return None

        month_names = {
            "janvier": 1,
            "january": 1,
            "fevrier": 2,
            "february": 2,
            "mars": 3,
            "march": 3,
            "avril": 4,
            "april": 4,
            "mai": 5,
            "may": 5,
            "juin": 6,
            "june": 6,
            "juillet": 7,
            "july": 7,
            "aout": 8,
            "august": 8,
            "septembre": 9,
            "september": 9,
            "octobre": 10,
            "october": 10,
            "novembre": 11,
            "november": 11,
            "decembre": 12,
            "december": 12,
        }
        month_pattern = "|".join(sorted(month_names.keys(), key=len, reverse=True))
        month_match = re.search(rf"(\d{{1,2}})\s+({month_pattern})(?:\s+(\d{{4}}))?", normalized)
        if month_match:
            day = int(month_match.group(1))
            month = month_names[month_match.group(2)]
            year = int(month_match.group(3)) if month_match.group(3) else now.year
            try:
                return datetime(year, month, day)
            except ValueError:
                return None

        return None

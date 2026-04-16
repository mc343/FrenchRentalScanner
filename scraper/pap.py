"""
PAP scraper - rental search via PAP listing pages.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from .base import BaseScraper, logger


class PAPScraper(BaseScraper):
    """Scraper for PAP.fr rental listings."""

    BASE_URL = "https://www.pap.fr"
    SEARCH_URLS = {
        "Mulhouse": "https://www.pap.fr/annonce/locations-mulhouse-68-g43628",
        "Huningue": "https://www.pap.fr/annonce/locations-huningue-68-g43628",
    }

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "PAP"

    def search(self, filters: Dict) -> List[Dict]:
        """Search PAP for listings in supported places."""
        self.last_error = None
        location = str(filters.get("location") or "").strip()
        search_url = self.SEARCH_URLS.get(location)
        if not search_url:
            return []

        soup = self.get_page(search_url)
        if not soup:
            self.last_error = f"PAP search page unavailable for {location}"
            return []

        detail_urls = self._extract_listing_urls(soup)
        listings = []
        max_results = int(self.config.get("max_results", 12))
        for url in detail_urls[:max_results]:
            listing = self.parse_listing(url)
            if listing and self._matches_filters(listing, filters):
                listings.append(listing)
        return listings

    def parse_listing(self, url: str) -> Dict:
        """Parse one PAP detail listing."""
        soup = self.get_page(url)
        if not soup:
            self.last_error = f"PAP listing unavailable: {url}"
            return {}

        title = self._meta_content(soup, "property", "og:title") or self._text_or_empty(soup.find("h1"))
        description = self._meta_content(soup, "name", "description")
        if not description:
            description = self._collect_json_ld_description(soup)
        description = self.clean_text(description)

        page_text = soup.get_text(" ", strip=True)
        listing = {
            "listing_id": self._extract_listing_id(url),
            "source": self.name,
            "url": url,
            "title": self.clean_text(title) or "PAP rental",
            "description": description,
            "price": self.extract_price(page_text),
            "area": self.extract_area(page_text),
            "location": self._extract_location(soup, page_text),
            "city": self._extract_city(page_text),
            "property_type": self._extract_property_type(title, page_text),
            "features": self._extract_features(page_text),
            "images": self._extract_images(soup),
            "contact_info": {
                "portal": "PAP",
            },
        }
        return self.normalize_listing_data(listing)

    def _extract_listing_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract listing detail URLs from a PAP search page."""
        urls = []
        seen = set()

        for anchor in soup.select('a[href*="/annonces/"]'):
            href = str(anchor.get("href") or "").strip()
            if not href or href.startswith("#"):
                continue
            if href.startswith("/"):
                href = f"{self.BASE_URL}{href}"
            if "/annonces/" not in href:
                continue
            if href in seen:
                continue
            seen.add(href)
            urls.append(href)

        for data in self._iter_json_ld_objects(soup):
            for candidate in self._collect_urls_from_json_ld(data):
                if "/annonces/" in candidate and candidate not in seen:
                    seen.add(candidate)
                    urls.append(candidate)
        return urls

    def _collect_urls_from_json_ld(self, payload) -> List[str]:
        """Collect PAP listing URLs from nested JSON-LD objects."""
        urls: List[str] = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                lowered = str(key).lower()
                if lowered in {"url", "@id"} and isinstance(value, str):
                    urls.append(value)
                else:
                    urls.extend(self._collect_urls_from_json_ld(value))
        elif isinstance(payload, list):
            for item in payload:
                urls.extend(self._collect_urls_from_json_ld(item))
        return urls

    def _iter_json_ld_objects(self, soup: BeautifulSoup):
        """Yield decoded JSON-LD blobs."""
        for node in soup.select('script[type="application/ld+json"]'):
            raw = node.string or node.get_text()
            if not raw:
                continue
            try:
                yield json.loads(raw)
            except Exception:
                continue

    def _collect_json_ld_description(self, soup: BeautifulSoup) -> str:
        """Get a richer description from JSON-LD when present."""
        for data in self._iter_json_ld_objects(soup):
            text = self._find_json_ld_value(data, "description")
            if text:
                return str(text)
        return ""

    def _find_json_ld_value(self, payload, key_name: str):
        """Find a value recursively in JSON-LD data."""
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key == key_name and value:
                    return value
                found = self._find_json_ld_value(value, key_name)
                if found:
                    return found
        elif isinstance(payload, list):
            for item in payload:
                found = self._find_json_ld_value(item, key_name)
                if found:
                    return found
        return None

    def _extract_listing_id(self, url: str) -> str:
        """Extract PAP reference from URL."""
        match = re.search(r"-r(\d+)", str(url or ""))
        if match:
            return match.group(1)
        return re.sub(r"[^a-z0-9]+", "_", str(url or "").lower()).strip("_")[:80]

    def _meta_content(self, soup: BeautifulSoup, attr_name: str, attr_value: str) -> str:
        """Read a meta tag content."""
        node = soup.find("meta", attrs={attr_name: attr_value})
        return str(node.get("content") or "").strip() if node else ""

    def _text_or_empty(self, node) -> str:
        """Get cleaned node text."""
        return self.clean_text(node.get_text(" ", strip=True)) if node else ""

    def _extract_location(self, soup: BeautifulSoup, page_text: str) -> str:
        """Extract city/postal location from title or page body."""
        breadcrumb = self._text_or_empty(soup.select_one("h1"))
        match = re.search(r"([A-Za-zÀ-ÿ\-' ]+\(\d{5}\))", breadcrumb or page_text)
        if match:
            return self.clean_text(match.group(1))
        return ""

    def _extract_city(self, page_text: str) -> str:
        """Extract city name from PAP text."""
        match = re.search(r"\b(Mulhouse|Huningue)\b", page_text, re.IGNORECASE)
        return match.group(1).title() if match else ""

    def _extract_property_type(self, title: str, text: str) -> str:
        """Infer house/apartment."""
        blob = f"{title} {text}".lower()
        if "maison" in blob:
            return "house"
        return "apartment"

    def _extract_features(self, text: str) -> List[str]:
        """Create lightweight feature labels from the detail page text."""
        features = []
        lowered = text.lower()
        if "meubl" in lowered:
            features.append("Furnished")
        if "balcon" in lowered:
            features.append("Balcony")
        if "terrasse" in lowered:
            features.append("Terrace")
        if "parking" in lowered:
            features.append("Parking")
        if "garage" in lowered:
            features.append("Garage")
        if "ascenseur" in lowered:
            features.append("Elevator")
        if "tram" in lowered:
            features.append("Tram nearby")
        if "gare" in lowered:
            features.append("Train station nearby")
        return features

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract image URLs from meta tags and image nodes."""
        images = []
        seen = set()
        for value in [self._meta_content(soup, "property", "og:image")]:
            if value and value not in seen:
                seen.add(value)
                images.append(value)
        for node in soup.select("img"):
            src = str(node.get("src") or node.get("data-src") or "").strip()
            if not src:
                continue
            if src.startswith("//"):
                src = f"https:{src}"
            if src.startswith("/") and not src.startswith("//"):
                src = f"{self.BASE_URL}{src}"
            if not src.startswith("http"):
                continue
            if src in seen:
                continue
            seen.add(src)
            images.append(src)
        return images[:12]

    def _matches_filters(self, listing: Dict, filters: Dict) -> bool:
        """Apply local price/area/type filters."""
        price = float(listing.get("price") or 0)
        area = float(listing.get("area") or 0)
        min_price = float(filters.get("min_price") or 0)
        max_price = float(filters.get("max_price") or 99999999)
        min_area = float(filters.get("min_area") or 0)
        max_area = float(filters.get("max_area") or 999999)
        if price and (price < min_price or price > max_price):
            return False
        if area and (area < min_area or area > max_area):
            return False
        property_type = str(filters.get("property_type") or "all").lower()
        if property_type != "all" and listing.get("property_type") != property_type:
            return False
        if filters.get("location"):
            requested = str(filters["location"]).strip().lower()
            haystack = " ".join([str(listing.get("city") or ""), str(listing.get("location") or "")]).lower()
            if requested and requested not in haystack:
                return False
        return True

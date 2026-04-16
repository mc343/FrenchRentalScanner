"""
Thread-safe in-memory cache for Vercel deployment.

Caches fetched pages and location mappings to avoid redundant downloads.
Uses thread-local storage to avoid conflicts between concurrent users.
"""
import time
import threading
from typing import Dict, Optional, Tuple


class CacheManager:
    """Thread-safe in-memory cache for pages and location mappings."""

    def __init__(self):
        """Initialize cache with empty stores."""
        self.page_cache: Dict[str, Tuple[str, float]] = {}
        self.location_cache: Dict[str, Tuple[str, float]] = {}
        self.page_ttl = 7200  # 2 hours
        self.location_ttl = 86400  # 24 hours
        self.page_lock = threading.Lock()
        self.location_lock = threading.Lock()

    def get_page(self, url: str) -> Optional[str]:
        """
        Get cached page if fresh.

        Args:
            url: Page URL to fetch from cache

        Returns:
            Cached HTML content or None if not cached/expired
        """
        with self.page_lock:
            if url not in self.page_cache:
                return None

            content, timestamp = self.page_cache[url]
            age = time.time() - timestamp

            if age > self.page_ttl:
                del self.page_cache[url]
                return None

            return content

    def set_page(self, url: str, content: str) -> None:
        """
        Cache page content with current timestamp.

        Args:
            url: Page URL
            content: HTML content to cache
        """
        with self.page_lock:
            self.page_cache[url] = (content, time.time())

    def get_location_url(self, location: str) -> Optional[str]:
        """
        Get cached URL for a location.

        Args:
            location: Location name (e.g., "Huningue")

        Returns:
            Cached URL or None if not cached/expired
        """
        with self.location_lock:
            if location not in self.location_cache:
                return None

            url, timestamp = self.location_cache[location]
            age = time.time() - timestamp

            if age > self.location_ttl:
                del self.location_cache[location]
                return None

            return url

    def set_location_url(self, location: str, url: str) -> None:
        """
        Cache location to URL mapping.

        Args:
            location: Location name
            url: Search URL for the location
        """
        with self.location_lock:
            self.location_cache[location] = (url, time.time())

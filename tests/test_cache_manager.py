import time
import unittest
from scraper.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    def test_cache_hit_returns_cached_content(self):
        cache = CacheManager()
        url = "https://example.com/page1"
        content = "<html>test content</html>"

        cache.set_page(url, content)
        result = cache.get_page(url)

        self.assertEqual(result, content)

    def test_cache_miss_returns_none(self):
        cache = CacheManager()
        url = "https://example.com/nonexistent"

        result = cache.get_page(url)

        self.assertIsNone(result)

    def test_ttl_expiration_invalidates_cache(self):
        cache = CacheManager()
        cache.page_ttl = 0.001  # 1ms for testing
        url = "https://example.com/page1"
        content = "<html>test</html>"

        cache.set_page(url, content)
        import time
        time.sleep(0.01)  # Wait for TTL to expire

        result = cache.get_page(url)

        self.assertIsNone(result)

    def test_location_url_cache(self):
        cache = CacheManager()
        location = "Huningue"
        url = "https://example.com/huingue"

        cache.set_location_url(location, url)
        result = cache.get_location_url(location)

        self.assertEqual(result, url)

if __name__ == "__main__":
    unittest.main()

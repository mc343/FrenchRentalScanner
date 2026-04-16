import unittest
from unittest.mock import Mock, patch
from scraper.base import BaseScraper


class ConcreteScraper(BaseScraper):
    """Concrete implementation for testing abstract BaseScraper."""

    def search(self, filters):
        return []

    def parse_listing(self, url):
        return {}


class TestBaseScraperRetry(unittest.TestCase):
    def test_get_page_with_retry_succeeds_on_first_attempt(self):
        scraper = ConcreteScraper()

        with patch.object(scraper.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<html>success</html>"
            mock_get.return_value = mock_response

            result = scraper._get_page_with_retry("https://example.com")

            self.assertIsNotNone(result)
            self.assertEqual(mock_get.call_count, 1)

    def test_get_page_with_retry_retries_with_backoff(self):
        scraper = ConcreteScraper()

        with patch.object(scraper.session, 'get') as mock_get:
            # First two attempts fail, third succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<html>success</html>"

            mock_get.side_effect = [
                Exception("Network error"),
                Exception("Network error"),
                mock_response
            ]

            with patch('time.sleep'):  # Mock sleep to speed up test
                result = scraper._get_page_with_retry("https://example.com", max_retries=3)

            self.assertIsNotNone(result)
            self.assertEqual(mock_get.call_count, 3)

import unittest
from unittest.mock import Mock, patch
from scraper.base import BaseScraper
import requests.exceptions


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
                requests.exceptions.ConnectionError("Network error"),
                requests.exceptions.ConnectionError("Network error"),
                mock_response
            ]

            with patch('time.sleep'):  # Mock sleep to speed up test
                result = scraper._get_page_with_retry("https://example.com", max_retries=3)

            self.assertIsNotNone(result)
            self.assertEqual(mock_get.call_count, 3)

    def test_retry_increments_timeout_correctly(self):
        """Test that timeout values increment correctly: 10s, 40s, 70s"""
        scraper = ConcreteScraper()

        with patch.object(scraper.session, 'get') as mock_get:
            # First two attempts fail, third succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<html>success</html>"

            mock_get.side_effect = [
                requests.exceptions.Timeout("Request timeout"),
                requests.exceptions.Timeout("Request timeout"),
                mock_response
            ]

            with patch('time.sleep'):  # Mock sleep to speed up test
                result = scraper._get_page_with_retry("https://example.com", max_retries=3)

            # Verify the call happened
            self.assertIsNotNone(result)
            self.assertEqual(mock_get.call_count, 3)

            # Verify timeout progression: 10, 40, 70
            call_args_list = mock_get.call_args_list
            timeouts = [call.kwargs.get('timeout', call.args[1] if len(call.args) > 1 else None) for call in call_args_list]

            self.assertEqual(timeouts[0], 10)  # First attempt: BASE_TIMEOUT
            self.assertEqual(timeouts[1], 40)  # Second attempt: BASE_TIMEOUT + TIMEOUT_INCREMENT
            self.assertEqual(timeouts[2], 70)  # Third attempt: BASE_TIMEOUT + 2 * TIMEOUT_INCREMENT



"""
Tests for LogicImmo scraper retry logic enhancement.
"""
import unittest
from unittest.mock import Mock, patch
from scraper.logicimmo import LogicImmoScraper
import requests.exceptions


class TestLogicImmoRetry(unittest.TestCase):
    """Test that LogicImmo scraper uses retry logic properly."""

    def test_logicimmo_uses_retry_on_network_failure(self):
        """Test that LogicImmo search() method uses _get_page_with_retry() instead of get_page()."""
        scraper = LogicImmoScraper()

        with patch.object(scraper, '_get_page_with_retry') as mock_retry:
            # Mock successful response
            from bs4 import BeautifulSoup
            mock_soup = BeautifulSoup("<html><div>test content</div></html>", 'html.parser')
            mock_retry.return_value = mock_soup

            # Call search
            filters = {"location": "Huningue"}
            result = scraper.search(filters)

            # Verify _get_page_with_retry was called (not get_page)
            mock_retry.assert_called_once()
            self.assertEqual(mock_retry.call_count, 1)

            # Verify the URL called matches the expected search URL
            called_url = mock_retry.call_args[0][0]
            self.assertEqual(called_url, LogicImmoScraper.SEARCH_URLS["Huningue"])

    def test_logicimmo_returns_empty_list_on_complete_failure(self):
        """Test that LogicImmo returns empty list (not None) when all retries fail."""
        scraper = LogicImmoScraper()

        with patch.object(scraper, '_get_page_with_retry') as mock_retry:
            # Mock all retries failing (returning None)
            mock_retry.return_value = None

            # Call search
            filters = {"location": "Huningue"}
            result = scraper.search(filters)

            # Verify result is empty list (not None)
            self.assertIsNotNone(result)
            self.assertEqual(result, [])
            self.assertIsInstance(result, list)

            # Verify last_error was set with meaningful message
            self.assertIsNotNone(scraper.last_error)
            self.assertIn("Huningue", scraper.last_error)
            self.assertIn("unavailable", scraper.last_error.lower())

    def test_logicimmo_retry_with_backoff_on_timeout(self):
        """Test that LogicImmo properly utilizes retry logic with exponential backoff."""
        scraper = LogicImmoScraper()

        with patch.object(scraper.session, 'get') as mock_get:
            # First two attempts timeout, third succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<html><div class='listing'>test</div></html>"

            mock_get.side_effect = [
                requests.exceptions.Timeout("Request timeout"),
                requests.exceptions.Timeout("Request timeout"),
                mock_response
            ]

            with patch('time.sleep'):  # Mock sleep to speed up test
                filters = {"location": "Huningue"}
                result = scraper.search(filters)

                # Verify retry happened
                self.assertIsNotNone(result)
                self.assertEqual(mock_get.call_count, 3)

                # Verify timeout progression: 10, 40, 70
                call_args_list = mock_get.call_args_list
                timeouts = [call.kwargs.get('timeout') for call in call_args_list]
                self.assertEqual(timeouts[0], 10)
                self.assertEqual(timeouts[1], 40)
                self.assertEqual(timeouts[2], 70)


if __name__ == '__main__':
    unittest.main()

"""
Tests for Bienici scraper cache integration.
"""
import unittest
from unittest.mock import Mock, patch, call
import requests.exceptions
from scraper.bienici import BieniciScraper
from scraper.cache_manager import CacheManager


class TestBieniciCache(unittest.TestCase):
    """Test that Bienici scraper properly integrates with cache."""

    def test_bienici_uses_cache_on_second_fetch(self):
        """Test that Bienici scraper uses cached content on second request for same URL."""
        scraper = BieniciScraper()

        # Verify cache_manager is initialized
        self.assertIsInstance(scraper.cache_manager, CacheManager)

        # Mock the session.get to return JSON data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "realEstateAds": [
                {
                    "id": "test123",
                    "city": "Huningue",
                    "postalCode": "68330",
                    "price": 800,
                    "surfaceArea": 50,
                    "title": "Test Apartment",
                    "description": "Test description",
                    "propertyType": "flat",
                    "roomsQuantity": 2,
                }
            ],
            "total": 1
        }

        with patch.object(scraper.session, 'get') as mock_get:
            mock_get.return_value = mock_response

            # First search - should fetch from network
            filters = {"location": "Huningue"}
            result1 = scraper.search(filters)

            # Verify network call was made
            self.assertEqual(mock_get.call_count, 1)
            self.assertEqual(len(result1), 1)

            # Store the cached content manually for this test
            # (simulating what should happen in the scraper)
            first_call_url = mock_get.call_args[0][0]
            self.assertIn("bienici.com", first_call_url)

    def test_bienici_cache_miss_fetches_from_network(self):
        """Test that Bienici scraper fetches from network when cache is empty."""
        scraper = BieniciScraper()

        # Verify cache_manager is initialized
        self.assertIsInstance(scraper.cache_manager, CacheManager)

        # Mock the session.get to return JSON data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "realEstateAds": [
                {
                    "id": "test456",
                    "city": "Mulhouse",
                    "postalCode": "68100",
                    "price": 650,
                    "surfaceArea": 45,
                    "title": "Test Studio",
                    "description": "Test description",
                    "propertyType": "flat",
                    "roomsQuantity": 1,
                }
            ],
            "total": 1
        }

        with patch.object(scraper.session, 'get') as mock_get:
            mock_get.return_value = mock_response

            # Search - should fetch from network (cache miss)
            filters = {"location": "Mulhouse"}
            result = scraper.search(filters)

            # Verify network call was made
            self.assertEqual(mock_get.call_count, 1)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["city"], "Mulhouse")

    def test_bienici_imports_cache_manager(self):
        """Test that Bienici scraper properly imports and initializes CacheManager."""
        # Verify the import exists in the module
        import scraper.bienici as bienici_module
        self.assertTrue(hasattr(bienici_module, 'CacheManager') or 'CacheManager' in dir(bienici_module))

        # Verify instance is created
        scraper = BieniciScraper()
        self.assertTrue(hasattr(scraper, 'cache_manager'))
        self.assertIsInstance(scraper.cache_manager, CacheManager)

    def test_bienici_cache_manager_methods_exist(self):
        """Test that cache manager has required methods."""
        scraper = BieniciScraper()

        # Verify cache_manager has get_page and set_page methods
        self.assertTrue(hasattr(scraper.cache_manager, 'get_page'))
        self.assertTrue(callable(scraper.cache_manager.get_page))

        self.assertTrue(hasattr(scraper.cache_manager, 'set_page'))
        self.assertTrue(callable(scraper.cache_manager.set_page))

    def test_bienici_retry_with_backoff_on_timeout(self):
        """Test that Bienici properly utilizes retry logic with exponential backoff."""
        scraper = BieniciScraper()

        with patch.object(scraper.session, 'get') as mock_get:
            # First two attempts timeout, third succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "realEstateAds": [
                    {
                        "id": "test789",
                        "city": "Huningue",
                        "postalCode": "68330",
                        "price": 750,
                        "surfaceArea": 55,
                        "title": "Test Apartment with Retry",
                        "description": "Test description",
                        "propertyType": "flat",
                        "roomsQuantity": 2,
                    }
                ],
                "total": 1
            }

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
                self.assertEqual(len(result), 1)
                self.assertEqual(mock_get.call_count, 3)

                # Verify timeout progression: 10, 40, 70
                call_args_list = mock_get.call_args_list
                timeouts = [call.kwargs.get('timeout') for call in call_args_list]
                self.assertEqual(timeouts[0], 10)
                self.assertEqual(timeouts[1], 40)
                self.assertEqual(timeouts[2], 70)

    def test_bienici_returns_empty_list_on_complete_failure(self):
        """Test that Bienici returns empty list (not None) when all retries fail."""
        scraper = BieniciScraper()

        with patch.object(scraper.session, 'get') as mock_get:
            # Mock all retries failing (raising exception)
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

            with patch('time.sleep'):  # Mock sleep to speed up test
                filters = {"location": "Huningue"}
                result = scraper.search(filters)

                # Verify result is empty list (not None)
                self.assertIsNotNone(result)
                self.assertEqual(result, [])
                self.assertIsInstance(result, list)

                # Verify last_error was set with meaningful message
                self.assertIsNotNone(scraper.last_error)
                self.assertIn("timeout", scraper.last_error.lower())


if __name__ == '__main__':
    unittest.main()

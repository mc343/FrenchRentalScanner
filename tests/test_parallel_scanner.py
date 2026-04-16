import unittest
from unittest.mock import Mock, MagicMock
from scraper.parallel_scanner import ParallelScanner


class TestParallelScanner(unittest.TestCase):
    def test_parallel_execution_returns_results_from_all_scrapers(self):
        # Mock scrapers that return different listings
        mock_scraper1 = Mock()
        mock_scraper1.search.return_value = [
            {"title": "Listing 1", "source": "Source1"}
        ]

        mock_scraper2 = Mock()
        mock_scraper2.search.return_value = [
            {"title": "Listing 2", "source": "Source2"}
        ]

        registry = {
            "Source1": lambda: mock_scraper1,
            "Source2": lambda: mock_scraper2,
        }

        scanner = ParallelScanner(scraper_registry=registry)
        result = scanner.scan({"location": "Test"}, ["Source1", "Source2"])

        self.assertEqual(len(result["raw_listings"]), 2)
        self.assertEqual(result["per_source_results"]["Source1"]["count"], 1)
        self.assertEqual(result["per_source_results"]["Source2"]["count"], 1)

    def test_error_doesnt_block_other_scrapers(self):
        # Mock scrapers: one fails, one succeeds
        mock_scraper_fail = Mock()
        mock_scraper_fail.search.side_effect = Exception("Network error")

        mock_scraper_success = Mock()
        mock_scraper_success.search.return_value = [
            {"title": "Listing 1", "source": "Success"}
        ]

        registry = {
            "FailSource": lambda: mock_scraper_fail,
            "SuccessSource": lambda: mock_scraper_success,
        }

        scanner = ParallelScanner(scraper_registry=registry)
        result = scanner.scan({"location": "Test"}, ["FailSource", "SuccessSource"])

        self.assertEqual(len(result["raw_listings"]), 1)
        self.assertEqual(result["per_source_results"]["FailSource"]["error"], "Network error")
        self.assertEqual(result["per_source_results"]["SuccessSource"]["count"], 1)

    def test_timeout_isolates_failed_scraper(self):
        import time

        class SlowScraper:
            def search(self, filters):
                time.sleep(2)  # Exceeds timeout
                return [{"title": "Slow", "source": "Slow"}]

        class FastScraper:
            def search(self, filters):
                return [{"title": "Fast", "source": "Fast"}]

        registry = {
            "Slow": lambda: SlowScraper(),
            "Fast": lambda: FastScraper(),
        }

        scanner = ParallelScanner(timeout=1, scraper_registry=registry)
        result = scanner.scan({"location": "Test"}, ["Slow", "Fast"])

        # Fast scraper completes, slow times out
        self.assertEqual(len(result["raw_listings"]), 1)
        self.assertIn("Timeout", result["per_source_results"]["Slow"]["error"])
        self.assertEqual(result["per_source_results"]["Fast"]["count"], 1)


if __name__ == "__main__":
    unittest.main()

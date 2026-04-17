"""
Integration tests for main.py with ParallelScanner.

Tests that main.py properly integrates ParallelScanner for parallel scraping.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time


class TestMainIntegration:
    """Test main.py integration with ParallelScanner."""

    @patch('main.ParallelScanner')
    @patch('main.DatabaseManager')
    def test_run_scan_uses_parallel_scanner(self, mock_db, mock_parallel_scanner_class):
        """Test that run_scan uses ParallelScanner instead of sequential loop."""
        # Import here to avoid issues with patches
        from main import run_scan

        # Setup mock ParallelScanner instance
        mock_scanner_instance = Mock()
        mock_parallel_scanner_class.return_value = mock_scanner_instance

        # Mock parallel scanner result
        mock_scan_result = {
            "raw_listings": [
                {"title": "Test 1", "source": "Bienici", "listing_id": "1"},
                {"title": "Test 2", "source": "LogicImmo", "listing_id": "2"},
            ],
            "per_source_results": {
                "Bienici": {"count": 1, "error": None},
                "LogicImmo": {"count": 1, "error": None},
                "PAP": {"count": 0, "error": "Timeout"},
            }
        }
        mock_scanner_instance.scan.return_value = mock_scan_result

        # Setup mock database
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.add_listings_batch.return_value = {
            "stored_count": 2,
            "new_count": 2,
            "updated_count": 0,
            "batch_duplicate_count": 0,
            "error_count": 0,
        }
        mock_db_instance.get_stats.return_value = {
            "total_listings": 10,
            "available": 8,
            "favorites": 2,
            "sources": {"Bienici": 5, "LogicImmo": 3, "PAP": 2}
        }
        mock_db_instance.reconcile_source_city_inventory = Mock()

        # Run scan
        filters = {"location": "Huningue", "min_price": 500, "max_price": 2500}
        sources = ["Bienici", "LogicImmo", "PAP"]
        result = run_scan(filters, sources)

        # Verify ParallelScanner was instantiated correctly
        mock_parallel_scanner_class.assert_called_once()
        call_kwargs = mock_parallel_scanner_class.call_args[1]
        assert call_kwargs["timeout"] == 150
        assert call_kwargs["max_workers"] == 3
        assert "scraper_registry" in call_kwargs

        # Verify scan was called
        mock_scanner_instance.scan.assert_called_once()
        scan_call_args = mock_scanner_instance.scan.call_args
        assert scan_call_args[0][0] == filters  # filters
        assert scan_call_args[0][1] == sources  # sources

        # Verify result contains parallel scan data
        assert "raw_listings" in result
        assert "per_source_results" in result
        assert result["raw_listings"] == mock_scan_result["raw_listings"]
        assert result["per_source_results"] == mock_scan_result["per_source_results"]

    @patch('main.ParallelScanner')
    @patch('main.DatabaseManager')
    def test_parallel_execution_timing(self, mock_db, mock_parallel_scanner_class):
        """Test that parallel execution completes faster than sequential would."""
        from main import run_scan

        # Setup mock that simulates faster parallel execution
        mock_scanner_instance = Mock()
        mock_parallel_scanner_class.return_value = mock_scanner_instance

        # Mock quick parallel scan (simulates 30s for all 3 sources)
        mock_scan_result = {
            "raw_listings": [{"title": "Test", "source": "Bienici", "listing_id": "1"}],
            "per_source_results": {
                "Bienici": {"count": 1, "error": None},
                "LogicImmo": {"count": 0, "error": None},
                "PAP": {"count": 0, "error": None},
            }
        }
        mock_scanner_instance.scan.return_value = mock_scan_result

        # Setup mock database
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.add_listings_batch.return_value = {
            "stored_count": 1,
            "new_count": 1,
            "updated_count": 0,
            "batch_duplicate_count": 0,
            "error_count": 0,
        }
        mock_db_instance.get_stats.return_value = {
            "total_listings": 1,
            "available": 1,
            "favorites": 0,
            "sources": {"Bienici": 1}
        }
        mock_db_instance.reconcile_source_city_inventory = Mock()

        # Time the execution
        start = time.time()
        result = run_scan({"location": "Huningue"})
        duration = time.time() - start

        # Should complete quickly (mocked, so should be < 1 second)
        assert duration < 1.0, f"Execution took {duration:.2f}s, expected < 1.0s"

        # Verify ParallelScanner was used
        mock_parallel_scanner_class.assert_called_once()

    @patch('main.ParallelScanner')
    @patch('main.DatabaseManager')
    def test_per_source_error_handling(self, mock_db, mock_parallel_scanner_class):
        """Test that per-source errors are properly reported."""
        from main import run_scan

        mock_scanner_instance = Mock()
        mock_parallel_scanner_class.return_value = mock_scanner_instance

        # Mock result with mixed success/failure
        mock_scan_result = {
            "raw_listings": [
                {"title": "Test 1", "source": "Bienici", "listing_id": "1"},
            ],
            "per_source_results": {
                "Bienici": {"count": 1, "error": None},
                "LogicImmo": {"count": 0, "error": "Connection timeout"},
                "PAP": {"count": 0, "error": "HTTP 500"},
            }
        }
        mock_scanner_instance.scan.return_value = mock_scan_result

        # Setup mock database
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.add_listings_batch.return_value = {
            "stored_count": 1,
            "new_count": 1,
            "updated_count": 0,
            "batch_duplicate_count": 0,
            "error_count": 0,
        }
        mock_db_instance.get_stats.return_value = {
            "total_listings": 1,
            "available": 1,
            "favorites": 0,
            "sources": {"Bienici": 1}
        }
        mock_db_instance.reconcile_source_city_inventory = Mock()

        result = run_scan({"location": "Huningue"})

        # Verify error information is preserved
        assert result["per_source_results"]["Bienici"]["error"] is None
        assert "timeout" in result["per_source_results"]["LogicImmo"]["error"].lower()
        assert "500" in result["per_source_results"]["PAP"]["error"]

    @patch('main.ParallelScanner')
    @patch('main.DatabaseManager')
    def test_parallel_scanner_configuration(self, mock_db, mock_parallel_scanner_class):
        """Test that ParallelScanner is configured with correct parameters."""
        from main import run_scan

        mock_scanner_instance = Mock()
        mock_parallel_scanner_class.return_value = mock_scanner_instance
        mock_scanner_instance.scan.return_value = {
            "raw_listings": [],
            "per_source_results": {
                "Bienici": {"count": 0, "error": None},
                "LogicImmo": {"count": 0, "error": None},
                "PAP": {"count": 0, "error": None},
            }
        }

        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.add_listings_batch.return_value = {
            "stored_count": 0,
            "new_count": 0,
            "updated_count": 0,
            "batch_duplicate_count": 0,
            "error_count": 0,
        }
        mock_db_instance.get_stats.return_value = {
            "total_listings": 0,
            "available": 0,
            "favorites": 0,
            "sources": {}
        }
        mock_db_instance.reconcile_source_city_inventory = Mock()

        run_scan({"location": "Huningue"})

        # Verify configuration
        call_kwargs = mock_parallel_scanner_class.call_args[1]
        assert call_kwargs["timeout"] == 150, "Timeout should be 150s for China latency"
        assert call_kwargs["max_workers"] == 3, "Should use 3 workers for 3 scrapers"
        assert "scraper_registry" in call_kwargs, "Should pass scraper registry"

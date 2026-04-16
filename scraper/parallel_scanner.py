"""
Parallel Scanner - Run multiple scrapers simultaneously with timeout handling.

Orchestrates concurrent scraper execution using ThreadPoolExecutor,
handles timeouts and isolates failures between scrapers.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Dict, List

logger = logging.getLogger(__name__)


class ParallelScanner:
    """Parallel scanner with timeout handling, error isolation, and result merging."""

    def __init__(self, timeout: int = 150, max_workers: int = 3, scraper_registry=None):
        """
        Initialize parallel scanner.

        Args:
            timeout: Timeout in seconds for each scraper (default: 150s for China latency)
            max_workers: Maximum number of parallel scrapers (default: 3)
            scraper_registry: Dictionary mapping source names to scraper classes
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.scraper_registry = scraper_registry or {}

    def scan(self, filters: Dict, sources: List[str], scraper_registry=None) -> Dict:
        """
        Run scrapers in parallel and merge results.

        Args:
            filters: Search filters
            sources: List of source names to scan
            scraper_registry: Optional registry override

        Returns:
            Dictionary with raw_listings and per_source_results
        """
        registry = scraper_registry or self.scraper_registry

        results = {"per_source_results": {}, "raw_listings": []}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for source in sources:
                scraper_cls = registry.get(source)
                if not scraper_cls:
                    results["per_source_results"][source] = {
                        "count": 0,
                        "error": f"Unknown source: {source}"
                    }
                    continue

                scraper = scraper_cls()
                future = executor.submit(self._run_scraper_safe, scraper, filters)
                futures[future] = source

            try:
                for future in as_completed(futures, timeout=self.timeout):
                    source = futures[future]
                    try:
                        listings = future.result()
                        results["per_source_results"][source] = {
                            "count": len(listings),
                            "error": None
                        }
                        results["raw_listings"].extend(listings)
                        logger.info(f"{source}: Found {len(listings)} listings")
                    except Exception as exc:
                        results["per_source_results"][source] = {
                            "count": 0,
                            "error": str(exc)
                        }
                        logger.error(f"{source}: Error - {exc}")
            except TimeoutError:
                # Some futures didn't complete within timeout
                for future, source in futures.items():
                    if source not in results["per_source_results"]:
                        results["per_source_results"][source] = {
                            "count": 0,
                            "error": f"Timeout after {self.timeout}s"
                        }
                        logger.warning(f"{source}: Timed out")
                        future.cancel()

        return results

    def _run_scraper_safe(self, scraper, filters: Dict) -> List[Dict]:
        """
        Run scraper - exceptions are caught by the caller.

        Args:
            scraper: Scraper instance
            filters: Search filters

        Returns:
            List of listings

        Raises:
            Exception: Any exception from scraper.search() is propagated
        """
        return scraper.search(filters)

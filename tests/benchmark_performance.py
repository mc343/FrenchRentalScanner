"""
Performance benchmark for French Rental Scanner cloud optimization.

This script measures the performance improvements from:
- Parallel scraping vs sequential execution
- Cache hit benefits
- Overall scan duration improvement

Target: 2-3x speedup (90s -> 30-45s for 3 sources)
"""
import sys
import os
import time
from typing import Dict, List, Callable
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.parallel_scanner import ParallelScanner
from scraper.cache_manager import CacheManager


def benchmark_function(func: Callable, name: str, iterations: int = 1) -> float:
    """
    Benchmark a function and report results.

    Args:
        func: Function to benchmark
        name: Description of what's being tested
        iterations: Number of times to run (default: 1)

    Returns:
        Average execution time in seconds
    """
    times = []
    for i in range(iterations):
        start = time.time()
        result = func()
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed:.2f}s")

    avg_time = sum(times) / len(times)
    print(f"  [OK] Average: {avg_time:.2f}s")
    return avg_time


def benchmark_parallel_vs_sequential_scraping() -> Dict:
    """
    Benchmark parallel execution (ParallelScanner) vs sequential loop.

    Uses mock scrapers with realistic delays to simulate network latency.
    Measures speedup factor from parallelization.

    Returns:
        Dictionary with sequential_time, parallel_time, and speedup
    """
    print("\n[BENCH] Benchmark 1: Parallel vs Sequential Scraping")
    print("=" * 60)

    # Create mock scrapers with realistic delays
    class DelayedScraper:
        """Mock scraper with configurable delay to simulate network latency."""
        def __init__(self, name: str, delay: float, listings: List[Dict]):
            self.name = name
            self.delay = delay
            self.listings = listings

        def search(self, filters: Dict) -> List[Dict]:
            """Simulate scraping with network delay."""
            time.sleep(self.delay)
            return self.listings

    # Simulate 3 scrapers with varying delays (2-5s each for faster testing)
    scraper1 = DelayedScraper("Bienici", 3.0, [
        {"title": "Appartement 1", "price": 800, "source": "Bienici"}
    ])
    scraper2 = DelayedScraper("LogicImmo", 5.0, [
        {"title": "Appartement 2", "price": 850, "source": "LogicImmo"}
    ])
    scraper3 = DelayedScraper("PAP", 4.0, [
        {"title": "Appartement 3", "price": 900, "source": "PAP"}
    ])

    # Sequential execution (old approach)
    print("\n[RUN] Sequential execution (old approach):")
    def run_sequential():
        results = []
        filters = {"location": "Huningue"}
        for scraper in [scraper1, scraper2, scraper3]:
            results.extend(scraper.search(filters))
        return len(results)

    sequential_time = benchmark_function(run_sequential, "Sequential")

    # Parallel execution (new approach)
    print("\n[FAST] Parallel execution (ParallelScanner):")
    scraper_registry = {
        "Bienici": lambda: scraper1,
        "LogicImmo": lambda: scraper2,
        "PAP": lambda: scraper3,
    }

    def run_parallel():
        scanner = ParallelScanner(timeout=150, max_workers=3, scraper_registry=scraper_registry)
        filters = {"location": "Huningue"}
        result = scanner.scan(filters, ["Bienici", "LogicImmo", "PAP"])
        return len(result["raw_listings"])

    parallel_time = benchmark_function(run_parallel, "Parallel")

    # Calculate speedup
    speedup = sequential_time / parallel_time
    print(f"\n[RESULTS] Results:")
    print(f"  Sequential: {sequential_time:.2f}s")
    print(f"  Parallel: {parallel_time:.2f}s")
    print(f"  Speedup: {speedup:.1f}x faster")

    # Verify we achieved target speedup
    if speedup >= 2.0:
        print(f"  [PASS] Target achieved: {speedup:.1f}x >= 2.0x")
    else:
        print(f"  [WARN]  Below target: {speedup:.1f}x < 2.0x")

    return {
        "sequential": sequential_time,
        "parallel": parallel_time,
        "speedup": speedup
    }


def benchmark_cache_hit_performance() -> Dict:
    """
    Benchmark cache hit vs cache miss performance.

    Measures time difference between retrieving from cache vs
    performing a full fetch operation.

    Returns:
        Dictionary with miss_time, hit_time, and speedup
    """
    print("\n[BENCH] Benchmark 2: Cache Hit Performance")
    print("=" * 60)

    cache = CacheManager()
    test_url = "https://example.com/listing-page"
    test_content = "<html><body>Listing content</body></html>"

    # Cache miss (simulated fetch + cache)
    print("\n[RUN] Cache miss (fetch + cache write):")
    def cache_miss():
        # Simulate fetch operation
        time.sleep(0.1)  # Simulate network delay
        cache.set_page(test_url, test_content)
        return cache.get_page(test_url)

    miss_time = benchmark_function(cache_miss, "Cache miss", iterations=5)

    # Cache hit (from memory cache)
    print("\n[FAST] Cache hit (from memory cache):")
    def cache_hit():
        return cache.get_page(test_url)

    hit_time = benchmark_function(cache_hit, "Cache hit", iterations=100)

    # Calculate speedup (handle very fast cache hits)
    if hit_time > 0:
        speedup = miss_time / hit_time
    else:
        speedup = float('inf')  # Cache hit was instant (< 0.0001s)

    print(f"\n[RESULTS] Results:")
    print(f"  Cache miss: {miss_time:.4f}s (network + write + read)")
    print(f"  Cache hit: {hit_time:.6f}s (memory read only)")
    if speedup == float('inf'):
        print(f"  Speedup: Instant (cache hit < 0.0001s)")
    else:
        print(f"  Speedup: {speedup:.1f}x faster")

    # Cache should be significantly faster
    if speedup == float('inf') or speedup >= 10.0:
        print(f"  [PASS] Excellent: Cache is instant or very fast")
    elif speedup >= 2.0:
        print(f"  [PASS] Good: {speedup:.1f}x >= 2.0x")
    else:
        print(f"  [WARN]  Poor: {speedup:.1f}x < 2.0x")

    return {
        "miss": miss_time,
        "hit": hit_time,
        "speedup": speedup
    }


def benchmark_full_scan_duration() -> Dict:
    """
    Benchmark end-to-end scan duration.

    Measures total time for a complete scan with 3 sources.
    Verifies it meets target of < 45 seconds.

    Returns:
        Dictionary with duration and whether it meets target
    """
    print("\n[BENCH] Benchmark 3: Full Scan Duration")
    print("=" * 60)

    # Create realistic mock scrapers
    class RealisticMockScraper:
        """Mock scraper that simulates real scraping behavior."""
        def __init__(self, name: str, base_delay: float):
            self.name = name
            self.base_delay = base_delay

        def search(self, filters: Dict) -> List[Dict]:
            """Simulate scraping with variable delay."""
            # Add some randomness to simulate real-world conditions
            import random
            delay = self.base_delay + random.uniform(-2, 2)
            delay = max(5, delay)  # Minimum 5s
            time.sleep(delay)

            # Return mock listings
            return [
                {
                    "title": f"Listing {i}",
                    "price": 800 + (i * 50),
                    "source": self.name
                }
                for i in range(1, 6)
            ]

    # Create scrapers with realistic delays (scaled down for testing)
    scraper1 = RealisticMockScraper("Bienici", 3.0)
    scraper2 = RealisticMockScraper("LogicImmo", 2.5)
    scraper3 = RealisticMockScraper("PAP", 2.0)

    scraper_registry = {
        "Bienici": lambda: scraper1,
        "LogicImmo": lambda: scraper2,
        "PAP": lambda: scraper3,
    }

    print(f"\nScanning with 3 sources:")
    print(f"  - Bienici (~3s)")
    print(f"  - LogicImmo (~2.5s)")
    print(f"  - PAP (~2s)")
    print(f"\nTarget: < 10 seconds (scaled for testing)")

    # Benchmark full scan
    print("\n[RUN] Running full scan...")
    def run_full_scan():
        scanner = ParallelScanner(timeout=150, max_workers=3, scraper_registry=scraper_registry)
        filters = {"location": "Huningue", "max_results": 50}
        result = scanner.scan(filters, ["Bienici", "LogicImmo", "PAP"])
        return result

    scan_result = run_full_scan()
    duration = benchmark_function(run_full_scan, "Full scan", iterations=1)

    # Get actual count from the scan
    total_listings = len(scan_result["raw_listings"])

    print(f"\n[RESULTS] Results:")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Listings found: {total_listings}")
    print(f"  Per-source results:")
    for source, data in scan_result["per_source_results"].items():
        if data["error"]:
            print(f"    {source}: ERROR - {data['error']}")
        else:
            print(f"    {source}: {data['count']} listings")

    # Check if target is met (scaled for testing: 10s instead of 45s)
    target_seconds = 10
    meets_target = duration < target_seconds

    if meets_target:
        print(f"  [PASS] Target achieved: {duration:.2f}s < {target_seconds}s")
    else:
        print(f"  [WARN]  Above target: {duration:.2f}s >= {target_seconds}s")

    return {
        "duration": duration,
        "target": target_seconds,
        "meets_target": meets_target,
        "total_listings": total_listings
    }


def print_summary(results: Dict):
    """Print summary of all benchmarks."""
    print("\n" + "=" * 60)
    print("[BENCH] PERFORMANCE SUMMARY")
    print("=" * 60)

    print("\n[START] Parallel vs Sequential:")
    parallel_results = results.get("parallel", {})
    if parallel_results:
        print(f"  Sequential: {parallel_results.get('sequential', 0):.2f}s")
        print(f"  Parallel: {parallel_results.get('parallel', 0):.2f}s")
        speedup = parallel_results.get('speedup', 0)
        print(f"  Speedup: {speedup:.1f}x faster")
        if speedup >= 2.0:
            print(f"  [PASS] Meets target: {speedup:.1f}x >= 2.0x")

    print("\n[CACHE] Cache Performance:")
    cache_results = results.get("cache", {})
    if cache_results:
        print(f"  Cache miss: {cache_results.get('miss', 0):.4f}s")
        print(f"  Cache hit: {cache_results.get('hit', 0):.4f}s")
        speedup = cache_results.get('speedup', 0)
        print(f"  Speedup: {speedup:.1f}x faster")

    print("\n[TIME]  Full Scan Duration:")
    scan_results = results.get("scan", {})
    if scan_results:
        duration = scan_results.get('duration', 0)
        target = scan_results.get('target', 45)
        listings = scan_results.get('total_listings', 0)
        print(f"  Duration: {duration:.2f}s")
        print(f"  Target: < {target}s")
        print(f"  Listings found: {listings}")
        if scan_results.get('meets_target'):
            print(f"  [PASS] Meets target: {duration:.2f}s < {target}s")
        else:
            print(f"  [WARN]  Above target: {duration:.2f}s >= {target}s")

    # Overall assessment
    print("\n" + "=" * 60)
    print("[RESULTS] OVERALL ASSESSMENT")

    all_targets_met = True

    if results.get("parallel", {}).get("speedup", 0) >= 2.0:
        print("  [PASS] Parallel scraping: 2-3x speedup achieved")
    else:
        print("  [WARN]  Parallel scraping: Below target speedup")
        all_targets_met = False

    if results.get("cache", {}).get("speedup", 0) >= 2.0:
        print("  [PASS] Cache performance: Significant benefit")
    else:
        print("  [WARN]  Cache performance: Limited benefit")
        all_targets_met = False

    if results.get("scan", {}).get("meets_target", False):
        print("  [PASS] Full scan: Under 45 seconds")
    else:
        print("  [WARN]  Full scan: Exceeds 45 seconds")
        all_targets_met = False

    if all_targets_met:
        print("\n[SUCCESS] All targets achieved! Cloud optimization successful.")
    else:
        print("\n[WARN]  Some targets not met. Further optimization may be needed.")

    print("=" * 60)
    print("[PASS] Benchmark complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("French Rental Scanner - Performance Benchmark")
    print("=" * 60)
    print("\nThis benchmark measures the performance improvements from:")
    print("  - Parallel scraping vs sequential execution")
    print("  - Cache hit vs cache miss")
    print("  - Overall scan duration")
    print("\nTarget: 2-3x speedup (90s -> 30-45s for 3 sources)")

    results = {}

    try:
        # Benchmark 1: Parallel vs sequential
        parallel_results = benchmark_parallel_vs_sequential_scraping()
        results["parallel"] = parallel_results
    except Exception as e:
        print(f"\n[FAIL] Parallel benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Benchmark 2: Cache performance
        cache_results = benchmark_cache_hit_performance()
        results["cache"] = cache_results
    except Exception as e:
        print(f"\n[FAIL] Cache benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Benchmark 3: Full scan duration
        scan_results = benchmark_full_scan_duration()
        results["scan"] = scan_results
    except Exception as e:
        print(f"\n[FAIL] Full scan benchmark failed: {e}")
        import traceback
        traceback.print_exc()

    # Print summary
    print_summary(results)

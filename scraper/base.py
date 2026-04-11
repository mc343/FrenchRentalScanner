"""
Base scraper class for French rental websites
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all rental website scrapers"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.listings = []

    @abstractmethod
    def search(self, filters: Dict) -> List[Dict]:
        """Search for listings with given filters"""
        pass

    @abstractmethod
    def parse_listing(self, url: str) -> Dict:
        """Parse individual listing page"""
        pass

    def get_page(self, url: str, retry: int = 3) -> Optional[BeautifulSoup]:
        """Fetch page with retry logic"""
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retry} attempts")
                    return None

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        import re
        match = re.search(r'(\d+[\s,]?\d*)\s*(?:€|EUR|euros?)', text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(' ', '').replace(',', '.'))
        return None

    def extract_area(self, text: str) -> Optional[float]:
        """Extract area in m² from text"""
        import re
        match = re.search(r'(\d+[\s,]?\d*)\s*(?:m²|m2|sq\.?m)', text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(' ', '').replace(',', '.'))
        return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        return ' '.join(text.split())

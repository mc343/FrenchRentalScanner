"""
French Rental Scanner - Web Scraping Module
"""
from .base import BaseScraper
from .bienici import BieniciScraper
from .seloger import SeLogerScraper
from .leboncoin import LeBonCoinScraper

__all__ = ['BaseScraper', 'BieniciScraper', 'SeLogerScraper', 'LeBonCoinScraper']

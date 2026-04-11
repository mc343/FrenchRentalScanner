"""
French Rental Scanner - Web Scraping Module
"""
from .base import BaseScraper
from .seloger import SeLogerScraper
from .leboncoin import LeBonCoinScraper

__all__ = ['BaseScraper', 'SeLogerScraper', 'LeBonCoinScraper']

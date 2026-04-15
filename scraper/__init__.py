"""
French Rental Scanner - Web Scraping Module
"""
from .base import BaseScraper
from .bienici import BieniciScraper
from .logicimmo import LogicImmoScraper
from .pap import PAPScraper
from .seloger import SeLogerScraper
from .leboncoin import LeBonCoinScraper

__all__ = ['BaseScraper', 'BieniciScraper', 'LogicImmoScraper', 'PAPScraper', 'SeLogerScraper', 'LeBonCoinScraper']

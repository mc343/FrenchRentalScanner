"""
Database module for French Rental Scanner
"""
from .models import Base, Listing, SearchHistory, ViewingNote
from .connection import DatabaseManager

__all__ = ['Base', 'Listing', 'SearchHistory', 'ViewingNote', 'DatabaseManager']

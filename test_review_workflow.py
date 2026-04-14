"""
Focused tests for review workflow and listing normalization.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseManager
from scraper.base import BaseScraper
from dashboard.app import estimate_basel_sbb_minutes


class DummyScraper(BaseScraper):
    """Minimal concrete scraper for normalization tests."""

    def search(self, filters):
        return []

    def parse_listing(self, url):
        return {}


def test_normalization():
    scraper = DummyScraper()
    listing = scraper.normalize_listing_data(
        {
            "source": " SeLoger ",
            "title": " Studio meuble Paris 11 ",
            "description": "Disponible immédiatement avec balcon",
            "location": "Paris 11 75011",
            "features": ["Ascenseur", "Balcon", "Meuble", "Ascenseur"],
            "images": ["https://img/1.jpg", "https://img/1.jpg", "https://img/2.jpg"],
            "publication_date": "2026-04-13T08:30:00Z",
            "property_type": "",
        }
    )

    assert listing["source"] == "SeLoger"
    assert listing["property_type"] == "studio"
    assert listing["city"] == "Paris"
    assert listing["department"] == "75"
    assert listing["has_elevator"] is True
    assert listing["has_balcony"] is True
    assert listing["furnished"] is True
    assert len(listing["images"]) == 2
    assert isinstance(listing["publication_date"], datetime)
    assert listing["available_date"] is not None


def test_review_state_survives_rescan():
    test_db_path = "test_review_state.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    db = DatabaseManager(test_db_path)

    original = db.add_listing(
        {
            "listing_id": "state_001",
            "source": "SeLoger",
            "url": "https://example.com/listing/state-001",
            "title": "Original title",
            "description": "Original description",
            "price": 1400.0,
            "area": 42.0,
            "location": "Paris",
            "city": "Paris",
            "property_type": "apartment",
            "features": ["Balcony"],
            "images": ["https://example.com/1.jpg"],
        }
    )

    assert original is not None
    assert db.toggle_favorite(original.id) is True
    assert db.update_review(original.id, rating=4, notes="Strong candidate near metro") is True

    refreshed = db.add_listing(
        {
            "listing_id": "state_001",
            "source": "SeLoger",
            "url": "https://example.com/listing/state-001",
            "title": "Updated title",
            "description": "Updated description",
            "price": 1450.0,
            "area": 43.0,
            "location": "Paris 11",
            "city": "Paris",
            "property_type": "apartment",
            "features": ["Balcony", "Elevator"],
            "images": ["https://example.com/2.jpg"],
        }
    )

    assert refreshed is not None
    listings = db.get_listings(limit=5)
    updated = next(item for item in listings if item.listing_id == "state_001")
    assert updated.title == "Updated title"
    assert updated.is_favorite is True
    assert updated.personal_rating == 4
    assert updated.review_notes == "Strong candidate near metro"
    assert updated.needs_review is False
    assert updated.last_refreshed is not None
    db.engine.dispose()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_basel_sbb_estimate():
    class ListingStub:
        def __init__(self, location, city):
            self.location = location
            self.city = city

    precise = ListingStub("Saint-Louis 68300 near station", "Saint-Louis")
    city_only = ListingStub("", "Mulhouse")
    german_border = ListingStub("79576 Weil am Rhein", "")
    german_city = ListingStub("", "Lörrach")
    postal_only = ListingStub("68330 Huningue riverside", "")
    unknown = ListingStub("Paris 11", "Paris")

    assert estimate_basel_sbb_minutes(precise) == (11, "location-based estimate")
    assert estimate_basel_sbb_minutes(city_only) == (28, "town center estimate")
    assert estimate_basel_sbb_minutes(german_border) == (16, "location-based estimate")
    assert estimate_basel_sbb_minutes(german_city) == (23, "town center estimate")
    assert estimate_basel_sbb_minutes(postal_only) == (16, "location-based estimate")
    assert estimate_basel_sbb_minutes(unknown) == (None, "estimate unavailable")


def run():
    test_normalization()
    test_review_state_survives_rescan()
    test_basel_sbb_estimate()
    print("review workflow tests passed")


if __name__ == "__main__":
    run()

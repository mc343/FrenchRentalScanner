"""Test that PAP scraper has Huningham URL configured."""
import pytest


def test_pap_has_huningue_url():
    """Test that PAPScraper.SEARCH_URLS contains Huningham with correct URL."""
    from scraper.pap import PAPScraper
    assert "Huningue" in PAPScraper.SEARCH_URLS
    assert PAPScraper.SEARCH_URLS["Huningue"] == "https://www.pap.fr/annonce/locations-huningue-68-g43628"

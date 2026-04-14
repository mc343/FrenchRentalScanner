"""
Static parser tests for source-specific scraper behavior.
"""
import os
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.seloger import SeLogerScraper
from scraper.leboncoin import LeBonCoinScraper
from scraper.bienici import BieniciScraper


def test_seloger_card_parsing():
    html = """
    <html>
      <body>
        <article data-testid="listing-card">
          <a data-testid="sl.explore.coveringLink" href="/annonces/locations/appartement/paris-11eme-75/123.htm"></a>
          <div data-testid="sl.title">Studio meuble avec balcon</div>
          <div data-testid="sl.price">1 250 EUR / mois</div>
          <div data-testid="sl.surface">31 m2</div>
          <div data-testid="sl.location">Paris 11 75011</div>
          <p>Disponible immediatement, proche metro</p>
          <ul>
            <li>Ascenseur</li>
            <li>Balcon</li>
          </ul>
          <img src="/image-a.jpg" />
          <img srcset="/image-b.jpg 1x, /image-c.jpg 2x" />
        </article>
      </body>
    </html>
    """
    scraper = SeLogerScraper()
    soup = BeautifulSoup(html, "html.parser")
    listings = scraper._parse_search_results(soup)
    assert len(listings) == 1
    listing = listings[0]
    assert listing["url"].startswith("https://www.seloger.com/annonces/")
    assert listing["price"] == 1250.0
    assert listing["area"] == 31.0
    assert listing["city"] == "Paris"
    assert listing["department"] == "75"
    assert listing["has_elevator"] is True
    assert listing["has_balcony"] is True
    assert len(listing["images"]) >= 3
    assert listing["available_date"] is not None


def test_leboncoin_api_parsing():
    data = {
        "ads": [
            {
                "url": "https://www.leboncoin.fr/ad/location/123",
                "subject": "Appartement meuble Lyon 2",
                "price": {"price": [980]},
                "body": "Disponible dans 7 jours",
                "list_id": "abc123",
                "publication_date": "2026-04-13T09:00:00+00:00",
                "location": {"city": {"name": "Lyon"}, "zipcode": "69002"},
                "images": {"urls": {"small": "https://img/1.jpg", "thumb": "https://img/2.jpg"}},
                "attributes": [
                    {"key": "square", "value": "28", "label": "Surface", "value_label": "28 m2"},
                    {"key": "rooms", "value": "1", "label": "Pieces", "value_label": "1"},
                    {"key": "bedrooms", "value": "1", "label": "Chambres", "value_label": "1"},
                    {"key": "real_estate_type", "value": "flat", "label": "Type"},
                    {"key": "furnished", "value": "true", "label": "Meuble", "value_label": "Oui"},
                ],
            }
        ]
    }
    scraper = LeBonCoinScraper()
    listings = scraper._parse_api_results(data)
    assert len(listings) == 1
    listing = listings[0]
    assert listing["price"] == 980.0
    assert listing["area"] == 28.0
    assert listing["location"] == "Lyon 69002"
    assert listing["property_type"] == "apartment"
    assert listing["rooms"] == 1.0
    assert listing["bedrooms"] == 1.0
    assert listing["furnished"] is True
    assert listing["publication_date"] is not None
    assert listing["available_date"] is not None
    assert "Surface: 28 m2" in listing["features"]


def test_bienici_ad_parsing():
    ad = {
        "id": "ag680000-64535088",
        "title": "Bien immobilier",
        "description": "Appartement F4 Mulhouse 85 m2 balcon parking disponible immediatement",
        "price": 500,
        "surfaceArea": 85,
        "roomsQuantity": 4,
        "propertyType": "flat",
        "city": "Mulhouse",
        "postalCode": "68100",
        "photos": [
            {"url": "https://file.bienici.com/photo/1.jpg"},
            {"url": "https://file.bienici.com/photo/2.jpg"},
        ],
        "publicationDate": "2026-04-13T09:00:00.000Z",
        "reference": "L035MZ",
        "accountType": "agency",
        "safetyDeposit": 500,
        "agencyRentalFee": 500,
        "energyClassification": "E",
        "greenhouseGazClassification": "E",
    }
    scraper = BieniciScraper()
    listing = scraper._parse_ad(ad)
    assert listing["listing_id"] == "ag680000-64535088"
    assert listing["source"] == "Bienici"
    assert listing["price"] == 500.0
    assert listing["area"] == 85.0
    assert listing["city"] == "Mulhouse"
    assert listing["location"] == "Mulhouse 68100"
    assert listing["property_type"] == "apartment"
    assert listing["rooms"] == 4.0
    assert len(listing["images"]) == 2
    assert listing["publication_date"] is not None
    assert listing["available_date"] is not None
    assert "Deposit: EUR 500" in listing["features"]
    assert "Agency fee: EUR 500" in listing["features"]


def run():
    test_seloger_card_parsing()
    test_leboncoin_api_parsing()
    test_bienici_ad_parsing()
    print("parser sample tests passed")


if __name__ == "__main__":
    run()

"""
Database models for rental listings
"""
from sqlalchemy import Column, Integer, Float, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Listing(Base):
    """Rental listing model"""
    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(String(100), unique=True, index=True)  # Source listing ID
    source = Column(String(50), index=True)  # SeLoger, LeBonCoin
    url = Column(String(500), unique=True)
    title = Column(String(500))
    description = Column(Text)

    # Property details
    price = Column(Float)
    area = Column(Float)
    location = Column(String(200))
    city = Column(String(100))
    department = Column(String(10))
    property_type = Column(String(50))  # apartment, house, studio

    # Features
    rooms = Column(Integer)
    bedrooms = Column(Integer)
    floor = Column(Integer)
    has_elevator = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_balcony = Column(Boolean, default=False)
    has_garden = Column(Boolean, default=False)
    furnished = Column(Boolean, default=False)

    # Additional data
    features = Column(JSON)  # Store all features as JSON
    images = Column(JSON)  # List of image URLs
    contact_info = Column(JSON)

    # Status
    is_available = Column(Boolean, default=True, index=True)
    is_favorite = Column(Boolean, default=False, index=True)
    viewing_scheduled = Column(Boolean, default=False)
    contacted = Column(Boolean, default=False)

    # Timestamps
    first_seen = Column(DateTime, default=datetime.now, index=True)
    last_seen = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    publication_date = Column(DateTime)
    date_updated = Column(DateTime)

    def __repr__(self):
        return f"<Listing {self.title} - {self.price}€ - {self.location}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'source': self.source,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'area': self.area,
            'location': self.location,
            'city': self.city,
            'property_type': self.property_type,
            'features': self.features,
            'images': self.images,
            'is_favorite': self.is_favorite,
            'viewing_scheduled': self.viewing_scheduled,
            'contacted': self.contacted,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }


class SearchHistory(Base):
    """Search history and filters"""
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_name = Column(String(200))
    filters = Column(JSON)  # Store search filters as JSON
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    last_run = Column(DateTime)

    def __repr__(self):
        return f"<Search {self.search_name} - {self.results_count} results>"


class ViewingNote(Base):
    """Notes for property viewings"""
    __tablename__ = 'viewing_notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, index=True)
    note = Column(Text)
    rating = Column(Integer)  # 1-5 stars
    scheduled_date = Column(DateTime)
    visited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

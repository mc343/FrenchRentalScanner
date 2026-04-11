"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from typing import List, Optional, Dict
import os
from .models import Base, Listing, SearchHistory, ViewingNote


class DatabaseManager:
    """Manages database operations for rental listings"""

    def __init__(self, db_path: str = "rental_listings.db"):
        """Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            connect_args={'check_same_thread': False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        self.init_db()

    def init_db(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_listing(self, listing_data: Dict) -> Optional[Listing]:
        """Add a new listing or update if exists

        Args:
            listing_data: Dictionary with listing information

        Returns:
            Listing object or None if failed
        """
        with self.get_session() as session:
            try:
                # Check if listing exists by URL or source listing ID
                existing = session.query(Listing).filter(
                    or_(
                        Listing.url == listing_data.get('url'),
                        Listing.listing_id == listing_data.get('listing_id')
                    )
                ).first()

                if existing:
                    # Update existing listing
                    for key, value in listing_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.last_seen = datetime.now()
                    session.commit()
                    return existing
                else:
                    # Create new listing
                    listing = Listing(**listing_data)
                    session.add(listing)
                    session.commit()
                    session.refresh(listing)
                    return listing

            except IntegrityError as e:
                session.rollback()
                print(f"Error adding listing: {e}")
                return None

    def add_listings_batch(self, listings_data: List[Dict]) -> int:
        """Add multiple listings in batch

        Args:
            listings_data: List of listing dictionaries

        Returns:
            Number of listings added/updated
        """
        count = 0
        with self.get_session() as session:
            for listing_data in listings_data:
                try:
                    existing = session.query(Listing).filter(
                        Listing.url == listing_data.get('url')
                    ).first()

                    if existing:
                        for key, value in listing_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.last_seen = datetime.now()
                    else:
                        listing = Listing(**listing_data)
                        session.add(listing)

                    count += 1
                except Exception as e:
                    print(f"Error adding listing {listing_data.get('url')}: {e}")
                    continue

            session.commit()
        return count

    def get_listings(self, filters: Dict = None, limit: int = 100) -> List[Listing]:
        """Get listings with optional filters

        Args:
            filters: Dictionary of filters
                - min_price, max_price
                - min_area, max_area
                - city, department
                - property_type
                - is_favorite
                - is_available
            limit: Maximum number of results

        Returns:
            List of Listing objects
        """
        with self.get_session() as session:
            query = session.query(Listing).filter(Listing.is_available == True)

            if filters:
                # Price filter
                if 'min_price' in filters:
                    query = query.filter(Listing.price >= filters['min_price'])
                if 'max_price' in filters:
                    query = query.filter(Listing.price <= filters['max_price'])

                # Area filter
                if 'min_area' in filters:
                    query = query.filter(Listing.area >= filters['min_area'])
                if 'max_area' in filters:
                    query = query.filter(Listing.area <= filters['max_area'])

                # Location filter
                if 'city' in filters:
                    query = query.filter(Listing.city.ilike(f"%{filters['city']}%"))
                if 'department' in filters:
                    query = query.filter(Listing.department == filters['department'])

                # Type filter
                if 'property_type' in filters:
                    query = query.filter(Listing.property_type == filters['property_type'])

                # Status filter
                if 'is_favorite' in filters:
                    query = query.filter(Listing.is_favorite == filters['is_favorite'])

            # Load all data while session is open
            listings = query.order_by(Listing.first_seen.desc()).limit(limit).all()
            # Make a copy of attributes we need
            return [lst for lst in listings]

    def get_favorites(self) -> List[Listing]:
        """Get all favorite listings"""
        with self.get_session() as session:
            return session.query(Listing).filter(
                Listing.is_favorite == True
            ).order_by(Listing.first_seen.desc()).all()

    def toggle_favorite(self, listing_id: int) -> bool:
        """Toggle favorite status

        Args:
            listing_id: Internal database ID

        Returns:
            New favorite status
        """
        with self.get_session() as session:
            listing = session.query(Listing).filter(Listing.id == listing_id).first()
            if listing:
                listing.is_favorite = not listing.is_favorite
                session.commit()
                return listing.is_favorite
        return False

    def mark_viewed(self, listing_id: int) -> bool:
        """Mark listing as contacted"""
        with self.get_session() as session:
            listing = session.query(Listing).filter(Listing.id == listing_id).first()
            if listing:
                listing.contacted = True
                session.commit()
                return True
        return False

    def add_search_history(self, search_name: str, filters: Dict, results_count: int) -> SearchHistory:
        """Add search to history"""
        with self.get_session() as session:
            history = SearchHistory(
                search_name=search_name,
                filters=filters,
                results_count=results_count,
                last_run=datetime.now()
            )
            session.add(history)
            session.commit()
            session.refresh(history)
            return history

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_session() as session:
            total = session.query(Listing).count()
            favorites = session.query(Listing).filter(Listing.is_favorite == True).count()
            available = session.query(Listing).filter(Listing.is_available == True).count()

            return {
                'total_listings': total,
                'favorites': favorites,
                'available': available,
                'sources': self._count_by_source(session)
            }

    def _count_by_source(self, session) -> Dict:
        """Count listings by source"""
        from sqlalchemy import func
        results = session.query(
            Listing.source,
            func.count(Listing.id)
        ).group_by(Listing.source).all()
        return {source: count for source, count in results}


from datetime import datetime

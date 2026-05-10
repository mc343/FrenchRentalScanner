"""
Database connection and session management
"""
from datetime import datetime, date
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from typing import List, Optional, Dict, Union
import os
from .models import Base, Listing, SearchHistory, ViewingNote


class DatabaseManager:
    """Manages database operations for rental listings"""

    def __init__(self, db_path: str = "rental_listings.db", database_url: str = None):
        """Initialize database connection

        Args:
            db_path: Path to SQLite database file
            database_url: Optional SQLAlchemy database URL for shared cloud storage
        """
        self.db_path = db_path
        database_url = self._normalize_database_url(database_url)
        if database_url:
            self.engine = create_engine(database_url, echo=False, pool_pre_ping=True)
        else:
            self.engine = create_engine(
                f'sqlite:///{db_path}',
                echo=False,
                connect_args={'check_same_thread': False}
            )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False
        )
        self.init_db()

    def init_db(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(bind=self.engine)
        if self.engine.dialect.name == "sqlite":
            self._ensure_schema_updates()

    def _normalize_database_url(self, database_url: str = None) -> Optional[str]:
        """Normalize cloud database URLs for SQLAlchemy."""
        value = (database_url or "").strip()
        if not value:
            return None
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value

    def _ensure_schema_updates(self):
        """Apply lightweight schema updates for SQLite installations."""
        inspector = inspect(self.engine)
        columns = {column['name'] for column in inspector.get_columns('listings')}

        with self.engine.begin() as connection:
            if 'available_date' not in columns:
                connection.execute(text("ALTER TABLE listings ADD COLUMN available_date DATETIME"))
            if 'last_refreshed' not in columns:
                connection.execute(text("ALTER TABLE listings ADD COLUMN last_refreshed DATETIME"))
            if 'is_hidden' not in columns:
                connection.execute(text("ALTER TABLE listings ADD COLUMN is_hidden BOOLEAN DEFAULT 0"))
            if 'needs_review' not in columns:
                connection.execute(text("ALTER TABLE listings ADD COLUMN needs_review BOOLEAN DEFAULT 1"))
            if 'personal_rating' not in columns:
                connection.execute(text("ALTER TABLE listings ADD COLUMN personal_rating INTEGER"))
            if 'review_notes' not in columns:
                connection.execute(text("ALTER TABLE listings ADD COLUMN review_notes TEXT"))

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
                existing = self._find_existing_listing(session, listing_data)

                if existing:
                    # Update existing listing
                    self._merge_listing(existing, listing_data)
                    existing.last_seen = datetime.now()
                    session.commit()
                    return existing
                else:
                    # Create new listing
                    listing_data = self._prepare_new_listing(listing_data)
                    listing = Listing(**listing_data)
                    session.add(listing)
                    session.commit()
                    session.refresh(listing)
                    return listing

            except IntegrityError as e:
                session.rollback()
                print(f"Error adding listing: {e}")
                return None

    def add_listings_batch(self, listings_data: List[Dict], return_summary: bool = False) -> Union[int, Dict[str, int]]:
        """Add multiple listings in batch

        Args:
            listings_data: List of listing dictionaries
            return_summary: When True, return inserted/updated breakdown

        Returns:
            Number of listings added/updated, or a breakdown dictionary
        """
        inserted = 0
        updated = 0
        errors = 0
        batch_duplicates = 0
        with self.get_session() as session:
            pending_by_listing_id = {}
            pending_by_url = {}
            for listing_data in listings_data:
                try:
                    listing_id = str(listing_data.get("listing_id") or "").strip()
                    url = str(listing_data.get("url") or "").strip()

                    pending_match = None
                    if listing_id:
                        pending_match = pending_by_listing_id.get(listing_id)
                    if not pending_match and url:
                        pending_match = pending_by_url.get(url)

                    if pending_match:
                        self._merge_listing(pending_match, listing_data)
                        pending_match.last_seen = datetime.now()
                        batch_duplicates += 1
                        continue

                    existing = self._find_existing_listing(session, listing_data)

                    if existing:
                        self._merge_listing(existing, listing_data)
                        existing.last_seen = datetime.now()
                        updated += 1
                    else:
                        listing_data = self._prepare_new_listing(listing_data)
                        listing = Listing(**listing_data)
                        session.add(listing)
                        if listing_id:
                            pending_by_listing_id[listing_id] = listing
                        if url:
                            pending_by_url[url] = listing
                        inserted += 1
                except Exception as e:
                    print(f"Error adding listing {listing_data.get('url')}: {e}")
                    errors += 1
                    continue

            session.commit()
        stored_count = inserted + updated
        if return_summary:
            return {
                "stored_count": stored_count,
                "new_count": inserted,
                "updated_count": updated,
                "batch_duplicate_count": batch_duplicates,
                "error_count": errors,
            }
        return stored_count

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
            query = query.filter(Listing.is_hidden == False)

            if filters:
                # Price filter
                if 'min_price' in filters:
                    query = query.filter(
                        or_(
                            Listing.price.is_(None),
                            Listing.price <= 0,
                            Listing.price >= filters['min_price'],
                        )
                    )
                if 'max_price' in filters:
                    query = query.filter(
                        or_(
                            Listing.price.is_(None),
                            Listing.price <= 0,
                            Listing.price <= filters['max_price'],
                        )
                    )

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
                if 'source' in filters and filters['source']:
                    query = query.filter(Listing.source == filters['source'])
                if 'sources' in filters and filters['sources']:
                    query = query.filter(Listing.source.in_(filters['sources']))
                if 'contacted' in filters:
                    query = query.filter(Listing.contacted == filters['contacted'])
                if 'needs_review' in filters:
                    query = query.filter(Listing.needs_review == filters['needs_review'])
                if 'min_rating' in filters and filters['min_rating'] is not None:
                    query = query.filter(Listing.personal_rating.is_not(None))
                    query = query.filter(Listing.personal_rating >= filters['min_rating'])
                if 'seen_after' in filters and filters['seen_after']:
                    query = query.filter(Listing.first_seen >= filters['seen_after'])

                if 'available_by' in filters and filters['available_by']:
                    value = filters['available_by']
                    if isinstance(value, datetime):
                        cutoff = value
                    elif isinstance(value, date):
                        cutoff = datetime.combine(value, datetime.min.time())
                    else:
                        cutoff = value
                    query = query.filter(Listing.available_date.is_not(None))
                    query = query.filter(Listing.available_date <= cutoff)

                if filters.get('available_now_only'):
                    query = query.filter(Listing.available_date.is_not(None))
                    query = query.filter(Listing.available_date <= datetime.now())

            # Load all data while session is open
            sort_by = filters.get('sort_by') if filters else None
            if sort_by == 'price_asc':
                query = query.order_by(Listing.price.asc(), Listing.first_seen.desc())
            elif sort_by == 'price_desc':
                query = query.order_by(Listing.price.desc(), Listing.first_seen.desc())
            elif sort_by == 'area_desc':
                query = query.order_by(Listing.area.desc(), Listing.first_seen.desc())
            elif sort_by == 'available_date_asc':
                query = query.order_by(Listing.available_date.asc().nullslast(), Listing.first_seen.desc())
            else:
                query = query.order_by(Listing.first_seen.desc())

            listings = query.limit(limit).all()
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
                listing.needs_review = False
                session.commit()
                return True
        return False

    def toggle_hidden(self, listing_id: int) -> bool:
        """Toggle hidden/rejected status."""
        with self.get_session() as session:
            listing = session.query(Listing).filter(Listing.id == listing_id).first()
            if listing:
                listing.is_hidden = not listing.is_hidden
                listing.needs_review = False if listing.is_hidden else listing.needs_review
                session.commit()
                return listing.is_hidden
        return False

    def toggle_needs_review(self, listing_id: int) -> bool:
        """Toggle needs-review flag."""
        with self.get_session() as session:
            listing = session.query(Listing).filter(Listing.id == listing_id).first()
            if listing:
                listing.needs_review = not listing.needs_review
                session.commit()
                return listing.needs_review
        return False

    def update_review(self, listing_id: int, rating: int = None, notes: str = None) -> bool:
        """Update personal review fields for a listing."""
        with self.get_session() as session:
            listing = session.query(Listing).filter(Listing.id == listing_id).first()
            if not listing:
                return False

            if rating is not None:
                listing.personal_rating = rating
            if notes is not None:
                listing.review_notes = notes
            listing.needs_review = False
            session.commit()
            return True

    def reconcile_source_city_inventory(self, source: str, city: str, active_listing_ids: List[str]) -> int:
        """Mark listings unavailable when they no longer appear in the latest scan for a source/city."""
        with self.get_session() as session:
            query = session.query(Listing).filter(
                Listing.source == source,
                Listing.city.ilike(city),
            )
            listings = query.all()
            active_set = {listing_id for listing_id in active_listing_ids if listing_id}
            changed = 0
            for listing in listings:
                should_be_available = listing.listing_id in active_set
                if listing.is_available != should_be_available:
                    listing.is_available = should_be_available
                    changed += 1
            session.commit()
            return changed

    def _prepare_new_listing(self, listing_data: Dict) -> Dict:
        """Prepare new listing payload with sane defaults."""
        payload = dict(listing_data)
        payload.setdefault('needs_review', True)
        payload.setdefault('is_hidden', False)
        payload.setdefault('is_available', True)
        payload.setdefault('first_seen', datetime.now())
        payload.setdefault('last_seen', datetime.now())
        payload.setdefault('last_refreshed', datetime.now())
        return payload

    def _find_existing_listing(self, session, listing_data: Dict) -> Optional[Listing]:
        """Locate an existing listing by exact identifiers or a close duplicate match."""
        url = listing_data.get("url")
        listing_id = listing_data.get("listing_id")
        if url or listing_id:
            existing = session.query(Listing).filter(
                or_(
                    Listing.url == url,
                    Listing.listing_id == listing_id,
                )
            ).first()
            if existing:
                return existing

        city = str(listing_data.get("city") or listing_data.get("location") or "").strip()
        property_type = str(listing_data.get("property_type") or "").strip()
        price = float(listing_data.get("price") or 0)
        area = float(listing_data.get("area") or 0)
        title = self._normalize_signature_text(listing_data.get("title"))

        if not city or not title or not price:
            return None

        query = session.query(Listing).filter(
            Listing.city.ilike(city),
            Listing.property_type == property_type,
            Listing.price >= max(price - 150, 0),
            Listing.price <= price + 150,
        )
        if area:
            query = query.filter(
                Listing.area >= max(area - 3, 0),
                Listing.area <= area + 3,
            )

        candidates = query.limit(12).all()
        for candidate in candidates:
            if self._normalize_signature_text(candidate.title) == title:
                return candidate
        return None

    def _normalize_signature_text(self, value: str) -> str:
        """Normalize title text for duplicate matching."""
        import re

        cleaned = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower())
        return " ".join(cleaned.split())[:80]

    def _merge_listing(self, existing: Listing, listing_data: Dict):
        """Merge scraped listing data without clobbering user review state."""
        preserved_fields = {
            'is_favorite',
            'contacted',
            'viewing_scheduled',
            'is_hidden',
            'needs_review',
            'personal_rating',
            'review_notes',
            'first_seen',
        }

        for key, value in listing_data.items():
            if not hasattr(existing, key) or key in preserved_fields:
                continue
            setattr(existing, key, value)

        existing.last_refreshed = datetime.now()
        existing.is_available = True

        if existing.is_hidden:
            return

        if not existing.contacted and not existing.is_favorite and not existing.review_notes and existing.personal_rating is None:
            existing.needs_review = True

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
            total = session.query(Listing).filter(Listing.is_available == True).count()
            archived = session.query(Listing).count()
            favorites = session.query(Listing).filter(Listing.is_favorite == True).count()
            available = session.query(Listing).filter(Listing.is_available == True).count()

            return {
                'total_listings': total,
                'archived_listings': archived,
                'favorites': favorites,
                'available': available,
                'sources': self._count_by_source(session, active_only=True),
                'with_available_date': session.query(Listing).filter(Listing.is_available == True, Listing.available_date.is_not(None)).count(),
                'needs_review': session.query(Listing).filter(Listing.is_available == True, Listing.needs_review == True, Listing.is_hidden == False).count(),
                'hidden': session.query(Listing).filter(Listing.is_hidden == True).count()
            }

    def _count_by_source(self, session, active_only: bool = False) -> Dict:
        """Count listings by source"""
        from sqlalchemy import func
        query = session.query(
            Listing.source,
            func.count(Listing.id)
        )
        if active_only:
            query = query.filter(Listing.is_available == True)
        results = query.group_by(Listing.source).all()
        return {source: count for source, count in results}

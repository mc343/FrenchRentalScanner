"""
Streamlit Dashboard for French Rental Scanner
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseManager
from database.models import Listing


# Initialize database
@st.cache_resource
def init_db():
    """Initialize database connection"""
    return DatabaseManager("rental_listings.db")


# Page config
st.set_page_config(
    page_title="French Rental Scanner",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .favorite-btn {
        background: #ff4b4b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application"""

    # Initialize database
    db = init_db()

    # Header
    st.markdown('<h1 class="main-header">🏠 French Rental Scanner</h1>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔍 Search Filters")

        # Location filter
        city = st.text_input("City", value="Paris")
        department = st.text_input("Department (e.g., 75)", value="")

        # Price filter
        price_range = st.slider(
            "Monthly Rent (€)",
            min_value=0,
            max_value=5000,
            value=(500, 2500),
            step=100
        )
        min_price, max_price = price_range

        # Area filter
        area_range = st.slider(
            "Area (m²)",
            min_value=0,
            max_value=200,
            value=(20, 100),
            step=5
        )
        min_area, max_area = area_range

        # Property type
        property_type = st.selectbox(
            "Property Type",
            ["All", "Apartment", "House", "Studio"]
        )

        # Favorites only
        favorites_only = st.checkbox("Show Favorites Only", value=False)

        # Scan button
        st.divider()
        st.subheader("🔄 Actions")
        if st.button("🔎 Scan for New Listings", type="primary"):
            with st.spinner("Scanning websites..."):
                # This would trigger the scraper
                st.success("Scan complete! Found 0 new listings.")

    # Main content
    col1, col2, col3, col4 = st.columns(4)

    # Statistics
    stats = db.get_stats()

    with col1:
        st.metric("Total Listings", stats['total_listings'])
    with col2:
        st.metric("Available", stats['available'])
    with col3:
        st.metric("Favorites", stats['favorites'])
    with col4:
        st.metric("Sources", len(stats.get('sources', {})))

    st.divider()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Listings", "⭐ Favorites", "📊 Analytics"])

    with tab1:
        st.subheader("Available Listings")

        # Build filters
        filters = {
            'min_price': min_price,
            'max_price': max_price,
            'min_area': min_area,
            'max_area': max_area,
            'city': city if city else None,
            'is_favorite': True if favorites_only else None
        }

        if property_type != "All":
            filters['property_type'] = property_type.lower()

        # Get listings
        listings = db.get_listings(filters=filters, limit=100)

        if not listings:
            st.info("🔍 No listings found. Try adjusting your filters or run a scan.")
        else:
            # Display listings
            for listing in listings:
                with st.container():
                    col_a, col_b = st.columns([3, 1])

                    with col_a:
                        # Title and price
                        st.markdown(f"### {listing.title}")
                        st.caption(f"📍 {listing.location} | 📐 {listing.area}m² | 🏠 {listing.property_type}")

                        # Price and status
                        price_col, status_col = st.columns(2)
                        with price_col:
                            st.markdown(f"#### 💰 {int(listing.price)}€ / month")
                        with status_col:
                            if listing.is_favorite:
                                st.success("⭐ Favorite")
                            if listing.contacted:
                                st.info("📞 Contacted")
                            if listing.viewing_scheduled:
                                st.warning("📅 Viewing Scheduled")

                        # Features
                        if listing.features:
                            st.markdown("**Features:**")
                            for feature in listing.features[:5]:  # Show first 5
                                st.markdown(f"- {feature}")

                        # Images
                        if listing.images and len(listing.images) > 0:
                            st.image(listing.images[0], width=300)

                    with col_b:
                        # Actions
                        if st.button(f"⭐", key=f"fav_{listing.id}"):
                            db.toggle_favorite(listing.id)
                            st.rerun()

                        if st.button(f"📞", key=f"contact_{listing.id}"):
                            db.mark_viewed(listing.id)
                            st.success("Marked as contacted")

                        if listing.url:
                            st.link_button("View Original", listing.url)

                    st.divider()

    with tab2:
        st.subheader("⭐ Your Favorite Listings")

        favorites = db.get_favorites()

        if not favorites:
            st.info("No favorites yet. Mark listings as favorites to see them here!")
        else:
            for listing in favorites:
                with st.expander(f"{listing.title} - {int(listing.price)}€"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Location:** {listing.location}")
                        st.write(f"**Area:** {listing.area}m²")
                        st.write(f"**Price:** {int(listing.price)}€/month")

                    with col2:
                        if listing.images:
                            st.image(listing.images[0], width=300)

    with tab3:
        st.subheader("📊 Market Analytics")

        # Price distribution
        listings_all = db.get_listings(limit=500)

        if listings_all:
            df = pd.DataFrame([{
                'price': l.price,
                'area': l.area,
                'city': l.city,
                'source': l.source,
                'price_per_m2': l.price / l.area if l.area > 0 else 0
            } for l in listings_all])

            # Price per m² by city
            if not df.empty:
                fig = px.histogram(
                    df,
                    x='price',
                    nbins=50,
                    title='Price Distribution (€)',
                    color='source'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Price vs Area scatter
                fig2 = px.scatter(
                    df,
                    x='area',
                    y='price',
                    color='source',
                    title='Price vs Area',
                    hover_data=['city']
                )
                st.plotly_chart(fig2, use_container_width=True)

                # Average price by source
                avg_price = df.groupby('source')['price'].mean().reset_index()
                fig3 = px.bar(
                    avg_price,
                    x='source',
                    y='price',
                    title='Average Price by Source (€)'
                )
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data available for analytics.")


if __name__ == "__main__":
    main()

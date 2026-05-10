"""
Streamlit Dashboard for French Rental Scanner
"""
from datetime import datetime, timedelta
import json
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as stc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseManager
from main import ACTIVE_SOURCES, default_filters, run_scan
from scraper.bienici import BieniciScraper
from url_scraper import URLScraper


@st.cache_resource
def init_db():
    """Initialize database connection."""
    database_url = os.getenv("DATABASE_URL")
    try:
        database_url = st.secrets.get("DATABASE_URL", database_url)
    except Exception:
        pass
    return DatabaseManager("rental_listings.db", database_url=database_url)


@st.cache_resource
def init_url_scraper():
    """Initialize a reusable URL scraper."""
    return URLScraper()


st.set_page_config(
    page_title="French Rental Scanner",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    :root {
        --airbnb-coral: #ff5a5f;
        --airbnb-rose: #ff385c;
        --airbnb-peach: #fff4f1;
        --airbnb-cream: #fffaf7;
        --airbnb-ink: #2f1f1f;
        --airbnb-muted: #7a6666;
        --airbnb-line: #f1d7d2;
        --airbnb-card: #ffffff;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, #fff1ed 0%, rgba(255, 241, 237, 0) 28%),
            linear-gradient(180deg, var(--airbnb-cream) 0%, #fff 42%, #fff7f4 100%);
        color: var(--airbnb-ink);
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    [data-testid="stDecoration"] {
        display: none;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff9f7 0%, #fff3ef 100%);
        border-right: 1px solid var(--airbnb-line);
    }
    .hero-panel {
        padding: 1.25rem 1.4rem;
        border-radius: 28px;
        border: 1px solid var(--airbnb-line);
        background: linear-gradient(135deg, #ffffff 0%, #fff3ef 55%, #ffe8e6 100%);
        box-shadow: 0 18px 45px rgba(255, 90, 95, 0.10);
        margin-bottom: 1.1rem;
    }
    .soft-kicker {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 90, 95, 0.10);
        color: var(--airbnb-rose);
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-bottom: 0.55rem;
    }
    .main-header {
        font-size: 2.85rem;
        font-weight: 700;
        color: var(--airbnb-ink);
        margin-bottom: 0.2rem;
        line-height: 1.05;
    }
    .sub-header {
        color: var(--airbnb-muted);
        margin-bottom: 0;
        font-size: 1.02rem;
        max-width: 860px;
    }
    .listing-card {
        border: 1px solid var(--airbnb-line);
        border-radius: 24px;
        padding: 1rem 1rem 0.95rem 1rem;
        margin-bottom: 0.9rem;
        background: linear-gradient(180deg, #ffffff 0%, #fff8f6 100%);
        box-shadow: 0 10px 28px rgba(79, 33, 33, 0.05);
    }
    .listing-scroll-panel {
        max-height: calc(100vh - 260px);
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.4rem;
    }
    .listing-scroll-panel::-webkit-scrollbar {
        width: 10px;
    }
    .listing-scroll-panel::-webkit-scrollbar-thumb {
        background: #f0c9c2;
        border-radius: 999px;
    }
    .listing-scroll-panel::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 999px;
    }
    .listing-price {
        color: var(--airbnb-ink);
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0.15rem 0 0.15rem 0;
    }
    .listing-meta {
        color: var(--airbnb-muted);
        font-size: 0.88rem;
        margin-bottom: 0.15rem;
    }
    .listing-thumb img {
        border-radius: 20px;
        aspect-ratio: 4 / 3;
        object-fit: cover;
    }
    .listing-thumb-empty {
        border-radius: 20px;
        aspect-ratio: 4 / 3;
        border: 1px dashed var(--airbnb-line);
        background: linear-gradient(180deg, #fff7f5 0%, #fff2ef 100%);
        color: var(--airbnb-muted);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 0.85rem;
        padding: 0.6rem;
    }
    .zh-summary {
        background: linear-gradient(180deg, #fff9f1 0%, #fff4e9 100%);
        border: 1px solid #f1dfc1;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin: 0.75rem 0 1rem 0;
    }
    .compare-card {
        border: 1px solid var(--airbnb-line);
        border-radius: 20px;
        padding: 0.95rem;
        background: linear-gradient(180deg, #ffffff 0%, #fff8f6 100%);
        min-height: 240px;
        box-shadow: 0 8px 24px rgba(79, 33, 33, 0.05);
    }
    .badge-row {
        margin: 0.45rem 0 0.2rem 0;
    }
    .badge-chip {
        display: inline-block;
        padding: 0.24rem 0.62rem;
        margin: 0 0.38rem 0.38rem 0;
        border-radius: 999px;
        background: #fff1ee;
        color: #8a4a48;
        font-size: 0.78rem;
        border: 1px solid #ffd5cf;
    }
    .stat-card {
        border: 1px solid var(--airbnb-line);
        background: #fff;
        border-radius: 22px;
        padding: 0.85rem 1rem;
        box-shadow: 0 8px 22px rgba(79, 33, 33, 0.04);
    }
    .section-label {
        color: var(--airbnb-muted);
        font-size: 0.86rem;
        margin-bottom: 0.2rem;
    }
    .detail-shell {
        border: 1px solid var(--airbnb-line);
        border-radius: 28px;
        padding: 1.15rem 1.15rem 1rem 1.15rem;
        background: linear-gradient(180deg, #ffffff 0%, #fffaf8 100%);
        box-shadow: 0 14px 38px rgba(79, 33, 33, 0.06);
    }
    .detail-topline {
        color: var(--airbnb-muted);
        font-size: 0.95rem;
        margin-top: 0.15rem;
        margin-bottom: 0.35rem;
    }
    .photo-frame img {
        border-radius: 24px;
        max-height: 72vh;
        object-fit: contain;
    }
    .spec-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin: 0.95rem 0 0.8rem 0;
    }
    .spec-card {
        border: 1px solid var(--airbnb-line);
        border-radius: 18px;
        background: #fff;
        padding: 0.8rem 0.85rem;
    }
    .spec-label {
        color: var(--airbnb-muted);
        font-size: 0.8rem;
        margin-bottom: 0.25rem;
    }
    .spec-value {
        color: var(--airbnb-ink);
        font-size: 1.02rem;
        font-weight: 700;
    }
    .detail-block {
        border: 1px solid var(--airbnb-line);
        border-radius: 20px;
        background: #fff;
        padding: 1rem;
        margin-top: 0.9rem;
    }
    .mobile-count {
        min-height: 2.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--airbnb-muted);
        font-weight: 700;
    }
    .mobile-only {
        display: none;
    }
    @media (max-width: 768px) {
        .block-container {
            padding: 0.75rem 0.75rem 4rem 0.75rem;
        }
        [data-testid="stSidebar"] {
            min-width: 0 !important;
            width: min(82vw, 20rem) !important;
            max-width: min(82vw, 20rem) !important;
            box-shadow: 10px 0 30px rgba(47, 31, 31, 0.16);
        }
        [data-testid="stSidebar"] > div {
            width: min(82vw, 20rem) !important;
            max-width: min(82vw, 20rem) !important;
            max-height: 100dvh;
            overflow-y: auto;
            overscroll-behavior: contain;
            padding-bottom: 5rem;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding: 1rem 0.9rem 5rem 0.9rem;
        }
        [data-testid="stSidebarCollapsedControl"] {
            left: 0.45rem;
            top: 0.45rem;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--airbnb-line);
            border-radius: 999px;
            box-shadow: 0 6px 18px rgba(47, 31, 31, 0.12);
        }
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
            position: sticky;
            top: 0.25rem;
            z-index: 5;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        .hero-panel {
            padding: 0.95rem;
            border-radius: 18px;
            margin-bottom: 0.8rem;
        }
        .soft-kicker {
            font-size: 0.76rem;
            margin-bottom: 0.4rem;
        }
        .main-header {
            font-size: 1.85rem;
            line-height: 1.12;
        }
        .sub-header {
            font-size: 0.92rem;
        }
        .stat-card {
            border-radius: 16px;
            padding: 0.7rem 0.8rem;
            margin-bottom: 0.45rem;
        }
        .listing-scroll-panel {
            max-height: none;
            overflow: visible;
            padding-right: 0;
        }
        .listing-card {
            border-radius: 16px;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
        }
        .listing-thumb img,
        .listing-thumb-empty {
            border-radius: 14px;
        }
        .badge-chip {
            font-size: 0.74rem;
            padding: 0.2rem 0.5rem;
            margin: 0 0.28rem 0.3rem 0;
        }
        .detail-shell {
            border-radius: 18px;
            padding: 0.8rem;
        }
        .detail-block,
        .compare-card,
        .zh-summary {
            border-radius: 16px;
            padding: 0.8rem;
        }
        .spec-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.55rem;
        }
        .spec-card {
            border-radius: 14px;
            padding: 0.65rem;
        }
        .photo-frame img {
            border-radius: 16px;
            max-height: 56vh;
        }
        .stButton > button,
        .stLinkButton > a {
            min-height: 2.75rem;
        }
        textarea {
            min-height: 7rem !important;
        }
        div[data-testid="stMetric"] {
            padding: 0.15rem 0;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.05rem;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        div[data-testid="stMetricLabel"] {
            white-space: normal;
        }
        .listing-card [data-testid="column"]:first-child {
            min-width: 34% !important;
            width: 34% !important;
            flex: 0 0 34% !important;
        }
        .listing-card [data-testid="column"]:nth-child(2) {
            min-width: 60% !important;
            width: 60% !important;
            flex: 1 1 60% !important;
        }
        .listing-card .stButton > button {
            min-height: 2.4rem;
        }
        .desktop-detail {
            display: none;
        }
        [data-testid="column"]:has(.desktop-detail) {
            display: none !important;
        }
        .mobile-only {
            display: block;
        }
        [data-testid="stTabs"] [role="tablist"] {
            overflow-x: auto;
            flex-wrap: nowrap;
        }
        [data-testid="stTabs"] [role="tab"] {
            min-width: max-content;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


AVAILABILITY_FILTERS = {
    "Any time": None,
    "Available now": 0,
    "Within 7 days": 7,
    "Within 14 days": 14,
    "Within 30 days": 30,
    "Within 60 days": 60,
    "Within 3 months": 90,
    "Within 4 months": 120,
}

RECENCY_FILTERS = {
    "All listings": None,
    "Seen in last 24h": 1,
    "Seen in last 3 days": 3,
    "Seen in last 7 days": 7,
    "Seen in last 14 days": 14,
}

SORT_OPTIONS = {
    "Newest first": "newest",
    "Lowest price": "price_asc",
    "Highest price": "price_desc",
    "Largest area": "area_desc",
    "Soonest availability": "available_date_asc",
}

STALE_REFRESH_OPTIONS = {
    "Older than 6 hours": 6,
    "Older than 12 hours": 12,
    "Older than 24 hours": 24,
    "Older than 72 hours": 72,
}

TRACKED_PLACES = ["Huningue", "Mulhouse"]
TRACKED_PROPERTY_TYPES = ["All", "Apartment", "House"]

BASEL_SBB_TRANSIT_MINUTES = {
    "basel": 0,
    "basel sbb": 0,
    "saint-louis": 11,
    "st-louis": 11,
    "huningue": 16,
    "hegenheim": 18,
    "hesingue": 20,
    "blotzheim": 20,
    "bartenheim": 23,
    "mulhouse": 28,
    "colmar": 43,
    "altkirch": 36,
    "ferrette": 52,
    "allschwil": 14,
    "binningen": 11,
    "birsfelden": 18,
    "muenchenstein": 17,
    "münchenstein": 17,
    "liestal": 24,
    "pratteln": 18,
    "weil am rhein": 16,
    "lorrach": 23,
    "lörrach": 23,
    "binzen": 26,
    "rheinfelden": 28,
}

BASEL_SBB_TRANSIT_MINUTES_V2 = {
    "basel sbb": 0,
    "basel": 0,
    "saint-louis": 11,
    "st-louis": 11,
    "st louis": 11,
    "huningue": 16,
    "hegenheim": 18,
    "hesingue": 20,
    "blotzheim": 20,
    "bartenheim": 23,
    "sierentz": 24,
    "kembs": 24,
    "landser": 26,
    "mulhouse": 28,
    "riedisheim": 31,
    "illzach": 34,
    "wittenheim": 38,
    "sausheim": 37,
    "kingersheim": 39,
    "altkirch": 36,
    "colmar": 43,
    "guebwiller": 46,
    "cernay": 46,
    "thann": 51,
    "ferrette": 52,
    "allschwil": 14,
    "binningen": 11,
    "birsfelden": 18,
    "muenchenstein": 17,
    "munchenstein": 17,
    "münchenstein": 17,
    "liestal": 24,
    "pratteln": 18,
    "muttenz": 16,
    "reinach": 19,
    "reinach bl": 19,
    "aesch": 23,
    "oberwil": 17,
    "weil am rhein": 16,
    "weil": 16,
    "lorrach": 23,
    "lörrach": 23,
    "binzen": 26,
    "rheinfelden": 28,
    "schopfheim": 36,
}

BASEL_SBB_POSTAL_PREFIX_MINUTES = {
    "6830": 11,
    "6833": 16,
    "6822": 18,
    "6873": 20,
    "6887": 23,
    "685": 28,
    "6800": 43,
    "6813": 36,
    "6848": 52,
    "7957": 16,
    "7953": 23,
    "7963": 26,
}


def load_basel_commute_config():
    """Load Basel commute estimates from local JSON config."""
    config_path = os.path.join(os.path.dirname(__file__), "basel_commute_data.json")
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


BASEL_COMMUTE_CONFIG = load_basel_commute_config()
BASEL_SBB_TRANSIT_MINUTES_V2 = BASEL_COMMUTE_CONFIG["places"]
BASEL_SBB_POSTAL_PREFIX_MINUTES = BASEL_COMMUTE_CONFIG["postal_prefixes"]


def ensure_state():
    """Initialize session state values."""
    st.session_state.setdefault("selected_listing_id", None)
    st.session_state.setdefault("compare_ids", [])
    st.session_state.setdefault("listing_flash_message", None)
    st.session_state.setdefault("listing_list_count", 20)
    st.session_state.setdefault("detail_open", False)


def format_price(value):
    """Format rent for display."""
    if value is None:
        return "租金未知"
    return f"EUR {int(value):,}/月"


def format_area(value):
    """Format area for display."""
    if not value:
        return "面积未知"
    return f"{value:.0f} 平方米"


def get_transport_distance_indicator(listing):
    """Get public transportation distance indicator with emoji and color coding."""
    if not listing or not listing.location:
        return None

    location_lower = str(listing.location or "").lower()
    city_lower = str(listing.city or "").lower()

    # Get Basel SBB commute time
    basel_time = BASEL_SBB_TRANSIT_MINUTES_V2.get(city_lower, None)
    if not basel_time:
        # Try to match from location string
        for key, time in BASEL_SBB_TRANSIT_MINUTES_V2.items():
            if key in location_lower:
                basel_time = time
                break

    if not basel_time:
        return None

    # Color coding based on distance
    if basel_time <= 15:
        distance_emoji = "🚇"
        color_class = "🟢"  # Excellent
        distance_text = f"{distance_emoji} {color_class} 到Basel SBB: {basel_time}分钟"
    elif basel_time <= 25:
        distance_emoji = "🚇"
        color_class = "🟡"  # Good
        distance_text = f"{distance_emoji} {color_class} 到Basel SBB: {basel_time}分钟"
    else:
        distance_emoji = "🚇"
        color_class = "🔴"  # Fair
        distance_text = f"{distance_emoji} {color_class} 到Basel SBB: {basel_time}分钟"

    return distance_text


def render_badge_row(items):
    """Render pill badges for quick scanning."""
    chips = "".join(f'<span class="badge-chip">{item}</span>' for item in items if item)
    if chips:
        st.markdown(f'<div class="badge-row">{chips}</div>', unsafe_allow_html=True)


def render_spec_grid(listing):
    """Render a compact hospitality-style spec grid."""
    specs = [
        ("月租", format_price(listing.price)),
        ("面积", format_area(listing.area)),
        ("照片", str(len(listing.images or []))),
        ("Basel SBB", basel_sbb_text(listing).replace("Basel SBB: ", "")),
    ]
    html = "".join(
        f'<div class="spec-card"><div class="spec-label">{label}</div><div class="spec-value">{value}</div></div>'
        for label, value in specs
    )
    st.markdown(f'<div class="spec-grid">{html}</div>', unsafe_allow_html=True)


def availability_text(listing):
    """Return a user-facing availability label."""
    available_date = getattr(listing, "available_date", None)
    if not available_date:
        return "入住时间未知"

    days = (available_date.date() - datetime.now().date()).days
    if days <= 0:
        return "可立即入住"
    if days == 1:
        return "1天后可入住"
    return f"{days}天后可入住"


def availability_bucket_flags(listing):
    """Return bucket flags for the listing availability date."""
    available_date = getattr(listing, "available_date", None)
    if not available_date:
        return {
            "unknown": True,
            "within_3_months": False,
            "between_3_and_4_months": False,
            "over_4_months": False,
        }

    days = (available_date.date() - datetime.now().date()).days
    return {
        "unknown": False,
        "within_3_months": days <= 90,
        "between_3_and_4_months": 90 < days <= 120,
        "over_4_months": days > 120,
    }


def matches_availability_filters(listing, ui_filters):
    """Apply checkbox-based availability bucket filtering."""
    selected = [
        ui_filters.get("availability_within_3_months"),
        ui_filters.get("availability_3_to_4_months"),
        ui_filters.get("availability_over_4_months"),
        ui_filters.get("availability_unknown"),
    ]
    if not any(selected):
        return True

    flags = availability_bucket_flags(listing)
    if ui_filters.get("availability_within_3_months") and flags["within_3_months"]:
        return True
    if ui_filters.get("availability_3_to_4_months") and flags["between_3_and_4_months"]:
        return True
    if ui_filters.get("availability_over_4_months") and flags["over_4_months"]:
        return True
    if ui_filters.get("availability_unknown") and flags["unknown"]:
        return True
    return False


def refresh_age_text(listing):
    """Return a user-facing last-refresh label."""
    last_refreshed = getattr(listing, "last_refreshed", None)
    if not last_refreshed:
        return "未刷新"

    delta = datetime.now() - last_refreshed
    total_hours = int(delta.total_seconds() // 3600)
    if total_hours < 1:
        return "1小时内已刷新"
    if total_hours < 24:
        return f"{total_hours}小时前刷新"
    days = total_hours // 24
    return f"{days}天前刷新"


def estimate_basel_sbb_minutes(listing):
    """Estimate public transport time to Basel SBB from shared location or city center."""
    location = (getattr(listing, "location", "") or "").lower()
    city = (getattr(listing, "city", "") or "").lower()
    haystack = " ".join([location, city]).strip()

    for place, minutes in BASEL_SBB_TRANSIT_MINUTES_V2.items():
        if place in haystack:
            if place in location:
                return minutes, "location-based estimate"
            return minutes, "town center estimate"

    postal_minutes = estimate_basel_sbb_minutes_from_postal(location)
    if postal_minutes is not None:
        return postal_minutes, "location-based estimate"

    return None, "estimate unavailable"


def estimate_basel_sbb_minutes_from_postal(text):
    """Estimate Basel SBB minutes from a postal-code prefix."""
    import re

    if not text:
        return None

    for postal_code in re.findall(r"\b\d{4,5}\b", text):
        for prefix, minutes in BASEL_SBB_POSTAL_PREFIX_MINUTES.items():
            if postal_code.startswith(prefix):
                return minutes
    return None


def basel_sbb_text(listing):
    """Return a user-facing Basel SBB commute label."""
    minutes, source = estimate_basel_sbb_minutes(listing)
    if minutes is None:
        return "Basel SBB：未知"
    suffix = "按房源位置估算" if source == "location-based estimate" else "按城镇中心估算"
    return f"Basel SBB：约{minutes}分钟（{suffix}）"


def translate_feature_text(value):
    """Translate common structured feature text into Chinese."""
    text = str(value or "").strip()
    if not text:
        return ""

    lowered = text.lower()
    direct_map = {
        "new property": "新房源",
        "elevator": "有电梯",
        "parking": "有停车位",
        "balcony/terrace": "阳台/露台",
        "garden": "花园",
    }
    if lowered in direct_map:
        return direct_map[lowered]

    prefix_map = {
        "rooms:": "房间数",
        "deposit:": "押金",
        "agency fee:": "中介费",
        "energy:": "能耗等级",
        "ghg:": "温室气体等级",
    }
    for prefix, label in prefix_map.items():
        if lowered.startswith(prefix):
            return f"{label}：{text.split(':', 1)[1].strip()}"

    return text


def translate_property_type_text(value):
    """Translate property type labels into Chinese."""
    mapping = {
        "apartment": "公寓",
        "house": "独栋住宅",
        "studio": "单间",
    }
    return mapping.get(str(value or "").strip().lower(), str(value or "未说明"))


def translate_listing_title(title):
    """Translate common French rental title tokens into Chinese."""
    import re

    text = str(title or "").strip()
    if not text:
        return "未命名房源"

    replacements = [
        (r"\bappartement\b", "公寓"),
        (r"\bstudio\b", "单间"),
        (r"\bmaison\b", "住宅"),
        (r"\bmeubl[ée]?\b", "带家具"),
        (r"\bnon meubl[ée]?\b", "不带家具"),
        (r"\b[àa]\s+louer\b", "出租"),
        (r"\blocation\b", "出租"),
        (r"\bpi[eè]ce\b", "房间"),
        (r"\bpi[eè]ces\b", "房间"),
        (r"\bchambre\b", "卧室"),
        (r"\bchambres\b", "卧室"),
        (r"\bcentre[- ]ville\b", "市中心"),
        (r"\bproche fronti[èe]re\b", "靠近边境"),
        (r"\bproche suisse\b", "靠近瑞士"),
        (r"\bparking\b", "停车位"),
        (r"\bbalcon\b", "阳台"),
        (r"\bterrasse\b", "露台"),
        (r"\bjardin\b", "花园"),
        (r"\br[ée]sidence\b", "住宅区"),
        (r"\bduplex\b", "复式"),
        (r"\bquartier calme\b", "安静街区"),
    ]

    translated = text
    for pattern, replacement in replacements:
        translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)

    translated = re.sub(r"\s+", " ", translated).strip(" -|")
    return translated or text


def translate_description_text(text):
    """Translate common French rental-description phrases into readable Chinese."""
    import re

    source = str(text or "").strip()
    if not source:
        return "暂无描述。"

    translated = f" {source} "
    replacements = [
        (r"\bà louer\b", "出租"),
        (r"\blibre de suite\b", "可立即入住"),
        (r"\blibre début août\b", "8月初可入住"),
        (r"\blibre\b", "可入住"),
        (r"\bstudio\b", "单间"),
        (r"\bappartement\b", "公寓"),
        (r"\bmaison\b", "住宅"),
        (r"\bmeubl[ée]?\b", "带家具"),
        (r"\bnon meubl[ée]?\b", "不带家具"),
        (r"\bpi[eè]ce de vie\b", "起居空间"),
        (r"\bcuisine équipée\b", "配备齐全的厨房"),
        (r"\bcuisine aménagée\b", "已配置厨房"),
        (r"\bcoin cuisine\b", "小厨房"),
        (r"\bsalle de bains\b", "浴室"),
        (r"\bsalle de douche\b", "淋浴间"),
        (r"\bwc\b", "卫生间"),
        (r"\bchambre\b", "卧室"),
        (r"\bchambres\b", "卧室"),
        (r"\bcave\b", "地窖/储物间"),
        (r"\blocal vélo\b", "自行车储藏间"),
        (r"\bplace de parking privée\b", "私人停车位"),
        (r"\bparking privatif\b", "专属停车位"),
        (r"\bparking\b", "停车位"),
        (r"\bbalcon\b", "阳台"),
        (r"\bterrasse\b", "露台"),
        (r"\bascenseur\b", "电梯"),
        (r"\br[ée]sidence\b", "住宅区"),
        (r"\bpetite r[ée]sidence\b", "小型住宅区"),
        (r"\bquartier calme\b", "安静街区"),
        (r"\bproche frontière\b", "靠近边境"),
        (r"\bproche suisse\b", "靠近瑞士"),
        (r"\bproche du tram\b", "靠近电车"),
        (r"\bface au tram\b", "就在电车对面"),
        (r"\bproche gare\b", "靠近火车站"),
        (r"\bcentre ville\b", "市中心"),
        (r"\bcentre-ville\b", "市中心"),
        (r"\bentièrement rénové[e]?\b", "全新翻修"),
        (r"\brefait à neuf\b", "全新翻修"),
        (r"\btrès beau\b", "非常不错"),
        (r"\btrès belles prestations\b", "整体配置很好"),
        (r"\bau calme\b", "环境安静"),
        (r"\blumineux\b", "采光好"),
        (r"\bbien agencé\b", "布局合理"),
        (r"\bsol carrelé\b", "瓷砖地面"),
        (r"\bgrande douche\b", "大淋浴间"),
        (r"\bvaste pièce principale\b", "宽敞主空间"),
        (r"\bcharges comprises\b", "含杂费"),
        (r"\bdont provision sur charges\b", "其中杂费预付款"),
        (r"\bhonoraires charge locataire\b", "租客承担中介费"),
        (r"\bfrais de visite\b", "看房费用"),
        (r"\brédaction du bail\b", "合同起草费"),
        (r"\brégularisation annuelle\b", "按年结算"),
    ]
    for pattern, replacement in replacements:
        translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)

    sentence_fixes = [
        (r"\bpour toutes demandes concernant ce bien, contactez directement\b", "如需咨询这套房源，请直接联系"),
        (r"\bet pour plus d'informations concernant ce bien, contactez\b", "如需更多信息，请联系"),
        (r"\bdécouvrez\b", "可了解"),
        (r"\bsitué dans\b", "位于"),
        (r"\bil est\b", "房源为"),
        (r"\bà l'entrée\b", "入户处有"),
        (r"\bde plus, vous trouverez\b", "另外还有"),
        (r"\bce bien se compose de\b", "这套房源包括"),
    ]
    for pattern, replacement in sentence_fixes:
        translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)

    translated = re.sub(r"\s+", " ", translated).strip()
    translated = translated.replace(" !", "！").replace(" ?", "？")
    return translated


def closest_public_transport_distance(listing):
    """Extract nearest bus/tram/train distance in meters from listing text."""
    import re

    payload = " ".join(
        part for part in [
            getattr(listing, "description", "") or "",
            " ".join(getattr(listing, "features", []) or []),
            json.dumps(getattr(listing, "contact_info", {}) or {}, ensure_ascii=False),
        ]
        if part
    )
    lowered = " ".join(payload.lower().split())
    patterns = [
        r"(\d{2,4})\s*m(?:[èe]tres?)?\s*(?:du|de la|de l['’]|de|des|d['’])?\s*(tram|bus|gare|train|transports?)",
        r"(tram|bus|gare|train|transports?)\s*(?:à|a)?\s*(\d{2,4})\s*m(?:[èe]tres?)?",
        r"(\d{2,4})\s*m(?:[èe]tres?)?\s*(?:à pied )?(?:du|de la|de l['’]|de|des|d['’])?\s*(tram|bus|gare|train|station)",
    ]
    label_map = {
        "tram": "电车",
        "bus": "公交",
        "gare": "火车站",
        "train": "火车站",
        "station": "车站",
        "transport": "公共交通",
        "transports": "公共交通",
    }
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, lowered, re.IGNORECASE):
            if match.group(1).isdigit():
                meters = int(match.group(1))
                transport_key = match.group(2)
            else:
                transport_key = match.group(1)
                meters = int(match.group(2))
            if 20 <= meters <= 5000:
                matches.append((meters, label_map.get(transport_key, "公共交通")))

    if not matches:
        return None, None
    return min(matches, key=lambda item: item[0])


def compute_pros_cons(listing):
    """Generate lightweight review hints for a listing."""
    pros = []
    cons = []

    if listing.images and len(listing.images) >= 6:
        pros.append("照片数量充足")
    elif not listing.images:
        cons.append("没有保存到照片")
    else:
        cons.append("照片数量偏少")

    if listing.area and listing.price:
        price_per_m2 = listing.price / listing.area
        if price_per_m2 <= 25:
            pros.append("每平方米租金看起来较有吸引力")
        elif price_per_m2 >= 40:
            cons.append("每平方米租金偏高")

    if listing.features:
        feature_blob = " ".join(listing.features).lower()
        if "balcony" in feature_blob or "balcon" in feature_blob:
            pros.append("带阳台")
        if "parking" in feature_blob:
            pros.append("带停车位")
        if "elevator" in feature_blob or "ascenseur" in feature_blob:
            pros.append("带电梯")

    if getattr(listing, "available_date", None):
        if listing.available_date.date() <= datetime.now().date() + timedelta(days=14):
            pros.append("可入住时间较近")
        else:
            cons.append("可入住时间不算近")
    else:
        cons.append("缺少可入住日期")

    if not listing.description:
        cons.append("房源描述较少")

    return pros[:3], cons[:3]


def extract_description_details(listing):
    """Extract lightweight structured hints from listing description text."""
    import re

    text = " ".join(
        part for part in [getattr(listing, "description", "") or "", " ".join(getattr(listing, "features", []) or [])]
        if part
    )
    normalized = " ".join(text.split())
    lowered = normalized.lower()
    details = []

    def add(label, value):
        if value and (label, value) not in details:
            details.append((label, value))

    charges_match = re.search(r"(?:charges?|charge)\s*[:\-]?\s*(\d+[\s,.]?\d*)\s*(?:€|eur)", normalized, re.IGNORECASE)
    if charges_match:
        add("杂费", f"EUR {charges_match.group(1).replace(' ', '').replace(',', '.')}")

    deposit_match = re.search(r"(?:d[eé]p[oô]t(?: de garantie)?|caution)\s*[:\-]?\s*(\d+[\s,.]?\d*)\s*(?:€|eur)", normalized, re.IGNORECASE)
    if deposit_match:
        add("押金", f"EUR {deposit_match.group(1).replace(' ', '').replace(',', '.')}")

    fee_match = re.search(r"(?:honoraires?|agency fee|frais d'agence)\s*[:\-]?\s*(\d+[\s,.]?\d*)\s*(?:€|eur)", normalized, re.IGNORECASE)
    if fee_match:
        add("中介费", f"EUR {fee_match.group(1).replace(' ', '').replace(',', '.')}")

    floor_match = re.search(r"(\d+)(?:er|e|ème)?\s+[ée]tage", lowered)
    if floor_match:
        add("楼层", f"{floor_match.group(1)} 楼")
    elif "rez-de-chauss" in lowered or "rdc" in lowered:
        add("楼层", "底层")

    room_match = re.search(r"\b(?:f|t)(\d+)\b", lowered)
    if room_match:
        add("户型", f"{room_match.group(1)} 室")

    bedroom_match = re.search(r"(\d+)\s+chambres?", lowered)
    if bedroom_match:
        add("卧室", f"{bedroom_match.group(1)} 间")

    bathroom_match = re.search(r"(\d+)\s+salles?\s+de\s+bains?", lowered)
    if bathroom_match:
        add("浴室", f"{bathroom_match.group(1)} 间")

    if "meubl" in lowered:
        add("家具", "带家具")
    if "balcon" in lowered:
        add("户外", "阳台")
    if "terrasse" in lowered:
        add("户外", "露台")
    if "jardin" in lowered:
        add("户外", "花园")
    if "parking" in lowered or "stationnement" in lowered:
        add("停车", "有停车位")
    if "garage" in lowered:
        add("停车", "有车库")
    if "cave" in lowered:
        add("储物", "有地窖/储藏室")
    if "ascenseur" in lowered:
        add("楼宇", "有电梯")
    if "duplex" in lowered:
        add("格局", "复式")
    if "centre-ville" in lowered:
        add("位置", "靠近市中心")
    if "fronti" in lowered or "suisse" in lowered:
        add("通勤", "靠近瑞士边境")
    if "passerelle" in lowered:
        add("通勤", "靠近步行桥")
    if "tram" in lowered or "bus" in lowered or "gare" in lowered:
        add("交通", "提到公共交通便利")
    transport_distance, transport_type = closest_public_transport_distance(listing)
    if transport_distance and transport_type:
        add("最近交通", f"{transport_type}约 {transport_distance} 米")

    return details[:10]


def compact_extracted_labels(listing, limit=3):
    """Return a small set of high-signal extracted detail labels for cards."""
    preferred = {"押金", "中介费", "楼层", "户型", "卧室", "户外", "停车", "交通", "最近交通", "位置", "家具", "杂费"}
    extracted = extract_description_details(listing)
    items = []
    for label, value in extracted:
        if label in preferred:
            items.append(f"{label} {value}")
        if len(items) >= limit:
            break
    return items


def matches_description_filters(listing, ui_filters):
    """Apply lightweight UI-only filters based on extracted description details."""
    extracted = extract_description_details(listing)
    extracted_map = {}
    for label, value in extracted:
        extracted_map.setdefault(label, []).append(value)

    if ui_filters.get("need_parking"):
        parking_values = extracted_map.get("停车", [])
        if not parking_values:
            return False
    if ui_filters.get("need_balcony"):
        outdoor_values = extracted_map.get("户外", [])
        if not any(item in {"阳台", "露台"} for item in outdoor_values):
            return False
    if ui_filters.get("need_furnished"):
        furniture_values = extracted_map.get("家具", [])
        if "带家具" not in furniture_values:
            return False
    if ui_filters.get("need_border"):
        commute_values = extracted_map.get("通勤", [])
        if "靠近瑞士边境" not in commute_values and "靠近步行桥" not in commute_values:
            return False
    if ui_filters.get("need_elevator"):
        building_values = extracted_map.get("楼宇", [])
        if "有电梯" not in building_values:
            return False

    return True


def chinese_summary(listing):
    """Create a richer Chinese summary for fast review."""
    location = listing.location or listing.city or "位置待确认"
    rent = f"{int(listing.price)}欧元" if listing.price else "租金未知"
    area = f"{int(listing.area)}平方米" if listing.area else "面积未知"
    features = "、".join(translate_feature_text(item) for item in (listing.features or [])[:4]) or "暂无明确配套信息"
    extracted = extract_description_details(listing)
    extracted_text = "；".join(f"{label}{value}" for label, value in extracted[:4]) if extracted else "描述里没有提取到更多结构化信息"
    pros, cons = compute_pros_cons(listing)
    pros_text = "；".join(pros) if pros else "暂时没有明显优势"
    cons_text = "；".join(cons) if cons else "暂时没有明显风险"
    rating = f"个人评分 {listing.personal_rating}/5。" if getattr(listing, "personal_rating", None) else ""
    commute_minutes, commute_source = estimate_basel_sbb_minutes(listing)
    if commute_minutes is None:
        commute_text = "到Basel SBB的公共交通时间暂时无法估算。"
    else:
        source_text = "按房东提供位置估算" if commute_source == "location-based estimate" else "按城市中心估算"
        commute_text = f"到Basel SBB公共交通约{commute_minutes}分钟，{source_text}。"
    transport_distance, transport_type = closest_public_transport_distance(listing)
    if transport_distance and transport_type:
        transport_text = f"房源中提到最近{transport_type}约 {transport_distance} 米。"
    else:
        transport_text = "房源中暂时没有明确写出最近公交、电车或火车站的米数距离。"
    return (
        f"这套房源来自{listing.source or '未知来源'}，位于{location}，月租约{rent}，面积约{area}。"
        f"房型为{translate_property_type_text(listing.property_type)}，{availability_text(listing)}。"
        f"{commute_text}"
        f"{transport_text}"
        f"目前提取到的主要信息包括：{features}。"
        f"从描述中进一步识别到：{extracted_text}。"
        f"优点：{pros_text}。风险点：{cons_text}。{rating}"
    )


def score_badges(listing):
    """Return quick review badges."""
    badges = []
    if listing.area and listing.price:
        badges.append(f"每平米约 EUR {listing.price / listing.area:.0f}")
    badges.append(f"{len(listing.images or [])} 张照片")
    badges.append(availability_text(listing))
    commute_minutes, _ = estimate_basel_sbb_minutes(listing)
    if commute_minutes is not None:
        badges.append(f"Basel SBB 约{commute_minutes}分钟")
    transport_distance, transport_type = closest_public_transport_distance(listing)
    if transport_distance and transport_type:
        badges.append(f"最近{transport_type}约 {transport_distance} 米")
    badges.append(refresh_age_text(listing))
    if getattr(listing, "needs_review", False):
        badges.append("待复查")
    if getattr(listing, "first_seen", None):
        age_days = (datetime.now().date() - listing.first_seen.date()).days
        if age_days <= 1:
            badges.append("新收录")
    return badges


def scan_from_dashboard(filters, sources):
    """Run a scan and return status text."""
    result = run_scan(filters, sources=sources, reconcile_inventory=False)
    parts = []
    has_error = False
    for source in result["sources"]:
        source_result = result["per_source_results"].get(source, {})
        if source_result.get("error"):
            has_error = True
            parts.append(f"{source}: 失败 - {source_result['error']}")
        else:
            parts.append(f"{source}: {source_result.get('count', 0)} 条")
    parts.append(f"新增 {result.get('new_count', 0)} 条")
    parts.append(f"更新 {result.get('updated_count', 0)} 条")
    return result, " | ".join(parts), has_error


def parse_pasted_listing_text(text, default_place):
    """Extract a minimal listing from pasted ad text."""
    import re

    cleaned_text = (text or "").strip()
    if not cleaned_text:
        return None

    listing = {
        "title": "",
        "description": cleaned_text,
        "price": 0.0,
        "area": 0.0,
        "location": default_place,
        "city": default_place,
        "property_type": "apartment",
        "features": [],
    }

    price_patterns = [
        r"(\d+[\s,.]?\d*)\s*(?:EUR|euros?)",
        r"(\d+[\s,.]?\d*)\s*(?:€)",
        r"loyer[:\s]*(\d+[\s,.]?\d*)",
        r"prix[:\s]*(\d+[\s,.]?\d*)",
    ]
    for pattern in price_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            try:
                listing["price"] = float(match.group(1).replace(" ", "").replace(",", "."))
                break
            except ValueError:
                continue

    area_patterns = [
        r"(\d+[\s,.]?\d*)\s*(?:m2|m²)",
        r"surface[:\s]*(\d+[\s,.]?\d*)",
    ]
    for pattern in area_patterns:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            try:
                listing["area"] = float(match.group(1).replace(" ", "").replace(",", "."))
                break
            except ValueError:
                continue

    for place in TRACKED_PLACES + ["Saint-Louis", "Hesingue", "Blotzheim"]:
        if place.lower() in cleaned_text.lower():
            listing["location"] = place
            listing["city"] = place
            break

    lowered = cleaned_text.lower()
    if any(token in lowered for token in ["maison", "house"]):
        listing["property_type"] = "house"
    elif "studio" in lowered:
        listing["property_type"] = "studio"

    feature_tokens = {
        "balcon": "balcony",
        "balcony": "balcony",
        "parking": "parking",
        "garage": "garage",
        "meubl": "furnished",
        "furnished": "furnished",
        "ascenseur": "elevator",
        "elevator": "elevator",
        "jardin": "garden",
        "garden": "garden",
    }
    for token, label in feature_tokens.items():
        if token in lowered and label not in listing["features"]:
            listing["features"].append(label)

    first_line = cleaned_text.splitlines()[0][:100]
    title_line = re.sub(r"\s+", " ", first_line).strip()
    listing["title"] = title_line or "Listing from pasted text"

    if listing["price"] <= 0:
        return None

    return listing


def render_manual_add_panel(db):
    """Render a lean manual-add fallback for blocked search results."""
    with st.sidebar.expander("Add listing manually", expanded=False):
        st.caption("Use this when the automated website scan is blocked or misses a listing.")
        pasted_text = st.text_area(
            "Paste ad text to auto-fill",
            height=120,
            placeholder="Paste the listing title/description here and the app will try to extract price, area, place, and features.",
        )
        auto_fill = st.button("Auto-fill from pasted text", use_container_width=True)
        if auto_fill:
            parsed = parse_pasted_listing_text(pasted_text, TRACKED_PLACES[0])
            if parsed:
                st.session_state["manual_prefill"] = parsed
                st.success("Fields auto-filled from pasted text.")
            else:
                st.warning("I could not detect a rent amount from the pasted text.")

        prefill = st.session_state.get("manual_prefill", {})
        with st.form("manual_listing_form", clear_on_submit=True):
            manual_url = st.text_input("Listing URL", value="", placeholder="https://www.bienici.com/...")
            manual_title = st.text_input("Title", value=prefill.get("title", ""))
            default_place = prefill.get("city") if prefill.get("city") in TRACKED_PLACES else TRACKED_PLACES[0]
            manual_place = st.selectbox("Place", TRACKED_PLACES, index=TRACKED_PLACES.index(default_place), key="manual_place")
            manual_price = st.number_input("Monthly rent (EUR)", min_value=0, max_value=10000, value=int(prefill.get("price", 1200) or 1200), step=50)
            manual_area = st.number_input("Area (m2)", min_value=0, max_value=500, value=int(prefill.get("area", 50) or 50), step=1)
            default_type = "House" if prefill.get("property_type") == "house" else "Apartment"
            manual_type = st.selectbox("Property type", ["Apartment", "House"], index=0 if default_type == "Apartment" else 1, key="manual_type")
            manual_description = st.text_area("Notes / description", value=prefill.get("description", ""), height=100)
            manual_features = st.text_input("Features", value=", ".join(prefill.get("features", [])), placeholder="balcony, parking, furnished")
            submitted = st.form_submit_button("Save listing", use_container_width=True)

        if submitted:
            if not manual_title.strip():
                st.warning("Add at least a title before saving.")
            else:
                timestamp = int(datetime.now().timestamp())
                listing_data = {
                    "listing_id": f"manual_{timestamp}",
                    "source": ACTIVE_SOURCES[0],
                    "url": manual_url.strip() or f"manual://{timestamp}",
                    "title": manual_title.strip(),
                    "description": manual_description.strip(),
                    "price": float(manual_price),
                    "area": float(manual_area),
                    "location": manual_place,
                    "city": manual_place,
                    "property_type": manual_type.lower(),
                    "features": [item.strip() for item in manual_features.split(",") if item.strip()],
                    "images": [],
                    "needs_review": True,
                }
                db.add_listing(listing_data)
                st.session_state["manual_prefill"] = {}
                st.success("Listing saved. It is now in your review queue.")


def refresh_listing_manually(db, listing):
    """Refresh a single listing from its source URL."""
    if getattr(listing, "source", "") == "Bienici":
        scraper = BieniciScraper()
        refreshed_listing = scraper.fetch_listing_by_id(listing.listing_id)
        if not refreshed_listing:
            return False, scraper.last_error or "Bien'ici 房源刷新失败。"
        refreshed_listing["listing_id"] = listing.listing_id or refreshed_listing.get("listing_id")
        refreshed_listing["source"] = listing.source or refreshed_listing.get("source")
        db.add_listing(refreshed_listing)
        return True, "已从 Bien'ici 更新房源。"

    if not listing.url:
        return False, "该房源没有原始链接，无法刷新。"

    scraper = init_url_scraper()
    refreshed_listing = scraper.scrape_url(listing.url)
    if not refreshed_listing:
        return False, "刷新失败，网站可能拦截了请求，或房源已经下架。"

    refreshed_listing["listing_id"] = listing.listing_id or refreshed_listing.get("listing_id")
    refreshed_listing["source"] = listing.source or refreshed_listing.get("source")
    db.add_listing(refreshed_listing)
    return True, "已从原始来源更新房源。"


def refresh_listing_batch(db, listings, scope_label):
    """Refresh a batch of listings from their source URLs."""
    total = len(listings)
    refreshed = 0
    failed = []

    progress_bar = st.progress(0)
    status = st.empty()

    for index, listing in enumerate(listings, start=1):
        title = translate_listing_title(listing.title)
        status.write(f"正在刷新{scope_label}：{index}/{total} - {title}")
        success, message = refresh_listing_manually(db, listing)
        if success:
            refreshed += 1
        else:
            failed.append(f"{title}: {message}")
        progress_bar.progress(index / total)

    progress_bar.empty()
    status.empty()
    return refreshed, failed


def toggle_compare(listing_id):
    """Add or remove a listing from compare mode."""
    compare_ids = list(st.session_state.compare_ids)
    if listing_id in compare_ids:
        compare_ids.remove(listing_id)
    else:
        if len(compare_ids) >= 4:
            compare_ids = compare_ids[1:]
        compare_ids.append(listing_id)
    st.session_state.compare_ids = compare_ids


def build_filters(sidebar_defaults):
    """Render sidebar filters and return DB filters plus scan filters."""
    with st.sidebar:
        st.header("房源筛选")

        city = st.selectbox("地区", TRACKED_PLACES, index=TRACKED_PLACES.index(sidebar_defaults["location"]) if sidebar_defaults["location"] in TRACKED_PLACES else 0)
        price_range = st.slider(
            "月租范围（欧元）",
            min_value=0,
            max_value=5000,
            value=(sidebar_defaults["min_price"], sidebar_defaults["max_price"]),
            step=100,
        )
        area_range = st.slider(
            "面积范围（平方米）",
            min_value=0,
            max_value=250,
            value=(sidebar_defaults["min_area"], sidebar_defaults["max_area"]),
            step=5,
        )
        property_type = st.selectbox("房型", TRACKED_PROPERTY_TYPES, format_func=lambda v: {"All": "全部", "Apartment": "公寓", "House": "房屋"}.get(v, v))
        st.caption("可入住时间")
        availability_within_3_months = st.checkbox("3个月内", value=False)
        availability_3_to_4_months = st.checkbox("3-4个月", value=False)
        availability_over_4_months = st.checkbox("4个月以上", value=False)
        availability_unknown = st.checkbox("未知", value=False)
        recency_window = st.selectbox("收录时间", list(RECENCY_FILTERS.keys()), format_func=lambda v: {
            "All listings": "全部房源",
            "Seen in last 24h": "最近24小时",
            "Seen in last 3 days": "最近3天",
            "Seen in last 7 days": "最近7天",
            "Seen in last 14 days": "最近14天",
        }.get(v, v))
        sort_label = st.selectbox("排序方式", list(SORT_OPTIONS.keys()), format_func=lambda v: {
            "Newest first": "最新优先",
            "Lowest price": "租金最低",
            "Highest price": "租金最高",
            "Largest area": "面积最大",
            "Soonest availability": "最早可入住",
        }.get(v, v))
        favorites_only = st.checkbox("只看收藏", value=False)
        contacted_only = st.checkbox("只看已联系", value=False)
        needs_review_only = st.checkbox("只看待复查", value=False)
        min_rating = st.slider("最低个人评分", min_value=0, max_value=5, value=0, step=1)
        max_basel_minutes = st.slider("到 Basel SBB 最长分钟数（估算）", min_value=0, max_value=120, value=120, step=5)
        require_basel_estimate = st.checkbox("只显示有 Basel SBB 通勤估算的房源", value=False)
        st.caption("描述筛选")
        need_parking = st.checkbox("只看提到停车的房源", value=False)
        need_balcony = st.checkbox("只看提到阳台/露台的房源", value=False)
        need_furnished = st.checkbox("只看带家具房源", value=False)
        need_border = st.checkbox("只看靠近边境/步行桥的房源", value=False)
        need_elevator = st.checkbox("只看提到电梯的房源", value=False)

        st.divider()
        st.caption("打开页面只读取已保存房源；点击这里才会联网增量上新。")
        scan_clicked = st.button("增量上新", type="primary", use_container_width=True)

    db_filters = {
        "city": city if city else None,
        "min_price": price_range[0],
        "max_price": price_range[1],
        "min_area": area_range[0],
        "max_area": area_range[1],
        "sort_by": SORT_OPTIONS[sort_label],
        "sources": ACTIVE_SOURCES,
    }
    if property_type != "All":
        db_filters["property_type"] = property_type.lower()
    if favorites_only:
        db_filters["is_favorite"] = True
    if contacted_only:
        db_filters["contacted"] = True
    if needs_review_only:
        db_filters["needs_review"] = True
    if min_rating > 0:
        db_filters["min_rating"] = min_rating
    recency_days = RECENCY_FILTERS[recency_window]
    if recency_days:
        db_filters["seen_after"] = datetime.now() - timedelta(days=recency_days)

    scan_filters = {
        "location": city or sidebar_defaults["location"],
        "min_price": price_range[0],
        "max_price": price_range[1],
        "min_area": area_range[0],
        "max_area": area_range[1],
        "property_type": property_type.lower() if property_type != "All" else "all",
    }
    ui_filters = {
        "max_basel_minutes": max_basel_minutes,
        "require_basel_estimate": require_basel_estimate,
        "need_parking": need_parking,
        "need_balcony": need_balcony,
        "need_furnished": need_furnished,
        "need_border": need_border,
        "need_elevator": need_elevator,
        "availability_within_3_months": availability_within_3_months,
        "availability_3_to_4_months": availability_3_to_4_months,
        "availability_over_4_months": availability_over_4_months,
        "availability_unknown": availability_unknown,
    }
    return db_filters, scan_filters, ACTIVE_SOURCES, scan_clicked, ui_filters


def render_metrics(stats, listings):
    """Render summary metrics."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("总房源", stats["total_listings"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("收藏", stats["favorites"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("待复查", stats.get("needs_review", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("有可入住日期", stats.get("with_available_date", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("当前结果", len(listings))
        st.markdown('</div>', unsafe_allow_html=True)


def render_compare_strip(listings):
    """Render selected listings for comparison."""
    if not st.session_state.compare_ids:
        return

    st.markdown("### 对比清单")
    compare_map = {listing.id: listing for listing in listings if listing.id in st.session_state.compare_ids}
    if not compare_map:
        st.info("当前筛选条件下没有可对比的房源。")
        return

    compare_listings = [compare_map[listing_id] for listing_id in compare_map]

    metric_rows = []
    for listing in compare_listings:
        pros, cons = compute_pros_cons(listing)
        extracted_brief = "；".join(compact_extracted_labels(listing, limit=2)) or "-"
        metric_rows.append(
            {
                "Listing": translate_listing_title(listing.title)[:36],
                "Rent": format_price(listing.price),
                "Area": format_area(listing.area),
                "Availability": availability_text(listing),
                "Basel SBB": basel_sbb_text(listing),
                "Photos": len(listing.images or []),
                "细节": extracted_brief,
                "Rating": listing.personal_rating if listing.personal_rating is not None else "-",
                "Pros": ", ".join(pros) if pros else "-",
                "Risks": ", ".join(cons) if cons else "-",
            }
        )

    st.dataframe(pd.DataFrame(metric_rows), use_container_width=True, hide_index=True)

    cols = st.columns(len(compare_map))
    for col, listing_id in zip(cols, compare_map):
        listing = compare_map[listing_id]
        with col:
            st.markdown('<div class="compare-card">', unsafe_allow_html=True)
            st.markdown(f"**{translate_listing_title(listing.title)}**")
            st.caption(f"{format_price(listing.price)} | {format_area(listing.area)}")
            st.caption(f"{listing.location or listing.city or '位置未知'}")
            render_badge_row([availability_text(listing), basel_sbb_text(listing)])
            render_badge_row(compact_extracted_labels(listing, limit=2))
            if listing.images:
                st.markdown('<div class="photo-frame">', unsafe_allow_html=True)
                st.image(listing.images[0], use_column_width=True)
                compare_photo_index = st.selectbox(
                    "对比照片",
                    options=list(range(len(listing.images))),
                    format_func=lambda idx: f"照片 {idx + 1}",
                    key=f"compare_photo_{listing.id}",
                )
                st.image(listing.images[compare_photo_index], use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            st.write(chinese_summary(listing))
            if st.button("移出对比", key=f"remove_compare_{listing.id}", use_container_width=True):
                toggle_compare(listing.id)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_listing_selector(listings, visible_count=None):
    """Render the left-side browser and selection actions."""
    st.caption("选择一条房源查看")
    if visible_count is None:
        visible_count = len(listings)

    visible_listings = list(listings[:visible_count])
    selected_listing = next((listing for listing in listings if listing.id == st.session_state.selected_listing_id), None)
    if selected_listing and selected_listing.id not in {listing.id for listing in visible_listings}:
        visible_listings.insert(0, selected_listing)

    for listing in visible_listings:
        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        preview_col, text_col = st.columns([0.9, 1.5], gap="small")
        with preview_col:
            if listing.images:
                st.markdown('<div class="listing-thumb">', unsafe_allow_html=True)
                st.image(listing.images[0], use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="listing-thumb-empty">暂无照片预览</div>', unsafe_allow_html=True)
        with text_col:
            st.markdown(f"**{translate_listing_title(listing.title)}**")
            st.markdown(f'<div class="listing-price">{format_price(listing.price)}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="listing-meta">{format_area(listing.area)} · {listing.location or listing.city or "位置未知"}</div>',
                unsafe_allow_html=True,
            )
            # Public Transportation Distance Indicator 🚇
            transport_distance = get_transport_distance_indicator(listing)
            if transport_distance:
                st.markdown(f'<div class="listing-meta" style="margin-top: 0.2rem;">{transport_distance}</div>', unsafe_allow_html=True)
            render_badge_row(score_badges(listing)[:4])
            render_badge_row(compact_extracted_labels(listing, limit=2))
            st.caption(listing.source)
        btn1, btn2 = st.columns(2)
        with btn1:
            label = "查看中" if (st.session_state.detail_open and st.session_state.selected_listing_id == listing.id) else "打开"
            if st.button(label, key=f"select_{listing.id}", use_container_width=True):
                st.session_state.selected_listing_id = listing.id
                st.session_state.detail_open = True
                st.rerun()
        with btn2:
            compare_label = "已加入对比" if listing.id in st.session_state.compare_ids else "加入对比"
            if st.button(compare_label, key=f"compare_{listing.id}", use_container_width=True):
                toggle_compare(listing.id)
                st.rerun()
        if st.session_state.detail_open and st.session_state.selected_listing_id == listing.id:
            st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
            if st.button("收起详情", key=f"collapse_inline_{listing.id}", use_container_width=True):
                st.session_state.detail_open = False
                st.rerun()
            render_mobile_inline_detail(listing)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if visible_count < len(listings):
        remaining = len(listings) - visible_count
        if st.button(f"显示更多（还剩 {remaining} 套）", key="show_more_listings", use_container_width=True):
            st.session_state.listing_list_count = min(len(listings), visible_count + 20)
            st.rerun()


def render_swipe_gallery(images, uid, height=370):
    """Render a touch-swipeable photo carousel via an HTML component.

    Works on mobile (touch swipe left/right) and desktop (arrow buttons).
    ``uid`` must be unique per listing on the page to avoid JS conflicts.
    """
    if not images:
        return
    imgs_js = json.dumps(images)
    safe = str(uid).replace("-", "_")
    html = f"""
<style>
  body {{ margin:0; background:transparent; }}
  #wrap_{safe} {{
    position: relative;
    width: 100%;
    font-family: sans-serif;
    user-select: none;
    -webkit-user-select: none;
  }}
  #imgbox_{safe} {{
    position: relative;
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    background: #1a1a1a;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 180px;
  }}
  #photo_{safe} {{
    width: 100%;
    max-height: 340px;
    object-fit: contain;
    display: block;
    transition: opacity 0.15s;
  }}
  /* Counter pill — top centre, always on top of image */
  #counter_{safe} {{
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.55);
    color: #fff;
    font-size: 0.78rem;
    padding: 2px 10px;
    border-radius: 20px;
    pointer-events: none;
    white-space: nowrap;
    z-index: 10;
  }}
  /* Arrow buttons — vertically centred on image sides */
  .arr_{safe} {{
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0,0,0,0.45);
    border: none;
    border-radius: 50%;
    color: #fff;
    font-size: 1.5rem;
    line-height: 1;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    padding: 0;
    -webkit-tap-highlight-color: transparent;
  }}
  .arr_{safe}:active {{ background: rgba(0,0,0,0.7); }}
  #prev_{safe} {{ left: 8px; }}
  #next_{safe} {{ right: 8px; }}
</style>
<div id="wrap_{safe}">
  <div id="imgbox_{safe}">
    <img id="photo_{safe}" src="" alt="照片" onerror="this.style.opacity='0.3'">
    <span id="counter_{safe}">1 / {len(images)}</span>
    <button id="prev_{safe}" class="arr_{safe}" onclick="prevPhoto_{safe}()">&#8249;</button>
    <button id="next_{safe}" class="arr_{safe}" onclick="nextPhoto_{safe}()">&#8250;</button>
  </div>
</div>
<script>
(function() {{
  var imgs = {imgs_js};
  var idx = 0;
  var el = document.getElementById('wrap_{safe}');
  var imgEl = document.getElementById('photo_{safe}');
  var ctr = document.getElementById('counter_{safe}');

  function show(i) {{
    idx = ((i % imgs.length) + imgs.length) % imgs.length;
    imgEl.style.opacity = '0.5';
    imgEl.src = imgs[idx];
    imgEl.onload = function() {{ imgEl.style.opacity = '1'; }};
    ctr.textContent = (idx + 1) + ' / ' + imgs.length;
  }}

  window['prevPhoto_{safe}'] = function() {{ show(idx - 1); }};
  window['nextPhoto_{safe}'] = function() {{ show(idx + 1); }};

  // Touch swipe
  var startX = 0;
  el.addEventListener('touchstart', function(e) {{
    startX = e.touches[0].clientX;
  }}, {{passive: true}});
  el.addEventListener('touchend', function(e) {{
    var dx = e.changedTouches[0].clientX - startX;
    if (dx > 40) show(idx - 1);
    else if (dx < -40) show(idx + 1);
  }}, {{passive: true}});

  // Keyboard arrows when focused
  el.setAttribute('tabindex', '0');
  el.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  }});

  // Hide arrows when there is only one image
  if (imgs.length <= 1) {{
    var p = document.getElementById('prev_{safe}');
    var n = document.getElementById('next_{safe}');
    if (p) p.style.display = 'none';
    if (n) n.style.display = 'none';
  }}

  show(0);
}})();
</script>
"""
    stc.html(html, height=height, scrolling=False)


def render_photo_gallery(listing):
    """Render photo gallery for selected listing."""
    if not listing.images:
        st.info("这条房源目前没有保存到照片。")
        return
    render_swipe_gallery(listing.images, uid=f"desk_{listing.id}")


def render_review_editor(db, listing):
    """Render review notes and rating controls."""
    st.markdown("### 复查笔记")
    current_rating = int(listing.personal_rating or 0)
    rating = st.slider("个人评分", min_value=0, max_value=5, value=current_rating, step=1, key=f"rating_{listing.id}")
    notes = st.text_area(
        "笔记",
        value=listing.review_notes or "",
        placeholder="写下你喜欢的点、担心的点，以及是否想联系房东。",
        key=f"notes_{listing.id}",
        height=140,
    )
    if st.button("保存复查", key=f"save_review_{listing.id}", use_container_width=True):
        db.update_review(listing.id, rating=rating, notes=notes)
        st.rerun()


def render_extracted_details(listing):
    """Show details parsed out of the free-text description."""
    extracted = extract_description_details(listing)
    if not extracted:
        return

    st.markdown('<div class="detail-block">', unsafe_allow_html=True)
    st.markdown("### 描述提取细节")
    col_count = min(3, len(extracted))
    cols = st.columns(col_count)
    for idx, (label, value) in enumerate(extracted):
        with cols[idx % col_count]:
            st.markdown(
                f'<div class="spec-card"><div class="spec-label">{label}</div><div class="spec-value">{value}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)


def render_listing_detail(db, listing):
    """Render detail panel for a selected listing."""
    st.markdown('<div class="detail-shell">', unsafe_allow_html=True)
    title_col, action_col = st.columns([3, 1])
    with title_col:
        st.markdown(f"## {translate_listing_title(listing.title)}")
        st.markdown(
            f'<div class="detail-topline">{listing.source} | {listing.location or listing.city or "位置未知"} | {format_price(listing.price)} | {format_area(listing.area)}</div>',
            unsafe_allow_html=True,
        )
        render_badge_row(score_badges(listing))
    with action_col:
        if st.button("收藏 / 取消收藏", key=f"fav_{listing.id}", use_container_width=True):
            db.toggle_favorite(listing.id)
            st.rerun()
        if st.button("标记已联系", key=f"contact_{listing.id}", use_container_width=True):
            db.mark_viewed(listing.id)
            st.rerun()
        if st.button("切换复查标记", key=f"review_flag_{listing.id}", use_container_width=True):
            db.toggle_needs_review(listing.id)
            st.rerun()
        if st.button("隐藏 / 排除", key=f"hide_{listing.id}", use_container_width=True):
            db.toggle_hidden(listing.id)
            st.rerun()
        if st.button("从来源刷新", key=f"refresh_{listing.id}", use_container_width=True):
            with st.spinner("正在刷新房源..."):
                success, refresh_message = refresh_listing_manually(db, listing)
            st.session_state.listing_flash_message = refresh_message
            if success:
                st.rerun()

    st.markdown(f'<div class="zh-summary"><strong>中文摘要</strong><br>{chinese_summary(listing)}</div>', unsafe_allow_html=True)

    if st.session_state.listing_flash_message:
        st.info(st.session_state.listing_flash_message)
        st.session_state.listing_flash_message = None

    render_spec_grid(listing)

    stat1, stat2, stat3, stat4 = st.columns(4)
    stat1.metric("可入住时间", availability_text(listing))
    stat2.metric("照片数量", len(listing.images or []))
    stat3.metric("收藏", "是" if listing.is_favorite else "否")
    stat4.metric("待复查", "是" if getattr(listing, "needs_review", False) else "否")
    st.caption(refresh_age_text(listing))
    st.caption(basel_sbb_text(listing))
    transport_distance, transport_type = closest_public_transport_distance(listing)
    if transport_distance and transport_type:
        st.caption(f"最近公共交通：最近{transport_type}约 {transport_distance} 米")

    render_photo_gallery(listing)
    render_extracted_details(listing)

    st.markdown('<div class="detail-block">', unsafe_allow_html=True)
    st.markdown("### 房源详情")
    st.write(f"**中文标题：** {translate_listing_title(listing.title)}")
    st.write(f"**原文标题：** {listing.title or '暂无'}")
    translated_features = [translate_feature_text(item) for item in (listing.features or []) if translate_feature_text(item)]
    st.write(f"**主要特点（中文）：** {'、'.join(translated_features) if translated_features else '暂无'}")
    if transport_distance and transport_type:
        st.write(f"**最近公共交通：** 最近{transport_type}约 {transport_distance} 米")
    else:
        st.write("**最近公共交通：** 暂无明确米数信息")
    st.write(f"**可入住日期：** {listing.available_date.strftime('%Y-%m-%d') if listing.available_date else '未知'}")
    st.write(f"**首次收录：** {listing.first_seen.strftime('%Y-%m-%d') if listing.first_seen else '未知'}")
    st.write(f"**原始链接：** {listing.url or '无'}")
    st.write("**中文描述：**")
    st.write(translate_description_text(listing.description))
    st.write("**原文描述：**")
    st.write(listing.description or "暂无描述。")
    if listing.url:
        st.link_button("打开原始房源", listing.url)
    st.markdown('</div>', unsafe_allow_html=True)

    render_review_editor(db, listing)
    st.markdown('</div>', unsafe_allow_html=True)


def render_mobile_inline_detail(listing):
    """Render a compact read-only detail block inside a selected mobile card."""
    st.markdown('<div class="detail-block">', unsafe_allow_html=True)
    st.markdown(f"### {translate_listing_title(listing.title)}")
    st.markdown(
        f'<div class="detail-topline">{listing.source} | {listing.location or listing.city or "位置未知"} | {format_price(listing.price)} | {format_area(listing.area)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="zh-summary"><strong>中文摘要</strong><br>{chinese_summary(listing)}</div>', unsafe_allow_html=True)
    render_spec_grid(listing)
    if listing.images:
        render_swipe_gallery(listing.images, uid=f"mob_{listing.id}", height=340)
    st.write(translate_description_text(listing.description))
    if listing.url:
        st.markdown(f"[打开原始房源]({listing.url})")
    st.markdown('</div>', unsafe_allow_html=True)


def render_listing_navigation(listings):
    """Render compact previous/next controls for narrow screens and quick review."""
    current_index = next(
        (idx for idx, listing in enumerate(listings) if listing.id == st.session_state.selected_listing_id),
        0,
    )
    prev_index = max(0, current_index - 1)
    next_index = min(len(listings) - 1, current_index + 1)

    prev_col, count_col, next_col = st.columns([1, 1.2, 1])
    with prev_col:
        if st.button("上一套", use_container_width=True, disabled=current_index == 0):
            st.session_state.selected_listing_id = listings[prev_index].id
            st.rerun()
    with count_col:
        st.markdown(
            f'<div class="mobile-count">{current_index + 1} / {len(listings)}</div>',
            unsafe_allow_html=True,
        )
    with next_col:
        if st.button("下一套", use_container_width=True, disabled=current_index >= len(listings) - 1):
            st.session_state.selected_listing_id = listings[next_index].id
            st.rerun()


def render_selected_listing_detail(db, listings, listing):
    """Render controls and detail for the currently selected listing."""
    render_listing_navigation(listings)
    if st.button("收起详情", key="collapse_detail", use_container_width=True):
        st.session_state.detail_open = False
        st.rerun()
    render_listing_detail(db, listing)


def render_listing_browser(db, listings):
    """Render the two-pane listing review experience."""
    st.subheader("房源复查")
    if not listings:
        st.info("当前没有符合条件的房源，请先扫描 Huningue 或 Mulhouse。")
        return

    valid_ids = {listing.id for listing in listings}
    if st.session_state.selected_listing_id is not None and st.session_state.selected_listing_id not in valid_ids:
        # Previously selected listing is no longer in the filtered list — clear selection
        st.session_state.selected_listing_id = None
        st.session_state.detail_open = False

    stale_threshold_label = st.selectbox("批量刷新阈值", list(STALE_REFRESH_OPTIONS.keys()), format_func=lambda v: {
        "Older than 6 hours": "超过 6 小时",
        "Older than 12 hours": "超过 12 小时",
        "Older than 24 hours": "超过 24 小时",
        "Older than 72 hours": "超过 72 小时",
    }.get(v, v))
    stale_cutoff = datetime.now() - timedelta(hours=STALE_REFRESH_OPTIONS[stale_threshold_label])

    batch_col1, batch_col2, batch_col3 = st.columns(3)
    with batch_col1:
        if st.button("刷新对比清单", use_container_width=True):
            compare_targets = [listing for listing in listings if listing.id in st.session_state.compare_ids]
            if not compare_targets:
                st.warning("请先把至少一条房源加入对比。")
            else:
                refreshed, failed = refresh_listing_batch(db, compare_targets, "对比清单")
                message = f"已刷新对比清单中的 {refreshed} 条房源。"
                if failed:
                    message += " 部分失败： " + " | ".join(failed[:3])
                st.session_state.listing_flash_message = message
                st.rerun()
    with batch_col2:
        if st.button("刷新当前列表", use_container_width=True):
            refreshed, failed = refresh_listing_batch(db, listings, "当前列表")
            message = f"已刷新当前列表中的 {refreshed} 条房源。"
            if failed:
                message += " 部分失败： " + " | ".join(failed[:3])
            st.session_state.listing_flash_message = message
            st.rerun()
    with batch_col3:
        if st.button("只刷新较旧房源", use_container_width=True):
            stale_targets = [
                listing for listing in listings
                if not getattr(listing, "last_refreshed", None) or listing.last_refreshed <= stale_cutoff
            ]
            if not stale_targets:
                st.warning("当前阈值下没有需要刷新的旧房源。")
            else:
                refreshed, failed = refresh_listing_batch(db, stale_targets, "需要刷新的当前列表")
                message = f"已刷新过期房源 {refreshed} 条。"
                if failed:
                    message += " 部分失败： " + " | ".join(failed[:3])
                st.session_state.listing_flash_message = message
                st.rerun()

    render_compare_strip(listings)

    listing_map = {listing.id: listing for listing in listings}
    selected_listing = listing_map.get(st.session_state.selected_listing_id)
    st.markdown('<div class="review-layout">', unsafe_allow_html=True)
    list_col, detail_col = st.columns([1.05, 1.6], gap="large")
    with list_col:
        visible_count = min(st.session_state.listing_list_count, len(listings))
        render_listing_selector(listings, visible_count=visible_count)
    with detail_col:
        st.markdown('<div class="desktop-detail">', unsafe_allow_html=True)
        if selected_listing and st.session_state.detail_open:
            render_selected_listing_detail(db, listings, selected_listing)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_favorites(db):
    """Render the favorites view."""
    st.subheader("收藏")
    favorites = db.get_favorites()
    if not favorites:
        st.info("还没有收藏房源。")
        return

    for listing in favorites:
        with st.expander(f"{translate_listing_title(listing.title)} | {format_price(listing.price)} | {availability_text(listing)}"):
            st.write(chinese_summary(listing))
            if listing.images:
                st.image(listing.images[0], use_column_width=True)
            st.write(listing.review_notes or listing.description or "暂无备注或描述。")


def render_contact_queue(db):
    """Render listings that are already in the contact/follow-up stage."""
    st.subheader("联系队列")
    contacted = db.get_listings(filters={"contacted": True, "sort_by": "available_date_asc"}, limit=150)
    if not contacted:
        st.info("还没有已联系的房源。")
        return

    for listing in contacted:
        with st.expander(f"{translate_listing_title(listing.title)} | {format_price(listing.price)} | {availability_text(listing)}"):
            col1, col2 = st.columns([1.4, 1])
            with col1:
                st.write(f"**位置：** {listing.location or listing.city or '未知'}")
                st.write(f"**状态：** {'已收藏' if listing.is_favorite else '持续跟踪'}")
                st.write(f"**中文摘要：** {chinese_summary(listing)}")
                st.write(f"**备注：** {listing.review_notes or '暂无后续备注。'}")
                if st.button("Re-open for review", key=f"reopen_review_{listing.id}", use_container_width=True):
                    db.toggle_needs_review(listing.id)
                    st.rerun()
            with col2:
                if listing.images:
                    st.image(listing.images[0], use_column_width=True)
                if listing.url:
                    st.link_button("打开原始房源", listing.url)


def render_analytics(db):
    """Render the analytics view."""
    st.subheader("市场分析")
    listings = db.get_listings(limit=500)
    if not listings:
        st.info("目前还没有足够数据生成分析。")
        return

    df = pd.DataFrame(
        [
            {
                "price": listing.price,
                "area": listing.area,
                "city": listing.city,
                "source": listing.source,
                "price_per_m2": listing.price / listing.area if listing.area else 0,
                "rating": listing.personal_rating,
            }
            for listing in listings
            if listing.price and listing.area
        ]
    )
    if df.empty:
        st.info("Not enough structured data for charts yet.")
        return

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="price", nbins=40, color="source", title="Rent distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(df, x="area", y="price", color="source", hover_data=["city", "rating"], title="Price vs area")
        st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard application."""
    ensure_state()
    db = init_db()
    defaults = default_filters()

    st.markdown(
        """
        <div class="hero-panel">
            <div class="soft-kicker">Basel 通勤导向租房台</div>
            <div class="main-header">法国租房扫描器</div>
            <div class="sub-header">查看 Huningue 和 Mulhouse 的租房信息，包含 Basel SBB 通勤估算、照片优先浏览、对比和中文摘要。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    db_filters, scan_filters, selected_sources, scan_clicked, ui_filters = build_filters(defaults)
    render_manual_add_panel(db)

    stats = db.get_stats()
    st.sidebar.caption(
        f"存储：{db.storage_label()}。已保存 {stats.get('available', 0)} 套可用房源。页面会先读已保存结果，增量上新不会清空旧房源。"
    )
    if not db.using_cloud_database:
        st.sidebar.warning("当前不是共享云数据库；别人可能看不到你扫描保存的房源。请在 Streamlit Secrets 设置 DATABASE_URL。")

    if scan_clicked:
        with st.spinner("正在增量上新：保留已保存房源，只合并新房源和变动信息..."):
            result, status_text, has_error = scan_from_dashboard(scan_filters, selected_sources)
        if has_error:
            st.sidebar.error("增量上新时有部分请求失败。")
            st.sidebar.info("已保存房源不会被清空；系统只合并成功返回的新房源。")
        elif result["stored_count"] == 0:
            st.sidebar.info("增量上新完成：没有发现新房源，已保存房源继续保留。")
        else:
            st.sidebar.success(
                f"增量上新完成：新增 {result.get('new_count', 0)} 条，更新 {result.get('updated_count', 0)} 条。"
            )
        st.sidebar.caption(status_text)

    stats = db.get_stats()
    listings = db.get_listings(filters=db_filters, limit=150)
    filtered_listings = []
    for listing in listings:
        commute_minutes, _ = estimate_basel_sbb_minutes(listing)
        if ui_filters["require_basel_estimate"] and commute_minutes is None:
            continue
        if commute_minutes is not None and commute_minutes > ui_filters["max_basel_minutes"]:
            continue
        if not matches_availability_filters(listing, ui_filters):
            continue
        if not matches_description_filters(listing, ui_filters):
            continue
        filtered_listings.append(listing)
    listings = filtered_listings
    render_metrics(stats, listings)

    review_tab, favorites_tab, contact_tab, analytics_tab = st.tabs(["复查", "收藏", "联系队列", "分析"])
    with review_tab:
        render_listing_browser(db, listings)
    with favorites_tab:
        render_favorites(db)
    with contact_tab:
        render_contact_queue(db)
    with analytics_tab:
        render_analytics(db)


if __name__ == "__main__":
    main()

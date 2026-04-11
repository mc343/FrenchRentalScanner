# 🏠 French Rental Scanner

> Automatically scan French rental websites (SeLoger, LeBonCoin) for apartment and house listings. Get summaries, filter by your criteria, and track favorites with a live dashboard.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ Why French Rental Scanner?

### 🎯 The Problem
- French rental websites are time-consuming to check manually
- Listings appear and disappear quickly
- Hard to track what you've seen and what's new
- Difficult to compare properties across different platforms
- No easy way to filter by your specific criteria

### 💡 The Solution
**French Rental Scanner** automatically:
- Scans **SeLoger** and **LeBonCoin** (France's top rental sites)
- Extracts all property details (price, location, features, images)
- Stores everything in a searchable database
- Provides a **live dashboard** for filtering and favorites
- Tracks which properties you've contacted or scheduled viewings
- Updates weekly with new listings

---

## 🚀 Key Features

### 🔍 **Web Scraping**
- Scans **SeLoger.fr** and **LeBonCoin.fr** automatically
- Extracts: price, location, area, features, images, contact info
- Handles pagination and rate limiting
- Robust error handling and retry logic

### 📊 **Smart Dashboard**
- Filter by price, area, location, property type
- Mark favorites and track contacted properties
- View images and detailed descriptions
- Compare properties side-by-side
- Analytics: price distribution, price per m², market trends

### 🔄 **Auto-Scheduler**
- Weekly automatic scans (configurable)
- Only updates new or changed listings
- Removes listings that are no longer available

### 💾 **Database Storage**
- SQLite database (no setup required)
- Track favorites, viewing notes, contact history
- Search and filter across all listings
- Export to CSV/Excel

---

## 📸 Dashboard Preview

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 French Rental Scanner                                    │
├─────────────────────────────────────────────────────────────┤
│  Filters:                                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Location: [Paris           ]                          │  │
│  │ Price:    [500€ ━━━━━━━━━━ 2500€]                    │  │
│  │ Area:     [20m² ━━━━━━━━━━ 100m²]                    │  │
│  │ Type:     [Apartment ▼]                              │  │
│  │          [🔎 Scan for New Listings]                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  📊 Statistics:  Total: 150 | Available: 142 | ⭐ 5       │
│                                                              │
│  📋 Listings:                                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 2BR Apartment - Paris 11ème                           │  │
│  │ 📍 Paris 11ème | 📐 45m² | 🏠 Apartment              │  │
│  │ 💰 1,200€ / month                                    │  │
│  │ Features: Elevator, Balcony, Furnished                │  │
│  │ [⭐] [📞 Contact] [View Original]                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎬 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mc343/FrenchRentalScanner.git
cd FrenchRentalScanner
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run your first scan**
```bash
python main.py scan --location Paris --min-price 500 --max-price 2000
```

4. **Launch the dashboard**
```bash
python main.py dashboard
```

The dashboard will open at `http://localhost:8501`

---

## 💻 Usage

### Command Line Interface

```bash
# Scan for listings
python main.py scan --location "Paris" --min-price 500 --max-price 2000

# View database statistics
python main.py stats

# Launch dashboard
python main.py dashboard
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--location` | City or department | Paris |
| `--min-price` | Minimum rent (€) | 500 |
| `--max-price` | Maximum rent (€) | 2500 |
| `--min-area` | Minimum area (m²) | 20 |
| `--max-area` | Maximum area (m²) | 100 |
| `--type` | Property type | all |

### Dashboard Features

**📋 Listings Tab**
- View all available listings
- Filter by your criteria
- Mark favorites with one click
- Track contacted properties
- Link to original listings

**⭐ Favorites Tab**
- Quick access to saved properties
- Compare your favorites
- Add viewing notes

**📊 Analytics Tab**
- Price distribution charts
- Price vs area scatter plots
- Average price by source
- Market trends

---

## 📁 Project Structure

```
FrenchRentalScanner/
├── scraper/              # Web scraping modules
│   ├── base.py          # Base scraper class
│   ├── seloger.py       # SeLoger scraper
│   └── leboncoin.py     # LeBonCoin scraper
├── database/            # Database models & connection
│   ├── models.py        # SQLAlchemy models
│   └── connection.py    # Database manager
├── dashboard/           # Streamlit dashboard
│   └── app.py           # Dashboard application
├── scheduler/           # Auto-scan scheduler
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🗄️ Database Schema

### Listings Table
- Listing details (price, area, location, features)
- Images and contact information
- Status tracking (favorite, contacted, viewing scheduled)
- Timestamps (first seen, last seen, publication date)

### Search History
- Saved search filters
- Results count
- Last run timestamp

### Viewing Notes
- Notes for property viewings
- Ratings (1-5 stars)
- Scheduled visit dates

---

## ⚙️ Configuration

### Supported Websites
- ✅ **SeLoger.fr** - One of France's largest rental sites
- ✅ **LeBonCoin.fr** - Most popular classifieds in France

### Adding More Scrapers

To add a new rental website:

1. Create a new scraper in `scraper/` directory
2. Inherit from `BaseScraper` class
3. Implement `search()` and `parse_listing()` methods
4. Register in `scraper/__init__.py`

Example:
```python
from scraper.base import BaseScraper

class MyScraper(BaseScraper):
    def search(self, filters):
        # Your scraping logic
        pass

    def parse_listing(self, url):
        # Your parsing logic
        pass
```

---

## 📊 Roadmap

**Planned Features:**
- [ ] More rental websites (Logic-Immo, PAP, ImmoJeans)
- [ ] Email alerts for new listings
- [ ] Mobile app (React Native)
- [ ] Price history tracking
- [ ] Map view of listings
- [ ] Export to Excel/CSV
- [ ] Advanced analytics (price trends, hot areas)
- [ ] Multiple city comparison
- [ ] Integration with Google Maps

---

## 🤝 Contributing

Contributions are welcome! Areas where you can help:

- **Scrapers** - Add support for more rental websites
- **Dashboard** - Improve UI/UX
- **Features** - Suggest new features
- **Bug fixes** - Report and fix issues
- **Documentation** - Improve docs

---

## ⚠️ Legal & Ethical Notes

- This tool is for **personal use only**
- Respect website terms of service
- Don't overload servers (rate limiting built-in)
- Data is for personal research, not commercial use
- Always verify information on original websites

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Python](https://www.python.org/) - Programming language
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [FastAPI](https://fastapi.tiangolo.com/) - Backend API

---

## 📞 Support

- 📧 **Issues:** [GitHub Issues](https://github.com/mc343/FrenchRentalScanner/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/mc343/FrenchRentalScanner/discussions)
- 📖 **Wiki:** [Documentation Wiki](https://github.com/mc343/FrenchRentalScanner/wiki)

---

**Made with ❤️ by [mc343](https://github.com/mc343)**

*Find your perfect home in France without the endless searching!*

---

<a href="https://github.com/mc343/FrenchRentalScanner">
<img src="https://img.shields.io/badge/GitHub-French%20Rental%20Scanner-brightgreen?style=for-the-badge&logo=github" alt="GitHub">
</a>

# French Rental Scanner - Testing Guide

## Current Status: READY FOR TESTING

### What's Working:
- [x] Database (SQLite) - storing listings
- [x] Scrapers (SeLoger, LeBonCoin) - framework ready
- [x] Command-line interface
- [x] Sample data created
- [x] Core functionality tested

### What Needs Refinement:
- [ ] Web scraping (actual website access - may be blocked)
- [ ] Streamlit dashboard (requires installation)
- [ ] Error handling for production use
- [ ] Emoji encoding for Windows console

---

## Quick Start (What You Can Test NOW)

### 1. Check Database Status
```bash
cd "FrenchRentalScanner"
py -3 run_test.py
```

Expected output:
```
[OK] All imports successful
[OK] Database has 4 listings
[OK] SeLoger: https://www.seloger.com
[OK] LeBonCoin: https://www.leboncoin.fr
[SUCCESS] All core tests passed!
```

### 2. View Statistics
```bash
py -3 -c "from database.connection import DatabaseManager; db = DatabaseManager('rental_listings.db'); stats = db.get_stats(); print('Listings:', stats['total_listings']); print('Sources:', stats.get('sources', {}))"
```

### 3. Test Core Commands
```bash
# Run tests
py -3 main.py stats

# Try scan (may not get actual data due to anti-scraping)
py -3 main.py scan --location Paris
```

---

## What Works Now

### Database Features:
- Create listings
- Store in SQLite
- Filter by price, area, location
- Track favorites
- View statistics

### Scraper Framework:
- Base scraper class
- SeLoger scraper structure
- LeBonCoin scraper structure
- API integration ready
- Error handling in place

---

## Known Limitations

### Web Scraping:
The scrapers are structured correctly but may not retrieve actual data because:
1. Websites may block automated requests
2. JavaScript-rendered content (Selenium needed)
3. API keys may expire
4. Terms of service restrictions

### Dashboard:
Streamlit not installed yet. To install:
```bash
py -3 -m pip install streamlit
```

---

## Testing Checklist

### Phase 1: Core Functionality (READY)
- [x] Database operations
- [x] Scraper initialization
- [x] Import system
- [x] Sample data creation

### Phase 2: Real Scraping (NEEDS TESTING)
- [ ] Actual SeLoger.com scraping
- [ ] Actual LeBonCoin.fr scraping
- [ ] Handle CAPTCHA/blocks
- [ ] Rate limiting

### Phase 3: Dashboard (OPTIONAL)
- [ ] Install Streamlit
- [ ] Display listings
- [ ] Filter functionality
- [ ] Analytics

---

## Next Steps

### For You to Test:
1. **Run the test script:**
   ```bash
   py -3 run_test.py
   ```

2. **Check the database:**
   ```bash
   py -3 -c "from database.connection import DatabaseManager; db = DatabaseManager('rental_listings.db'); listings = db.get_listings(limit=10); print(f'Found {len(listings)} listings')"
   ```

3. **Try scanning (experimental):**
   ```bash
   py -3 main.py scan --location Paris
   ```

### For Refinement:
1. Fix web scraping (use Selenium for JS sites)
2. Add better error handling
3. Install Streamlit for dashboard
4. Test with actual websites

---

## File Structure
```
FrenchRentalScanner/
├── scraper/           # Scrapers (framework ready)
├── database/          # Database (WORKING)
├── dashboard/         # Streamlit app (needs install)
├── main.py            # CLI (ready)
├── run_test.py        # Test script (WORKING)
└── rental_listings.db # Database with sample data
```

---

## Summary

**WORKING:**
- Database operations
- Scraper framework
- CLI commands
- Sample data

**NEEDS WORK:**
- Actual web scraping (blocked by sites)
- Dashboard (needs Streamlit)
- Production error handling

**READY TO TEST:**
Run `py -3 run_test.py` to verify everything works!

# 🏠 French Rental Scanner - User Guide

**Complete guide for finding your perfect rental home in France**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Using the Dashboard](#using-the-dashboard)
4. [Understanding Availability Filters](#understanding-availability-filters)
5. [Common Use Cases](#common-use-cases)
6. [Tips & Tricks](#tips--tricks)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

**For Windows Users (Easiest Way):**

1. Download or clone the French Rental Scanner
2. Double-click `RUN_DASHBOARD.bat`
3. Dashboard opens automatically in your browser
4. Start searching for rentals!

**For Advanced Users:**

```bash
# Install dependencies
pip install -r requirements.txt

# Launch dashboard
python main.py dashboard
```

---

## 💻 Installation

### Method 1: One-Click Launcher (Recommended)

**Perfect for non-technical users!**

1. **Download** the French Rental Scanner files
2. **Double-click** `RUN_DASHBOARD.bat`
3. The launcher will:
   - ✅ Check if Python is installed
   - ✅ Install missing dependencies automatically
   - ✅ Launch the dashboard in your browser
   - ✅ Show helpful messages if something goes wrong

### Method 2: Desktop Shortcut

**For easy everyday access:**

1. **Double-click** `CREATE_SHORTCUT.bat`
2. A shortcut appears on your desktop
3. **Double-click** the shortcut anytime to launch the app

### Method 3: Manual Installation

**For users comfortable with command line:**

```bash
# 1. Install Python 3.8+ from python.org
# 2. Clone the repository
git clone https://github.com/mc343/FrenchRentalScanner.git
cd FrenchRentalScanner

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
python main.py dashboard
```

---

## 🎨 Using the Dashboard

### First Steps

1. **Dashboard opens** at `http://127.0.0.1:8501`
2. You'll see the main interface with filters on the left
3. **184 listings** are already loaded from the database

### Filter Options

#### **Location Filter (位置)**
- Search in specific cities: "Huningue", "Mulhouse"
- Leave empty to see all locations

#### **Price Range (价格范围)**
- Set minimum and maximum monthly rent (€)
- Example: 500€ - 1,500€ per month

#### **Area Range (面积范围)**
- Set minimum and maximum apartment size (m²)
- Example: 30m² - 80m²

#### **Property Type (房型)**
- **全部 (All)**: Show apartments and houses
- **公寓 (Apartment)**: Only apartments
- **房屋 (House)**: Only houses

#### **Availability Time (可入住时间)** 🆕
- **不限 (Any time)**: Show all listings regardless of availability
- **立即可入住 (Available now)**: Immediately available
- **7天内 (Within 7 days)**: Available within a week
- **14天内 (Within 14 days)**: Available within two weeks
- **30天内 (Within 30 days)**: Available within a month
- **60天内 (Within 60 days)**: Available within two months
- **3个月内 (Within 3 months)**: Available within 90 days 🆕
- **4个月内 (Within 4 months)**: Available within 120 days 🆕

### Other Filters

- **排序方式 (Sort)**: Newest, Lowest price, Highest price, Largest area, Earliest availability
- **只看收藏 (Favorites only)**: Show only saved listings
- **最低个人评分 (Minimum rating)**: Filter by your 1-5 star ratings
- **到 Basel SBB 最长分钟数 (Max commute time)**: Filter by commute duration

---

## 📅 Understanding Availability Filters

### Why Availability Matters

**Different rental situations need different timelines:**

| Situation | Recommended Filter |
|-----------|-------------------|
| **Need to move immediately** | "Available now" or "Within 7 days" |
| **Planning 1-2 months ahead** | "Within 30 days" or "Within 60 days" |
| **Planning for future move** | "Within 3 months" or "Within 4 months" |
| **Just browsing** | "Any time" |

### How It Works

**Smart Detection:**
- The scanner analyzes listing descriptions
- Extracts phrases like "available June 2024"
- Calculates days until availability
- Shows only matching listings

**Example Timeline:**
```
Today: April 15, 2024

Listing A: "Available immediately"      → Shows in "Available now"
Listing B: "Available from June 1"       → Shows in "Within 60 days"  
Listing C: "Available from July 15"      → Shows in "Within 3 months"
Listing D: "Available from August 2024"  → Shows in "Within 4 months"
```

### Using the New Filters

**Scenario 1: Student Housing (September Move)**
- Current date: April
- Need apartment for: September
- **Select:** "Within 4 months" (120 days)
- **Result:** See apartments available through August

**Scenario 2: Relocation (2-Month Notice)**
- Current date: April
- Need to move: June
- **Select:** "Within 60 days"
- **Result:** See apartments available in June

**Scenario 3: Urgent Move**
- Need to move immediately
- **Select:** "Available now" or "Within 7 days"
- **Result:** See only immediately available places

---

## 🎯 Common Use Cases

### Use Case 1: Budget Apartment in Huningue

**Goal:** Find affordable apartment under 1,000€

**Settings:**
- Location: "Huningue"
- Price range: 500€ - 1,000€
- Area: 25m² - 60m²
- Property type: "Apartment"
- Availability: "Within 2 months"

**Result:** All affordable apartments in Huningue available within 2 months

---

### Use Case 2: Family House in Mulhouse

**Goal:** Find larger house for family

**Settings:**
- Location: "Mulhouse"
- Price range: 1,200€ - 2,500€
- Area: 80m² - 150m²
- Property type: "House"
- Availability: "Within 3 months"

**Result:** Family-sized houses in Mulhouse available within 3 months

---

### Use Case 3: Quick Move (Under 1 Month)

**Goal:** Need to move urgently

**Settings:**
- Location: "Any"
- Price range: 800€ - 1,800€
- Availability: "Within 30 days"
- Sort: "Earliest availability"

**Result:** All apartments available within 30 days, sorted by availability

---

### Use Case 4: Planning Ahead (3-4 Months)

**Goal:** Plan move for September (currently April/May)

**Settings:**
- Location: "Huningue" or "Mulhouse"
- Your budget and area preferences
- Availability: "Within 4 months"

**Result:** See all options available through August, giving you time to choose

---

## 💡 Tips & Tricks

### Tip 1: Start Broad, Then Narrow

1. **Start:** Use "Any time" availability, wide price range
2. **Review:** See what's available overall
3. **Narrow:** Gradually tighten your filters
4. **Find:** Your perfect apartment

### Tip 2: Use Favorites Liberally

- **⭐ Star** interesting listings as you browse
- **Compare:** Your favorites side-by-side
- **Track:** Which ones you've contacted
- **Decide:** Make your final choice

### Tip 3: Check Commute Times

- Use the Basel SBB commute filter
- **Shorter commute** = better work-life balance
- **Saint-Louis:** 11 minutes
- **Huningue:** 16 minutes
- **Mulhouse:** 28 minutes

### Tip 4: Set Realistic Price Ranges

- **Include** some flexibility in your budget
- **Consider:** Additional costs (utilities, parking)
- **Market:** Huningue/Mulhouse average: 800-1,500€

### Tip 5: Act Fast on Good Listings

- **Good listings** disappear quickly
- **Contact** immediately when you find one you like
- **Schedule** viewings as soon as possible
- **Apply** early to avoid disappointment

---

## 🔧 Troubleshooting

### Problem: Dashboard Won't Open

**Solution 1:**
- Double-click `RUN_DASHBOARD.bat`
- Let it check and fix dependencies automatically

**Solution 2:**
- Make sure Python is installed: Download from python.org
- During installation, check "Add Python to PATH"

**Solution 3:**
```bash
# Manually install dependencies
pip install -r requirements.txt

# Then run dashboard
python main.py dashboard
```

---

### Problem: No Listings Appearing

**Solution 1:**
- Check your filters aren't too restrictive
- Try "Any time" for availability
- Widen price/area ranges

**Solution 2:**
- Click "扫描 Bien'ici" to scan for new listings
- This updates the database with current listings

**Solution 3:**
- Clear filters and start fresh
- Use the default settings

---

### Problem: Python Not Found

**Solution:**
1. Download Python from python.org
2. Run the installer
3. ✅ Check "Add Python to PATH"
4. Complete installation
5. Try `RUN_DASHBOARD.bat` again

---

### Problem: Dependencies Installation Failed

**Solution:**
```bash
# Update pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

---

### Problem: Browser Won't Open

**Solution:**
1. The dashboard runs at `http://127.0.0.1:8501`
2. Open this URL manually in your browser
3. Or try a different browser (Chrome, Firefox, Edge)

---

## 📞 Getting Help

### Common Questions

**Q: How often should I scan for new listings?**
A: **Weekly** is ideal. New listings appear daily, and good ones go fast.

**Q: Should I use "Within 3 months" or "Within 4 months"?**
A: Use **3 months** if you're flexible, **4 months** if you need more options and can wait longer.

**Q: Why do some listings not show availability dates?**
A: Not all listings mention when they're available. Use "Any time" to see these.

**Q: Can I save my favorite searches?**
A: Use the **⭐ favorites** feature to save interesting listings for later.

**Q: How accurate are the prices?**
A: Prices are from the original listings. **Always verify** on the original website.

---

## 🎓 Advanced Usage

### Command Line Interface

For users who prefer command line:

```bash
# Basic scan
python main.py scan --location "Huningue"

# With availability filter (NEW!)
python main.py scan --location "Mulhouse" --available-within 90

# View statistics
python main.py stats

# Launch dashboard
python main.py dashboard
```

### Understanding the Database

- **rental_listings.db**: SQLite database with all listings
- **Auto-updated**: Each scan adds new listings
- **Persistent**: Your favorites and notes are saved
- **Exportable:** Can export to CSV for analysis

---

## 🌟 Best Practices

### Do's ✅

- ✅ **Run weekly scans** to catch new listings
- ✅ **Use favorites** to track promising options
- ✅ **Contact quickly** when you find a good match
- ✅ **Verify details** on original websites
- ✅ **Plan ahead** using the new availability filters

### Don'ts ❌

- ❌ **Don't wait** - good listings disappear fast
- ❌ **Don't ignore** availability dates if you have a timeline
- ❌ **Don't forget** to check commute times
- ❌ **Don't skip** contacting multiple options
- ❌ **Don't assume** - always verify listing details

---

## 🎉 Conclusion

The French Rental Scanner with new availability filters makes it easier to:

1. **Plan ahead** with 3-4 month filtering
2. **Find immediate** options when needed
3. **Compare** availability across different timeframes
4. **Make informed** decisions about your rental search

**Remember:** The perfect rental is out there - use the right filters to find it! 🏠

---

**Made with ❤️ for anyone searching for a home in France**

*Last updated: April 2026*

# 🏠 French Rental Scanner - Quick Reference

**Get started in 5 minutes!**

---

## ⚡ Super Quick Start

**Windows Users:**
1. 📁 Download the French Scanner folder
2. 🖱️ Double-click `RUN_DASHBOARD.bat`
3. 🌐 Browser opens automatically
4. 🎉 Start searching!

---

## 🎛️ Dashboard Controls

### Filter Panel (Left Side)

| Control | What It Does | Example |
|---------|--------------|---------|
| **位置 (Location)** | Choose city | "Huningue", "Mulhouse" |
| **价格范围 (Price)** | Set min/max rent | 500€ - 1,500€ |
| **面积范围 (Area)** | Set min/max size | 30m² - 80m² |
| **房型 (Type)** | Apartment or House | "Apartment" |
| **可入住时间 (Availability)** | When it's available | "Within 3 months" 🆕 |
| **排序方式 (Sort)** | Order results | "Lowest price" |

---

## 📅 Availability Filters Explained

### Choose Your Timeline:

| If you need to move... | Use this filter |
|----------------------|-----------------|
| **Right now** | "Available now" |
| **Within 1-2 weeks** | "Within 7 days" or "Within 14 days" |
| **Within 1 month** | "Within 30 days" |
| **Within 2 months** | "Within 60 days" |
| **Within 3 months** | "Within 3 months" 🆕 |
| **Within 4 months** | "Within 4 months" 🆕 |
| **Just browsing** | "Any time" |

### Example:

**Today = April 15, 2024**

| Selection | Shows listings available through... |
|-----------|-------------------------------------|
| "Within 3 months" | ~July 15, 2024 |
| "Within 4 months" | ~August 15, 2024 |

---

## 🎯 Common Search Scenarios

### Scenario 1: Student - September Move

```
Location: Huningue
Price: 600€ - 1,200€
Area: 25m² - 60m²
Type: Apartment
Availability: Within 4 months ✅
```

### Scenario 2: Professional - Immediate Move

```
Location: Mulhouse
Price: 1,000€ - 2,000€
Area: 50m² - 100m²
Type: Apartment
Availability: Available now ✅
```

### Scenario 3: Family - 2-Month Notice

```
Location: Saint-Louis
Price: 1,200€ - 2,500€
Area: 80m²+
Type: House
Availability: Within 60 days ✅
```

---

## ⭐ Pro Tips

### Tip 1: Use the ⭐ Button
- **Star** interesting listings while browsing
- **Compare** your favorites later
- **Track** which ones you've contacted

### Tip 2: Check Commute Times
- **Basel SBB** filter shows travel time
- **Saint-Louis:** 11 min | **Huningue:** 16 min | **Mulhouse:** 28 min

### Tip 3: Scan Regularly
- **Weekly scans** catch new listings
- **Good apartments** disappear fast
- **Contact quickly** when you find a match

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Dashboard won't open | Double-click `RUN_DASHBOARD.bat` |
| Python not found | Install Python from python.org (check "Add to PATH") |
| No listings showing | Try "Any time" availability, widen price range |
| Browser won't open | Go to http://127.0.0.1:8501 manually |

---

## 📱 Quick Commands

```bash
# Scan with availability filter (NEW!)
python main.py scan --location "Huningue" --available-within 90

# Launch dashboard
python main.py dashboard

# View statistics  
python main.py stats
```

---

## 🎓 Availability Filter Guide

### 🆕 NEW: 3-Month & 4-Month Filters

**Perfect for:**
- ✅ Students planning for September
- ✅ Professionals with 2-3 month notice periods
- ✅ Anyone planning ahead
- ✅ Flexible timeline situations

**How to use:**
1. Look for "可入住时间" dropdown
2. Select "3个月内" or "4个月内"
3. See listings available in your timeframe
4. Plan your move with confidence!

---

## 📊 Filter Combinations That Work

### Budget Hunter
```
Price: 500€ - 1,000€
Area: Any
Availability: Any time
Sort: Lowest price
```

### Quick Move
```
Availability: Available now or Within 7 days
Location: Your preferred city
Price: Your budget range
Sort: Earliest availability
```

### Planner (Ahead of Time)
```
Availability: Within 3 months or Within 4 months
Location: Multiple cities
Price: Flexible range
Sort: Newest first
```

### Commute Optimized
```
Max Basel commute: 20 minutes
Availability: Within your timeline
Location: Saint-Louis, Huningue, etc.
```

---

## 💾 Remember

- **Favorites** (⭐) are saved permanently
- **Database** updates with each scan
- **Filters** don't delete listings, just hide them
- **Original websites** have the most current info

---

## 🎯 Next Steps

1. **Launch** the dashboard (double-click `RUN_DASHBOARD.bat`)
2. **Experiment** with different filters
3. **Save favorites** with the ⭐ button
4. **Contact quickly** when you find a match
5. **Verify details** on original websites

---

**🏠 Happy house hunting!**

*Need more help? Check USER_GUIDE.md for detailed instructions*

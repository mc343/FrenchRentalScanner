# French Rental Scanner - Quick Start Guide

## 🚀 Launch the Application

### Option 1: Double-click (Easiest)
```
Double-click: RUN.bat
```

### Option 2: Command Line
```bash
cd FrenchRentalScanner
py -3 interactive.py
```

---

## 📋 Main Menu Options

```
[1] View all listings      - See all properties in database
[2] Search listings        - Filter by price, area, location
[3] Add listing manually    - Add a property you found
[4] Manage favorites       - View and manage saved favorites
[5] View statistics        - See database stats
[6] Scan websites          - Try web scraping (experimental)
[7] Database operations    - Export/Import data
[0] Exit                   - Close application
```

---

## 💡 Quick Tasks

### **View a Listing:**
1. Press `1` (View all listings)
2. Enter listing number to see details
3. Use actions: [F]avorite, [C]ontact, [D]elete

### **Search for Properties:**
1. Press `2` (Search listings)
2. Enter filters (or press Enter to skip):
   - Location (e.g., "Paris")
   - Min price (e.g., "1000")
   - Max price (e.g., "2000")
   - Min area (e.g., "40")
   - Max area (e.g., "80")
3. View results

### **Add a Listing:**
1. Press `3` (Add listing manually)
2. Enter property details:
   - Title: "2BR Apartment in Marais"
   - Location: "Paris 4eme"
   - Price: "1500"
   - Area: "65"
   - Features: "Elevator, Balcony, Near Metro"

### **Manage Favorites:**
1. Press `4` (Manage favorites)
2. View all saved favorites
3. Press `V` to view details
4. Press `R` to remove from favorites

### **Export to CSV:**
1. Press `7` (Database operations)
2. Press `1` (Export to CSV)
3. Enter filename or press Enter for default
4. File saved with all listings

---

## 🎨 Color Legend

```
Blue  - Headers and menus
Green - Success messages / Favorites
Cyan  - Information / Contacted
Red   - Errors
Yellow - Warnings / Viewings
```

---

## 📊 Sample Database Contents

```
Total: 4 listings

1. Beautiful 2BR in Marais
   SeLoger | 1800 EUR | 65 m2 | Paris 4eme
   
2. Modern Studio - Canal Saint-Martin
   LeBonCoin | 950 EUR | 28 m2 | Paris 10eme
   
3. House with Garden - Belleville
   SeLoger | 3200 EUR | 120 m2 | Paris 20eme
```

---

## ⌨️ Keyboard Shortcuts

- `Enter` - Confirm / Continue
- `0` - Return to previous menu / Exit
- `Ctrl+C` - Emergency exit

---

## 💾 Data Persistence

- Database: `rental_listings.db`
- All changes saved automatically
- Export CSV for backup

---

## 🆘 Troubleshooting

### Application won't start:
```bash
py -3 interactive.py
```

### Database issues:
```bash
# Check database
py -3 run_test.py
```

### Reset everything:
```bash
# Delete database and start fresh
del rental_listings.db
py -3 run_test.py
```

---

**Ready to use! Double-click RUN.bat to start!** 🏠

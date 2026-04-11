# Build Your Executable

## 🚀 Quick Build

### Option 1: Automated Build (Recommended)

1. **Double-click: `build-exe.bat`**
2. Wait for build to complete (2-3 minutes)
3. Find your exe in: `dist\FrenchRentalScanner.exe`

### Option 2: Manual Build

```bash
cd FrenchRentalScanner
py -3 -m PyInstaller FrenchRentalScanner.spec
```

Your exe will be in: `dist\FrenchRentalScanner.exe`

---

## 📦 What You Get

**Single executable file:**
- Size: ~17 MB
- Location: `dist\FrenchRentalScanner.exe`
- No installation required
- Portable - copy anywhere

---

## 📋 Requirements

- Windows 10 or 11
- Python 3.8+ installed
- PyInstaller installed (build script handles this)

---

## 🎯 After Building

1. **Copy the exe anywhere** you want
2. **Double-click to run**
3. **Database created automatically** in same folder

---

## 🔧 Troubleshooting Build

### Build fails:
```bash
# Install PyInstaller manually
py -3 -m pip install pyinstaller

# Try building again
py -3 -m PyInstaller FrenchRentalScanner.spec
```

### Exe too large:
- This is normal - includes all dependencies
- Size is ~17 MB (reasonable for features)

### Exe won't run:
- Make sure you built on same Windows version
- Check Windows Defender isn't blocking it
- Run from a writable folder

---

## 📁 Files Created During Build

```
FrenchRentalScanner/
├── build/                          # Build files (can be deleted)
├── dist/
│   └── FrenchRentalScanner.exe    # YOUR APP!
└── FrenchRentalScanner.spec        # Build configuration
```

---

## 🎉 Ready to Use!

After building, you have a portable executable that:
- Works on any Windows 10/11 computer
- Requires no installation
- Creates `rental_listings.db` automatically
- All features included

---

## 💡 Tip

**For personal use:** Build once and copy to multiple locations
**For sharing:** Others can build from source using this guide

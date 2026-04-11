# Quick Guide - Remove "Unknown Publisher" Warning

## Method 1: Unblock the File (Easiest)

1. **Right-click** on `FrenchRentalScanner.exe`
2. Select **Properties**
3. At the bottom, check **"Unblock"**
4. Click **Apply** → **OK**
5. **Run the exe** - No more warning!

---

## Method 2: Windows Defender Exclusion (Best for Regular Use)

### Option A: Automatic Script
1. Right-click `add-exclusion.bat`
2. Select **"Run as administrator"**
3. Click **Yes** to the prompt
4. Done!

### Option B: Manual Steps
1. Open **Windows Security**
2. Click **Virus & threat protection**
3. Under "Virus & threat protection settings", click **Manage settings**
4. Scroll to **Exclusions**
5. Click **Add or remove exclusions**
6. Select **Add an exclusion** → **Folder**
7. Browse to the FrenchRentalScanner folder
8. Click **Add**

---

## Method 3: Run Anyway (One-Time)

1. Double-click `FrenchRentalScanner.exe`
2. Windows shows warning
3. Click **"More info"**
4. Click **"Run anyway"**
5. Next time: No warning!

---

## Which Method Should You Use?

| Method | Effort | Result |
|--------|--------|--------|
| **Unblock** | 30 seconds | Warning gone forever |
| **Exclusion** | 2 minutes | Warning gone forever |
| **Run Anyway** | 5 seconds | Warning shows once |

---

## Important Notes

### For Your Personal Use:
✅ Use **Method 1 (Unblock)** - Simplest, fastest

### For Family/Friends:
✅ Use **Method 2 (Exclusion)** - One-time setup

### For Public Distribution:
❌ **Need to purchase code signing certificate** ($100-500/year)

---

## Why This Warning Appears

This is a **Windows security feature**, not a problem with the app:

✅ **Your app is safe** - It's just not signed with an expensive certificate
✅ **This is normal** - Most personal/open-source apps show this
✅ **Easy to fix** - Use Method 1 or 2 above
✅ **No security issue** - The app is completely safe

---

## Purchase Code Signing Certificate (Optional)

If you want to eliminate the warning for everyone:

### Recommended Providers:
- **Sectigo** - $175/year
- **DigiCert** - $470/year
- **GlobalSign** - $250/year

### Process:
1. Purchase certificate (requires business verification)
2. Install certificate on your computer
3. Rebuild exe with signature
4. No warning for anyone!

---

## My Recommendation

**For personal use: Use Method 1 (Unblock)**

It takes 30 seconds and the warning is gone forever!

---

**Need help?** Check `CODE_SIGNING.md` for detailed information.

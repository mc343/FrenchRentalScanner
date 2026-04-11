# Code Signing Certificate Guide

## The "Unknown Publisher" Warning Explained

### Why This Happens

Windows shows "Unknown Publisher: Unknown" for your exe because:
1. **No digital signature** - The exe isn't signed with a certificate
2. **Windows SmartScreen** - Protects users from potentially harmful software
3. **Security feature** - This is by design in Windows 10/11

**This is NORMAL for personal/open-source projects without paid certificates.**

---

## Your Options

### Option 1: Purchase Code Signing Certificate (RECOMMENDED)

**Cost:** $100-500 USD per year
**Effect:** Eliminates warning completely

**Providers:**
- DigiCert (Standard Code Signing - $470/year)
- Sectigo (Code Signing Certificate - $175/year)
- GlobalSign (Code Signing - $250/year)
- SSL.com (Code Signing EV - $200/year)

**Requirements:**
- Business registration documents
- Identity verification
- Payment
- Usually takes 1-3 business days

**Process:**
1. Purchase certificate from provider
2. Install certificate on your build machine
3. Sign the exe during build
4. No more warning!

---

### Option 2: Self-Signed Certificate (FREE - But Still Shows Warning)

**Cost:** Free
**Effect:** Changes warning from "Unknown Publisher" to different warning

**Result:** Still shows security warning, just different appearance

---

### Option 3: Windows Defender Exclusion (FREE - Workaround)

**Cost:** Free
**Effect:** Warning appears once, then never again

**Best for:** Personal use, distributing to known people

---

### Option 4: Right-Click → Run Anyway (FREE - Manual)

**Cost:** Free
**Effect:** Warning appears every time, user clicks "Run anyway"

**Best for:** Testing your own exe

---

## Recommended Solution for Personal Use

### Windows Defender Exclusion Method

This is FREE and makes the warning appear only ONCE:

#### Step 1: Add to Windows Defender Exclusions

1. Open Windows Security
2. Go to **Virus & threat protection**
3. Scroll down to **Exclusions**
4. Click **Add or remove exclusions**
5. Select **Add an exclusion** → **Folder**
6. Browse to your FrenchRentalScanner folder
7. Click **Add**

#### Step 2: Run Once

1. Double-click FrenchRentalScanner.exe
2. Click **"More info"** on the warning
3. Click **"Run anyway"**
4. Windows will remember this choice

#### Result
- Next time you run it: **No warning!**
- Only you can run it (unless someone else adds their own exclusion)

---

## For Distribution to Others

### If you want to share this with others:

**Option A: Document the workaround**
- Include a README explaining how to add exclusion
- Tell them it's safe and explain the warning
- One-time setup for them

**Option B: Purchase certificate** (if you plan to distribute widely)
- Purchase from certificate authority
- Sign all future builds
- No warnings for anyone

**Option C: Use trusted installer**
- Wrap exe in an installer (NSIS, Inno Setup)
- Sign the installer instead
- More professional appearance

---

## Temporary Solutions

### For Testing NOW:

1. **Right-click method:**
   - Right-click FrenchRentalScanner.exe
   - Click "Properties"
   - Check "Unblock" at the bottom
   - Click "Apply" → "OK"
   - Run again

2. **SmartScreen bypass:**
   - Run once and click "Run anyway"
   - Windows remembers for a while

---

## What I Can Do Now

### Free Options I Can Implement:

1. ✅ **Add UNBLOCK instructions** - Right-click → Properties → Unblock
2. ✅ **Create exclusion guide** - Step-by-step Windows Defender setup
3. ✅ **Document the warning** - Explain why it's safe
4. ✅ **Create README** - Tell users how to trust it

### Paid Options (You Need to Do):

1. ❌ **Purchase certificate** - $100-500/year
2. ❌ **Set up signing** - Requires certificate purchase
3. ❌ **Sign builds** - After certificate obtained

---

## Comparison

| Option | Cost | Warning | Distribution |
|--------|------|---------|--------------|
| **Unsigned (current)** | Free | Shows every time | Personal only |
| **Self-signed** | Free | Shows (different) | Personal only |
| **Defender Exclusion** | Free | Shows once, then gone | Personal use |
| **Paid Certificate** | $100-500/year | No warning | Professional distribution |

---

## My Recommendation

### For Personal Use:
**Use Windows Defender Exclusion** (FREE)
- One-time setup
- Warning disappears after first run
- Safe and secure

### For Sharing with Friends/Family:
**Provide exclusion instructions**
- Include README with steps
- They do it once
- No more warnings

### For Public Distribution:
**Purchase code signing certificate**
- Professional appearance
- No warnings for anyone
- Worth it if distributing widely

---

## What Should I Do?

I can create:
1. ✅ **Exclusion guide** - Step-by-step with screenshots
2. ✅ **Unblock instructions** - Quick reference
3. ✅ **README** - Explaining the warning
4. ✅ **Build script** - Ready for when you get certificate

**What do you want me to do?**

A. Create exclusion guide (FREE - warning appears once)
B. Wait until you buy certificate (PAID - no warning ever)
C. Document the workaround (FREE - users do it themselves)
D. Something else?

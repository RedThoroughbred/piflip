# 🔧 PiFlip Hardware Strategy Guide

## 🎯 Your Current Situation

### **What's Working:**
✅ Mac + GQRX + RTL-SDR = Sees key fobs, sees flights
❌ Pi + rtl_433/dump1090 = Doesn't see same signals

### **The Question:**
Should RTL-SDR stay on Pi or move to Mac?

---

## 📊 **RTL-SDR Placement Comparison**

### **Option 1: RTL-SDR on Pi** (RECOMMENDED)

| Pro | Con |
|-----|-----|
| ✅ Integrated PiFlip device | ❌ Needs better antenna placement |
| ✅ 24/7 operation possible | ❌ USB hub may limit power |
| ✅ Auto-capture scripts | ❌ Requires troubleshooting setup |
| ✅ Web interface from phone | ❌ Pi 3B is slower than Mac |
| ✅ True portable when done | |
| ✅ Dedicated RF device | |

**Best for:** Building real Flipper-style portable device

---

### **Option 2: RTL-SDR on Mac**

| Pro | Con |
|-----|-----|
| ✅ Already works well | ❌ Mac is your main computer |
| ✅ More processing power | ❌ Not portable |
| ✅ Better GUI tools (GQRX) | ❌ Can't run 24/7 |
| ✅ Easy to troubleshoot | ❌ Defeats PiFlip concept |
|  | ❌ Mac tied to RF operations |

**Best for:** Development, testing, learning

---

### **Option 3: Two RTL-SDR Dongles** (BEST!)

| Device | Location | Purpose |
|--------|----------|---------|
| RTL-SDR #1 | **Pi** | Flight tracking (1090MHz) |
| RTL-SDR #2 | **Pi** | Everything else (433/315/868MHz) |

**Cost:** $35 for second dongle

**Benefits:**
- ✅ No more mode switching needed!
- ✅ Can track flights AND scan 433MHz simultaneously
- ✅ Dedicated antennas for each frequency
- ✅ Both always available

**This solves your biggest pain point!**

---

## 🔍 **Why Mac Works But Pi Doesn't**

### **1. Antenna Placement** (Most Likely!)

**Your Mac:**
- Probably on desk near window
- RTL-SDR antenna vertical and elevated
- Clear line of sight

**Your Pi:**
- Where is it located?
- Antenna position?
- Obstructions?

**Test:** Move Pi + RTL-SDR to **exact same spot** as Mac and try again.

---

### **2. USB Power Issue**

**Kensington Hub:**
- May not be **powered** hub
- RTL-SDR needs 500mA
- PN532 needs power
- CC1101 needs power
- Total: **Over 1A**

**Pi 3B USB ports:**
- Total 1.2A shared across all ports
- With hub + 3 devices = borderline

**Solution:**
```
Get POWERED USB hub with external power supply
Examples:
- Anker 7-Port USB 3.0 Hub ($30)
- Sabrent 4-Port USB 3.0 Hub ($15)
- AmazonBasics Powered Hub ($20)
```

---

### **3. Gain Settings**

**GQRX (on Mac):**
- You manually adjusted gain slider
- Probably set to 30-40dB
- Optimized for your location

**rtl_433 (on Pi):**
- Default gain = AUTO (not always optimal)
- May be too low for your setup

**Solution:**
```bash
# Add -g 40 to all rtl_433 commands
rtl_433 -f 433.92M -g 40 -F json

# For dump1090:
# Edit: /etc/default/dump1090-fa
# Change: RECEIVER_OPTIONS="--gain 40"
```

---

## 🎯 **My Recommendation: Fix the Pi Setup**

### **Step 1: Improve Antenna Placement**

**Move Pi to better location:**
- Near window (if possible)
- Elevated (not on floor)
- Away from metal objects
- Keep antenna vertical

**Or get antenna extension:**
```
USB Extension Cable (10-15 feet)
- Allows RTL-SDR to be at window
- Pi can stay at desk
- Cost: $5-10
```

---

### **Step 2: Get Powered USB Hub**

**Your current Kensington hub:**
- Is it powered? (has AC adapter plug?)
- If not, this is likely your problem

**Recommended hubs:**
```
For Portable PiFlip:
- Sabrent 4-Port Powered Hub ($15)
- Small, compact, external power

For Desktop Use:
- Anker 7-Port USB 3.0 Hub ($30)
- More ports for future expansion
```

---

### **Step 3: Add Gain to Commands**

Let me update your web interface to use higher gain:

---

## 🦊 **What Flipper Zero Does Differently**

### **Flipper Zero Specs:**

| Feature | Flipper Zero | Your PiFlip |
|---------|--------------|-------------|
| **Sub-GHz RX** | CC1101 | ✅ CC1101 |
| **Sub-GHz TX** | CC1101 | ✅ CC1101 |
| **125kHz RFID** | Built-in coil | ❌ (could add) |
| **NFC** | PN532-like | ✅ PN532 |
| **Infrared** | Built-in LED | ❌ (could add) |
| **iButton** | 1-Wire | ❌ (could add) |
| **GPIO** | 18 pins | ✅ 40 pins |
| **Screen** | 128x64 LCD | ⏳ Coming |
| **Battery** | 2000mAh | ⏳ Coming |
| **Antenna** | PCB antenna | External (better!) |

**Key difference:** Flipper uses **CC1101 for receive AND transmit**
- No RTL-SDR (narrowband only)
- Can't do wideband captures
- Can't track flights (no 1090MHz)
- Can't do 2.4GHz/WiFi/BLE

**Your PiFlip advantage:**
- RTL-SDR = Wideband receiver (24-1700MHz)
- Can capture full IQ data
- Flight tracking possible
- More powerful Linux software

---

## 📦 **Compact Hardware Options**

### **For True Portable PiFlip:**

#### **Option A: Minimal Build** ($200)
```
- Raspberry Pi Zero 2 W ($15)
  • Much smaller than Pi 3B
  • Still powerful enough
  • Built-in WiFi

- RTL-SDR Blog V4 ($35)
  • Keep current one

- CC1101 Module ($3)
  • Keep current one

- PN532 Module ($10)
  • Keep current one

- Waveshare 3.5" LCD ($25)
  • Touch screen
  • Direct GPIO connection

- Small USB Hub ($15)
  • Powered, 4-port

- 10,000mAh Battery Bank ($25)
  • Powers everything
  • 6+ hours runtime

- 3D Printed Case ($10 materials)
  • Flipper-sized
  • Belt clip
```

**Total size:** Slightly larger than Flipper Zero
**Runtime:** 6-8 hours
**Screen:** Yes (3.5" touch)

---

#### **Option B: Desktop Build** ($150)
```
- Keep Pi 3B (you have it)
- Powered USB Hub ($20)
- Better antennas ($30)
- Second RTL-SDR ($35)
- 3D printed case ($10)
- Future: Add screen later ($25)
```

**Advantages:**
- More powerful
- Dual RTL-SDR setup
- No battery needed
- Room for expansion

---

#### **Option C: Hybrid** ($120)
```
- Keep Pi 3B for development
- Buy Pi Zero 2 W for portable ($15)
- Share all modules between them
- SD card images for each
```

**Switch between:**
- Desktop mode (Pi 3B, all features, monitor)
- Portable mode (Pi Zero 2W, compact, battery)

---

## 🔌 **USB Hub Recommendations**

### **For Portable:**
**Sabrent 4-Port Powered USB 2.0 Hub (HB-ACP3)**
- $15
- Compact size (2.5" x 2.5")
- External power adapter included
- Perfect for Pi projects

### **For Desktop:**
**Anker 7-Port USB 3.0 Hub**
- $30
- 36W power adapter
- Fast charging ports
- Room for future expansion
- USB 3.0 (faster)

### **Budget Option:**
**AmazonBasics 4-Port USB 2.0 Hub**
- $12
- External power optional
- Basic but works

---

## ✈️ **Fixing Flight Tracking**

### **Why Mac sees flights but Pi doesn't:**

**1. dump1090 Configuration**

Check current gain setting:
```bash
cat /etc/default/dump1090-fa | grep gain
```

**Should be:**
```
RECEIVER_OPTIONS="--gain 42 --max-range 300"
```

**Edit:**
```bash
sudo nano /etc/default/dump1090-fa

# Change to:
RECEIVER_OPTIONS="--gain 42 --max-range 300 --aggressive"

# Save and restart:
sudo systemctl restart dump1090-fa
```

**2. Antenna**

1090MHz needs **DIFFERENT antenna** than 433MHz!

**Your RTL-SDR came with:**
- Telescoping antenna (optimized for FM ~100MHz)
- NOT ideal for 1090MHz

**Better options:**
```
For ADS-B (flights):
- FlightAware ADS-B Antenna ($20)
- DIY 1090MHz dipole (free!)

For 433MHz (key fobs):
- Stock antenna works OK
- Or make 433MHz dipole
```

**DIY 1090MHz Antenna:**
```
Wire length: 69mm (1/4 wavelength)
Cost: $0 (coat hanger wire)
Performance: Better than stock!
```

**3. Location**

ADS-B needs **line of sight to sky:**
- Window placement best
- Higher is better
- Indoor: 5-40 mile range
- Outdoor elevated: 100-200 miles

---

## 🔑 **Capturing Your Key Fob (Pi)**

### **Test Right Now:**

**1. Check mode:**
```bash
# Should be "scanning mode"
curl http://127.0.0.1:5000/api/rtlsdr/mode
```

**2. Run optimized capture:**
```bash
# I created this script for you:
~/piflip/capture_keyfob.sh

# Or manually:
timeout 20 rtl_433 -f 433.92M -g 40 -s 250000 -Y auto -F json
```

**3. Press key fob DURING scan:**
- Lock button
- Unlock button
- Press 3-4 times
- Hold each for 1 second

**4. If still nothing:**

**Check frequency:**
- Most US key fobs: 315MHz
- Most EU key fobs: 433.92MHz
- Some US: 433.92MHz

**Try 315MHz:**
```bash
timeout 20 rtl_433 -f 315M -g 40 -F json
```

---

## 🎯 **Recommended Action Plan**

### **Immediate (Today):**

1. ✅ **Test antenna placement**
   - Move Pi to window
   - Or move RTL-SDR to window with USB cable

2. ✅ **Add gain to commands**
   - Test with: `~/piflip/capture_keyfob.sh`
   - Try both 315MHz and 433MHz

3. ✅ **Check USB power**
   - Is hub powered?
   - Try RTL-SDR direct to Pi (bypass hub test)

### **This Week:**

4. **Get powered USB hub** ($15-20)
   - Sabrent 4-port recommended
   - Solves power issues

5. **Update dump1090 gain**
   - Edit /etc/default/dump1090-fa
   - Set gain to 42
   - Test flight tracking

### **Next Month:**

6. **Consider second RTL-SDR** ($35)
   - Eliminates mode switching
   - One for flights, one for 433MHz
   - Best long-term solution

7. **Order display** ($25)
   - Waveshare 3.5" touch screen
   - Makes it truly portable

8. **Design case**
   - Measure components
   - 3D model in Fusion 360
   - Print prototype

---

## 🆚 **Final Verdict: Pi vs Mac**

### **Keep RTL-SDR on Pi Because:**

✅ You're building a **portable Flipper alternative**
✅ PiFlip needs RTL-SDR for key features
✅ Mac is your development machine
✅ Issues are **solvable** (antenna, power, gain)
✅ Second RTL-SDR is cheap ($35)

### **Use Mac For:**

✅ Development and testing
✅ URH GUI analysis (better than Pi)
✅ GQRX for signal discovery
✅ Backup when Pi has issues

---

## 📋 **Shopping List (Priority Order)**

### **Essential:**
1. **Powered USB Hub** - $15 (fixes power issues)
2. **USB Extension Cable** - $7 (better antenna placement)

### **Highly Recommended:**
3. **Second RTL-SDR** - $35 (no more mode switching!)
4. **Better antenna** - $20 or DIY (better reception)

### **Nice to Have:**
5. **Pi Zero 2 W** - $15 (portable version)
6. **3.5" Touch Screen** - $25 (local UI)
7. **Battery Bank** - $25 (portable power)

### **Total to Complete PiFlip:**
- **Minimum**: $22 (hub + cable)
- **Recommended**: $77 (hub + cable + RTL-SDR + antenna)
- **Full Build**: $137 (all items)

---

## 🚀 **Try This NOW:**

```bash
# Test with high gain and proper settings
cd ~/piflip
./capture_keyfob.sh

# Press your key fob 4-5 times during the 20 second scan
# Try BOTH lock and unlock buttons
```

**If this works:**
→ Problem was gain/settings (easy fix!)

**If this doesn't work:**
→ Problem is antenna placement or power (need hub/cable)

---

Let me know what the keyfob test shows and I'll help debug further! 🔧

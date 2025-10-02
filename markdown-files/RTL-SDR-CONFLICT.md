# RTL-SDR Hardware Conflict - SOLVED ✓

## The Problem

**Your RTL-SDR dongle can only be used by ONE program at a time.**

Currently:
- ✅ **dump1090-fa is using the RTL-SDR** for flight tracking
- ❌ **rtl_433 cannot use it** for 433MHz/TPMS/Weather scanning

This is why you saw:
- No data from 433MHz scanning
- No data from TPMS scanning
- No data from Weather scanning
- Error: `usb_claim_interface error -6`

## The Solutions

### Option 1: Use the Web Interface Toggle (EASIEST) ✅

**I've added a "Switch Mode" button to your web interface!**

Location: Top of the page, right under the hardware status

**How it works:**
1. Click "🔄 Switch Mode" button
2. Switches between:
   - **✈️ Flight Tracking Mode** - dump1090 running, no 433MHz scanning
   - **📡 433MHz Scanning Mode** - dump1090 stopped, can scan 433MHz/TPMS/Weather

**Usage:**
- Want to track flights? → Switch to "Flight Tracking" mode
- Want to scan 433MHz devices? → Switch to "Scanning" mode

The page will automatically reload and show which mode you're in.

---

### Option 2: Manual Command Line

**Stop flights, enable scanning:**
```bash
sudo systemctl stop dump1090-fa
# Now you can use rtl_433
rtl_433 -f 433.92M -F json
```

**Stop scanning, enable flights:**
```bash
sudo systemctl start dump1090-fa
# Now flights work, but rtl_433 won't
```

---

### Option 3: Buy a Second RTL-SDR Dongle (BEST LONG-TERM)

**Recommended:** Get another RTL-SDR (~$30-40)

**With 2 dongles you can:**
- Dongle #1 → Dedicated to dump1090-fa (flight tracking 24/7)
- Dongle #2 → Use for rtl_433 (433MHz, TPMS, weather whenever you want)

**Setup with 2 dongles:**
```bash
# List your RTL-SDR devices
rtl_test

# Will show something like:
# Found 2 device(s):
#   0: Realtek, RTL2838UHIDIR, SN: 00000001
#   1: Realtek, RTL2838UHIDIR, SN: 00000002

# Configure dump1090 to use specific dongle
# Edit /etc/default/dump1090-fa
sudo nano /etc/default/dump1090-fa

# Set RECEIVER_SERIAL to the serial number of dongle you want for flights:
RECEIVER_SERIAL=00000001

# Then use the other dongle for rtl_433
rtl_433 -d 1 -f 433.92M -F json
```

---

## Current Status

✅ **sudoers configured** - You can now switch modes without entering password
✅ **Web interface updated** - Toggle button added
✅ **Error detection added** - APIs now tell you when RTL-SDR is busy
✅ **Auto-reload** - Interface refreshes when you switch modes

## Why No Planes Yet?

Your flight tracking **IS working**, but you may not see planes because:

1. **Location** - Check https://globe.adsbexchange.com/ to see if planes fly over your area
2. **Antenna placement** - Indoor antennas typically get 5-40 mile range
3. **Time of day** - More flights during daytime hours
4. **Antenna type** - Stock antenna isn't optimized for 1090MHz

**To improve flight reception:**
- Move antenna near window or outdoors
- Position antenna vertically
- Consider upgrading to a 1090MHz-optimized antenna
- Add an LNA (Low Noise Amplifier) between antenna and RTL-SDR

## Testing Your Setup

### Test 433MHz Scanning (After Switching to Scanning Mode)

```bash
# Make sure dump1090 is stopped
sudo systemctl stop dump1090-fa

# Try 433MHz scan
rtl_433 -f 433.92M -F json -T 10

# Should see devices if any are nearby (car key fobs, doorbells, sensors, etc.)
```

### Test Flight Tracking (After Switching to Flight Mode)

```bash
# Make sure dump1090 is running
sudo systemctl start dump1090-fa

# Check for aircraft data
curl http://localhost:8080/data/aircraft.json

# Open map in browser
http://<your-pi-ip>:8080
```

## Web Interface Features Now Working

✅ **NFC Operations** - Always works (separate hardware)
✅ **Flight Tracking** - Works in Flight Mode
✅ **433MHz Scanning** - Works in Scanning Mode
✅ **TPMS** - Works in Scanning Mode
✅ **Weather Stations** - Works in Scanning Mode
✅ **Mode Toggle** - Switch between modes with one click

## Recommended Workflow

**Most users should:**
1. Keep dump1090-fa running 24/7 for flight tracking
2. When you need to scan 433MHz/TPMS/Weather:
   - Click "Switch Mode" → Scanning Mode
   - Do your scans
   - Click "Switch Mode" → Flight Tracking Mode

**Or just buy a second RTL-SDR** and use both simultaneously!

## Summary

The "no data" issue was **NOT a bug** - it's a hardware limitation. Your RTL-SDR can only do one job at a time.

**Solution implemented:** Toggle button in web interface to switch between modes!

**Better solution:** Buy a second RTL-SDR dongle for ~$30-40 and run both features simultaneously.

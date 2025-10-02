# 🧪 PiFlip Web Interface - Complete Test Guide

## 📱 **How to Access**

**New UI (Flipper-style):**
```
http://192.168.86.141:5000
```

**Old UI (if needed):**
```
http://192.168.86.141:5000/old
```

---

## ✅ **Complete Feature Test Checklist**

### **Before You Start:**
1. Open web interface in browser
2. Check status bar shows: 🟢 NFC | 🟢 RTL | 🟢 CC1101
3. Note current mode: **📡 Scanning Mode** or **✈️ Flight Mode**

---

## 🧪 **TEST 1: NFC Tools** ✅ Should Work Always

### **Test 1A: Scan Card**

**Steps:**
1. Tap: **NFC Tools** → **Scan Card**
2. Place NFC card on PN532 reader
3. Wait 1-2 seconds

**Expected Result:**
```
✅ Card Found!

UID: 97:43:70:06
Length: 4 bytes
```

**If it works:** ✅ NFC is functional!
**If it fails:** ❌ Check PN532 connection

---

### **Test 1B: Backup Card**

**Steps:**
1. Tap: **NFC Tools** → **Backup Card**
2. Place card on reader
3. Wait for confirmation

**Expected Result:**
```json
{
  "status": "success",
  "uid": "97437006",
  "file": "~/piflip/backups/backup_TIMESTAMP.json"
}
```

**Check file was created:**
```bash
ls ~/piflip/backups/
```

**If it works:** ✅ Backup functional!

---

## 🧪 **TEST 2: RF Tools** ⚠️ Requires Scanning Mode

### **Check Mode First:**
- Look at toggle switch at top
- Should say: **📡 Scanning Mode**
- If says **✈️ Flight Mode**, click toggle to switch

---

### **Test 2A: Scan 433MHz** (30 seconds)

**Steps:**
1. **Switch to Scanning Mode** (if needed)
2. Tap: **RF Tools** → **Scan 433MHz**
3. **IMMEDIATELY press a device:**
   - Car key fob (lock/unlock button)
   - Garage door opener
   - Doorbell
   - TV remote
4. Press it **4-5 times** during the 30 seconds
5. Wait for results

**Expected Results:**

**If device is detected:**
```json
{
  "devices": [
    {
      "model": "Generic-Remote",
      "id": 12345,
      "data": "abc123",
      ...
    }
  ],
  "count": 1
}
```

**If no device detected but scan works:**
```
Scan complete (30 seconds)
No devices found.
```
*(This is OK - means no device transmitted or too weak)*

**If RTL-SDR is busy:**
```
❌ RTL-SDR is in use
Switch to Scanning Mode first
```
*(Click mode toggle at top)*

**Troubleshooting:**
- Device must transmit DURING scan
- Try 315MHz devices too (TPMS frequency)
- Move RTL-SDR closer to device
- Check antenna is connected

---

### **Test 2B: Capture Signal** (5 seconds)

**This is the key test for your keyfob!**

**Steps:**
1. Tap: **RF Tools** → **Capture Signal**
2. Enter details:
   - **Name:** `my_keyfob_test`
   - **Frequency:** `433.92` (or `315` for US keyfobs)
   - **Duration:** `5`
3. Click **Start** (or equivalent)
4. **IMMEDIATELY press your key fob 3-4 times**
5. Hold each press for 1 second
6. Wait for capture to complete

**Expected Result:**
```json
{
  "status": "success",
  "message": "Captured 5 seconds at 433.92 MHz",
  "metadata": {
    "name": "my_keyfob_test",
    "frequency": 433920000,
    "file_size": 20480000,
    "auto_analyzed": true
  }
}
```

**Verify capture:**
```bash
ls ~/piflip/captures/my_keyfob_test.*
# Should show: my_keyfob_test.cu8 and my_keyfob_test.json
```

**If it works:** ✅ Capture system functional!

---

### **Test 2C: TPMS Sensors** (45 seconds)

**Steps:**
1. Tap: **RF Tools** → **TPMS Sensors**
2. If you have a car nearby:
   - Roll car forward/backward to wake up sensors
3. Wait 45 seconds

**Expected Results:**

**If car is nearby and sensors activate:**
```json
{
  "sensors": [
    {
      "model": "Toyota-TPMS",
      "id": "abc123",
      "pressure_kPa": 220,
      "temperature_C": 22
    }
  ]
}
```

**If no car nearby:**
```
Scan complete
No sensors found
```
*(This is normal if no car nearby)*

---

### **Test 2D: Weather Stations** (60 seconds)

**Steps:**
1. Tap: **RF Tools** → **Weather Stations**
2. Wait 60 seconds (weather stations transmit every 30-60s)

**Expected Results:**

**If weather station is nearby:**
```json
{
  "stations": [
    {
      "model": "Acurite-5in1",
      "temperature_F": 72,
      "humidity": 55
    }
  ]
}
```

**If no weather station in range:**
```
Scan complete
No stations found
```
*(Normal if no weather stations nearby)*

---

## 🧪 **TEST 3: Signal Library** ✅ Should Work Always

### **Test 3A: View Library**

**Steps:**
1. Tap: **Signal Library**
2. Should see list of all captures

**Expected Result:**
```
📻 my_keyfob_test
   433.92MHz • 5s • 19.5MB
   2025-10-01

📻 testNumber1
   433.92MHz • 5s • 19.5MB
   2025-09-30
```

**If empty:**
- You haven't captured anything yet
- Capture a signal first (Test 2B)

---

### **Test 3B: Analyze Signal**

**Steps:**
1. In Signal Library, tap a capture
2. Choose: **2. Analyze**

**Expected Result:**
```json
{
  "capture_name": "my_keyfob_test",
  "status": "analyzed",
  "frequency": 433920000,
  "file_size": 20480000,
  "note": "URH installed - GUI analysis available"
}
```

---

### **Test 3C: Replay Signal** ⚠️ Transmits RF!

**⚠️ WARNING:** This transmits actual RF signal!

**Steps:**
1. In Signal Library, tap a capture
2. Choose: **1. Replay**
3. Confirm warning dialog

**Expected Result:**
```json
{
  "status": "success",
  "message": "Replayed for 0.5 seconds",
  "frequency": 433920000
}
```

**What happens:**
- CC1101 transmits test burst
- Currently sends carrier wave
- Full replay needs manual URH analysis first

**If error:**
```json
{
  "error": "CC1101 not initialized"
}
```
*(Check CC1101 wiring)*

---

### **Test 3D: Delete Signal**

**Steps:**
1. In Signal Library, tap a capture
2. Choose: **3. Delete**
3. Confirm deletion

**Expected Result:**
```json
{
  "status": "deleted",
  "files": ["test.cu8", "test.json"]
}
```

---

## 🧪 **TEST 4: Flight Tracking** ⚠️ Requires Flight Mode

### **Switch to Flight Mode:**
1. Tap mode toggle at top
2. Should change to: **✈️ Flight Mode**
3. Page reloads

---

### **Test 4A: Open Flight Map**

**Steps:**
1. Ensure in **Flight Mode**
2. Tap: **Flight Tracking** → **Open Map**

**Expected Result:**
- New browser tab opens
- URL: `http://192.168.86.141:8080`
- Map shows (may be empty if no planes)

**If map doesn't open:**
- Check dump1090 is running: `sudo systemctl status dump1090-fa`

---

### **Test 4B: View Statistics**

**Steps:**
1. Tap: **Flight Tracking** → **Live Statistics**

**Expected Result:**
```json
{
  "total_aircraft": 0,
  "with_position": 0,
  "messages": 1234
}
```

**If 0 aircraft:**
- Normal if no planes overhead
- Check https://globe.adsbexchange.com/ to see if planes are in your area
- May need better antenna placement

---

## 🧪 **TEST 5: Mode Switching** ✅ Should Work Always

### **Test 5A: Toggle Between Modes**

**Steps:**
1. Note current mode
2. Click toggle switch at top
3. Wait for page reload

**Expected Result:**
- Mode changes
- Page reloads automatically
- New mode shown

**Modes:**
- **📡 Scanning Mode** → Can do: 433MHz, TPMS, Weather, Capture
- **✈️ Flight Mode** → Can do: Track aircraft, View map

---

## 🧪 **TEST 6: Settings** ✅ Should Work Always

### **Test 6A: Hardware Status**

**Steps:**
1. Tap: **Settings** → **Hardware Status**

**Expected Result:**
```
🔧 Hardware Status:

NFC (PN532): ✅
RTL-SDR: ✅
CC1101: ⚠️
dump1090: 📡 Stopped
```

*(CC1101 may show ⚠️ but still work)*

---

## 📊 **Test Results Summary Table**

| Test | Feature | Expected Status | Notes |
|------|---------|-----------------|-------|
| 1A | NFC Scan | ✅ Works | Always available |
| 1B | NFC Backup | ✅ Works | Always available |
| 2A | 433MHz Scan | ⚠️ Needs device | Requires Scanning Mode |
| 2B | Signal Capture | ✅ Works | Requires Scanning Mode |
| 2C | TPMS | ⚠️ Needs car | Requires Scanning Mode |
| 2D | Weather | ⚠️ Needs station | Requires Scanning Mode |
| 3A | View Library | ✅ Works | Always available |
| 3B | Analyze | ✅ Works | Always available |
| 3C | Replay | ⚠️ Test burst | Always available |
| 3D | Delete | ✅ Works | Always available |
| 4A | Flight Map | ⚠️ Needs planes | Requires Flight Mode |
| 4B | Flight Stats | ✅ Works | Requires Flight Mode |
| 5A | Mode Toggle | ✅ Works | Always available |
| 6A | Hardware Status | ✅ Works | Always available |

**Legend:**
- ✅ = Should work immediately
- ⚠️ = Requires specific conditions
- ❌ = Not working/needs fix

---

## 🎯 **Quick Test Sequence (5 Minutes)**

### **Test everything quickly:**

```
1. Open browser: http://192.168.86.141:5000
2. Check status bar (hardware indicators)
3. Test NFC: Scan Card (place card on reader)
4. Check mode: Should be Scanning Mode
5. Test Capture: Capture 5s signal (press keyfob!)
6. View Library: Should show your capture
7. Toggle Mode: Switch to Flight Mode
8. Open Flight Map: New tab opens
9. Toggle back to Scanning Mode
10. Check Settings: Hardware Status
```

**Time:** 5 minutes
**Result:** Know exactly what works and what doesn't!

---

## 🐛 **Common Issues & Fixes**

### **Issue: "RTL-SDR is in use"**
**Fix:** Click mode toggle to switch to Scanning Mode

### **Issue: "No card found"**
**Fix:** Place card directly on PN532 (within 1cm)

### **Issue: "CC1101 not initialized"**
**Fix:** Check wiring, restart web interface

### **Issue: No flights showing**
**Fix:**
1. Check you're in Flight Mode
2. Wait for planes to fly over
3. Improve antenna placement
4. Check dump1090 is running

### **Issue: Capture works but no signal detected**
**Fix:**
1. Press device DURING capture (not before)
2. Hold button longer (1-2 seconds)
3. Try different frequency (315 vs 433)
4. Move RTL-SDR closer to device

---

## 📋 **Detailed Test Log Template**

**Copy this and fill it out as you test:**

```
═══════════════════════════════════════
PIFLIP WEB INTERFACE TEST LOG
Date: 2025-10-01
═══════════════════════════════════════

HARDWARE STATUS:
[ ] NFC (PN532): Working / Not Working
[ ] RTL-SDR: Detected / Not Detected
[ ] CC1101: Working / Not Working

NFC TESTS:
[ ] Scan Card: Pass / Fail
    UID detected: __________
[ ] Backup Card: Pass / Fail
    File created: Yes / No

RF TOOLS (Scanning Mode):
[ ] 433MHz Scan: Pass / Fail / No device
    Devices found: ___
[ ] Signal Capture: Pass / Fail
    File size: _____ MB
[ ] TPMS: Pass / Fail / No car
[ ] Weather: Pass / Fail / No station

SIGNAL LIBRARY:
[ ] View Library: Pass / Fail
    Captures shown: ___
[ ] Analyze Signal: Pass / Fail
[ ] Replay Signal: Pass / Fail
[ ] Delete Signal: Pass / Fail

FLIGHT TRACKING (Flight Mode):
[ ] Open Map: Pass / Fail
[ ] View Statistics: Pass / Fail
    Aircraft count: ___

MODE SWITCHING:
[ ] Toggle to Flight Mode: Pass / Fail
[ ] Toggle to Scanning Mode: Pass / Fail

SETTINGS:
[ ] Hardware Status: Pass / Fail

OVERALL RESULT:
[ ] All core features work
[ ] Some features need fixing
[ ] Major issues found

NOTES:
_________________________________
_________________________________
```

---

## 🚀 **Start Testing Now!**

**Recommended order:**

1. **Hardware Status** (baseline check)
2. **NFC Scan** (easiest test)
3. **Signal Capture** (most important for keyfob)
4. **Signal Library** (verify capture worked)
5. **Everything else** (as time permits)

**Open the web interface and start with Test 1A (NFC Scan)!**

Let me know what works and what doesn't, and I'll help fix any issues. 🔧

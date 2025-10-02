# 🚀 PiFlip Quick Start - Test Your Key Fob NOW

## ✅ You Just Ran All Tests - Now What?

### **Most Important Test: Capture Your Key Fob!**

---

## 🔑 **Method 1: Web Interface** (Recommended)

### **Steps:**

1. **Refresh your browser** (to see new Scanning Mode)

2. **Go back to main interface:**
   ```
   http://192.168.86.141:5000
   ```

3. **Verify you're in Scanning Mode:**
   - Look at toggle at top
   - Should say: **📡 Scanning Mode**
   - If not, click the toggle

4. **Capture your key fob:**
   - Tap: **RF Tools → Capture Signal**
   - Enter:
     * **Name:** `my_car_key`
     * **Frequency:** `433.92` (try 315 if this doesn't work)
     * **Duration:** `5` seconds
   - Click start/capture
   - **IMMEDIATELY press your key fob lock button 4-5 times!**
   - Hold each press for 1-2 seconds
   - Wait for capture to finish

5. **Check if it worked:**
   - Go to: **Signal Library**
   - Should see: `my_car_key` in the list
   - File size should be ~20 MB
   - Tap it to see details

**Expected Result:**
```
✅ Captured 5 seconds at 433.92 MHz
File: my_car_key.cu8 (19.5 MB)
Status: Ready for analysis
```

---

## 🔑 **Method 2: Command Line** (Faster!)

```bash
cd ~/piflip
./test_keyfob_now.sh
```

**Then:**
- Press your key fob when prompted
- Try BOTH tests (315MHz and 433.92MHz)
- Look for JSON output

**If you see JSON data:**
✅ Your key fob was detected!

**If you see nothing:**
❌ Need to troubleshoot (see below)

---

## 🔑 **Method 3: Test Suite** (Visual Feedback)

1. Go back to test suite:
   ```
   http://192.168.86.141:5000/test
   ```

2. Click: **Test 5: Signal Capture**

3. **IMMEDIATELY press your key fob when it says "PRESS DEVICE NOW!"**

4. Check if test turns **GREEN** (pass) or **RED** (fail)

---

## 📊 **What Your Test Results Mean:**

### **If Hardware Tests Passed:**
✅ Test 1 (Hardware Status): PN532 is working
✅ Test 2 (NFC Scan): NFC reader is functional
✅ Test 3 (Mode Check): Mode switching works
✅ Test 6 (List Captures): Signal library works

**This means your PiFlip core is working!**

### **If Hardware Tests Failed:**
❌ Check which specific test failed
❌ Look at the output log for error messages

---

## 🎯 **Next Steps Based on Results:**

### **Scenario A: Key Fob Capture Works!** ✅

**What to do:**
1. Go to **Signal Library**
2. Tap your capture
3. Choose: **2. Analyze**
   - See URH analysis results
4. Choose: **1. Replay**
   - ⚠️ WARNING: This transmits!
   - Confirm warning
   - CC1101 will transmit test burst

**Then:**
- Try more captures (garage door, doorbell, etc.)
- Build your signal library
- Experiment with replay

---

### **Scenario B: Key Fob Capture Doesn't Detect Signal** ⚠️

**File is created but no signal detected in analysis**

**Troubleshooting:**

1. **Try Different Frequency:**
   - US key fobs often use **315 MHz**
   - EU key fobs often use **433.92 MHz**
   - Capture again with different frequency

2. **Press Device DURING Capture:**
   - Don't press before
   - Press multiple times (4-5 times)
   - Hold each press 1-2 seconds
   - Keep pressing the whole 5 seconds

3. **Get Closer:**
   - Hold key fob within 10 feet of RTL-SDR
   - Point antenna at device

4. **Check Antenna:**
   - Is antenna screwed in tight?
   - Is it vertical?
   - Move to window if possible

5. **Verify Mode:**
   ```bash
   curl http://127.0.0.1:5000/api/rtlsdr/mode
   ```
   - Should say: `"mode": "scanning"`
   - If not, toggle mode

---

### **Scenario C: Capture Fails Completely** ❌

**Error: "RTL-SDR is in use"**

**Fix:**
```bash
# Switch to scanning mode
curl -X POST http://127.0.0.1:5000/api/rtlsdr/toggle

# Verify
curl http://127.0.0.1:5000/api/rtlsdr/mode
```

**Error: "Timeout" or "USB error"**

**Fix:**
- Check RTL-SDR is plugged in
- Try different USB port
- Check powered USB hub

---

## 🧪 **Other Features to Test:**

### **After Key Fob Capture Works:**

**1. Test NFC Card:**
- NFC Tools → Scan Card
- Place any NFC card on PN532
- Should show UID instantly

**2. Test 433MHz Scan:**
- RF Tools → Scan 433MHz
- Press any 433MHz device during 30s scan
- See if it's detected

**3. Test Flight Tracking:**
- Click mode toggle (switch to Flight Mode)
- Flight Tracking → Open Map
- See if any planes are overhead

**4. Test Weather Stations:**
- Switch back to Scanning Mode
- RF Tools → Weather Stations
- Wait 60 seconds
- May detect neighbor's weather station

---

## 📋 **Report Card - What Should Work:**

| Feature | Should Work? | Test It |
|---------|--------------|---------|
| **Hardware Status** | ✅ Always | Test 1 |
| **NFC Scan** | ✅ Always | Test 2 |
| **Mode Check** | ✅ Always | Test 3 |
| **Signal Library** | ✅ Always | Test 6 |
| **433MHz Scan** | ⚠️ Needs device | Test 4 |
| **Signal Capture** | ✅ Should work | Test 5 |
| **Analyze** | ✅ Should work | Test 7 |
| **Replay** | ⚠️ Test burst only | Test 8 |
| **Mode Toggle** | ✅ Should work | Test 9 |

---

## 🎯 **Your Action Plan:**

### **Right Now:**
1. ✅ Switch to Scanning Mode (DONE)
2. ⏳ **Capture your key fob** (DO THIS NOW!)
3. ⏳ Check Signal Library for capture
4. ⏳ Try replaying the signal

### **If Capture Works:**
🎉 **Success!** Your PiFlip is fully functional!
- Build your signal library
- Test other devices
- Read `SIGNAL_WORKFLOW_EXPLAINED.md` for advanced features

### **If Capture Doesn't Work:**
🔧 **Troubleshoot:**
- Try 315 MHz frequency
- Move RTL-SDR to window
- Get powered USB hub ($15)
- Check `HARDWARE_STRATEGY.md` for solutions

---

## 📞 **Report Back:**

**Tell me:**
1. Did key fob capture work?
2. What frequency worked? (315 or 433.92 MHz)
3. File size of capture? (should be ~20MB)
4. Did you see signal when analyzed?

**Then I'll help you:**
- Replay the signal
- Decode it properly with URH
- Capture more devices
- Build advanced features

---

## 🚀 **Go Capture Your Key Fob Now!**

Use any of the 3 methods above. The easiest is the command line:

```bash
cd ~/piflip
./test_keyfob_now.sh
```

**Press your key fob when it starts scanning!**

Then tell me what happened! 🔑

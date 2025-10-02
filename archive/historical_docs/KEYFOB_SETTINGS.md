# 🔑 Key Fob - Verified Settings from Mac

## ✅ **CONFIRMED WORKING SETTINGS (From GQRX on Mac)**

**Date:** October 1, 2025
**Device:** Key Fob
**Tool:** GQRX on MacBook Air M1

---

## 📊 **Exact Settings:**

```
Display Frequency:     433.920 MHz
Filter Width:          214.700 kHz
Hardware Frequency:    433.705300 MHz  ← This is what RTL-SDR is actually tuned to!
Gain:                  -6.0 dB (AGC likely enabled, or relative gain)
Signal:                ✅ Very obvious, strong signal
```

---

## 🎯 **Key Insight:**

**Hardware Frequency is Different from Display!**

- **Display:** 433.920 MHz (what you see)
- **Hardware:** 433.705300 MHz (actual RTL-SDR tuning)
- **Difference:** 214.7 kHz (the filter offset)

This is normal in GQRX - it uses an IF offset for better reception.

---

## 🔧 **How to Apply to Pi:**

### **Option 1: Use Hardware Frequency (Recommended)**

```bash
# Use the ACTUAL hardware frequency GQRX used
rtl_sdr -f 433705300 -s 2048000 -g 40 -n 10240000 keyfob_pi.cu8

# Press key fob during capture!
```

**Why 433.705300 MHz?**
- This is what the RTL-SDR was ACTUALLY tuned to
- GQRX shows 433.920 but that's after filter offset
- Raw capture needs hardware frequency

---

### **Option 2: Use Display Frequency**

```bash
# Use the display frequency
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 10240000 keyfob_pi_2.cu8

# Press key fob during capture!
```

**Try both and see which gives better results!**

---

### **Option 3: rtl_433 with Exact Frequency**

```bash
# Use rtl_433 with hardware frequency
timeout 20 rtl_433 -f 433.705M -g 40 -s 250000 -F json

# Or display frequency
timeout 20 rtl_433 -f 433.92M -g 40 -s 250000 -F json

# Press key fob when it starts!
```

---

## 🧪 **Test Plan:**

### **Test 1: Capture with Hardware Frequency**

```bash
cd ~/piflip/captures

# Capture using GQRX's hardware frequency
rtl_sdr -f 433705300 -s 2048000 -g 40 -n 10240000 keyfob_hw_freq.cu8

# Press key fob NOW (multiple times)!
```

**Expected result:** File size ~20 MB

---

### **Test 2: Capture with Display Frequency**

```bash
# Capture using display frequency
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 10240000 keyfob_display_freq.cu8

# Press key fob NOW (multiple times)!
```

**Expected result:** File size ~20 MB

---

### **Test 3: Compare Results**

```bash
# Check file sizes
ls -lh keyfob_*.cu8

# Both should be ~20MB
# But signal strength might differ
```

**To check which is better:**
- Transfer both to Mac
- Open both in URH
- See which has stronger/clearer signal

---

## 📊 **Understanding GQRX Display:**

**What you saw in GQRX:**

```
┌─────────────────────────────────────┐
│ Frequency: 433.920 MHz              │  ← Display (after offset)
│ Filter BW: 214.700 kHz              │  ← How wide the filter is
│ Hardware:  433.705300 MHz           │  ← ACTUAL RTL tuning
└─────────────────────────────────────┘
```

**Why the offset?**
- GQRX uses IF (Intermediate Frequency) offset
- Avoids DC spike in center of spectrum
- Better image rejection
- Common SDR technique

**For raw capture:**
- Use hardware frequency for exact match
- OR use display frequency (might work too)
- Test both!

---

## 🎯 **Gain Settings:**

**GQRX showed:** -6.0 dB

**What this means:**
- Could be AGC (Automatic Gain Control) enabled
- Could be relative to max gain (49.6 - 6 = 43.6 dB actual)
- GQRX gain display varies

**For Pi, try these gains:**
- 40 dB (good starting point)
- 43.6 dB (if -6 means relative)
- 49.6 dB (max gain)

**Test command with different gains:**
```bash
# Try gain 40
rtl_sdr -f 433705300 -s 2048000 -g 40 -n 10240000 test_g40.cu8

# Try gain 44
rtl_sdr -f 433705300 -s 2048000 -g 44 -n 10240000 test_g44.cu8

# Try max gain
rtl_sdr -f 433705300 -s 2048000 -g 49.6 -n 10240000 test_g49.cu8
```

---

## 🚀 **Quick Test Script:**

Let me create a script to test all combinations:

```bash
#!/bin/bash
# Test key fob with Mac's settings

echo "Testing key fob capture with Mac-verified settings"
echo "=================================================="
echo ""

cd ~/piflip/captures

# Test 1: Hardware frequency, gain 40
echo "Test 1: Hardware freq (433.705 MHz), Gain 40dB"
echo "Press key fob in 3 seconds..."
sleep 3
rtl_sdr -f 433705300 -s 2048000 -g 40 -n 10240000 keyfob_test1.cu8
echo "✅ Captured: keyfob_test1.cu8"
echo ""

# Test 2: Display frequency, gain 40
echo "Test 2: Display freq (433.920 MHz), Gain 40dB"
echo "Press key fob in 3 seconds..."
sleep 3
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 10240000 keyfob_test2.cu8
echo "✅ Captured: keyfob_test2.cu8"
echo ""

# Show results
echo "=================================================="
echo "Results:"
ls -lh keyfob_test*.cu8
echo ""
echo "Both files should be ~20MB"
echo "Transfer to Mac and open in URH to compare signal strength"
```

---

## 📱 **Using Web Interface:**

You can also capture via web interface with exact settings:

```
http://192.168.86.141:5000

RF Tools → Capture Signal

Name: keyfob_hardware_freq
Frequency: 433.705 (enter as 433.705 MHz, not 433.920!)
Duration: 5
```

**OR:**

```
Name: keyfob_display_freq
Frequency: 433.920
Duration: 5
```

**Test both!**

---

## 🎯 **Most Likely to Work:**

**My prediction:** Hardware frequency (433.705300 MHz) will give better results on Pi because that's what GQRX actually tuned to.

**But also test:** Display frequency (433.920 MHz) because rtl_433 might handle the offset automatically.

---

## 📊 **Next Steps:**

1. **Run test captures on Pi** (use script above or manual commands)

2. **Transfer to Mac for comparison:**
   ```bash
   # On Mac
   scp seth@192.168.86.141:~/piflip/captures/keyfob_test*.cu8 ~/Desktop/
   ```

3. **Open in URH on Mac:**
   ```bash
   urh ~/Desktop/keyfob_test1.cu8
   urh ~/Desktop/keyfob_test2.cu8
   ```

4. **Compare:**
   - Which has stronger signal?
   - Which shows clearer bit pattern?
   - Use that frequency going forward!

---

## 💡 **Expected Outcome:**

**If Pi capture looks similar to Mac:**
✅ Pi is working perfectly!
✅ Just needed exact settings!
✅ Can now capture/replay on Pi!

**If Pi capture is weaker:**
⚠️ Antenna placement issue (most likely)
⚠️ Try USB extension to match Mac position
⚠️ Or keep RTL-SDR on Mac for captures, use Pi for CC1101 replay

---

## 🎉 **You're Almost There!**

You now have:
- ✅ Exact working settings from Mac
- ✅ Two frequencies to test (hardware vs display)
- ✅ Gain settings to try
- ✅ Working Pi hardware

**Just need to capture on Pi with these exact settings and compare!**

**Ready to test?** 🔑

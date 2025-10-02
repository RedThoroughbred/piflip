# 🍎 Mac + Pi Dual Setup Workflow

## 🎯 Strategy: Use Mac for Development, Pi for Deployment

**Smart approach!** Use Mac's GQRX to verify signals, then apply same settings to Pi.

---

## 🔧 **Current Situation:**

**Mac (Works Great):**
- ✅ GQRX shows signals visually
- ✅ Can see key fob transmissions
- ✅ Can adjust gain/frequency in real-time
- ✅ Flight tracking works

**Pi (Weaker but Functional):**
- ✅ Hardware works (proven with FM radio test)
- ⚠️ Reception weaker than Mac
- ⚠️ No visual feedback (command-line only)
- ✅ Power fixed (3A supply)

**The Gap:** Mac has GUI tools + better antenna placement

---

## 🎨 **Recommended Dual Setup:**

### **Use Mac For:**
1. **Signal Discovery**
   - Use GQRX to find exact frequency
   - Adjust gain to see signal best
   - Verify device is transmitting
   - Record settings that work

2. **Signal Analysis**
   - URH GUI for protocol analysis
   - Visual waterfall display
   - Easy bit pattern extraction
   - Protocol reverse engineering

3. **Development**
   - Testing new capture methods
   - Verifying replay accuracy
   - Quick iterations

### **Use Pi For:**
1. **Portable Operations**
   - Captures when away from Mac
   - Autonomous monitoring
   - 24/7 flight tracking
   - NFC operations (Pi-only)

2. **Transmission**
   - CC1101 for replay (Pi-only)
   - Automated captures
   - Web interface access from phone

3. **Final Deployment**
   - After you've proven signals on Mac
   - Apply exact same settings to Pi

---

## 📊 **Workflow Example: Capture Key Fob**

### **Step 1: On Mac (Discovery)**

**A. Open GQRX:**
```
1. Plug RTL-SDR into Mac
2. Launch GQRX
3. Set frequency: 433.920 MHz
4. Set mode: AM (for OOK signals)
5. Adjust gain: Try 30-40 dB
```

**B. Find Your Key Fob:**
```
1. Press key fob
2. Watch waterfall display
3. Look for signal spike
4. Adjust frequency if needed
5. Note exact frequency where signal is strongest
```

**C. Record Settings:**
```
✅ Exact frequency: ___.___MHz
✅ Gain setting: ___dB
✅ Sample rate: ___.___MS/s
✅ Modulation: AM/FM/SSB
✅ Signal strength: ___dB
```

---

### **Step 2: On Mac (Capture & Analyze)**

**A. Capture with rtl_sdr:**
```bash
# Use settings from GQRX
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 10240000 keyfob.cu8
# Press key fob NOW!
```

**B. Analyze in URH:**
```bash
# Open URH GUI
urh keyfob.cu8

# In URH:
1. Auto-detect modulation
2. View bit pattern
3. Export protocol
4. Save for Pi replay
```

---

### **Step 3: Transfer to Pi (Apply Settings)**

**A. Transfer capture file:**
```bash
# On Mac:
scp keyfob.cu8 seth@192.168.86.141:~/piflip/captures/
scp keyfob.json seth@192.168.86.141:~/piflip/captures/
```

**B. Update Pi settings to match Mac:**
```bash
# On Pi, use EXACT settings from Mac
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 10240000 test.cu8
# Press key fob
```

**C. Compare results:**
```bash
# Check file sizes (should be similar)
ls -lh keyfob.cu8  # Mac
ls -lh test.cu8    # Pi

# Both should be ~20MB for 5 seconds
```

---

### **Step 4: Replay on Pi (CC1101)**

```bash
# Use URH-analyzed protocol
# Configure CC1101 with exact frequency
# Transmit decoded bits
```

---

## 🎯 **Why This Works:**

**Mac as "Reference":**
- Visual confirmation signals exist
- Easy to find exact frequency
- Quick parameter adjustments
- Immediate feedback

**Pi as "Production":**
- Once settings proven on Mac
- Apply exact same settings
- Should work identically
- Bonus: CC1101 for TX

---

## 📱 **Current Pi Settings vs Mac Settings:**

### **What We Need to Match:**

| Setting | Mac (GQRX) | Pi (rtl_433/rtl_sdr) | How to Fix |
|---------|------------|----------------------|------------|
| **Frequency** | Visual, adjust live | Command line | Use `-f` flag |
| **Gain** | Slider (0-50) | `-g` flag | Match Mac's gain |
| **Sample Rate** | Dropdown | `-s` flag | Match Mac's rate |
| **Filter BW** | Adjustable | Fixed | Use matching sample rate |

---

## 🔍 **Debugging Pi Reception:**

### **Test 1: Match Mac's Exact Settings**

**On Mac, note these from GQRX:**
```
Frequency: _________ Hz
Gain: _________ dB
Sample Rate: _________ S/s
LNA Gain: _________ (if shown)
```

**On Pi, use EXACT same values:**
```bash
rtl_sdr \
  -f [Mac's frequency] \
  -s [Mac's sample rate] \
  -g [Mac's gain] \
  -n 10240000 \
  test.cu8
```

---

### **Test 2: Pi Can Receive FM Radio (Proven!)**

We already proved Pi can receive:
```bash
rtl_fm -f 88.5M -M wbfm -s 200000 -r 48000 - 2>&1
# ✅ Got audio data!
```

**This means:**
- ✅ RTL-SDR hardware works on Pi
- ✅ Can receive signals
- ✅ Problem is likely gain/frequency settings for 433MHz

---

### **Test 3: Antenna Position**

**Mac:** Where exactly is the antenna when it works?
- Window?
- Desk position?
- Height?
- Orientation?

**Pi:** Put antenna in EXACT same position
- Use USB extension if needed
- Same height, same orientation
- Test again

---

## 💡 **The Real Difference: GQRX vs Command Line**

### **GQRX (Mac) Advantages:**

**Visual Waterfall:**
```
Frequency →
Time
↓
[Shows signal as bright line when device transmits]
```

**You can SEE:**
- Exact frequency of signal
- When device transmits
- Signal strength
- Interference

**Real-time adjustments:**
- Drag frequency
- Slide gain
- Immediate results

---

### **rtl_433 (Pi) Limitations:**

**No visual feedback:**
```
[Running...]
[No output if nothing detected]
```

**You can't see:**
- If signal is being received but not decoded
- Exact frequency offset
- Signal strength
- What's happening in real-time

**Solution:** Use rtl_sdr raw capture like Mac does!

---

## 🎯 **Recommended Setup Going Forward:**

### **Option 1: Dual RTL-SDR (Best!)**

**Buy second RTL-SDR:** $35

**Setup:**
```
Pi with 2x RTL-SDR:
  RTL-SDR #1 → 1090MHz (flights) - permanent
  RTL-SDR #2 → 433MHz (scanning) - permanent

No mode switching needed!
Both always available!
```

**Mac:**
- Use your RTL-SDR for development
- GQRX for discovery
- URH for analysis
- Transfer results to Pi

---

### **Option 2: Share One RTL-SDR**

**Current approach:**

**Mac workflow:**
1. Plug RTL-SDR into Mac
2. Use GQRX to find signals
3. Use URH to analyze
4. Record exact settings
5. Transfer capture to Pi

**Pi workflow:**
6. Unplug from Mac
7. Plug into Pi
8. Use exact Mac settings
9. Capture/replay on Pi
10. Use CC1101 for TX

**Downside:** Lots of swapping cables

---

### **Option 3: Keep RTL-SDR on Pi, Use Mac for Analysis Only**

**Pi:**
- Capture raw IQ files
- Transfer to Mac for analysis

**Mac:**
- Open captures in URH
- Analyze and decode
- Send protocol back to Pi for replay

**Workflow:**
```bash
# On Pi: Capture
rtl_sdr -f 433920000 -s 2048000 -g 40 -n 10240000 capture.cu8

# Transfer to Mac
scp seth@192.168.86.141:~/piflip/captures/capture.cu8 ~/Desktop/

# On Mac: Analyze in URH
urh ~/Desktop/capture.cu8

# Extract protocol, send back to Pi
```

---

## 🔧 **Immediate Action Plan:**

### **Tonight: Use Mac to Find Your Key Fob's Exact Settings**

1. **Plug RTL-SDR into Mac**

2. **Open GQRX**

3. **Configure:**
   - Frequency: 433.920 MHz
   - Gain: 35 dB (start here)
   - Mode: AM

4. **Press key fob, watch waterfall**

5. **Adjust frequency if needed** (might be 433.85 or 434.0)

6. **Note exact frequency where signal is strongest**

7. **Record these settings:**
   ```
   Frequency: _____________
   Gain: _____________
   Sample Rate: _____________
   ```

8. **Capture with rtl_sdr:**
   ```bash
   rtl_sdr -f [frequency] -s 2048000 -g [gain] -n 10240000 keyfob_mac.cu8
   ```

9. **Verify capture in URH:**
   ```bash
   urh keyfob_mac.cu8
   # Should see signal!
   ```

---

### **Tomorrow: Apply to Pi**

1. **Plug RTL-SDR back into Pi**

2. **Use EXACT settings from Mac:**
   ```bash
   rtl_sdr -f [Mac frequency] -s 2048000 -g [Mac gain] -n 10240000 keyfob_pi.cu8
   ```

3. **Compare file sizes:**
   ```bash
   # Should both be ~20MB
   ls -lh keyfob_mac.cu8
   ls -lh keyfob_pi.cu8
   ```

4. **If Pi file is much smaller:**
   - Pi didn't receive signal
   - Antenna placement issue
   - Try moving Pi antenna to Mac's position

---

## 📊 **Expected Results:**

### **Mac:**
- ✅ Clear signal in GQRX waterfall
- ✅ Strong capture in URH
- ✅ Easy to decode protocol
- ✅ Can verify transmission works

### **Pi (After Settings Match):**
- ✅ Should capture similar data
- ✅ Same file size as Mac
- ✅ Same signal strength
- ✅ Ready for replay

### **If Pi Still Weaker:**
- Antenna position different
- USB power (but we fixed this!)
- Need USB extension to match Mac position

---

## 🎉 **Benefits of This Approach:**

**Development on Mac:**
- ✅ Fast iteration
- ✅ Visual feedback
- ✅ Easy debugging
- ✅ Comfortable environment

**Deployment on Pi:**
- ✅ Portable
- ✅ Web interface
- ✅ CC1101 transmission
- ✅ 24/7 operation
- ✅ NFC integration

**Best of both worlds!** 🍎 + 🥧

---

## 💰 **Cost for Second RTL-SDR:**

**If you decide to get second one:**
- RTL-SDR Blog V4: $35
- Pi has both permanently
- No more swapping!
- Flight + 433MHz simultaneously

**Total setup:**
- Mac: 1x RTL-SDR (for development)
- Pi: 2x RTL-SDR (flights + scanning)

**Use case:**
- Mac for protocol reverse engineering
- Pi for production captures
- Both available anytime

---

## 🎯 **Next Steps:**

**Right now:**
1. Plug RTL-SDR into Mac
2. Open GQRX
3. Find your key fob's exact frequency
4. Record the settings that work
5. Capture one good signal

**Tell me:**
- What frequency did you find?
- What gain worked best?
- Did URH show the signal clearly?

**Then we'll:**
- Apply exact same settings to Pi
- Should work identically!
- Or we'll know it's antenna placement

---

**This is the smart way to do it!** Use Mac's visual tools to find the right settings, then copy them to Pi. 🎯

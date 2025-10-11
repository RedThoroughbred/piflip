# Advanced Features Guide 📊

## How to Test TX & Verify It's Working

---

## ✅ **WHAT WE JUST ADDED**

### **1. Signal Library Enhancements**
Your saved captures now have **6 buttons** per signal:

**Row 1:**
- ▶️ **REPLAY** - Basic replay
- 🔍 **ANALYZE** - URH analysis
- 📊 **VISUALIZE** - See waveform & decoded binary ← NEW!

**Row 2:**
- 🔄 **VARIATIONS** - Replay with freq/timing offsets ← NEW!
- 🎲 **FUZZ** - Random timing variations ← NEW!
- 🗑️ **DELETE** - Remove capture

### **2. Visual Signal Analysis**
Click **VISUALIZE** on any signal to see:
- ASCII waveform visualization
- Decoded binary pattern
- Timing analysis (shortest/longest pulses)
- Hex representation
- Tips for SDR++ comparison

### **3. TX Indicator**
Yellow **"TX"** indicator appears in status bar when transmitting:
- Blinks while transmitting
- Disappears when done
- **Watch this + SDR++ waterfall to verify TX!**

---

## 🧪 **HOW TO VERIFY TX IS WORKING**

### **Setup: SDR++ on Mac + PiFlip**

**Step 1: Configure SDR++ (on your Mac)**
```
1. Open SDR++
2. Set frequency: 433.920 MHz
3. Set mode: RAW (or WFM for visualization)
4. Enable waterfall display
5. Adjust gain if needed
6. Look for baseline noise (should be relatively flat)
```

**Step 2: Capture a Signal on PiFlip**
```
1. PiFlip: RF Tools → Capture Signal
2. Frequency: 433.92 MHz
3. Duration: 10 seconds
4. Press a remote (garage, car, doorbell)
5. Save as: "test_signal"
```

**Step 3: Replay and Watch SDR++**
```
1. PiFlip: Signal Library → test_signal
2. Click: 🔄 VARIATIONS
3. Confirm transmission

WATCH FOR:
✅ Yellow "TX" indicator appears on PiFlip
✅ Waterfall shows activity on SDR++
✅ Bursts appear at ~433.92 MHz
✅ Should see 15 bursts (frequency variations)
```

---

## 📊 **WHAT TO LOOK FOR IN SDR++**

### **When TX is Working:**
```
Waterfall Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ████                    433.92 MHz
        ████                    (Your signal)
        ████
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  433.4   433.9   434.4
```

**You should see:**
1. **Vertical bursts** on waterfall at 433.92 MHz
2. **Multiple bursts** (15 for variations, 50 for fuzz)
3. **Slightly different frequencies** (433.42, 433.67, 433.92, 434.17, 434.42)
4. **Signal strength spike** on spectrum display

### **When TX is NOT Working:**
```
Waterfall Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                (Just noise)
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**No signal = Check:**
- CC1101 wiring (SPI connection)
- Frequency accuracy (is it really 433.92?)
- Antenna connected
- PiFlip actually transmitting (TX indicator?)

---

## 🔍 **VISUALIZATION FEATURES**

### **How to Use VISUALIZE Button:**

**Click 📊 VISUALIZE on any saved signal:**
```
╔══════════════════════════════════════════╗
║   📊 SIGNAL VISUALIZATION              ║
╚══════════════════════════════════════════╝

Signal: car_key_test
Frequency: 433.92 MHz
Sample Rate: 2.0 MS/s

═══ DECODED BINARY ═══
111100001111000011110000111100001111
Bits: 36
Hex: F0F0F0F0

═══ TIMING ANALYSIS ═══
Transitions: 72
Shortest: 450μs
Longest: 950μs

═══ WAVEFORM ═══
████████████                    ████████████
████████████                    ████████████
            ████████████████████
            ████████████████████

💡 TIP: Compare this with SDR++
to verify accuracy!
```

**What this tells you:**
- **Binary Pattern** - The actual data being sent
- **Hex Code** - Same data in hexadecimal
- **Timing** - How long each pulse is
- **Waveform** - Visual representation of HIGH/LOW states

---

## 🎯 **TESTING SCENARIOS**

### **Scenario 1: Verify Brute Force Actually Works**

**Test with simple wireless doorbell:**
```
1. SDR++: Set to 433.92 MHz, waterfall on

2. PiFlip: Advanced TX → Brute Force Codes
   - Frequency: 433.92
   - Bit length: 8 (256 codes)
   - Confirm

3. WATCH SDR++:
   ✅ Should see 256 bursts on waterfall
   ✅ One burst every ~100ms
   ✅ Takes ~25 seconds total
   ✅ Doorbell might ring (if code matches!)

4. WATCH PiFlip:
   ✅ Yellow TX indicator blinks entire time
   ✅ Status shows: "Transmitting X/256"
```

### **Scenario 2: Compare Captured vs Transmitted Signal**

**Capture, then replay, then compare:**
```
1. Capture signal:
   - RF Tools → Capture Signal
   - Press remote
   - Save as: "original"

2. Visualize original:
   - Library → original → 📊 VISUALIZE
   - Note the binary pattern
   - Note the waveform

3. Replay with variations:
   - Library → original → 🔄 VARIATIONS
   - Watch SDR++ waterfall

4. Capture the replay:
   - RF Tools → Capture Signal
   - (While replay is transmitting)
   - Save as: "replayed"

5. Compare:
   - Library → replayed → 📊 VISUALIZE
   - Binary should be similar/identical!
   - Waveform should match original
```

**If they match = TX is accurate! ✅**

### **Scenario 3: Signal Fuzzing Visual Verification**

**Test timing variations:**
```
1. SDR++: Set to 433.92 MHz

2. PiFlip: Library → test_signal → 🎲 FUZZ
   - Fuzz: 10%
   - Iterations: 50

3. WATCH SDR++:
   ✅ Should see 50 bursts
   ✅ Each slightly different duration
   ✅ All around 433.92 MHz
   ✅ Takes ~15 seconds (50 × 0.3s)

4. LOOK FOR:
   - Longer bursts (110% timing)
   - Shorter bursts (90% timing)
   - Some might look "wrong" (that's fuzzing!)
```

---

## 📈 **TROUBLESHOOTING TX ISSUES**

### **Problem: No Activity on SDR++**

**Check 1: Is PiFlip actually transmitting?**
```bash
# On PiFlip terminal:
python3 -c "
from cc1101_enhanced import CC1101Enhanced
cc = CC1101Enhanced()
cc.set_frequency(433.92)
cc.set_tx_power('max')
cc.enter_tx_mode()
import time; time.sleep(2)
cc.idle()
print('TX test complete')
"
```

**Check 2: Is CC1101 connected?**
```bash
# Check SPI connection:
ls -l /dev/spidev0.0
# Should exist

# Check if CC1101 responds:
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
# Read version register
result = spi.xfer2([0xF1, 0x00])
print(f'CC1101 version: {result[1]:02X}')
# Should be 0x14 or 0x04
"
```

**Check 3: SDR++ Settings**
```
✅ Correct frequency (433.920 MHz)?
✅ Gain high enough (30-40dB)?
✅ Sample rate appropriate (2-3 MS/s)?
✅ Waterfall actually enabled?
✅ SDR dongle working (other signals visible)?
```

### **Problem: TX Indicator Shows But No SDR++ Activity**

**Possible causes:**
1. **Frequency mismatch** - PiFlip at 433.92, SDR++ at 443.92?
2. **Low TX power** - CC1101 power too low
3. **Antenna issue** - No antenna or poor connection
4. **Shielding** - Pi in metal case blocking signal
5. **Distance** - SDR++ antenna too far away

**Test:**
```
1. Move SDR++ antenna CLOSE to PiFlip (10cm)
2. Use MAXIMUM tx power
3. Double-check frequency on both
4. Use external antenna on CC1101
```

### **Problem: Signal Looks Different**

**Original vs Replay don't match?**

**Possible reasons:**
1. **Timing drift** - PiFlip replay timing slightly off
2. **Frequency offset** - Not exactly 433.92 MHz
3. **Modulation difference** - ASK vs OOK interpretation
4. **Sample rate** - Different capture/replay rates

**Solution:**
```
Use VARIATIONS button - tries multiple frequencies/timings
One of the 15 variations should match better!
```

---

## 💡 **PRO TIPS**

### **Tip 1: Visual Confirmation is Key**
```
Always watch BOTH:
1. PiFlip TX indicator (yellow blink)
2. SDR++ waterfall (signal bursts)

If TX indicator shows but SDR++ doesn't = hardware issue
If both show = TX is working! ✅
```

### **Tip 2: Use Visualize Before Replay**
```
Before transmitting:
1. Click 📊 VISUALIZE
2. Check decoded binary makes sense
3. Check timing looks reasonable
4. Compare with known good signals

This catches bad captures before wasting TX attempts
```

### **Tip 3: Start Simple**
```
Test TX with known good signal:
1. Capture garage remote (known working)
2. Replay with variations
3. Watch SDR++ - should see activity
4. Compare visualizations

Once working, try advanced features!
```

### **Tip 4: Record SDR++ for Later Analysis**
```
In SDR++:
1. Enable recording
2. Run PiFlip TX test
3. Stop recording
4. Analyze recording for exact timing/frequency
5. Compare with PiFlip visualization

Proves TX accuracy scientifically!
```

---

## 🎓 **LEARNING EXERCISES**

### **Exercise 1: Capture-Compare-Verify**
```
Goal: Verify TX accuracy

1. Capture a remote signal
2. Visualize: Note binary pattern
3. Replay with variations
4. Capture the replay on SDR++
5. Analyze: Does binary match?

Success = Binary patterns identical!
```

### **Exercise 2: Frequency Accuracy Test**
```
Goal: Test frequency precision

1. SDR++: Set to 433.92 MHz exactly
2. PiFlip: Replay variations
3. Note: Which offset shows strongest?

If 0 MHz offset strongest = Frequency accurate!
If +0.25 MHz strongest = PiFlip transmits 0.25 MHz high
```

### **Exercise 3: Timing Precision Test**
```
Goal: Test timing accuracy

1. Capture signal with known timing
2. Visualize: Note shortest/longest pulses
3. Fuzz signal (10%)
4. Watch SDR++: How different do bursts look?

Learn: How much timing variation devices tolerate
```

### **Exercise 4: Power Level Test**
```
Goal: Understand TX power

1. Set SDR++ gain fixed (e.g., 30dB)
2. PiFlip: Replay at different power levels
3. Note: Signal strength on SDR++

Compare: Max power vs medium power
Distance test: How far does signal reach?
```

---

## 📚 **REFERENCE**

### **Frequency Bands:**
- **433.92 MHz** - Most garage doors, weather stations (US/EU)
- **315 MHz** - Some car keys, garage doors (US)
- **868 MHz** - European devices
- **915 MHz** - US ISM band

### **Modulation Types:**
- **OOK** (On-Off Keying) - Simple on/off
- **ASK** (Amplitude Shift Keying) - Amplitude changes
- **FSK** (Frequency Shift Keying) - Frequency changes

### **Timing Terminology:**
- **μs** (microsecond) - 1/1,000,000 second
- **ms** (millisecond) - 1/1,000 second
- **Transition** - Change from HIGH to LOW (or vice versa)
- **Pulse** - One HIGH or LOW period

### **Signal Strength:**
- **dBm** - Power measurement
- **RSSI** - Received Signal Strength Indicator
- Higher = Stronger signal

---

## ✅ **VERIFICATION CHECKLIST**

**Before claiming TX works, verify ALL:**
- [ ] TX indicator blinks when transmitting
- [ ] SDR++ waterfall shows bursts
- [ ] Bursts appear at correct frequency
- [ ] Number of bursts matches expected (15, 50, 256, etc.)
- [ ] Visualized binary makes sense
- [ ] Replayed signal matches captured signal
- [ ] Device responds (if simple fixed code)

**If ALL checked = TX is working perfectly! 🎉**

---

## 🚀 **NEXT STEPS**

Once TX is verified working:
1. Test on YOUR garage door (safe!)
2. Try car key fob (educational)
3. Experiment with wireless doorbell
4. Compare different modulation types
5. Build signal database
6. Share findings (responsibly!)

**Remember: Only YOUR devices, YOUR property!**

---

**Questions?**
- Check TX indicator first
- Then check SDR++ waterfall
- Use VISUALIZE to debug signals
- Compare captured vs transmitted
- Test with known good signals first

**Happy testing! 🎓📡**

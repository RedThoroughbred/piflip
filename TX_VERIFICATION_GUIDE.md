# TX Verification Guide 🎯

## How to Verify PiFlip TX is Actually Working

---

## 🚀 **QUICK START TEST**

### **What You Need:**
- PiFlip with CC1101 connected
- SDR++ running on Mac (or any computer)
- RTL-SDR dongle connected to Mac
- Both devices on same network (or close proximity)

### **5-Minute Verification Test:**

**Step 1: Set Up SDR++ (Mac)**
```
1. Open SDR++
2. Source: RTL-SDR
3. Frequency: 433.920 MHz (exactly)
4. Mode: RAW or WFM
5. Enable waterfall display
6. Set gain: 30-40 dB
7. Sample rate: 2.048 MS/s
```

**Step 2: Generate Test Signal (PiFlip)**
```
1. Open PiFlip Web Interface
2. Go to: Advanced TX
3. Click: Generate Custom Signal
4. Frequency: 433.92
5. Pattern: 11110000111100001111
6. Bit Duration: 500
7. Click: TRANSMIT
```

**Step 3: Watch for Confirmation**
```
✅ PiFlip: Yellow "TX" indicator blinks
✅ SDR++: See bursts on waterfall at 433.92 MHz
✅ SDR++: Signal strength spike during TX

If BOTH show = TX WORKS! 🎉
```

---

## 📊 **DETAILED TESTING METHODS**

### **Method 1: Custom Signal Test (Simplest)**

**Purpose:** Verify basic TX works

**Steps:**
```
1. SDR++: Set to 433.92 MHz, waterfall on

2. PiFlip: Advanced TX → Generate Custom Signal
   - Frequency: 433.92
   - Pattern: 10101010 (alternating bits)
   - Bit Duration: 500μs
   - Click TRANSMIT

3. Watch SDR++:
   ✅ Should see 3 bursts (repeats=3)
   ✅ Each burst ~4ms long (8 bits × 500μs)
   ✅ At exactly 433.92 MHz

4. If visible = Basic TX works!
```

### **Method 2: Replay with Variations (Most Visual)**

**Purpose:** See multiple frequency offsets

**Steps:**
```
1. Capture any signal:
   - RF Tools → Capture Signal
   - Press remote while capturing
   - Save as: "test_remote"

2. SDR++: Set to 433.92 MHz, waterfall on

3. PiFlip: Signal Library → test_remote
   - Click: 🔄 VARIATIONS
   - Confirm transmission

4. Watch SDR++:
   ✅ Should see 15 bursts total
   ✅ At 5 different frequencies:
      - 433.42 MHz (−0.5)
      - 433.67 MHz (−0.25)
      - 433.92 MHz (base)
      - 434.17 MHz (+0.25)
      - 434.42 MHz (+0.5)
   ✅ Each frequency transmitted 3 times

5. If you see the pattern = TX works perfectly!
```

### **Method 3: Signal Fuzzing (Continuous TX)**

**Purpose:** Test sustained transmission

**Steps:**
```
1. SDR++: Set to 433.92 MHz

2. PiFlip: Signal Library → test_remote
   - Click: 🎲 FUZZ
   - Fuzz %: 10
   - Iterations: 50
   - Confirm

3. Watch SDR++:
   ✅ Should see 50 bursts
   ✅ Each slightly different duration
   ✅ All at 433.92 MHz
   ✅ Takes ~15 seconds (50 × 0.3s)
   ✅ TX indicator blinks entire time

4. If continuous bursts visible = TX sustained!
```

### **Method 4: Brute Force (Stress Test)**

**Purpose:** Verify TX under heavy load

**Steps:**
```
1. SDR++: Set to 433.92 MHz

2. PiFlip: Advanced TX → Brute Force
   - Frequency: 433.92
   - Bit Length: 8 (256 codes)
   - Click: START

3. Watch SDR++:
   ✅ Should see 256 bursts
   ✅ One every ~100ms
   ✅ Takes ~25 seconds total
   ✅ Regular pattern on waterfall

4. Count bursts. 256 = TX reliable!
```

---

## 🔬 **WHAT YOU SHOULD SEE**

### **SDR++ Waterfall - TX Working:**
```
Time →
433.42  ████ ████ ████               ← -0.5 MHz offset
433.67        ████ ████ ████         ← -0.25 MHz offset
433.92              ████ ████ ████   ← Base frequency
434.17                    ████ ████  ← +0.25 MHz offset
434.42                          ████ ← +0.5 MHz offset
```

### **SDR++ Waterfall - TX NOT Working:**
```
Time →
433.42  ░░░░░░░░░░░░░░░░░░░░░░░░░   ← Just noise
433.67  ░░░░░░░░░░░░░░░░░░░░░░░░░
433.92  ░░░░░░░░░░░░░░░░░░░░░░░░░   ← No signal
434.17  ░░░░░░░░░░░░░░░░░░░░░░░░░
434.42  ░░░░░░░░░░░░░░░░░░░░░░░░░
```

### **PiFlip TX Indicator:**
```
✅ Blinking yellow "TX" during transmission
✅ Disappears when complete
✅ Timing matches SDR++ bursts
```

---

## 🛠️ **TROUBLESHOOTING**

### **Problem: No Signal on SDR++**

**Check 1: CC1101 Hardware**
```bash
# On PiFlip, test CC1101 connection:
python3 << 'EOF'
from cc1101_enhanced import CC1101Enhanced
cc = CC1101Enhanced()
print("CC1101 initialized!")

cc.set_frequency(433.92)
cc.set_tx_power('max')
print("Entering TX mode for 2 seconds...")

cc.enter_tx_mode()
import time
time.sleep(2)
cc.idle()

print("TX test complete!")
EOF

# Watch SDR++ during this test
# Should see 2-second carrier burst
```

**Check 2: Frequency Accuracy**
```
PiFlip shows: 433.92 MHz
SDR++ set to: 433.92 MHz

Try scanning SDR++ 433.0 - 434.5 MHz
to see if signal appears elsewhere
```

**Check 3: Distance**
```
Move RTL-SDR antenna VERY CLOSE to PiFlip (10-20cm)
Sometimes signal is too weak if far apart
```

**Check 4: SDR++ Gain**
```
Increase RTL-SDR gain to 40-50 dB
Some dongles need higher gain
```

### **Problem: TX Indicator Shows, But No SDR++ Signal**

**Possible Causes:**
1. **Antenna missing** - CC1101 has no antenna connected
2. **Wrong frequency** - Double-check both frequencies match
3. **Shielding** - Pi in metal case blocking RF
4. **SDR++ not working** - Try receiving known signal (FM radio, etc.)

**Test:**
```
1. Use external antenna on CC1101
2. Move antennas closer (touching distance)
3. Use MAX power setting
4. Increase SDR++ gain to MAX
```

### **Problem: Signal Looks Wrong/Different**

**Possible Reasons:**
1. **Frequency offset** - Not exactly 433.92
2. **Timing drift** - Replay timing slightly off
3. **Modulation** - ASK vs OOK interpretation

**Solution:**
```
Use VARIATIONS button - tries 5 frequencies
One should match better than others
Note which offset looks best
```

---

## 📈 **ADVANCED VERIFICATION**

### **Record & Compare (Most Accurate)**

**Step 1: Capture Original Signal**
```
1. Press remote near PiFlip
2. RF Tools → Capture Signal
3. Save as: "original"
4. Library → original → 📊 VISUALIZE
5. Note binary pattern & timings
```

**Step 2: Record Replay on SDR++**
```
1. SDR++ → Enable IQ recording
2. Set to 433.92 MHz
3. Start recording
4. PiFlip → Library → original → ▶️ REPLAY
5. Stop recording
6. Save as: "piflip_tx_test.cu8"
```

**Step 3: Analyze Recording**
```
1. Open "piflip_tx_test.cu8" in SDR++
2. Look at spectrum
3. Measure exact frequency
4. Compare with original

If frequency matches within 0.01 MHz = Accurate!
```

### **Use PiFlip to Receive Own TX**

**Setup: Need TWO CC1101 modules**
```
1. CC1101 #1 (TX): Connected to PiFlip
2. CC1101 #2 (RX): Connected to RTL-SDR

(Or use same CC1101 - TX then RX)
```

**Test:**
```
1. PiFlip: Capture signal, save as "test"
2. PiFlip: Library → test → 📊 VISUALIZE
3. Note binary pattern
4. PiFlip: Library → test → ▶️ REPLAY
5. (While replaying) Use RTL-SDR to capture
6. Decode RTL-SDR capture
7. Compare binary patterns

If patterns match = Perfect accuracy!
```

---

## 🎯 **EXPECTED RESULTS**

### **Frequency Accuracy:**
```
✅ Should be within ±0.05 MHz of target
✅ Most CC1101 modules accurate to ±0.01 MHz
```

### **Timing Accuracy:**
```
✅ Should be within ±5% of original
✅ 500μs pulse should show 475-525μs on SDR++
```

### **Power Output:**
```
✅ Max power: ~10 dBm (10mW)
✅ Range: 10-100 meters (depends on antenna)
✅ SDR++ should see signal at 1-5 meters easily
```

---

## ✅ **VERIFICATION CHECKLIST**

**Before claiming TX works, confirm ALL:**

Hardware:
- [ ] CC1101 connected to correct SPI pins
- [ ] Antenna connected to CC1101
- [ ] Power supply adequate (5V 2.5A+)

Software:
- [ ] TX indicator appears when transmitting
- [ ] No errors in browser console
- [ ] PiFlip shows "Transmitted successfully"

SDR++ Verification:
- [ ] Waterfall shows bursts at correct frequency
- [ ] Burst count matches expected (3, 15, 50, 256, etc.)
- [ ] Signal strength visible above noise floor
- [ ] Timing matches expected duration

Signal Quality:
- [ ] Visualized binary makes sense
- [ ] Timings are consistent
- [ ] Frequency accurate to ±0.05 MHz

**If ALL checked = TX is working! 🎉**

---

## 📱 **REAL-WORLD TESTS**

### **Test 1: Garage Door (If You Have One)**
```
1. Capture garage remote signal
2. Save as "garage_test"
3. Visualize to verify capture
4. Stand near garage door
5. Replay signal
6. Door opens = TX works AND accurate!
```

### **Test 2: Wireless Doorbell**
```
1. Capture doorbell button press
2. Replay signal
3. Doorbell rings = TX works!

(Simple doorbells use fixed codes - easy test)
```

### **Test 3: Car Key Fob (READ ONLY!)**
```
⚠️ WARNING: Don't replay car signals!
Rolling codes can desync your key!

SAFE TEST:
1. Capture car unlock signal
2. Visualize only (don't replay)
3. Use SDR++ to capture replay
4. Compare visualizations
5. Verify accuracy without replaying
```

---

## 💡 **PRO TIPS**

### **Tip 1: Start Simple**
```
First test: Generate custom "10101010"
This is easiest to see on waterfall
Clear pattern = working
Noise = not working
```

### **Tip 2: Use Variations for Unknown Frequencies**
```
If exact frequency uncertain:
1. Use VARIATIONS button
2. Tries 5 frequencies
3. See which one appears strongest on SDR++
4. That's your actual TX frequency!
```

### **Tip 3: Visual Confirmation is Key**
```
ALWAYS verify with SDR++ before claiming success
PiFlip can show "TX" but have hardware issue
SDR++ is ground truth
```

### **Tip 4: Record Everything**
```
When testing:
1. Enable SDR++ recording
2. Run PiFlip TX test
3. Save recording with date/name
4. Later analysis if needed
```

---

## 🔗 **HELPFUL SDR++ SETTINGS**

### **For 433 MHz Testing:**
```
Source: RTL-SDR
Frequency: 433.920 MHz
Mode: RAW (or WFM for audio)
Sample Rate: 2.048 MS/s
Gain: 35 dB (adjust as needed)
Waterfall Speed: Medium
FFT Size: 8192
```

### **For Finding Weak Signals:**
```
Increase gain to 45-50 dB
Reduce FFT averaging
Increase waterfall contrast
Zoom into exact frequency
```

### **For Accurate Frequency Measurement:**
```
Use "peak hold" on spectrum
Click exact peak to read frequency
Should match PiFlip TX freq
```

---

## 📊 **INTERPRETATION GUIDE**

### **What Strong Signal Looks Like:**
```
Waterfall: Bright yellow/red vertical lines
Spectrum: Clear spike 20+ dB above noise
Duration: Matches expected (ms scale)
```

### **What Weak Signal Looks Like:**
```
Waterfall: Faint green/blue lines
Spectrum: Small bump 5-10 dB above noise
Might need higher gain to see clearly
```

### **What NO Signal Looks Like:**
```
Waterfall: Unchanged noise pattern
Spectrum: Flat noise floor
No variation during TX
= Hardware problem!
```

---

## 🚀 **QUICK REFERENCE**

**TX Working = ALL of these:**
```
✅ Yellow TX indicator on PiFlip
✅ Bursts visible on SDR++ waterfall
✅ Frequency matches (±0.05 MHz)
✅ Burst count correct (3, 15, 50, etc.)
✅ Timing matches (visualize → SDR++)
✅ No errors in browser console
```

**TX NOT Working = ANY of these:**
```
❌ TX indicator but no SDR++ signal
❌ Wrong frequency on waterfall
❌ Continuous carrier (should be bursts)
❌ Random noise pattern
❌ Errors in console
```

---

## 🎓 **LEARNING OUTCOMES**

After completing these tests, you'll know:

1. **If TX actually works** - Visual confirmation via SDR++
2. **Frequency accuracy** - How close to target frequency
3. **Timing accuracy** - How precise replay is
4. **Power output** - Effective range of transmission
5. **Signal quality** - Clean modulation vs noisy

---

## 📚 **FURTHER READING**

- `ADVANCED_FEATURES_GUIDE.md` - All Advanced TX features explained
- `SIGNAL_TYPES_EXPLAINED.md` - RTL-SDR vs CC1101 captures
- `WHATS_NEW.md` - Recent feature additions

---

## ✨ **SUCCESS CRITERIA**

**Minimum (TX works):**
- See signal on SDR++ during PiFlip TX
- Frequency within ±0.1 MHz
- TX indicator shows

**Good (TX accurate):**
- Signal within ±0.05 MHz
- Timing accurate to ±10%
- Replayed signal similar to original

**Excellent (TX perfect):**
- Signal within ±0.01 MHz
- Timing accurate to ±5%
- Replayed signal matches original exactly
- Device responds (garage door, doorbell)

---

**Still not working after all tests?**

Check:
1. CC1101 wiring diagram
2. SPI enabled on Pi (`raspi-config`)
3. CC1101 power (3.3V NOT 5V!)
4. Antenna connected
5. Try different frequency (315 MHz, 868 MHz)

**Happy testing! 📡🎯**

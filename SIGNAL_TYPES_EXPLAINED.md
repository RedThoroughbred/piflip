# Signal Types Explained 📡

## Understanding RTL-SDR vs CC1101 Captures

---

## 🎯 **THE KEY DIFFERENCE**

### **RTL-SDR Captures (.cu8 files)**
- **What:** Raw IQ samples from wideband receiver
- **Frequency:** 24 MHz - 1.7 GHz
- **Data Format:** Complex unsigned 8-bit (I/Q pairs)
- **File Size:** Large (2 MB/second typically)
- **Use For:** Analysis, visualization, research
- **Can Transmit:** ❌ NO - Raw samples, no timing data

### **CC1101 Captures (.json files)**
- **What:** Decoded timing data from sub-GHz transceiver
- **Frequency:** 300-928 MHz only
- **Data Format:** JSON with timing transitions
- **File Size:** Small (few KB typically)
- **Use For:** Replay, transmission, advanced TX
- **Can Transmit:** ✅ YES - Has exact timing data

---

## 📊 **EXAMPLE: Same Signal, Two Capture Types**

### **RTL-SDR Capture (testNumber1.json):**
```json
{
  "name": "testNumber1",
  "filename": "testNumber1.cu8",
  "frequency": 433920000,
  "sample_rate": 2048000,
  "duration": 5,
  "num_samples": 10240000,
  "file_size": 20480000
}
```

**What you get:**
- 20 MB file of raw IQ samples
- Can visualize in SDR++
- Can analyze spectrum
- Can't directly transmit

### **CC1101 Capture (garage_remote.json):**
```json
{
  "name": "garage_remote",
  "frequency": 433.92,
  "timings": [
    {"state": 1, "duration_us": 500},
    {"state": 0, "duration_us": 500},
    {"state": 1, "duration_us": 1000},
    {"state": 0, "duration_us": 500}
  ],
  "timestamp": "2025-10-03T14:30:00"
}
```

**What you get:**
- Small JSON file with exact timings
- Can replay exactly
- Can fuzz timing
- Can transmit with variations

---

## 🔄 **WHICH FEATURES WORK WITH WHAT?**

### **RTL-SDR Captures Only:**
- ✅ **Analyze** - Spectrum analysis
- ✅ **Visualize** - If timing data can be decoded
- ❌ **Replay** - No timing data to transmit
- ❌ **Variations** - No timing data
- ❌ **Fuzz** - No timing data
- ❌ **Brute Force** - Doesn't apply

**Purpose:** Receive, analyze, research

### **CC1101 Captures Only:**
- ✅ **Analyze** - Timing analysis
- ✅ **Visualize** - Waveform from timings
- ✅ **Replay** - Exact retransmission
- ✅ **Variations** - Freq/timing offsets
- ✅ **Fuzz** - Random timing changes
- ✅ **Brute Force** - Generate codes (not replay)

**Purpose:** Transmit, replay, attack

---

## 🛠️ **HOW TO USE EACH**

### **Use RTL-SDR When:**
```
1. Wide frequency range (need 868 MHz or 2.4 GHz)
2. Just want to see what's there (spectrum scan)
3. Research/analysis only
4. Compare your TX with received signal
5. Verify PiFlip is transmitting

Examples:
- Scan entire 433 MHz band
- Find unknown frequencies
- See if TX is working (waterfall)
- Analyze signal characteristics
```

### **Use CC1101 When:**
```
1. Need to transmit (300-928 MHz)
2. Want to replay captured signals
3. Testing signal variations
4. Sub-GHz TX/RX only
5. Need exact timing data

Examples:
- Capture garage remote and replay
- Test car key fob (rolling code demo)
- Replay with frequency offsets
- Fuzz signal timing
- Transmit custom patterns
```

---

## 📝 **WORKFLOW EXAMPLES**

### **Workflow 1: Verify TX Works**
```
1. SDR++ (RTL-SDR): Set to 433.92 MHz, waterfall on
2. PiFlip (CC1101): Capture signal from remote
3. PiFlip: Replay → Variations
4. SDR++ (RTL-SDR): See bursts on waterfall

RTL-SDR verifies CC1101 TX!
```

### **Workflow 2: Analyze Unknown Signal**
```
1. PiFlip (RTL-SDR): Capture 5 seconds at 433.92 MHz
2. SDR++ (RTL-SDR): Open .cu8 file, analyze
3. PiFlip (CC1101): Try to capture same signal
4. PiFlip: If CC1101 got it, can replay

RTL-SDR finds it, CC1101 captures it!
```

### **Workflow 3: Test Device Security**
```
1. PiFlip (CC1101): Capture device remote
2. PiFlip: Visualize → See binary pattern
3. PiFlip: Replay → Variations
4. Device response = fixed code (insecure!)
5. No response = rolling code (secure!)

CC1101 tests security, RTL-SDR watches!
```

---

## ⚠️ **COMMON ERRORS EXPLAINED**

### **Error: "Signal has no timing data"**
```
Cause: Trying Advanced TX on RTL-SDR capture

Solution:
- RTL-SDR captures are raw IQ samples
- Can't be transmitted via CC1101
- Use CC1101 to capture for TX features
```

### **Error: "Only CC1101 captures can be replayed"**
```
Cause: Trying to replay RTL-SDR capture

Solution:
- Use CC1101 to capture the signal
- Or decode RTL-SDR capture to timing data first
- Then save as CC1101 format
```

### **Error: "Raw IQ samples"**
```
Cause: RTL-SDR capture selected for TX

Solution:
1. Go to RF Tools (CC1101)
2. Capture Signal (same frequency)
3. Now you have timing data
4. Can use Advanced TX features
```

---

## 🎯 **QUICK REFERENCE**

### **Want to RECEIVE wideband?**
→ Use RTL-SDR (24 MHz - 1.7 GHz)

### **Want to TRANSMIT sub-GHz?**
→ Use CC1101 (300-928 MHz)

### **Want to ANALYZE spectrum?**
→ Use RTL-SDR captures

### **Want to REPLAY signals?**
→ Use CC1101 captures

### **Want to VERIFY TX works?**
→ Use both (CC1101 TX, RTL-SDR RX)

### **Want ADVANCED TX features?**
→ Use CC1101 captures only

---

## 🔬 **TECHNICAL DETAILS**

### **RTL-SDR IQ Samples:**
```
File: testNumber1.cu8
Format: I/Q pairs (8-bit each)
Sample: [I1, Q1, I2, Q2, I3, Q3, ...]

I = In-phase (real)
Q = Quadrature (imaginary)

Can decode to:
- Amplitude (sqrt(I² + Q²))
- Phase (atan2(Q, I))
- Frequency (phase changes)
```

### **CC1101 Timing Data:**
```
File: garage.json
Format: State transitions

{state: 1, duration_us: 500}  // HIGH for 500μs
{state: 0, duration_us: 500}  // LOW for 500μs

Can transmit:
- Exact timing replay
- Frequency variations
- Timing fuzzing
```

---

## ✅ **BEST PRACTICES**

### **For Capture:**
1. **RTL-SDR** for finding unknown signals
2. **CC1101** for capturing to replay
3. Use RTL-SDR to verify CC1101 TX

### **For Analysis:**
1. **RTL-SDR** for spectrum/waterfall
2. **CC1101** for timing/protocol analysis
3. Compare both for accuracy

### **For Transmission:**
1. **CC1101 only** - RTL-SDR can't transmit
2. Capture with CC1101 first
3. Verify with RTL-SDR waterfall

---

## 🚀 **NEXT STEPS**

**You have RTL-SDR capture and want to use Advanced TX?**
```
1. Note the frequency from RTL-SDR capture
2. Go to: RF Tools (CC1101)
3. Capture Signal at same frequency
4. Press remote while capturing
5. Now you have CC1101 capture with timing data
6. Use Advanced TX features!
```

**You captured with CC1101 and want to verify?**
```
1. Open SDR++ (RTL-SDR)
2. Set to same frequency
3. Enable waterfall
4. Click Replay on CC1101 capture
5. Watch waterfall - should see bursts!
```

---

## 📚 **SUMMARY**

**RTL-SDR:**
- 📡 Wide frequency (24 MHz - 1.7 GHz)
- 📊 Raw IQ samples
- 👁️ Receive & analyze only
- 📈 Large files
- ✅ See what's transmitting

**CC1101:**
- 📡 Sub-GHz only (300-928 MHz)
- ⏱️ Timing data
- 📤 Transmit & receive
- 💾 Small files
- ✅ Replay & advanced TX

**Use Both:**
- CC1101 captures → Transmit
- RTL-SDR → Verify transmission
- Perfect combo! 🎯

---

**Still confused? Just remember:**
- **RTL-SDR = See signals** 👀
- **CC1101 = Send signals** 📤
- **Use both together = Powerful!** 💪

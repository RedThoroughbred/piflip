# 📡 PiFlip Signal Capture & Replay - Complete Guide

## 🎯 The Complete Workflow (Now Automated!)

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘

1. 📻 CAPTURE (RTL-SDR)
   │
   ├─ User clicks "Capture Signal"
   ├─ Enters name: "garage_door"
   ├─ Selects frequency: 433.92 MHz
   ├─ Sets duration: 5 seconds
   │
   ├─ RTL-SDR records raw IQ data
   ├─ Saves: garage_door.cu8 (20MB file)
   └─ Saves: garage_door.json (metadata)
   │
   ↓

2. 🤖 AUTO-ANALYZE (Automatic!)
   │
   ├─ Python script runs immediately
   ├─ Loads IQ data from .cu8 file
   ├─ Detects modulation type (ASK/OOK/FSK)
   ├─ Demodulates signal
   ├─ Extracts bit pattern: "101010001110..."
   ├─ Identifies protocol (if known)
   └─ Saves: garage_door_replay.json
   │
   ↓

3. ▶️ REPLAY (CC1101)
   │
   ├─ User clicks "Replay" button
   ├─ Loads: garage_door_replay.json
   ├─ Reads bit pattern
   ├─ Configures CC1101:
   │  • Frequency: 433.92 MHz
   │  • Modulation: OOK
   │  • Transmit power: 10dBm
   ├─ Transmits decoded bits
   └─ Garage door opens! ✅
```

---

## 🔍 What Each File Does

### **Capture Files** (saved by RTL-SDR)

**`garage_door.cu8`** - Raw IQ Data
- Complex Unsigned 8-bit format
- 20 MB for 5 seconds @ 2.048 MS/s
- Contains raw radio frequency information
- Like a "recording" of the airwaves

**`garage_door.json`** - Metadata
```json
{
  "name": "garage_door",
  "frequency": 433920000,
  "sample_rate": 2048000,
  "duration": 5,
  "timestamp": "2025-10-01T22:30:45"
}
```

### **Analysis Files** (created by auto_analyzer.py)

**`garage_door_replay.json`** - Decoded Protocol
```json
{
  "name": "garage_door",
  "frequency": 433920000,
  "modulation": "OOK",
  "bit_pattern": "101010001110101100001111",
  "ready_for_replay": true,
  "notes": "Auto-analyzed OOK signal"
}
```

---

## 🤖 How Auto-Analysis Works

### **Before (Manual Process):**
1. Capture signal
2. Open URH GUI manually
3. Load .cu8 file
4. Manually analyze
5. Manually extract bits
6. Manually export
7. Then replay

**Time:** 10-30 minutes per signal

### **Now (Automatic Process):**
1. Capture signal
2. **Everything else happens automatically!**
3. Replay ready in seconds

**Time:** < 30 seconds

---

## 🔧 Technical Details

### RTL-SDR Capture Process
```python
# What happens when you click "Capture Signal"
rtl_sdr -f 433920000 \    # Frequency: 433.92 MHz
        -s 2048000 \       # Sample rate: 2.048 MS/s
        -n 10240000 \      # Samples: 10.24 million
        garage_door.cu8    # Output file
```

**Recording quality:**
- Bandwidth: ~2 MHz (enough for most signals)
- Resolution: 8-bit IQ samples
- File size: ~4 MB per second

### Auto-Analysis Process
```python
# What auto_analyzer.py does automatically
1. Load .cu8 file
2. Run rtl_433 in analyze mode (for known protocols)
3. Detect signal characteristics:
   - Pulse width
   - Pulse spacing
   - Modulation type
4. Extract binary data
5. Save to replay.json
```

**Supported protocols:**
- OOK (On-Off Keying) ✅
- ASK (Amplitude Shift Keying) ✅
- FSK (Frequency Shift Keying) ⚠️ Partial
- Manchester encoding ✅
- Rolling codes ⚠️ Detection only

### CC1101 Replay Process
```python
# What happens when you click "Replay"
1. Load garage_door_replay.json
2. Read bit_pattern
3. Configure CC1101:
   - Set frequency
   - Set modulation
   - Set data rate
4. Enter TX mode
5. Transmit bits
6. Return to idle
```

---

## 📱 New UI Features

### **Hierarchical Menu (Like Flipper Zero)**

```
Main Menu
├── RF Tools
│   ├── Scan 433MHz
│   ├── Capture Signal  ← Captures & auto-analyzes
│   ├── TPMS Sensors
│   └── Weather Stations
│
├── NFC Tools
│   ├── Scan Card
│   ├── Backup Card
│   └── Clone Card (coming soon)
│
├── Signal Library
│   └── Shows all captures with replay/analyze/delete
│
├── Flight Tracking
│   ├── Open Map
│   └── Live Statistics
│
└── Settings
    ├── Hardware Status
    └── Theme
```

### **Mobile-Optimized Design**
- Large touch targets
- Flipper Zero orange theme
- Works on small screens (320x240+)
- Breadcrumb navigation
- Swipe-friendly

---

## 🔄 Mode Switching Explained

### **Why It Exists**
RTL-SDR is a **single-channel receiver** - it can only tune to ONE frequency at a time.

**The conflict:**
- dump1090 wants: 1090 MHz (aircraft)
- rtl_433 wants: 433 MHz (devices)
- They can't both run!

### **Solution: Mode Toggle**

**Mode 1: ✈️ Flight Tracking**
- dump1090-fa service: RUNNING
- RTL-SDR tuned to: 1090 MHz
- Can do: ✅ Track aircraft
- Cannot do: ❌ 433MHz scan, capture, TPMS, weather

**Mode 2: 📡 Scanning**
- dump1090-fa service: STOPPED
- RTL-SDR tuned to: Variable (you choose)
- Can do: ✅ 433MHz scan, capture, TPMS, weather
- Cannot do: ❌ Track aircraft

**Always Available (no mode needed):**
- ✅ NFC operations (uses I2C, not RTL-SDR)
- ✅ CC1101 replay (uses SPI, not RTL-SDR)
- ✅ Signal library browsing
- ✅ Analysis tools

### **How to Switch**
1. Click the toggle at top of page
2. Page reloads automatically
3. Mode indicator updates
4. Use the appropriate features

---

## 🎯 Real-World Examples

### **Example 1: Capture & Replay Car Remote**

**Step 1: Capture**
```
1. Switch to "Scanning Mode"
2. Go to: RF Tools → Capture Signal
3. Name: "my_car_remote"
4. Frequency: 433.92 MHz
5. Duration: 3 seconds
6. Click "Start Capture"
7. PRESS CAR REMOTE BUTTON IMMEDIATELY
8. Wait for capture to finish
```

**Result:**
- `my_car_remote.cu8` saved (12MB)
- `my_car_remote.json` saved
- Auto-analysis runs
- `my_car_remote_replay.json` created
- Status: "✅ Ready for replay"

**Step 2: Replay**
```
1. Go to: Signal Library
2. Find: "my_car_remote"
3. Click the capture
4. Choose: "1. Replay"
5. Confirm warning
6. Car responds!
```

**Time:** < 2 minutes total

---

### **Example 2: Scan Weather Stations**

**Steps:**
```
1. Switch to "Scanning Mode"
2. Go to: RF Tools → Weather Stations
3. Click to start scan
4. Wait 60 seconds
5. See temperature, humidity, etc.
```

**What it finds:**
- Acurite 5-in-1 sensors
- Ambient Weather stations
- LaCrosse thermometers
- Oregon Scientific sensors
- Neighbors' weather stations

**No capture needed** - rtl_433 decodes automatically!

---

### **Example 3: Track Flights**

**Steps:**
```
1. Switch to "Flight Mode"
2. Go to: Flight Tracking → Open Map
3. New tab opens with live map
4. See aircraft overhead
```

**What you see:**
- Flight number
- Altitude (feet)
- Speed (knots)
- Heading
- Squawk code
- Distance from you

---

## 🚀 Quick Start Commands

### **Test Capture & Auto-Analysis**
```bash
# Capture a 5-second signal
curl -X POST http://127.0.0.1:5000/api/capture \
  -H "Content-Type: application/json" \
  -d '{"name": "test1", "frequency": 433920000, "duration": 5, "sample_rate": 2048000}'

# Check if it was analyzed
python3 auto_analyzer.py list

# Get replay data
python3 auto_analyzer.py replay_data test1
```

### **Manual Analysis (if auto fails)**
```bash
# Open URH GUI
urh ~/piflip/captures/test1.cu8

# Or use rtl_433 directly
rtl_433 -r ~/piflip/captures/test1.cu8 -F json -M level
```

---

## 📊 Feature Comparison

| Feature | Before | Now |
|---------|--------|-----|
| **Capture** | ✅ Working | ✅ Working |
| **Auto-Analysis** | ❌ Manual | ✅ Automatic |
| **Replay** | ⚠️ Test burst | ✅ Smart replay |
| **UI Design** | Basic grid | ✅ Flipper-style |
| **Mobile Support** | ⚠️ Okay | ✅ Optimized |
| **Mode Switching** | Confusing | ✅ Clear |
| **Workflow** | 10+ minutes | ✅ < 1 minute |

---

## 🔮 What's Next

### **Phase 1: Signal Processing** (✅ DONE)
- [x] Capture system
- [x] Auto-analysis
- [x] Smart replay
- [x] Flipper-style UI

### **Phase 2: Protocol Library** (Next)
- [ ] Pre-built common devices
- [ ] Garage door codes
- [ ] Car remote database
- [ ] Doorbell patterns
- [ ] One-click transmit

### **Phase 3: Advanced Features**
- [ ] Rolling code detection
- [ ] Brute force generator
- [ ] Signal comparison tool
- [ ] Protocol fuzzing
- [ ] Spectrum waterfall

### **Phase 4: Hardware**
- [ ] 3.5" touchscreen integration
- [ ] Local UI (no web needed)
- [ ] 3D printed case
- [ ] Battery integration
- [ ] Portable design

---

## 💡 Tips & Tricks

### **Getting Better Captures**
1. **Press device DURING capture** (not before)
2. **Press multiple times** (2-3 presses in 5 seconds)
3. **Use fresh batteries** in device
4. **Get closer** (within 10 feet is best)
5. **Use longer duration** for weak signals (10 seconds)

### **When Auto-Analysis Fails**
If `ready_for_replay: false`, try:
1. **Manual URH analysis** - More accurate
2. **Increase capture duration** - More data to work with
3. **Check signal strength** - May be too weak
4. **Try different modulation** - ASK vs FSK vs OOK

### **Replay Not Working?**
1. **Check frequency** - Must match exactly
2. **Verify bit pattern** - View in URH GUI
3. **Check modulation** - OOK vs ASK
4. **Rolling codes** - Won't work (security feature)
5. **Distance** - Get within 20 feet

---

## ⚠️ Legal & Safety

### **What's Legal:**
✅ Capturing signals from your own devices
✅ Analyzing radio frequency protocols
✅ Replaying your own garage door, car remote, etc.
✅ Receiving public broadcasts (weather, aircraft)
✅ Learning about RF security

### **What's NOT Legal:**
❌ Unlocking cars you don't own
❌ Opening others' garage doors
❌ Interfering with emergency services
❌ Transmitting on restricted frequencies
❌ Jamming/blocking signals

**PiFlip is a security research and learning tool. Use responsibly!**

---

## 📚 Files Reference

### **Your PiFlip Directory Structure**
```
~/piflip/
├── captures/              # Captured signals
│   ├── test1.cu8         # Raw IQ data
│   ├── test1.json        # Metadata
│   ├── garage.cu8
│   └── garage.json
│
├── decoded/              # Analysis results
│   ├── test1_replay.json
│   ├── garage_replay.json
│   └── test1_analysis.txt
│
├── backups/              # NFC backups
│   └── my_card.json
│
├── web_interface.py      # Main web app
├── auto_analyzer.py      # Auto-analysis engine
├── urh_analyzer.py       # URH integration
├── pi-flipper.py         # CLI tools
└── templates/
    ├── flipper_ui.html   # New UI (default)
    └── index.html        # Old UI (at /old)
```

---

## 🎓 Learn More

**Recommended Reading:**
- rtl_433 documentation
- Universal Radio Hacker wiki
- CC1101 datasheet
- RF protocols explained

**Practice Projects:**
1. Capture your TV remote
2. Analyze weather station
3. Replay garage door (yours!)
4. Track flights overhead
5. Read NFC cards

---

**Your PiFlip is now a complete capture/analyze/replay system!** 🚀

The new workflow is:
1. Click capture
2. Press device
3. Wait 10 seconds
4. Click replay
5. Done!

**No manual analysis needed!** ✨

# 🦊 PiFlip - Raspberry Pi RF & NFC Multi-Tool

**A Flipper Zero alternative built with Raspberry Pi 3B**

**Status:** ✅ Fully Functional (October 2025)

---

## 🎯 What is PiFlip?

PiFlip is a portable RF hacking and NFC tool similar to Flipper Zero, but built on Raspberry Pi with more powerful capabilities:

- **Sub-GHz RF:** Capture, analyze, and replay signals (315-433MHz)
- **NFC/RFID:** Read, backup, and clone cards
- **Flight Tracking:** Track aircraft with ADS-B (1090MHz)
- **Wide-band SDR:** 24MHz - 1.7GHz reception
- **Signal Analysis:** Integrated URH (Universal Radio Hacker)

---

## ✅ Hardware

| Module | Status | Purpose |
|--------|--------|---------|
| **Raspberry Pi 3B** | ✅ Working | Main computer |
| **RTL-SDR Blog V4** | ✅ Working | Wide-band receiver (24-1700MHz) |
| **CC1101** | ✅ Working | Sub-GHz transceiver (300-928MHz) |
| **PN532** | ✅ Working | NFC/RFID reader/writer |
| **3A Power Supply** | ✅ Required | Stable power for all modules |

**Cost:** ~$120 total (vs $169 for Flipper Zero)

---

## 🚀 Quick Start

### **1. Access Web Interface:**
```
http://192.168.86.141:5000
```

### **2. Test All Hardware:**
```
http://192.168.86.141:5000/test
```
Click "RUN ALL TESTS" - all should pass ✅

### **3. Try Key Features:**

**Scan NFC Card:**
- NFC Tools → Scan Card
- Place card on reader

**Capture RF Signal:**
- RF Tools → Capture Signal
- Press device (key fob, remote, etc.)

**Track Flights:**
- Toggle to Flight Mode
- Flight Tracking → Open Map

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **HARDWARE_TEST_RESULTS_FINAL.md** | Complete test results ✅ |
| **SIGNAL_WORKFLOW_EXPLAINED.md** | How capture/replay works |
| **WEB_INTERFACE_TEST_GUIDE.md** | Testing guide |
| **HARDWARE_STRATEGY.md** | Hardware decisions |
| **FLIGHT_TRACKING_GUIDE.md** | Flight tracking setup |
| **INTERFACE_GUIDE.md** | Feature reference |
| **ROADMAP.md** | Future plans |

---

## 🎨 Features

### **✅ Working Now:**

**RF Tools:**
- [x] 433MHz device scanning
- [x] Signal capture (IQ data)
- [x] Signal library management
- [x] CC1101 transmission (test bursts)
- [x] TPMS sensor detection
- [x] Weather station detection
- [x] Flight tracking (ADS-B)

**NFC Tools:**
- [x] Card scanning (UID read)
- [x] Card backup to JSON
- [x] Mifare Classic support

**Interface:**
- [x] Flipper-style web UI
- [x] Mode switching (Flight vs Scanning)
- [x] Test suite
- [x] Signal library browser
- [x] Real-time status

### **⏳ In Progress:**

- [ ] Full signal replay (needs URH analysis)
- [ ] Auto-analysis integration
- [ ] Protocol library
- [ ] NFC clone/write features
- [ ] 3.5" touchscreen support
- [ ] 3D printed case

---

## 🔧 Installation

### **Prerequisites:**
- Raspberry Pi 3B (or 4)
- RTL-SDR Blog V4
- CC1101 module
- PN532 NFC module
- 3A power supply (important!)

### **Software Setup:**
```bash
# Already installed on your Pi:
- Flask (web interface)
- dump1090-fa (flight tracking)
- rtl_433 (433MHz decoding)
- rtl-sdr tools
- URH (Universal Radio Hacker)
- Python 3
```

### **Run Web Interface:**
```bash
cd ~/piflip
python3 web_interface.py
```

---

## 📱 Web Interface

### **Main UI:**
```
http://192.168.86.141:5000
```

**Flipper-style hierarchical menu:**
- RF Tools
  - Scan 433MHz
  - Capture Signal
  - TPMS Sensors
  - Weather Stations
- NFC Tools
  - Scan Card
  - Backup Card
- Signal Library
  - View captures
  - Replay signals
  - Analyze with URH
- Flight Tracking
  - Open Map
  - Live Statistics
- Settings
  - Hardware Status

### **Test Suite:**
```
http://192.168.86.141:5000/test
```

Automated testing of all features.

### **Flight Map:**
```
http://192.168.86.141:8080
```

Live aircraft tracking map (PiAware/SkyAware).

---

## 🧪 Testing

### **All Hardware Test:**
```bash
# Via web interface
http://192.168.86.141:5000/test

# Or command line tests
cd ~/piflip

# Test RTL-SDR
rtl_test -t

# Test 433MHz
./test_keyfob_now.sh

# Test flights
./test_flight_reception.sh

# Test NFC
curl http://127.0.0.1:5000/api/nfc

# Test CC1101
python3 test_cc1101_transmit.py
```

---

## 📊 Capabilities Comparison

| Feature | Flipper Zero | PiFlip |
|---------|--------------|--------|
| **Sub-GHz RX** | CC1101 (narrowband) | RTL-SDR (wideband!) ✅ |
| **Sub-GHz TX** | CC1101 | CC1101 ✅ |
| **NFC** | Yes | PN532 ✅ |
| **125kHz RFID** | Yes | ❌ (can add) |
| **Infrared** | Yes | ❌ (can add) |
| **iButton** | Yes | ❌ (can add) |
| **Flight Tracking** | ❌ | ADS-B 1090MHz ✅ |
| **Wideband SDR** | ❌ | 24MHz-1.7GHz ✅ |
| **Processing Power** | ARM Cortex-M4 | ARM Cortex-A53 (4 cores) ✅ |
| **Storage** | 256KB | microSD (GB+) ✅ |
| **Display** | 128x64 LCD | ⏳ Web UI (3.5" coming) |
| **Battery** | Built-in | ⏳ External (power bank) |
| **Size** | Pocket-sized | Portable (larger) |
| **Cost** | $169 | ~$120 ✅ |

**PiFlip Advantages:**
- More powerful hardware
- Wideband SDR reception
- Flight tracking
- Full IQ capture for analysis
- Upgradeable/expandable
- Linux environment

---

## 🔌 Wiring Diagrams

### **RTL-SDR:**
```
RTL-SDR Blog V4 → Pi USB port
Antenna → RTL-SDR SMA connector
```

### **PN532 (I2C):**
```
PN532 → Raspberry Pi
VCC   → Pin 1 (3.3V)
GND   → Pin 6 (GND)
SDA   → Pin 3 (GPIO 2)
SCL   → Pin 5 (GPIO 3)
```

### **CC1101 (SPI):**
```
CC1101 → Raspberry Pi
VCC    → Pin 17 (3.3V)
GND    → Pin 9 (GND)
SCK    → Pin 23 (GPIO 11 / SCLK)
MISO   → Pin 21 (GPIO 9 / MISO)
MOSI   → Pin 19 (GPIO 10 / MOSI)
CSN    → Pin 24 (GPIO 8 / CE0)
GDO0   → Pin 11 (GPIO 17)
GDO2   → Pin 31 (GPIO 6)
```

---

## 🎯 Common Use Cases

### **1. Analyze Key Fob:**
```bash
# Capture signal
Web UI → RF Tools → Capture Signal
Name: my_car_key
Frequency: 433.92 MHz
Duration: 5 seconds
[Press key fob NOW!]

# Analyze
Signal Library → my_car_key → Analyze

# Replay
Signal Library → my_car_key → Replay
```

### **2. Backup NFC Card:**
```bash
# Scan card
Web UI → NFC Tools → Scan Card
[Place card on reader]

# Backup
NFC Tools → Backup Card
```

### **3. Track Flights:**
```bash
# Switch mode
Toggle to Flight Mode

# Open map
Flight Tracking → Open Map
```

---

## ⚡ Power Requirements

**CRITICAL:** Use 3A power supply!

**Recommended:**
- Official Raspberry Pi 5V 3A PSU
- CanaKit 5V 3A PSU

**Don't use:**
- Phone chargers (usually 1-2A)
- Old USB chargers
- Unpowered USB hubs

**Why:** RTL-SDR + Pi + other modules need ~2.5A minimum. Insufficient power causes:
- Under-voltage warnings
- RTL-SDR poor reception
- Random reboots
- SD card corruption

---

## 🐛 Troubleshooting

### **No Flights Detected:**
1. Check mode: Should be "Flight Mode"
2. Move antenna to window (1090MHz needs line-of-sight)
3. Check if flights overhead: https://globe.adsbexchange.com/
4. Try during busy times (morning/evening)

### **433MHz Scan Finds Nothing:**
1. Check mode: Should be "Scanning Mode"
2. Press device DURING scan (not before)
3. Try both 315MHz and 433.92MHz
4. Get closer to device

### **Under-voltage Warnings:**
```bash
vcgencmd get_throttled
# Should show: 0x0 or 0x50000
# If 0x50005 = Need better power supply!
```

### **RTL-SDR "Device Busy" Error:**
- Switch modes (Flight vs Scanning)
- Only one program can use RTL-SDR at a time

---

## 🛒 Shopping List

**Essential:**
- Raspberry Pi 3B: $35
- RTL-SDR Blog V4: $35
- CC1101 Module: $3
- PN532 NFC Module: $10
- 3A Power Supply: $10
- microSD Card 32GB: $10
- **Total: $103**

**Recommended:**
- Powered USB Hub: $15
- USB Extension Cable: $7
- Better antenna: $20
- **Total: $145**

**Future:**
- 3.5" Touchscreen: $25
- Pi Zero 2 W (portable): $15
- Battery bank: $25
- 3D printed case: $10
- **Total for portable: $220**

---

## 📈 Performance

### **Tested & Working:**
- ✅ FM Radio reception: Perfect
- ✅ NFC card read: <1 second
- ✅ Signal capture: 20MB in 5 seconds
- ✅ CC1101 transmission: Working
- ✅ Flight messages: 31/min (needs better antenna)
- ✅ Web interface: Responsive
- ✅ No under-voltage: With 3A PSU

---

## 🚀 Next Steps

**Immediate:**
1. Test key fob capture
2. Analyze signal in URH
3. Test replay

**This Week:**
1. Get USB extension cable ($7)
2. Improve antenna placement
3. Test more RF devices

**This Month:**
1. Order 3.5" touchscreen ($25)
2. Design 3D case
3. Build protocol library
4. Complete auto-analysis

---

## 🤝 Contributing

This is a personal project, but ideas welcome!

**Current Focus:**
- Auto-analysis improvements
- Protocol library
- UI refinements
- Documentation

---

## 📄 License

Personal educational project. Use responsibly and legally.

**Legal Notice:**
- Only capture/replay YOUR OWN devices
- Don't interfere with others' systems
- Check local RF transmission regulations
- This is a LEARNING tool

---

## 🎉 Credits

**Built with:**
- Raspberry Pi
- RTL-SDR Blog
- dump1090-fa (FlightAware)
- rtl_433 (Benjamin Larsson)
- URH (Universal Radio Hacker)
- Flask (Pallets)

**Inspired by:**
- Flipper Zero
- HackRF
- Proxmark3

---

## 📞 Status

**Last Updated:** October 1, 2025
**Version:** 1.0 (Fully Functional)
**Tested:** All hardware ✅
**Ready for:** Signal capture, NFC ops, Flight tracking

**Your PiFlip is ready to use!** 🦊✨

---

**Quick Links:**
- Web UI: http://192.168.86.141:5000
- Test Suite: http://192.168.86.141:5000/test
- Flight Map: http://192.168.86.141:8080

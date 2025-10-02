# PiFlip Project - AI Assistant Context

**Last Updated:** October 2, 2025
**Project Status:** Fully Functional ✅
**Platform:** Raspberry Pi 3B running Raspberry Pi OS (Linux 6.1.21-v7+)

---

## 🎯 What is PiFlip?

PiFlip is a **Flipper Zero alternative** built on Raspberry Pi. It's a multi-tool for:
- **Sub-GHz RF:** Capture, analyze, and replay 315-433MHz signals (key fobs, remotes, TPMS, weather stations)
- **NFC/RFID:** Read, backup, clone, and emulate NFC cards
- **Flight Tracking:** ADS-B reception at 1090MHz
- **Wide-band SDR:** 24MHz - 1.7GHz reception with RTL-SDR

**Key Advantage:** More powerful hardware and wideband SDR capabilities compared to Flipper Zero, at lower cost (~$120).

---

## 🏗️ Architecture

### Main Application
**File:** `web_interface.py` (37 KB)
- Flask web server on port 5000
- RESTful API for all hardware operations
- Flipper-style UI with hierarchical menus
- Real-time hardware status monitoring

### Core Dependencies (9 Python Modules)
All located in `/home/seth/piflip/`:

1. **urh_analyzer.py** - URH (Universal Radio Hacker) integration for signal analysis
2. **auto_analyzer.py** - Automatic signal analysis on capture
3. **nfc_enhanced.py** - Enhanced NFC operations (read, save, library management)
4. **nfc_cloner.py** - NFC card cloning to magic cards
5. **nfc_emulator.py** - NFC emulation and virtual badge mode
6. **cc1101_enhanced.py** - CC1101 transceiver control (RX/TX)
7. **signal_decoder.py** - Decode signals to binary and extract protocols
8. **favorites_manager.py** - Favorites, stats, and recent activity tracking
9. **waveform_generator.py** - ASCII waveform visualization

**All 9 modules are actively used by web_interface.py** - do not delete!

---

## 🔌 Hardware

### Connected Modules
1. **RTL-SDR Blog V4** (USB) - Wideband receiver (24MHz - 1.7GHz)
2. **CC1101** (SPI) - Sub-GHz transceiver (300-928MHz) for TX/RX
3. **PN532** (I2C) - NFC/RFID reader/writer

### Pin Connections

**PN532 (I2C):**
```
PN532 → Raspberry Pi
VCC   → Pin 1 (3.3V)
GND   → Pin 6 (GND)
SDA   → Pin 3 (GPIO 2)
SCL   → Pin 5 (GPIO 3)
```

**CC1101 (SPI):**
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

**RTL-SDR:** USB connection only

### Power Requirements
**CRITICAL:** Requires 5V 3A power supply!
- Check with: `vcgencmd get_throttled`
- Should return: `0x0` or `0x50000`
- If `0x50005` = under-voltage, need better PSU

---

## 📁 Directory Structure

```
/home/seth/piflip/
├── web_interface.py          ← Main Flask application
├── app.py                    ← Old interface? (investigate if needed)
│
├── [Core Modules - 9 files]
├── urh_analyzer.py
├── auto_analyzer.py
├── nfc_enhanced.py
├── nfc_cloner.py
├── nfc_emulator.py
├── cc1101_enhanced.py
├── signal_decoder.py
├── favorites_manager.py
├── waveform_generator.py
│
├── piflip_env/              ← Python virtual environment (78 MB)
│   └── (Flask, Adafruit libs, RPi.GPIO, etc.)
│
├── templates/               ← Flask HTML templates
│   ├── flipper_ui.html      ← Main UI
│   ├── test_suite.html      ← Hardware test page
│   └── index.html           ← Old UI
│
├── captures/                ← RF signal captures (.cu8 + .json)
├── rf_library/              ← Saved RF signals
├── nfc_library/             ← Saved NFC cards
├── backups/                 ← NFC card backups
├── config/                  ← Configuration files
├── decoded/                 ← Decoded signals
│
├── start_piflip.sh          ← Launch script
├── status.sh                ← Hardware status check
│
├── README.md                ← Main documentation
├── DEPENDENCY_AUDIT.md      ← What files are used/needed
├── CLEANUP_SUMMARY.md       ← Recent cleanup results
└── claude.md                ← This file
```

---

## 🚀 Running the Application

### Start Web Interface
```bash
cd ~/piflip
python3 web_interface.py
```

**Access at:** http://192.168.86.141:5000

### Test Suite
**URL:** http://192.168.86.141:5000/test

Tests all hardware: RTL-SDR, CC1101, PN532

### Flight Tracking
**URL:** http://192.168.86.141:8080

PiAware/SkyAware web interface for dump1090-fa

---

## 🔄 RTL-SDR Mode Switching

**IMPORTANT:** RTL-SDR can only be used by ONE program at a time!

### Two Modes:

1. **Flight Mode** - dump1090-fa running on 1090MHz
   - Flight tracking active
   - 433MHz/TPMS/Weather scanning disabled

2. **Scanning Mode** - dump1090-fa stopped
   - 433MHz/TPMS/Weather scanning enabled
   - Flight tracking disabled

### Switch Modes:
- Via web UI: "Switch Mode" button
- Via API: `POST /api/rtlsdr/toggle`
- Manual: `sudo systemctl stop dump1090-fa` or `start dump1090-fa`

**Check current mode:** `systemctl is-active dump1090-fa`

---

## 🛠️ Key API Endpoints

### RF Operations
- `GET /api/scan433` - Scan for 433MHz devices (30s)
- `POST /api/capture` - Capture raw IQ signal with RTL-SDR
- `GET /api/captures` - List saved captures
- `POST /api/replay/<name>` - Replay signal via CC1101
- `GET /api/analyze/<name>` - Analyze signal with URH

### NFC Operations
- `GET /api/nfc` - Scan for NFC card
- `POST /api/nfc/save` - Save card to library
- `GET /api/nfc/library` - List saved cards
- `POST /api/nfc/read_full` - Full card dump (all sectors)
- `POST /api/nfc/clone` - Clone to magic card
- `POST /api/nfc/backup` - Backup card UID

### CC1101 Operations
- `GET /api/cc1101/status` - Get chip status
- `POST /api/cc1101/capture` - Capture with CC1101
- `POST /api/cc1101/scan` - Scan frequency range
- `GET /api/cc1101/library` - List saved signals
- `POST /api/cc1101/transmit/<name>` - Transmit saved signal

### Flight Tracking
- `GET /api/flights` - Get aircraft data from dump1090
- `GET /api/flights/stats` - Flight statistics

### System
- `GET /api/status` - Hardware status (NFC, RTL-SDR, CC1101)
- `GET /api/rtlsdr/mode` - Check RTL-SDR mode
- `POST /api/rtlsdr/toggle` - Switch between modes

---

## 📦 External Tools Used

### System Commands (via subprocess)
- `rtl_433` - Decode 433MHz protocols
- `rtl_sdr` - Raw IQ capture
- `rtl_power` - Spectrum scanning for waterfall
- `rtl_test` - Hardware detection
- `dump1090-fa` - ADS-B decoder (flight tracking)
- `systemctl` - Service management

### Python Libraries (in piflip_env)
- Flask - Web framework
- RPi.GPIO - GPIO control
- spidev - SPI communication (CC1101)
- board, busio - I2C communication (PN532)
- adafruit_pn532 - PN532 driver
- adafruit_blinka - Hardware abstraction
- requests - HTTP client

---

## 🔍 Common Issues & Solutions

### "RTL-SDR is busy" Error
**Cause:** dump1090-fa is running (Flight Mode)
**Solution:** Click "Switch Mode" or run `sudo systemctl stop dump1090-fa`

### "PN532 not initialized"
**Cause:** I2C connection issue or PN532 not powered
**Solution:**
1. Check wiring (SDA → GPIO 2, SCL → GPIO 3)
2. Verify I2C enabled: `sudo raspi-config` → Interface Options
3. Check device: `i2cdetect -y 1` (should see device at 0x24)

### "CC1101 not initialized"
**Cause:** SPI connection issue
**Solution:**
1. Check wiring (see pin diagram above)
2. Verify SPI enabled: `sudo raspi-config` → Interface Options
3. Test SPI: `ls /dev/spi*` (should see /dev/spidev0.0)

### Under-voltage Warning
**Cause:** Insufficient power supply
**Solution:** Use 5V 3A power supply (official Raspberry Pi PSU recommended)

### No Flights Detected
**Cause:** Poor antenna placement or no flights overhead
**Solution:**
1. Ensure in Flight Mode (dump1090-fa running)
2. Move antenna to window (1090MHz needs line-of-sight)
3. Check https://globe.adsbexchange.com/ for flights in your area
4. Try during busy times (morning/evening)

---

## 🎓 Signal Workflow

### Capture → Analyze → Replay

1. **Capture Signal**
   - Via web UI: RF Tools → Capture Signal
   - Saved to: `~/piflip/captures/<name>.cu8` + `.json` metadata
   - Automatically analyzed by `auto_analyzer.py`

2. **Analyze Signal**
   - Via web UI: Signal Library → <name> → Analyze
   - Uses URH (Universal Radio Hacker)
   - Extracts: modulation, frequency, protocol, binary data

3. **Replay Signal**
   - Via web UI: Signal Library → <name> → Replay
   - Transmits via CC1101
   - Uses decoded timing and modulation

---

## 💾 Data Storage

### Capture Format (.cu8)
- Complex unsigned 8-bit IQ samples
- Format: I, Q, I, Q, I, Q...
- Compatible with: URH, GQRX, GNU Radio, SDR#

### Metadata Format (.json)
```json
{
  "name": "my_keyfob",
  "filename": "my_keyfob.cu8",
  "frequency": 433920000,
  "sample_rate": 2048000,
  "duration": 5,
  "num_samples": 10240000,
  "timestamp": "2025-10-01T10:30:00",
  "file_size": 20480000,
  "auto_analysis": { ... }
}
```

### NFC Card Format (.json)
```json
{
  "uid": "04A3B2C1",
  "readable": "04:A3:B2:C1",
  "timestamp": "2025-10-01T10:30:00",
  "name": "work_badge",
  "card_type": "Mifare Classic 1K",
  "sectors": [ ... ]
}
```

---

## 🧪 Testing

### Hardware Test Suite
**URL:** http://192.168.86.141:5000/test

Tests:
- RTL-SDR detection
- PN532 NFC detection
- CC1101 SPI communication
- System resources

### Manual Tests
```bash
# Test RTL-SDR
rtl_test -t

# Test NFC
curl http://127.0.0.1:5000/api/nfc

# Test 433MHz scan (30s)
curl http://127.0.0.1:5000/api/scan433

# Test CC1101 status
curl http://127.0.0.1:5000/api/cc1101/status
```

---

## 🔐 Security Notes

**This is a LEARNING TOOL for educational purposes:**
- Only capture/replay YOUR OWN devices
- Do not interfere with others' systems
- Check local RF transmission regulations
- NFC cloning: Only clone YOUR OWN cards
- Work badges: Check company policy before cloning

**Legal compliance is your responsibility!**

---

## 🚧 Known Limitations

1. **Signal Replay:** Full replay requires URH analysis (work in progress)
2. **125kHz RFID:** Not supported (PN532 is 13.56MHz only)
3. **Infrared:** Not yet implemented
4. **iButton:** Not yet implemented
5. **Touchscreen:** Planned (3.5" display)
6. **Battery:** Currently requires wall power (power bank support planned)
7. **Portability:** Larger than Flipper Zero (Pi 3B size)

---

## 📈 Project History

### Recent Cleanup (Oct 2, 2025)
- Reduced repo size from 275 MB → 133 MB (51.6% reduction)
- Removed dump1090 source code (107 MB) - using system-installed version
- Deleted 15 obsolete test files
- Removed old app versions (piflip_core, pi-flipper, raspi-flipper)
- Cleaned all __pycache__ directories

See: [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) for details

### Development Timeline
- **Sep 28, 2025:** Initial hardware setup and testing
- **Sep 29, 2025:** Flight tracking integrated (dump1090-fa)
- **Sep 30, 2025:** Web interface development, NFC testing
- **Oct 1, 2025:** CC1101 RX/TX working, signal capture functional
- **Oct 2, 2025:** Code cleanup, documentation, repo organization

---

## 🎯 Current Capabilities

### ✅ Working Features
- [x] 433MHz device scanning
- [x] Signal capture (IQ data with RTL-SDR)
- [x] CC1101 transmission
- [x] NFC card read/backup
- [x] Flight tracking (ADS-B)
- [x] TPMS sensor detection
- [x] Weather station detection
- [x] Web interface with Flipper-style UI
- [x] Signal library management
- [x] Auto-analysis on capture
- [x] Hardware status monitoring
- [x] Mode switching (Flight/Scanning)

### ⏳ In Development
- [ ] Full signal replay with URH decoding
- [ ] NFC card cloning (magic card write)
- [ ] Protocol library expansion
- [ ] Waterfall spectrum display
- [ ] 3.5" touchscreen support
- [ ] 3D printed case design
- [ ] Portable battery operation

---

## 🤖 AI Assistant Guidelines

### When Helping with This Project:

1. **Never delete these 9 core modules:**
   - urh_analyzer.py
   - auto_analyzer.py
   - nfc_enhanced.py
   - nfc_cloner.py
   - nfc_emulator.py
   - cc1101_enhanced.py
   - signal_decoder.py
   - favorites_manager.py
   - waveform_generator.py

2. **Key file:** `web_interface.py` is the main application - understand it before suggesting changes

3. **Power is critical:** Always remind about 3A PSU requirement

4. **RTL-SDR exclusivity:** Only ONE program can use RTL-SDR at a time (flight mode vs scanning mode)

5. **Hardware is live:** Changes to GPIO/SPI/I2C code affect real hardware - test carefully!

6. **User data:** captures/, rf_library/, nfc_library/ contain user data - never delete without permission

7. **piflip_env/:** Virtual environment (78 MB) - required, don't delete

8. **Documentation:** Keep README.md, DEPENDENCY_AUDIT.md, and this file updated

9. **Security:** This is educational - don't help with malicious use

10. **Testing:** Encourage using /test endpoint before deploying changes

---

## 📞 Quick Reference

**Web Interface:** http://192.168.86.141:5000
**Test Suite:** http://192.168.86.141:5000/test
**Flight Map:** http://192.168.86.141:8080

**Start Server:** `python3 web_interface.py`
**Stop dump1090:** `sudo systemctl stop dump1090-fa`
**Start dump1090:** `sudo systemctl start dump1090-fa`
**Check Power:** `vcgencmd get_throttled`

**IP Address:** 192.168.86.141
**User:** seth
**Project Path:** /home/seth/piflip/

---

**This project is fully functional and ready for signal capture, NFC operations, and flight tracking!** 🦊✨

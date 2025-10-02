# PiFlip Nano - Development Roadmap
## Vision: Flipper Zero Alternative on Raspberry Pi

---

## Current Status ✅

### Hardware
- ✅ Raspberry Pi 3B
- ✅ PN532 NFC Module (I2C) - Fully working
- ✅ RTL-SDR Blog V4 (USB) - RX only, fully working
- ⏳ CC1101 Module (SPI) - Awaiting wiring (arrives tomorrow)
- 🔮 Future: Small LCD display (3.5" or 2.8" SPI display recommended)

### Software Features Working
- ✅ NFC read/write/clone/backup
- ✅ 433MHz scanning (passive receive)
- ✅ TPMS tire pressure monitoring
- ✅ Weather station decoding
- ✅ Flight tracking (ADS-B 1090MHz)
- ✅ Web interface with mode switching

---

## Phase 1: Signal Capture & Replay (Next 2 weeks)
**Goal:** Capture, analyze, and retransmit RF signals

### 1.1 Signal Recording (RTL-SDR)
- [ ] Raw IQ capture to file (rtl_sdr)
- [ ] Automatic frequency detection
- [ ] Signal visualization preview
- [ ] Metadata storage (frequency, sample rate, timestamp, name)
- [ ] File management UI (list/rename/delete captures)

**Implementation:**
```python
# Capture raw IQ data
rtl_sdr -f 433920000 -s 2048000 -n 4096000 capture_name.cu8

# Store metadata
{
  "name": "garage_door_remote",
  "frequency": 433920000,
  "sample_rate": 2048000,
  "timestamp": "2025-09-30T22:45:00",
  "modulation": "OOK/ASK",
  "file": "garage_door_remote.cu8"
}
```

### 1.2 URH Integration
- [ ] Install Universal Radio Hacker
- [ ] API wrapper for URH CLI
- [ ] Auto-decode captured signals
- [ ] Export to URH format
- [ ] Import URH decoded signals

**Features:**
- Automatic demodulation
- Protocol analysis
- Bit sequence extraction
- Pattern recognition

### 1.3 Signal Replay (CC1101)
- [ ] Convert IQ data to CC1101 format
- [ ] Frequency/modulation configuration
- [ ] Raw transmission mode
- [ ] Protocol-aware transmission (rolling code detection)
- [ ] Jamming detection/warnings

**CC1101 Functions:**
```python
def transmit_ook_signal(frequency, data, bitrate):
    # Configure CC1101 for OOK transmission
    # Send raw bit pattern
    pass

def replay_capture(capture_file):
    # Load IQ data
    # Decode with URH
    # Retransmit with CC1101
    pass
```

### 1.4 Web Interface Updates
- [ ] "Capture" mode with real-time preview
- [ ] Signal library browser
- [ ] One-click replay
- [ ] Frequency analyzer display
- [ ] Signal strength meter

---

## Phase 2: Advanced RF Features (3-4 weeks)

### 2.1 Sub-GHz Protocol Library
Pre-programmed transmitters for common devices:
- [ ] Fixed code garage doors (12-bit, 24-bit)
- [ ] Simple 433MHz switches
- [ ] Wireless doorbells
- [ ] Weather station emulation
- [ ] Custom protocol builder

### 2.2 Brute Force / Fuzzing
- [ ] Fixed code brute force (with warnings)
- [ ] Frequency sweep scanner
- [ ] Protocol fuzzer for research
- [ ] Rolling code detector (view only, no replay)

### 2.3 Signal Analysis Tools
- [ ] Waterfall display (real-time spectrum)
- [ ] FFT viewer
- [ ] Persistence mode (see intermittent signals)
- [ ] Signal comparison (diff two captures)
- [ ] Automatic modulation detection

---

## Phase 3: Enhanced NFC (4-5 weeks)

### 3.1 Advanced Card Operations
- [ ] MIFARE Classic full dump (all sectors)
- [ ] MIFARE DESFire support
- [ ] NTAG21x read/write
- [ ] Card emulation mode (if PN532 supports)
- [ ] Encrypted sector handling

### 3.2 NFC Tools
- [ ] Key dictionary for auth attempts
- [ ] Nested attack implementation
- [ ] Dark side attack (if applicable)
- [ ] Card type auto-detection
- [ ] NDEF message builder

---

## Phase 4: Display Integration (5-6 weeks)

### 4.1 Hardware Options
**Recommended displays:**
- Waveshare 3.5" SPI touchscreen (~$20)
- Adafruit 2.8" PiTFT Plus (~$35)
- Hyperpixel 4.0" Square (~$45)

### 4.2 Local UI Features
- [ ] Main menu (like Flipper Zero)
- [ ] Signal strength bars
- [ ] Frequency spectrum display
- [ ] NFC scan results
- [ ] Status indicators (battery, RF mode, etc.)
- [ ] Navigation (joystick or touchscreen)

### 4.3 UI Framework
```
Options:
1. pygame - Simple, lightweight
2. kivy - Touch-friendly
3. Qt - Professional but heavier
4. Custom framebuffer - Fastest

Recommendation: pygame for speed + simplicity
```

---

## Phase 5: Hardware Expansion (Ongoing)

### 5.1 Additional Modules to Consider
- [ ] **GPS Module** - Location tagging for wardriving
- [ ] **BLE Module** - Bluetooth LE scanning/spoofing
- [ ] **IR Transceiver** - TV remote cloning
- [ ] **125kHz RFID** - Low-frequency card reading
- [ ] **2.4GHz Module** (nRF24L01+) - Wireless keyboards/mice
- [ ] **WiFi Deauther** (ESP8266/ESP32 as co-processor)

### 5.2 Power Management
- [ ] Battery percentage display
- [ ] Low-power mode
- [ ] Auto-shutdown timer
- [ ] USB-C PD support for portable power
- [ ] Wake-on-button

**Recommended batteries:**
- Anker PowerCore 10000 PD
- RAVPower 20000mAh
- Custom 18650 pack (3S or 4S)

### 5.3 Portable Case Design
**Considerations:**
- Compact USB hub (Anker 4-port slim model)
- Internal antenna routing
- Display mounting
- Button/joystick placement
- Heat dissipation
- SD card access
- Charging port

**3D Printable case features:**
- Modular design (swap modules)
- Antenna compartment
- Battery bay
- Raspberry Pi mounting
- Display bezel
- Belt clip / lanyard loop

---

## Phase 6: Software Polish (7-8 weeks)

### 6.1 Database & Storage
- [ ] SQLite database for captures
- [ ] Tag/categorize signals
- [ ] Notes field for each capture
- [ ] Export/import signal packs
- [ ] Cloud backup integration (optional)

### 6.2 Workflow Improvements
- [ ] Keyboard shortcuts
- [ ] Batch operations
- [ ] Signal presets
- [ ] Favorite frequencies
- [ ] Quick access menu

### 6.3 Documentation
- [ ] User manual
- [ ] Protocol guides
- [ ] Legal warnings
- [ ] Tutorial videos
- [ ] API documentation

---

## Technical Specifications

### Signal Capture Workflow
```
┌─────────────┐
│  RTL-SDR    │ ──► Capture IQ data (.cu8)
└─────────────┘
       │
       ▼
┌─────────────┐
│     URH     │ ──► Decode to bits/protocol
└─────────────┘
       │
       ▼
┌─────────────┐
│   CC1101    │ ──► Retransmit signal
└─────────────┘
```

### File Structure
```
~/piflip/
├── captures/          # Raw IQ recordings
│   ├── garage_door.cu8
│   ├── car_remote.cu8
│   └── doorbell.cu8
├── decoded/           # URH analysis results
│   ├── garage_door.complex
│   └── garage_door.json
├── protocols/         # Pre-built protocols
│   ├── linear_garage.py
│   └── ac114.py
└── backups/          # NFC card backups
    └── blue_card.json
```

### Frequency Coverage
- **RTL-SDR:** 24 MHz - 1766 MHz (RX only)
- **CC1101:** 300-348 MHz, 387-464 MHz, 779-928 MHz (TX/RX)
- **Combined coverage:** Most common ISM bands

### Performance Targets
- Signal capture: < 2 seconds
- URH decode: < 5 seconds
- CC1101 replay: < 1 second
- Web interface response: < 200ms
- Display refresh: 30 fps minimum

---

## Security & Ethics

### Legal Warnings
- ⚠️ Only capture/replay signals you own
- ⚠️ Jamming is illegal in most countries
- ⚠️ Car key rolling codes should NOT be replayed
- ⚠️ NFC cloning restricted to your own cards
- ⚠️ No credit card skimming capabilities

### Safety Features
- [ ] Rolling code detection (block replay)
- [ ] Frequency blacklist (emergency frequencies)
- [ ] TX power limits
- [ ] Usage logging (for research)
- [ ] Confirmation prompts for TX

---

## Development Priority

### Immediate (This Week)
1. ✅ Web interface improvements - DONE
2. ✅ Mode switching - DONE
3. 🔨 Signal capture implementation - IN PROGRESS
4. 🔨 File management system - IN PROGRESS

### Week 2 (CC1101 Integration)
1. Wire CC1101 to Pi
2. Test basic TX/RX
3. OOK transmission
4. Simple replay function

### Week 3-4 (URH & Analysis)
1. Install URH
2. Create decode pipeline
3. Build signal library UI
4. Protocol database

### Month 2 (Display)
1. Order display
2. pygame UI framework
3. Menu system
4. Real-time visualization

### Month 3 (Polish)
1. Case design
2. Power optimization
3. Documentation
4. Beta testing

---

## Hardware Shopping List

### Essential
- [x] Raspberry Pi 3B - $35
- [x] PN532 NFC module - $8
- [x] RTL-SDR Blog V4 - $35
- [x] CC1101 module - $3
- [ ] MicroSD card (32GB+) - $10
- [ ] USB hub (compact) - $15

### Recommended
- [ ] 3.5" touchscreen - $20-35
- [ ] Portable battery pack - $30-50
- [ ] Antenna kit (433/915MHz) - $20
- [ ] Jumper wire kit - $10
- [ ] 3D printer filament - $20

### Optional
- [ ] GPS module - $15
- [ ] IR transceiver - $5
- [ ] BLE module - $10
- [ ] 125kHz RFID - $15

**Total Essential:** ~$106
**Total with Display:** ~$156
**Full build with extras:** ~$250

---

## Comparison to Flipper Zero

| Feature | Flipper Zero | PiFlip Nano |
|---------|-------------|-------------|
| Price | $169+ | ~$150-250 |
| NFC | ✅ | ✅ |
| Sub-GHz RX | ✅ (limited) | ✅ (wider range) |
| Sub-GHz TX | ✅ | ✅ (CC1101) |
| Display | Built-in | Add-on |
| Battery | Built-in | External |
| WiFi | Via module | Built-in Pi |
| IR | ✅ | Add-on |
| 125kHz RFID | ✅ | Add-on |
| CPU Power | Limited | Much stronger |
| Storage | 256KB | Unlimited (SD) |
| Upgradeable | Firmware only | Full hardware |
| Python scripting | ❌ | ✅ |
| Web interface | ❌ | ✅ |
| URH integration | ❌ | ✅ |

**Advantages over Flipper:**
- More powerful CPU (analysis on device)
- Better web interface
- Larger storage
- Easier to modify/expand
- Full Linux tooling
- Better RF analysis (URH)

**Flipper advantages:**
- More portable
- Better battery life
- Integrated design
- No assembly required

---

## Next Steps

**Tomorrow (CC1101 arrives):**
1. Wire CC1101 to Pi GPIO
2. Test basic communication
3. Implement first transmit function
4. Test with simple 433MHz device

**This week:**
1. Build signal capture system
2. Create file browser UI
3. Start URH integration
4. Test capture → replay workflow

**Next week:**
1. Expand protocol library
2. Add waterfall display
3. Improve web UI aesthetics
4. Start shopping for display

---

Ready to build the ultimate RF hacking tool! 🚀

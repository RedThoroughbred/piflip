# PiFlip Development Roadmap 🗺️

**Current Version:** v2.0 (HackRF Upgrade Complete)
**Last Updated:** October 3, 2025

---

## ✅ **COMPLETED FEATURES**

### **Core RF (v1.0)**
- [x] Sub-GHz RX/TX (CC1101)
- [x] 433MHz scanning
- [x] Signal capture & replay
- [x] TPMS sensors
- [x] Weather stations
- [x] RTL-SDR integration
- [x] Signal library management

### **NFC/RFID (v1.0)**
- [x] 13.56MHz NFC read/write
- [x] MIFARE Classic support
- [x] Card backup & cloning
- [x] Magic card write
- [x] NFC library management

### **HackRF Upgrade (v2.0 - October 3, 2025)** 🎉
- [x] Bluetooth BLE scanning
- [x] Bluetooth Classic scanning
- [x] Device enumeration (34 devices found!)
- [x] WiFi hotspot mode
- [x] iPad/iPhone remote access
- [x] Enhanced spectrum analyzer
- [x] PortaPack-style waterfall
- [x] Real NFC emulation (experimental)

### **Web Interface (v2.0)**
- [x] Flipper-style UI
- [x] Mobile-optimized
- [x] 80+ API endpoints
- [x] Real-time hardware status
- [x] Dashboard & stats

---

## 🎯 **PRIORITY 1: Quick Wins (1-7 days)**

### **1. Bluetooth Save Feature** ⚡
**Issue:** You found 34 devices but can't save them from scan results

**Fix Needed:**
- Add "Save Device" button to scan results
- Allow naming devices when saving
- Store MAC, name, type, RSSI
- Show saved devices in library

**Difficulty:** Easy (2 hours)
**Impact:** High - Makes Bluetooth actually useful!

---

### **2. IR Support** 📡
**What:** Add infrared remote control

**Hardware Needed:**
- IR LED ($1)
- IR receiver ($2)
- 2 resistors ($0.10)

**Software:**
- Install LIRC (Linux Infrared Remote Control)
- Create IR module for PiFlip
- Add IR menu to web UI

**Use Cases:**
- TV/AC remote control
- Universal remote
- Record & replay IR signals

**Difficulty:** Medium (1 day)
**Cost:** ~$3
**Impact:** High - Matches Flipper capability

**GPIO Connections:**
```
IR LED → GPIO 17 (TX)
IR Receiver → GPIO 18 (RX)
```

---

### **3. 125kHz RFID Support** 🏢
**What:** Low-frequency RFID (building access cards, some hotel keys)

**Hardware Needed:**
- USB RFID reader ($10-20)
- Example: ID-12LA or similar

**Software:**
- Add USB RFID module
- Interface via serial/USB
- Add 125kHz menu

**Use Cases:**
- Building access cards
- Employee badges (older systems)
- Some hotel room keys
- Animal ID tags

**Difficulty:** Easy (4 hours)
**Cost:** $10-20
**Impact:** Medium - Some buildings still use 125kHz

---

### **4. Better RTL-SDR Integration** 📻
**Issue:** Need USB extension for better reception

**Improvements:**
- Auto-detect RTL-SDR on boot
- Better error messages
- Mode switching UI improvements
- Add more frequency presets

**Hardware:**
- USB extension cable ($5)
- Better antenna ($10-20)

**Difficulty:** Easy (3 hours)
**Impact:** Medium - Better signal quality

---

### **5. Signal Replay Improvements** 🔄
**Current:** Basic transmission works
**Needed:** Better replay with timing

**Improvements:**
- URH integration for decoding
- Precise timing replay
- Multiple replay modes
- Power adjustment

**Difficulty:** Medium (1 day)
**Impact:** High - More reliable signal replay

---

## 🚀 **PRIORITY 2: Major Features (1-4 weeks)**

### **6. iButton / Dallas Key Support** 🔑
**What:** 1-Wire keys (building access, some safes)

**Hardware:**
- DS9490R USB adapter ($20)
- Or build DIY with DS2480B

**Features:**
- Read iButton keys
- Write to RW1990 blanks
- Emulate keys (experimental)

**Difficulty:** Medium (2 days)
**Cost:** $20
**Impact:** Medium - Less common but useful

---

### **7. 2.4GHz Analysis (Mice/Keyboards)** 🖱️
**What:** Analyze wireless mice, keyboards, game controllers

**Hardware:**
- NRF24L01+ module ($2)
- SPI connection to GPIO

**Features:**
- Scan for 2.4GHz devices
- Sniff mouse/keyboard packets
- Replay attacks (educational!)

**Use Cases:**
- Wireless device analysis
- Security testing
- Understand proprietary protocols

**Difficulty:** Medium-Hard (3-5 days)
**Cost:** $2
**Impact:** Medium - Cool for security research

---

### **8. Touchscreen Display** 📱
**What:** Portable display instead of web interface

**Hardware:**
- 3.5" TFT touchscreen ($25-35)
- SPI/GPIO connection

**Software:**
- Framebuffer UI
- Touch input handling
- PortaPack-style interface

**Benefits:**
- Portable (no need for phone)
- Direct interaction
- Better for field use

**Difficulty:** Hard (1-2 weeks)
**Cost:** $30
**Impact:** High - True portability!

---

### **9. Advanced WiFi Features** 📶
**Current:** Hotspot + scanning
**Add:** Packet capture, deauth detection, analysis

**Features:**
- Monitor mode
- Packet capture (pcap)
- Deauth detection
- WPA handshake capture
- Network analysis

**Requirements:**
- May need external WiFi adapter for monitor mode
- Some features require aircrack-ng suite

**Difficulty:** Medium (3-5 days)
**Impact:** Medium - Security research

---

### **10. GPS Module** 🗺️
**What:** Location tagging for captures

**Hardware:**
- USB GPS receiver ($15-25)
- Or GPIO-connected GPS

**Features:**
- Geotag RF captures
- Wardrive mapping
- Flight tracking with location
- WiFi AP mapping

**Use Cases:**
- TPMS location mapping
- Signal strength mapping
- Wardriving
- Flight tracking with location

**Difficulty:** Medium (2 days)
**Cost:** $20
**Impact:** Medium - Cool for mapping

---

## 🏗️ **PRIORITY 3: Advanced Projects (1-3 months)**

### **11. ESP32 Co-Processor** 🔥
**What:** Add ESP32 for WiFi/BLE attacks

**Hardware:**
- ESP32 DevKit ($8)
- USB or UART connection

**Features:**
- WiFi deauth attacks
- BLE 5.0 support
- Bluetooth packet injection
- ESP-NOW protocol
- Better WiFi penetration testing

**Why:**
- ESP32 has better WiFi attack capabilities
- BLE 5.0 (vs Pi's BLE 4.1)
- Dedicated processor for WiFi/BT

**Difficulty:** Hard (1-2 weeks)
**Cost:** $8
**Impact:** High - Professional WiFi pentesting

---

### **12. Ubertooth One Integration** 📡
**What:** Professional Bluetooth analysis

**Hardware:**
- Ubertooth One ($120)
- USB connection

**Features:**
- Bluetooth packet sniffing
- Packet injection
- Following connections
- Protocol analysis
- BLE security testing

**Why:**
- Can't do packet injection with built-in BT
- Professional Bluetooth pentesting
- Analyze Bluetooth traffic

**Difficulty:** Medium (3-5 days)
**Cost:** $120
**Impact:** High for BT security research

---

### **13. HackRF One Integration** 📻
**What:** Full-range SDR TX/RX

**Hardware:**
- HackRF One ($300)
- USB connection

**Features:**
- 1MHz - 6GHz RX/TX
- Replace RTL-SDR
- Transmit on ANY frequency
- Replay any signal
- Full SDR capabilities

**Why:**
- RTL-SDR is RX-only
- HackRF can TX on wideband
- Professional SDR platform

**Difficulty:** Medium (5-7 days)
**Cost:** $300
**Impact:** Massive - Full SDR capabilities

---

### **14. 3D Printed Case** 📦
**What:** Professional enclosure

**Features:**
- Raspberry Pi compartment
- Antenna mounts
- Screen mount (if adding touchscreen)
- Battery compartment
- Port access
- Cooling vents

**Design:**
- Flipper Zero inspired
- Portable
- Protective

**Difficulty:** Medium (design + print)
**Cost:** $10-20 filament
**Impact:** High - Professional look!

---

### **15. Mobile App** 📱
**What:** Native iOS/Android app

**Current:** Web interface works great
**Benefit:** Native app feels more polished

**Features:**
- Connect via WiFi/BLE
- Native UI
- Push notifications
- Offline capture viewing

**Difficulty:** Hard (2-4 weeks)
**Cost:** Free (development time)
**Impact:** Medium - Web works fine

---

## 🔧 **QUICK FIXES & IMPROVEMENTS**

### **Bluetooth Enhancements**
- [ ] Add "Save Device" button to scan results ⚡ **URGENT**
- [ ] Device nickname support
- [ ] RSSI history graphs
- [ ] Proximity alerts
- [ ] Device tracking over time

### **WiFi Enhancements**
- [ ] Auto-enable hotspot when no WiFi
- [ ] Password change for hotspot
- [ ] Custom SSID
- [ ] WiFi QR code generator
- [ ] Connection history

### **UI Improvements**
- [ ] Dark/light theme toggle
- [ ] Custom color schemes
- [ ] Bigger buttons for touch screens
- [ ] Gesture controls
- [ ] Keyboard shortcuts

### **Signal Library**
- [ ] Tags/categories
- [ ] Search functionality
- [ ] Bulk operations
- [ ] Export/import
- [ ] Cloud backup

### **Documentation**
- [ ] Video tutorials
- [ ] Step-by-step guides
- [ ] Hardware assembly guide
- [ ] Troubleshooting wiki
- [ ] Community contributions

---

## 📊 **SUGGESTED ORDER OF IMPLEMENTATION**

### **Week 1:**
1. ✅ Bluetooth save feature (2 hours) **DO THIS FIRST!**
2. ✅ Better error messages (1 hour)
3. ✅ UI tweaks (2 hours)

### **Week 2:**
4. IR support ($3, 1 day)
5. USB extension + antenna ($15)

### **Week 3:**
6. 125kHz RFID reader ($20, 4 hours)
7. Signal replay improvements (1 day)

### **Month 2:**
8. iButton support ($20, 2 days)
9. NRF24L01+ ($2, 3 days)
10. GPS module ($20, 2 days)

### **Month 3:**
11. Touchscreen ($30, 1-2 weeks)
12. 3D printed case ($15, design + print)

### **Future:**
13. ESP32 co-processor ($8)
14. Ubertooth One ($120) - if serious about BT
15. HackRF One ($300) - ultimate upgrade

---

## 💰 **BUDGET ROADMAP**

### **Phase 1: Quick Wins ($0-50)**
- Bluetooth save feature (FREE - software only)
- IR LED/receiver ($3)
- USB extension ($5)
- Better antenna ($15)
- 125kHz reader ($20)

**Total: $43**

### **Phase 2: Major Features ($50-150)**
- iButton reader ($20)
- NRF24L01+ ($2)
- GPS module ($20)
- Touchscreen ($30)
- 3D case ($15)
- ESP32 ($8)

**Total: $95**

### **Phase 3: Pro Upgrades ($150+)**
- Ubertooth One ($120)
- HackRF One ($300)
- PortaPack for HackRF ($450)

**Total: $870** (becomes ultimate SDR platform!)

---

## 🎯 **WHAT TO DO RIGHT NOW**

### **Immediate (This Week):**

1. **Fix Bluetooth Save** (Tonight - 2 hours)
   - Add save button to scan results
   - Test saving 34 devices you found!

2. **Get USB Extension** (Tomorrow - $5)
   - Amazon/local electronics store
   - Improves RTL-SDR reception

3. **Order IR Parts** (This week - $3)
   - IR LED + receiver
   - Adds remote control capability

4. **Test Spectrum Analyzer** (Once USB extension arrives)
   - Plug in RTL-SDR with extension
   - Run spectrum scans
   - Test waterfall mode

### **This Month:**

5. **Add 125kHz RFID** ($20)
   - Matches Flipper capability
   - Useful for building access

6. **Create 3D Case Design**
   - Start planning enclosure
   - Measure components

---

## 📈 **FEATURES BY DIFFICULTY**

### **Easy (0-1 day):**
- Bluetooth save function
- IR support
- 125kHz USB reader
- GPS module
- Better error messages

### **Medium (1-5 days):**
- iButton support
- NRF24L01+
- Signal replay improvements
- WiFi advanced features
- Touchscreen integration

### **Hard (1-4 weeks):**
- ESP32 integration
- Mobile app
- Advanced signal analysis
- Full HackRF integration

---

## 🏆 **ULTIMATE GOAL**

**PiFlip Super:**
- ✅ All Flipper Zero features
- ✅ Bluetooth BLE/Classic
- ✅ WiFi hotspot
- ✅ Wideband spectrum (24MHz-6GHz)
- ✅ Full TX/RX capabilities
- ✅ Touchscreen
- ✅ Portable (battery)
- ✅ 3D printed case
- ✅ Professional SDR platform

**Estimated cost:** ~$600 (vs $169 Flipper + $300 HackRF = $469, but with way more features!)

---

## 🦊 **NEXT STEPS**

**Tonight:**
1. I can help you add the Bluetooth save feature right now!

**This Week:**
2. Order USB extension + IR parts (~$8)
3. Test spectrum analyzer when extension arrives

**This Month:**
4. Add 125kHz reader
5. Design/print case

**Want me to add the Bluetooth save button to the UI right now?** It'll take 10 minutes! 🚀

---

**Questions? Suggestions? Let me know what you want to tackle first!**

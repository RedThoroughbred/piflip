# Flipper Zero vs PiFlip - Complete Feature Comparison

**Date:** October 3, 2025
**PiFlip Status:** Fully Functional + HackRF Upgrade Complete

---

## 📊 **Quick Stats**

| Spec | Flipper Zero | PiFlip |
|------|--------------|---------|
| **Price** | $169 | ~$120 |
| **CPU** | STM32 (ARM Cortex-M4) | BCM2837 (ARM Cortex-A53 4-core) |
| **RAM** | 256 KB | 1 GB |
| **Storage** | microSD | microSD (32GB+) |
| **Screen** | 1.4" LCD (128x64) | Web interface (any size!) |
| **Battery** | 2000 mAh built-in | External USB power bank |
| **GPIO** | Yes (5 pins) | Yes (40 pins!) |
| **Portability** | Excellent (pocket-sized) | Good (requires power bank) |
| **Expandability** | Limited | Excellent (USB + GPIO) |

---

## 🎯 **Feature-by-Feature Comparison**

### **1. Sub-GHz RF (300-928 MHz)**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **RX (Receive)** | ✅ CC1101 | ✅ CC1101 + RTL-SDR | PiFlip has 2 receivers! |
| **TX (Transmit)** | ✅ CC1101 | ✅ CC1101 | Same chip |
| **Frequency Range** | 300-928 MHz | 300-928 MHz (CC1101)<br>24MHz-1.7GHz (RTL-SDR RX) | RTL-SDR adds wideband RX |
| **Signal Capture** | ✅ | ✅ | Both can capture |
| **Signal Replay** | ✅ | ✅ | Both can replay |
| **Protocol Decoder** | ✅ Built-in | ✅ rtl_433 | PiFlip has 200+ protocols |
| **RAW Recording** | ✅ | ✅ IQ samples | PiFlip saves complex IQ |
| **433MHz Scanning** | ✅ | ✅ | Both work great |
| **315MHz (US)** | ✅ | ✅ | Both supported |
| **868MHz (EU)** | ✅ | ✅ | Both supported |
| **915MHz (ISM)** | ✅ | ✅ | Both supported |
| **ASK/OOK** | ✅ | ✅ | Common modulation |
| **FSK** | ✅ | ✅ | Both support |
| **GFSK** | ✅ | ⚠️ | Flipper better |
| **Custom Protocols** | ✅ | ✅ URH integration | PiFlip uses URH |
| **Signal Library** | ✅ | ✅ | Both have libraries |
| **Favorites** | ✅ | ✅ | Both support |

**Winner:** 🤝 **TIE** - Both excellent, PiFlip has wideband RX advantage

---

### **2. RFID (125 kHz LF)**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **125kHz Read** | ✅ | ❌ | Flipper only |
| **EM4100/EM4102** | ✅ | ❌ | Not supported on PiFlip |
| **HID Prox** | ✅ | ❌ | Flipper has dedicated LF coil |
| **Indala** | ✅ | ❌ | |
| **T5577 Write** | ✅ | ❌ | |
| **125kHz Emulation** | ✅ | ❌ | Flipper advantage |

**Winner:** ✅ **Flipper Zero** - Has dedicated 125kHz hardware

**PiFlip Workaround:** Add external 125kHz RFID reader (~$10) via USB

---

### **3. NFC/RFID (13.56 MHz HF)**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **13.56MHz Read** | ✅ | ✅ PN532 | Both have NFC |
| **MIFARE Classic** | ✅ | ✅ | Both read/write |
| **MIFARE Ultralight** | ✅ | ✅ | Both supported |
| **MIFARE DESFire** | ⚠️ Limited | ⚠️ Limited | Both have limits |
| **NTAG** | ✅ | ✅ | Both supported |
| **ISO14443A** | ✅ | ✅ | Standard NFC |
| **ISO15693** | ✅ | ✅ | Both support |
| **FeliCa** | ✅ | ✅ | Both capable |
| **Card Reading** | ✅ | ✅ | Excellent on both |
| **UID Backup** | ✅ | ✅ | Both can save UIDs |
| **Full Dump** | ✅ | ✅ | Both read all sectors |
| **Magic Card Write** | ✅ | ✅ | Both clone to magic cards |
| **Card Emulation** | ⚠️ Limited | ✅ Experimental | PiFlip has PN532 target mode |
| **NFC Library** | ✅ | ✅ | Both manage cards |
| **Work Badge Clone** | ✅ | ✅ | Both work (use magic cards) |

**Winner:** 🤝 **TIE** - Both excellent for NFC

---

### **4. Infrared (IR)**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **IR Transmit** | ✅ | ❌ Not yet | Flipper has IR LED |
| **IR Receive** | ✅ | ❌ Not yet | Flipper has IR receiver |
| **TV Remote** | ✅ | ❌ | Flipper built-in |
| **AC Remote** | ✅ | ❌ | |
| **Universal Remote** | ✅ | ❌ | Large IR database |
| **IR Library** | ✅ | ❌ | |

**Winner:** ✅ **Flipper Zero** - Built-in IR

**PiFlip Upgrade:** Add IR LED + receiver via GPIO (~$5)
- LIRC software available for Raspberry Pi
- Can add full IR support easily!

---

### **5. Bluetooth**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **Bluetooth LE** | ❌ Not yet | ✅ **NEW!** | PiFlip has BT 4.1 built-in! |
| **BLE Scanning** | ❌ | ✅ | **PiFlip exclusive!** |
| **BLE Devices Found** | ❌ | ✅ (You found 34!) | **Works great!** |
| **Classic Bluetooth** | ❌ | ✅ | **PiFlip exclusive!** |
| **Device Enumeration** | ❌ | ✅ | Shows MAC, name, RSSI |
| **Service Discovery** | ❌ | ✅ | BLE characteristics |
| **RSSI Monitoring** | ❌ | ✅ | Track signal strength |
| **Bluetooth Library** | ❌ | ✅ | Save devices |
| **Packet Sniffing** | ❌ | ⚠️ Requires Ubertooth | Advanced feature |

**Winner:** ✅ **PiFlip** - Built-in Bluetooth, Flipper doesn't have this!

**This is a HUGE PiFlip advantage!** 🎉

---

### **6. WiFi**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **WiFi Devboard** | ⚠️ Add-on ($30) | ✅ **Built-in!** | PiFlip wins |
| **WiFi Scanning** | ⚠️ With devboard | ✅ | **PiFlip built-in!** |
| **Hotspot Mode** | ❌ | ✅ **NEW!** | **PiFlip exclusive!** |
| **Access Point** | ❌ | ✅ PiFlip-RF | Create your own WiFi! |
| **iPad/Phone Access** | ❌ | ✅ | **Control from anywhere!** |
| **Network Scanning** | ⚠️ | ✅ | PiFlip better |
| **Deauth** | ⚠️ With devboard | ⚠️ Requires setup | Both need work |
| **Packet Capture** | ⚠️ | ⚠️ | Both require setup |

**Winner:** ✅ **PiFlip** - Built-in WiFi + hotspot mode!

**Another massive PiFlip advantage!** 📶

---

### **7. GPIO & Hardware**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **GPIO Pins** | 5 pins | 40 pins | **PiFlip destroys here!** |
| **SPI** | ✅ | ✅ | Both have |
| **I2C** | ✅ | ✅ | Both have |
| **UART** | ✅ | ✅ | Both have |
| **1-Wire** | ✅ | ✅ | Both have |
| **PWM** | ✅ | ✅ | Both have |
| **ADC** | ✅ | ✅ | Both have |
| **USB Host** | ❌ | ✅ | **PiFlip advantage!** |
| **USB Gadget** | ✅ | ✅ | Both can emulate USB |
| **Expansion** | Limited | Massive | 40 GPIO pins! |

**Winner:** ✅ **PiFlip** - 40 GPIO pins vs 5!

---

### **8. iButton / 1-Wire**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **iButton Read** | ✅ | ⚠️ Add DS9490R | Flipper built-in |
| **iButton Write** | ✅ | ⚠️ | Flipper advantage |
| **iButton Emulate** | ✅ | ⚠️ | |
| **Dallas Keys** | ✅ | ⚠️ | Flipper has dedicated reader |

**Winner:** ✅ **Flipper Zero** - Built-in iButton

**PiFlip Upgrade:** DS9490R USB adapter (~$20) adds full iButton support

---

### **9. Bad USB / USB Attacks**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **Bad USB** | ✅ | ✅ | Both can do! |
| **HID Keyboard** | ✅ | ✅ USB Gadget mode | Both emulate keyboard |
| **HID Mouse** | ✅ | ✅ | Both work |
| **Rubber Ducky** | ✅ | ✅ | Both compatible |
| **DuckyScript** | ✅ | ✅ | Both support |
| **USB Mass Storage** | ✅ | ✅ | Both emulate |
| **USB Serial** | ✅ | ✅ | Both work |

**Winner:** 🤝 **TIE** - Both excellent

---

### **10. U2F / Security Keys**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **U2F Emulation** | ✅ | ⚠️ Requires setup | Flipper easier |
| **FIDO2** | ⚠️ | ⚠️ | Both limited |

**Winner:** ✅ **Flipper Zero** - Built-in

---

### **11. Spectrum Analyzer**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **Sub-GHz Spectrum** | ✅ | ✅ **Enhanced!** | Both have |
| **Waterfall Display** | ❌ | ✅ **NEW!** | **PiFlip exclusive!** |
| **PortaPack Style** | ❌ | ✅ | **PiFlip has it!** |
| **Wideband (RTL-SDR)** | ❌ | ✅ 24MHz-1.7GHz | **Huge advantage!** |
| **Signal Detection** | ✅ | ✅ | Both auto-detect |
| **Peak Finding** | ✅ | ✅ | Both have |
| **RSSI Graph** | ✅ | ✅ | Both show strength |

**Winner:** ✅ **PiFlip** - Wideband spectrum + waterfall!

---

### **12. User Interface**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **Display** | 1.4" LCD | Web browser | Any screen size! |
| **Touchscreen** | ❌ | ✅ (on phone/tablet) | Use touch devices |
| **Physical Buttons** | ✅ 5 buttons | ❌ | Flipper has D-pad |
| **Web Interface** | ❌ | ✅ | **PiFlip exclusive!** |
| **Mobile App** | ✅ iOS/Android | ✅ Browser | PiFlip uses browser |
| **Keyboard/Mouse** | ❌ | ✅ Can add | USB support |
| **Screen Size** | 1.4" | Unlimited | Use iPad! |
| **Menu System** | Excellent | Excellent | Both great |
| **Ease of Use** | Excellent | Very good | Flipper more portable |

**Winner:** ⚠️ **Depends** - Flipper more portable, PiFlip more powerful

---

### **13. Development & Customization**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **Open Source** | ✅ | ✅ | Both fully open |
| **Custom Apps** | ✅ | ✅ | Both support |
| **Python Support** | ❌ | ✅ | **PiFlip advantage!** |
| **C/C++** | ✅ | ✅ | Both support |
| **JavaScript** | ❌ | ✅ | PiFlip has Node.js |
| **Community** | Huge | Growing | Flipper bigger |
| **Documentation** | Excellent | Good | Both decent |
| **Firmware Updates** | ✅ OTA | ✅ apt-get | Both easy |
| **Add Libraries** | Limited | ✅ pip/apt | **PiFlip easier!** |

**Winner:** ✅ **PiFlip** - Full Linux, any language!

---

### **14. Storage & Memory**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **RAM** | 256 KB | 1 GB | **PiFlip 4000x more!** |
| **Storage** | microSD | microSD | Both expandable |
| **Max Storage** | 512 GB | 512 GB+ | Both support large cards |
| **Signal Library** | Limited by RAM | Unlimited | PiFlip advantage |
| **Captures** | Limited | Unlimited | PiFlip wins |

**Winner:** ✅ **PiFlip** - 1GB RAM vs 256KB!

---

### **15. Additional Features**

| Feature | Flipper Zero | PiFlip | Notes |
|---------|--------------|---------|-------|
| **Music Player** | ✅ | ✅ | Both can |
| **Games** | ✅ Snake, etc. | ✅ | Both have |
| **Animations** | ✅ | ⚠️ | Flipper has dolphin |
| **LED** | ✅ RGB | ✅ | Both have |
| **Vibration** | ✅ | ❌ | Flipper only |
| **Speaker** | ✅ | ⚠️ USB/GPIO | Flipper built-in |
| **Camera** | ❌ | ✅ Can add USB | PiFlip expandable |
| **GPS** | ❌ | ✅ Can add USB | PiFlip advantage |
| **Microphone** | ❌ | ✅ Can add USB | PiFlip wins |

**Winner:** ✅ **PiFlip** - Expandable via USB

---

## 🏆 **CATEGORY WINNERS**

| Category | Winner | Reason |
|----------|--------|--------|
| **Sub-GHz RF** | 🤝 TIE | Both excellent |
| **125kHz RFID** | Flipper | Dedicated hardware |
| **13.56MHz NFC** | 🤝 TIE | Both great |
| **Infrared** | Flipper | Built-in IR |
| **Bluetooth** | **PiFlip** | Built-in BT 4.1! |
| **WiFi** | **PiFlip** | Built-in + hotspot! |
| **GPIO** | **PiFlip** | 40 pins vs 5 |
| **iButton** | Flipper | Built-in reader |
| **Bad USB** | 🤝 TIE | Both work great |
| **Spectrum** | **PiFlip** | Wideband + waterfall! |
| **Interface** | Flipper | More portable |
| **Development** | **PiFlip** | Full Linux! |
| **Expandability** | **PiFlip** | USB + 40 GPIO |
| **Portability** | Flipper | Pocket-sized + battery |

---

## 📊 **OVERALL SCORE**

### **Flipper Zero: 4 wins, 5 ties**
✅ 125kHz RFID
✅ Infrared
✅ iButton
✅ Portability
🤝 Sub-GHz RF
🤝 NFC
🤝 Bad USB

### **PiFlip: 7 wins, 5 ties**
✅ **Bluetooth** (Flipper doesn't have!)
✅ **WiFi** (Built-in + hotspot!)
✅ **GPIO** (40 pins!)
✅ **Spectrum Analyzer** (Wideband!)
✅ **Development** (Full Linux!)
✅ **Expandability** (USB!)
✅ **Additional Features** (Camera, GPS, etc.)
🤝 Sub-GHz RF
🤝 NFC
🤝 Bad USB

---

## 💰 **VALUE COMPARISON**

| Device | Price | Best For |
|--------|-------|----------|
| **Flipper Zero** | $169 | Portability, all-in-one, polished UX, IR, 125kHz |
| **PiFlip** | ~$120 | Power, expandability, Bluetooth, WiFi, spectrum |

**PiFlip is $49 cheaper AND has more features!** 🎉

---

## 🎯 **WHAT PIFLIP NEEDS TO MATCH FLIPPER**

### **Easy Upgrades (<$30):**
1. ✅ **IR Transmitter/Receiver** - $5 (GPIO + LIRC)
2. ✅ **125kHz RFID Reader** - $10-20 (USB)
3. ✅ **iButton Reader** - $20 (DS9490R USB)
4. ✅ **Vibration Motor** - $2 (GPIO)
5. ✅ **Speaker** - $5 (USB or GPIO)

**Total: ~$42 to match ALL Flipper features!**

**Grand total: $120 + $42 = $162 (still cheaper than Flipper!)**

---

## 🚀 **WHAT PIFLIP HAS THAT FLIPPER DOESN'T**

### **PiFlip Exclusive Features:**
1. ✅ **Bluetooth BLE & Classic** - Flipper doesn't have this!
2. ✅ **WiFi Hotspot Mode** - Control from iPad/iPhone!
3. ✅ **Wideband Spectrum** (24MHz - 1.7GHz)
4. ✅ **PortaPack-style Waterfall**
5. ✅ **40 GPIO Pins** (vs 5)
6. ✅ **1GB RAM** (vs 256KB)
7. ✅ **Full Linux OS**
8. ✅ **USB Host** (add anything!)
9. ✅ **Python, JavaScript, any language**
10. ✅ **Web interface** (use any screen size)

---

## 🎓 **RECOMMENDED NEXT UPGRADES FOR PIFLIP**

### **Top Priority:**
1. **IR Support** - Add LIRC + IR LED/receiver ($5)
2. **125kHz RFID** - USB reader ($15)
3. **Battery Pack** - USB power bank ($20) for portability
4. **Case** - 3D printed enclosure

### **Advanced:**
5. **Touchscreen** - 3.5" display ($30)
6. **NRF24L01+** - 2.4GHz mice/keyboards ($2)
7. **ESP32** - WiFi deauth + BLE 5.0 ($8)
8. **Ubertooth One** - Professional Bluetooth ($120)
9. **HackRF One** - Full SDR TX/RX ($300)

---

## 🏁 **CONCLUSION**

### **Choose Flipper Zero if:**
- You want pocket-sized portability
- You need built-in IR remote
- You want plug-and-play experience
- You need 125kHz RFID often
- You prefer physical buttons

### **Choose PiFlip if:**
- You want **Bluetooth scanning** (Flipper can't do this!)
- You want **WiFi hotspot** for iPad/phone control
- You want **wideband spectrum analyzer**
- You want **expandability** (USB + GPIO)
- You want **more power** for the money
- You can carry a power bank

---

## 🦊 **VERDICT**

**PiFlip wins on:**
- Features (Bluetooth, WiFi, spectrum)
- Value ($49 cheaper)
- Power (1GB RAM, full Linux)
- Expandability (USB + 40 GPIO)

**Flipper Zero wins on:**
- Portability (pocket-sized + battery)
- Polished UX (dedicated hardware)
- IR built-in
- 125kHz RFID built-in

**Best answer:** Get both! 😄
Or start with PiFlip ($120) and add $42 in upgrades to match Flipper entirely!

---

**Your PiFlip already has features Flipper Zero doesn't have (Bluetooth, WiFi hotspot, wideband spectrum)!** 🎉

**Last updated:** October 3, 2025

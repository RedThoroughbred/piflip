# 🔧 PiFlip Hardware Capabilities

Complete guide to what your Raspberry Pi components can do.

---

## 📡 CC1101 Sub-GHz Transceiver

**Frequency Range:** 300-928 MHz
**Power:** Transmit AND Receive
**Interface:** SPI (GPIO pins)

### What It Can Do:

#### 1. **RF Transmission (TX)**
- Transmit signals at 300-928 MHz
- Common frequencies:
  - **315 MHz** - garage door openers, car keys (North America)
  - **433.92 MHz** - key fobs, wireless sensors, weather stations
  - **868 MHz** - European ISM band
  - **915 MHz** - US ISM band

**Use Cases:**
- ✅ Replay captured RF signals (non-rolling codes)
- ✅ Garage door openers (older, fixed-code models)
- ✅ Wireless doorbells
- ✅ Weather station sensors
- ✅ RF remote controls
- ✅ Wireless light switches
- ✅ Custom RF communication

**Modulations Supported:**
- OOK/ASK (On-Off Keying / Amplitude Shift Keying)
- FSK (Frequency Shift Keying)
- GFSK (Gaussian FSK)
- MSK (Minimum Shift Keying)

**What You've Already Done:**
- ✅ Transmitted test signals
- ✅ Replayed key fob patterns
- ✅ Configured for 433.92 MHz OOK

---

#### 2. **RF Reception (RX)**
- Receive and decode signals at 300-928 MHz
- Can act as a **software-defined radio** for sub-GHz

**Use Cases:**
- ✅ Capture RF signals from remotes
- ✅ Monitor wireless sensors
- ✅ Decode weather station data
- ✅ Sniff wireless protocols
- ✅ Build RF spectrum analyzer
- ✅ Jamming detection

**What You Haven't Done Yet:**
- ⚠️ Receive mode not tested yet
- ⚠️ Can replace RTL-SDR for 300-928 MHz signals

---

#### 3. **Protocol Support**
The CC1101 can work with common protocols:
- **Fixed-code remotes** (garage doors, doorbells)
- **Weather sensors** (temperature, humidity)
- **Tire pressure monitors (TPMS)**
- **Wireless thermometers**
- **RC toys** (some)
- **Custom protocols**

---

### CC1101 Web Interface Ideas:

```
📡 RF Tools
├── 🔍 Scan Frequencies (300-928 MHz)
├── 📻 Receive Signal
│   ├── Choose frequency
│   ├── Choose modulation (OOK/FSK/etc)
│   ├── Live decode
│   └── Save to library
├── 📤 Transmit Signal
│   ├── Choose from saved signals
│   ├── Replay captured pattern
│   ├── Custom pattern editor
│   └── Repeat/interval settings
├── 🎛️ Signal Analyzer
│   ├── View signal strength
│   ├── Frequency spectrum
│   └── Decode common protocols
└── 📚 Signal Library
    ├── Saved captures
    ├── Metadata (freq, modulation, etc)
    ├── Replay
    └── Export/Import
```

---

## 💳 PN532 NFC Reader/Writer

**Standards:** NFC-A, NFC-B, ISO14443A/B, FeliCa
**Interface:** I2C (GPIO 2/3)
**Range:** ~5cm

### What It Can Do:

#### 1. **Read NFC/RFID Tags**

**Supported Tag Types:**
- **MIFARE Classic** (1K, 4K) - most common, used in:
  - Building access cards
  - Hotel room keys
  - Public transit cards
  - Gym membership cards
  - Library cards
- **MIFARE Ultralight** - simpler, used in:
  - Event wristbands
  - Disposable tickets
  - Smart posters
- **NTAG** (NTAG213, 215, 216) - used in:
  - NFC tags/stickers
  - Product authentication
  - Smart labels
- **FeliCa** - used in:
  - Japanese transit cards (Suica, Pasmo)
  - e-money systems

**What You Can Read:**
- ✅ Card UID (unique ID)
- ✅ Card type/manufacturer
- ✅ Memory contents (if not encrypted)
- ✅ Access control bits
- ✅ NDEF messages (URLs, text, etc)

**What You've Already Done:**
- ✅ Read card UID: 97:43:70:06
- ✅ Identified card type

---

#### 2. **Write NFC Tags**

**Use Cases:**
- ✅ Program blank NFC tags
- ✅ Write URLs (tap phone to open website)
- ✅ Write WiFi credentials (tap to connect)
- ✅ Write vCards (contact info)
- ✅ Write app launch commands
- ✅ Write custom NDEF messages

**Popular Uses:**
- Smart business cards
- "Tap here for WiFi" tags
- Product information tags
- Home automation triggers
- Location markers

---

#### 3. **Clone/Copy Cards** (where legal)

**Can Clone:**
- ✅ MIFARE Classic (if keys are known)
- ✅ MIFARE Ultralight
- ✅ UID-changeable cards
- ✅ Some access cards (building entry)

**Cannot Clone:**
- ❌ Cards with encrypted sectors (without keys)
- ❌ DESFire cards (high security)
- ❌ Cards with write-protected UIDs
- ❌ Most credit cards (EMV)
- ❌ Government IDs

**Legal Note:** Only clone cards you own or have permission to duplicate.

---

#### 4. **Card Emulation**

The PN532 can **pretend to be a card**:
- Act like a MIFARE card
- Respond to readers
- Custom protocols

**Use Cases:**
- Building access without physical card
- Public transit emulation (where legal)
- Testing access control systems
- Custom NFC applications

---

#### 5. **Peer-to-Peer (P2P) Mode**

Communicate with:
- Android phones (Android Beam)
- Other NFC devices
- Data exchange between devices

---

### PN532 Web Interface Ideas:

```
💳 NFC Tools
├── 🔍 Read Card/Tag
│   ├── Show UID
│   ├── Show type
│   ├── Read all sectors
│   ├── Dump to file
│   └── Analyze encryption
├── ✏️ Write Tag
│   ├── Write URL
│   ├── Write WiFi credentials
│   ├── Write text/vCard
│   ├── Write custom NDEF
│   └── Format tag
├── 📋 Clone Card
│   ├── Read source card
│   ├── Write to blank card
│   ├── Verify clone
│   └── Save to library
├── 🎭 Emulate Card
│   ├── Choose card from library
│   ├── Emulate UID
│   └── Custom responses
├── 📚 Card Library
│   ├── Saved cards
│   ├── Metadata (type, purpose, etc)
│   ├── View dumps
│   └── Export/Import
└── 🔐 Security Tools
    ├── Crack MIFARE keys
    ├── Test known keys
    ├── Analyze access bits
    └── Check write protection
```

---

## 🎯 Combined Use Cases

### Projects You Can Build:

#### 1. **Smart Home Automation**
- NFC tags around house trigger RF devices
- "Tap to turn on lights" (NFC) → sends RF signal
- "Tap to open garage" → RF transmission
- Location-based automation

#### 2. **Access Control System**
- Read NFC card → if authorized → trigger RF relay
- Building entry system
- Vehicle access control

#### 3. **Signal Library Manager**
- Capture RF signals (CC1101)
- Store with NFC tags (tag = signal ID)
- Tap tag to replay signal
- Physical "remote control" tokens

#### 4. **RF Remote Cloner**
- Capture signal from remote (CC1101 RX)
- Save to NFC tag
- Tap tag to replay (CC1101 TX)
- Universal remote system

#### 5. **IoT Device Controller**
- Control 433MHz wireless switches
- Program via NFC tags
- Schedule transmissions
- Remote control via web

#### 6. **Security Research** (defensive only)
- Test building access cards
- Analyze RF security
- Test wireless protocols
- Security auditing

---

## 🌐 Web Interface - Complete Plan

### Main Dashboard

```
┌─────────────────────────────────────────────┐
│  🔧 PiFlip - RF & NFC Multi-Tool            │
├─────────────────────────────────────────────┤
│                                             │
│  📡 RF Tools          💳 NFC Tools          │
│  ├─ Scan              ├─ Read Card          │
│  ├─ Receive           ├─ Write Tag          │
│  ├─ Transmit          ├─ Clone Card         │
│  └─ Library           └─ Library            │
│                                             │
│  🎯 Quick Actions                           │
│  ├─ Capture & Save                          │
│  ├─ Read & Clone NFC                        │
│  └─ Replay from Library                     │
│                                             │
│  📊 Status                                  │
│  ├─ CC1101: ✅ Ready (433.92 MHz)          │
│  └─ PN532: ✅ Card Detected                │
│                                             │
└─────────────────────────────────────────────┘
```

---

### Detailed Features to Implement:

#### **RF Tools Section**

1. **Frequency Scanner**
   - Scan 300-928 MHz range
   - Show signal strength graph
   - Auto-detect active frequencies
   - Save interesting signals

2. **Signal Capture**
   - Choose frequency
   - Choose modulation
   - Real-time waveform display
   - Save with metadata
   - Name and tag signals

3. **Signal Replay**
   - Browse saved signals
   - Edit before replay
   - Repeat count
   - Delay between repeats
   - Test mode

4. **Signal Library**
   - Grid/list view of saved signals
   - Filter by frequency/type
   - Edit metadata
   - Delete/export
   - Import from URH

5. **Protocol Analyzer**
   - Auto-detect common protocols
   - Decode weather sensors
   - Decode remote controls
   - Save decoded data

---

#### **NFC Tools Section**

1. **Card Reader**
   - Live detection (shows when card is near)
   - Display UID in real-time
   - Show card type
   - Read all sectors button
   - Save dump

2. **Tag Writer**
   - Templates:
     - WiFi credentials
     - URL/website
     - Text message
     - vCard contact
     - Custom NDEF
   - Format tag option
   - Verify after write

3. **Card Cloner**
   - Step 1: Read source card
   - Step 2: Preview data
   - Step 3: Write to blank
   - Step 4: Verify clone
   - Save to library

4. **Card Library**
   - Saved card dumps
   - Metadata (name, type, purpose)
   - Preview data
   - Clone to new card
   - Export format options

5. **Key Cracker** (for MIFARE)
   - Test default keys
   - Dictionary attack
   - Show cracked sectors
   - Save found keys

---

#### **Combined Features**

1. **Quick Actions**
   - "Capture RF + Save to NFC tag"
   - "Read NFC tag → Replay RF signal"
   - "Clone both RF remote and NFC card"

2. **Automation**
   - Schedule RF transmissions
   - Trigger on NFC tap
   - Web API for external control

3. **Settings**
   - Default frequencies
   - Gain settings
   - Power levels
   - Auto-save options

---

## 📝 Implementation Priority

### Phase 1: Core Functionality ✅ (Mostly Done)
- [x] CC1101 transmission
- [x] PN532 card reading
- [x] Basic web interface
- [x] Test scripts

### Phase 2: Signal Library (Next)
- [ ] Save RF captures to database
- [ ] Metadata (name, freq, modulation, notes)
- [ ] Web UI to browse/replay
- [ ] Import/export

### Phase 3: NFC Enhancement
- [ ] Write to tags
- [ ] Clone cards
- [ ] Card library
- [ ] NDEF message support

### Phase 4: CC1101 RX Mode
- [ ] Receive signals
- [ ] Live decode
- [ ] Frequency scanner
- [ ] Protocol analyzer

### Phase 5: Advanced Features
- [ ] Combined RF+NFC workflows
- [ ] Automation/scheduling
- [ ] Mobile-optimized UI
- [ ] API for external control

---

## 🎮 What Should You Build?

Based on your setup, here are the coolest projects:

### **Recommended: Universal RF Remote**
Build a web-based universal remote:
1. Capture signals from all your remotes (garage, lights, etc)
2. Store in library with names
3. Replay from web interface or phone
4. Bonus: Program NFC tags as physical buttons

**Why:** Practical, showcases both RF TX/RX, easy to use daily

---

### **Alternative: NFC Business Card System**
1. Program NFC tags with your info
2. Hand out as business cards
3. When tapped: opens your website/vCard
4. Track taps via web interface

**Why:** Useful, impressive, easy to implement

---

### **Advanced: Smart Home Controller**
1. Control 433MHz wireless outlets/lights
2. Program NFC tags as light switches
3. Schedule automations
4. Voice control via API

**Why:** Most complex, but very cool

---

## 🚀 Next Steps

**Tell me what you want to build and I'll help you implement it!**

Options:
1. **Signal Library** - store/replay RF captures
2. **NFC Tag Writer** - program NFC tags
3. **Universal Remote** - web-based RF remote
4. **Card Cloner** - duplicate access cards
5. **Something else?**

What sounds most interesting to you?

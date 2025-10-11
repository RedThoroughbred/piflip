# PiFlip Usage Guide

## 🚀 Quick Start Workflow

### Your Current Hardware:
- ✅ **CC1101** (Sub-GHz TX/RX) - 300-928 MHz
- ✅ **PN532** (NFC/RFID) - 13.56 MHz
- ⚠️ **RTL-SDR** (Wide-band RX) - Optional, currently not detected

---

## 📡 Sub-GHz RF Tools (CC1101)

### 1️⃣ **Signal Strength Meter** (Best Starting Point!)

**What it does:** Shows live signal strength in real-time

**When to use:**
- Before capturing - make sure you're in range
- Aiming your antenna for best reception
- Testing if your remote is transmitting

**How to use:**
1. Go to: **Sub-GHz Tools (CC1101) → Signal Strength Meter**
2. See live RSSI bars: `░░░▓▓▓▓▓▓▓`
3. Press your remote button and watch bars increase
4. Move antenna until you get **60%+** signal strength
5. Close when done (swipe down on mobile)

**What the numbers mean:**
- **RSSI (dBm):** -115 to -50 dBm (lower = weaker)
  - `-74 dBm` = Good signal (your current ambient level)
  - `-90 dBm` = Weak but usable
  - `-50 dBm` = Excellent (very close)
- **Signal Strength:** 0-100% (easier to read)
  - `60%+` = Good for capture
  - `40-60%` = Marginal
  - `<40%` = Too weak

**Pro Tip:** Leave this running while positioning your antenna before capturing!

---

### 2️⃣ **Quick Signal Test**

**What it does:** Automatically tests common frequencies to find your remote

**When to use:**
- You don't know what frequency your remote uses
- Testing multiple remotes quickly

**How to use:**
1. **Sub-GHz Tools → Quick Signal Test**
2. **HOLD** your remote button during the test
3. Tests these frequencies automatically:
   - 433.92 MHz (most common EU)
   - 315.00 MHz (US garage doors)
   - 433.07 MHz (alternate)
   - 433.42 MHz (alternate)
4. Shows which frequency has strongest signal
5. Use that frequency for capturing

**Expected output:**
```
433.92 MHz: -65 dBm ✅ STRONG
315.00 MHz: -95 dBm (weak)
433.07 MHz: -90 dBm (weak)
```

---

### 3️⃣ **Capture Signal** (Main Feature!)

**What it does:** Records RF signal from your remote/device

**Current captures:**
- `testNumber1.cu8` - 433.92 MHz, 5 seconds, 20MB
- `test_1759332591323.cu8` - 433.92 MHz, 5 seconds, 20MB

**How to capture a garage door remote:**

**STEP 1: Position antenna**
- Use Signal Strength Meter first
- Get 60%+ signal strength
- Keep remote 1-3 feet from antenna

**STEP 2: Start capture**
1. **Sub-GHz Tools → Capture Signal**
2. Enter frequency: `433.92` (most common)
3. Enter duration: `5` seconds
4. Enter name: `garage_door_open`
5. Click **Start Capture**

**STEP 3: Press remote button**
- Wait 1 second after capture starts
- Press and HOLD button for 2 seconds
- Release
- Capture will automatically stop after 5 seconds

**STEP 4: View capture**
- Go to **Sub-GHz Tools → RF Signal Library**
- You'll see: `garage_door_open`
- Shows: frequency, duration, file size

**What gets saved:**
- `garage_door_open.cu8` - Raw IQ samples (20MB for 5 sec)
- `garage_door_open.json` - Metadata (frequency, timestamp, etc.)

---

### 4️⃣ **Scan Frequencies**

**What it does:** Scans a range of frequencies to find active signals

**When to use:**
- Looking for unknown signals in your area
- Finding what frequency a device uses
- Monitoring ISM bands

**How to use:**
1. **Sub-GHz Tools → Scan Frequencies**
2. Set range: `433.0` to `434.0` MHz
3. Set step: `0.1` MHz (scans every 100 kHz)
4. Click **Start Scan**
5. Press devices while scanning
6. Shows which frequencies have activity

**Example results:**
```
Scanning 433.0 - 434.0 MHz...
433.0 MHz: -95 dBm
433.1 MHz: -92 dBm
433.92 MHz: -60 dBm ⚡ ACTIVE!
434.0 MHz: -94 dBm
```

**Common frequencies to scan:**
- **315 MHz** - US garage doors, car keys
- **433.92 MHz** - EU garage doors, remotes, sensors
- **868 MHz** - EU smart home devices
- **915 MHz** - US ISM band devices

---

### 5️⃣ **RF Signal Library**

**What it does:** Manages your saved captures

**Your current library:**
- 2 captures (40 MB total)
- Both at 433.92 MHz

**Features:**
- View all captures
- See metadata (frequency, duration, timestamp)
- Delete old captures
- Replay signals (future feature)

**How to use:**
1. **Sub-GHz Tools → RF Signal Library**
2. Browse your captures
3. Click to view details
4. Option to delete or replay

---

## 💳 NFC Tools (PN532)

### 1️⃣ **Scan Card** (Single Read)

**What it does:** Reads one NFC card's UID

**Your current library:**
- `blue_card.json` - One saved card

**How to use:**
1. **NFC Tools → Scan Card**
2. Hold card close to PN532 (within 1 inch)
3. Wait for beep/LED
4. Shows: UID, card type, SAK, ATQA
5. Option to save to library

**What you'll see:**
```
💳 NFC CARD DETECTED

UID: A1:B2:C3:D4
Type: Mifare Classic 1K
SAK: 08
ATQA: 00:04
```

---

### 2️⃣ **Continuous Scan**

**What it does:** Keeps scanning for NFC cards

**When to use:**
- Testing multiple cards quickly
- Monitoring for card presence
- Batch scanning

**How to use:**
1. **NFC Tools → Continuous Scan**
2. Tap cards one by one
3. Each tap shows UID
4. Close when done

---

### 3️⃣ **Read Full Card**

**What it does:** Reads all data from Mifare Classic cards

**How to use:**
1. **NFC Tools → Read Full Card**
2. Place card on reader
3. Reads all 16 sectors (64 blocks)
4. Shows hex dump of all data
5. Can save full dump

**Use cases:**
- Backing up access cards
- Analyzing card structure
- Before cloning

---

### 4️⃣ **Clone Card** (Magic Cards Only!)

**What it does:** Copies one card to another

**Requirements:**
- **Source:** Any Mifare Classic card
- **Target:** Magic card (Gen1a/Gen2)

**How to use:**
1. Read source card first (Read Full Card)
2. Save the dump
3. **NFC Tools → Clone Card**
4. Select saved dump
5. Place magic card on reader
6. Writes all data including UID

**⚠️ Warning:** Only works with magic cards! Regular cards are write-protected.

---

## 📊 Dashboard

**What it shows:**
- **Stats:**
  - RF Captures: 2
  - NFC Cards: 1
  - Storage Used: 40.19 MB
  - Total Scans: (tracked)

- **Top Frequencies:**
  - 433.92 MHz (2 captures)

- **Recent Activity:**
  - Your last 10 captures/scans
  - Shows time ago (5m ago, 2h ago)
  - Click to view details

- **Quick Actions:**
  - Jump to RF Tools
  - Jump to NFC Tools
  - Jump to Library
  - Hardware check

---

## 🎯 Common Use Cases

### Use Case 1: Capture a Garage Door Remote

1. **Signal Strength Meter**
   - Position antenna
   - Get 60%+ strength

2. **Quick Signal Test** (if unsure of frequency)
   - Hold button during test
   - Note strongest frequency

3. **Capture Signal**
   - Use frequency from test (likely 433.92 MHz)
   - Duration: 5 seconds
   - Name: `garage_open`
   - Press button during capture

4. **RF Signal Library**
   - Verify capture saved
   - View metadata

### Use Case 2: Copy an Access Card

1. **Read Full Card**
   - Place card on reader
   - Save dump as `office_access`

2. **Clone Card**
   - Insert magic card
   - Select `office_access` dump
   - Write to magic card
   - Test cloned card

### Use Case 3: Find Unknown Remote Frequency

1. **Quick Signal Test**
   - Hold remote button
   - See which frequency responds

2. **Scan Frequencies**
   - Scan around detected frequency
   - Fine-tune exact frequency

3. **Capture Signal**
   - Use exact frequency
   - Capture for analysis

---

## 📱 Mobile/Portable Usage

### When using hotspot mode:

**Connection:**
1. Pi creates "PiFlip" WiFi network
2. Connect phone: password `piflip123`
3. Open browser: `http://192.168.50.1:5000`

**Best practices:**
- Use **Signal Strength Meter** to aim antenna
- Bigger buttons optimized for fingers
- Swipe down to close panels
- Dashboard shows quick stats
- Works fully offline (no internet needed)

**Power:**
- Use 10,000 mAh battery bank
- Runtime: 6+ hours
- Signal Strength Meter uses minimal power
- Captures use more power (brief spikes)

---

## 🔧 Technical Details

### File Formats

**RF Captures (.cu8):**
- Complex IQ samples
- 8-bit unsigned integers
- 2 samples per complex value (I + Q)
- Sample rate: 2.048 MSPS
- File size: ~4 MB per second

**RF Metadata (.json):**
```json
{
    "name": "garage_door",
    "frequency": 433920000,
    "sample_rate": 2048000,
    "duration": 5,
    "num_samples": 10240000,
    "timestamp": "2025-10-02T15:30:00"
}
```

**NFC Dumps (.json):**
```json
{
    "uid": "A1:B2:C3:D4",
    "card_type": "Mifare Classic 1K",
    "sak": "08",
    "atqa": "00:04",
    "blocks": [...],
    "timestamp": "2025-10-02T15:30:00"
}
```

### Hardware Specifications

**CC1101:**
- Frequency: 300-928 MHz
- Modulation: OOK, ASK, FSK, MSK, GFSK
- Data rate: 0.6 - 500 kBaud
- TX power: ~10 dBm
- RX sensitivity: -110 dBm
- Interface: SPI (GPIO 8,9,10,11)

**PN532:**
- Frequency: 13.56 MHz
- Protocols: ISO14443A/B, FeliCa
- Cards: Mifare Classic, Ultralight, DESFire
- Range: ~5 cm
- Interface: I2C (GPIO 2,3)

---

## 💡 Tips & Tricks

### Signal Capture Tips:
1. **Always check signal strength first** (60%+ is good)
2. **Capture slightly longer** than needed (5 sec is safe)
3. **Press button 1 second after** capture starts
4. **Hold button for 2 seconds** for reliable capture
5. **Name captures descriptively** (`garage_open`, `car_lock`, etc.)

### NFC Tips:
1. **Hold card steady** for 1-2 seconds
2. **Dead center** of PN532 reader
3. **Within 1 inch** for best results
4. **Test magic cards first** before cloning important data
5. **Back up cards** before experimenting

### Storage Management:
- Captures are 20 MB each (5 seconds)
- Delete old test captures regularly
- SD card: ~133 MB available currently
- Consider shorter captures (2-3 seconds) for testing

### Battery Life (Portable):
- Idle: 6+ hours (10,000 mAh)
- Active scanning: 4-5 hours
- Continuous capture: 3-4 hours
- Signal Strength Meter: minimal impact

---

## 🐛 Troubleshooting

### "Low Signal Strength"
- Move closer to transmitter
- Reposition antenna (try vertical/horizontal)
- Check frequency is correct
- Battery in remote might be low

### "Capture Empty"
- Didn't press button during capture
- Wrong frequency
- Signal too weak
- Press button longer next time

### "NFC Card Not Detected"
- Card too far (< 1 inch needed)
- Wrong card type (PN532 is 13.56 MHz only)
- Card not centered on reader
- Try different orientation

### "Hardware Not Detected"
- Check physical connections
- Restart service: `sudo systemctl restart piflip`
- Check status bar indicators
- Welcome screen shows hardware status

---

## 📚 Next Steps

### To learn more:
1. Test Signal Strength Meter with various remotes
2. Capture your garage door remote
3. Experiment with different frequencies
4. Read your access cards
5. Build a library of common signals

### Advanced features (coming soon):
- Signal replay (transmit captures)
- URH integration (decode protocols)
- Signal analysis (rolling codes, etc.)
- Batch operations
- Cloud sync (optional)

---

## 🎓 Learning Resources

### Understanding RF:
- **Frequency:** Which "channel" device broadcasts on
- **Modulation:** How data is encoded (OOK, ASK, FSK)
- **RSSI:** Received Signal Strength Indicator (dBm)
- **IQ Samples:** Complex representation of signal

### Understanding NFC:
- **UID:** Unique card ID (4-7 bytes)
- **Mifare Classic:** Most common access cards (1K/4K)
- **Magic Cards:** Writable UID cards for cloning
- **Sectors:** Cards divided into 16 sectors (1K) or 40 (4K)

### Common Frequencies:
- **315 MHz:** US garage doors, car remotes
- **433.92 MHz:** EU remotes, sensors, alarms
- **868 MHz:** EU Z-Wave, smart home
- **915 MHz:** US ISM band devices
- **13.56 MHz:** NFC/RFID cards

---

**Need help?** Check the status bar for hardware indicators, use the Dashboard for quick stats, and remember - Signal Strength Meter is your friend! 📶

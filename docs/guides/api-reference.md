# PiFlip API Reference - Complete Endpoint List

**Total Endpoints:** 80+ (20+ new endpoints added!)

---

## 🔵 **Bluetooth API** (NEW!)

### Scanning

**POST /api/bluetooth/scan**
Scan for Bluetooth devices (BLE, Classic, or Comprehensive)

```json
Request:
{
  "type": "comprehensive",  // "ble", "classic", or "comprehensive"
  "duration": 15            // seconds
}

Response:
{
  "status": "success",
  "devices": [
    {
      "address": "AA:BB:CC:DD:EE:FF",
      "name": "Device Name",
      "type": "BLE",
      "rssi": -65,
      "timestamp": "2025-10-03T10:30:00"
    }
  ],
  "ble_count": 10,
  "classic_count": 5,
  "total_count": 15
}
```

### Device Information

**GET /api/bluetooth/device/{address}/info**
Get detailed information about a Bluetooth device

**GET /api/bluetooth/device/{address}/services?type=BLE**
Enumerate device services and characteristics

**POST /api/bluetooth/device/{address}/rssi**
Monitor device RSSI (signal strength) over time

```json
Request:
{
  "duration": 10  // seconds
}

Response:
{
  "address": "AA:BB:CC:DD:EE:FF",
  "rssi_readings": [
    {"timestamp": "...", "rssi": -65, "elapsed": 0.5},
    {"timestamp": "...", "rssi": -67, "elapsed": 1.0}
  ],
  "avg_rssi": -66.5
}
```

### Library Management

**GET /api/bluetooth/library**
List all saved Bluetooth devices

**POST /api/bluetooth/save**
Save a Bluetooth device to library

```json
Request:
{
  "device": {
    "address": "AA:BB:CC:DD:EE:FF",
    "name": "My Device",
    "type": "BLE"
  },
  "name": "my_device"
}
```

**DELETE /api/bluetooth/library/{name}**
Delete saved Bluetooth device

---

## 📡 **WiFi API** (NEW!)

### Status & Control

**GET /api/wifi/status**
Get current WiFi status

```json
Response (Client Mode):
{
  "mode": "client",
  "connected_to": "MyNetwork",
  "ip_address": "192.168.1.100"
}

Response (Hotspot Mode):
{
  "mode": "hotspot",
  "hotspot_ssid": "PiFlip-RF",
  "hotspot_ip": "10.0.0.1",
  "access_url": "http://10.0.0.1:5000"
}
```

**POST /api/wifi/hotspot/enable**
Enable WiFi hotspot mode

```json
Response:
{
  "status": "enabled",
  "ssid": "PiFlip-RF",
  "password": "piflip123",
  "ip": "10.0.0.1",
  "instructions": [
    "1. Connect to WiFi: PiFlip-RF",
    "2. Password: piflip123",
    "3. Open browser: http://10.0.0.1:5000"
  ]
}
```

**POST /api/wifi/hotspot/disable**
Disable hotspot, return to client mode

**POST /api/wifi/toggle**
Toggle between client and hotspot modes

### Network Management

**GET /api/wifi/scan**
Scan for available WiFi networks

```json
Response:
{
  "status": "success",
  "networks": [
    {
      "ssid": "MyNetwork",
      "quality": "70/70",
      "encrypted": true
    }
  ],
  "count": 5
}
```

**POST /api/wifi/connect**
Connect to a WiFi network

```json
Request:
{
  "ssid": "MyNetwork",
  "password": "password123"  // optional for open networks
}
```

---

## 📊 **Spectrum Analyzer API** (NEW!)

### Scanning

**POST /api/spectrum/scan**
Quick spectrum scan

```json
Request:
{
  "center_freq": 433.92,  // MHz
  "span": 2.0,            // MHz
  "bins": 256
}

Response:
{
  "status": "success",
  "spectrum": [
    {"frequency": 432.92, "power": -85.5},
    {"frequency": 433.92, "power": -45.2},
    {"frequency": 434.92, "power": -82.1}
  ],
  "peak": {
    "frequency": 433.92,
    "power": -45.2
  },
  "timestamp": 1696348800
}
```

**POST /api/spectrum/waterfall**
Continuous waterfall scan (PortaPack style!)

```json
Request:
{
  "center_freq": 433.92,
  "span": 2.0,
  "duration": 10,
  "interval": 0.2
}

Response:
{
  "status": "success",
  "waterfall": [
    {"timestamp": 1696348800, "powers": [-85, -87, -45, -82]},
    {"timestamp": 1696348800.2, "powers": [-86, -88, -46, -83]}
  ],
  "frequencies": [432.92, 433.42, 433.92, 434.42],
  "scan_count": 50
}
```

### Signal Detection

**POST /api/spectrum/detect**
Automatically detect signals in spectrum data

```json
Request:
{
  "spectrum_data": { /* scan result */ },
  "threshold": -80,      // dBm
  "min_width": 0.05      // MHz
}

Response:
{
  "status": "success",
  "signals": [
    {
      "center_freq": 433.92,
      "bandwidth": 0.15,
      "peak_power": -45.2,
      "avg_power": -50.1
    }
  ],
  "count": 3
}
```

**POST /api/spectrum/save**
Save spectrum scan for later analysis

---

## 💳 **Enhanced NFC Emulation API**

**POST /api/nfc/emulate_real/{name}**
Actually emulate NFC card (experimental)

```json
Request:
{
  "duration": 30  // seconds
}

Response:
{
  "status": "emulation_complete",
  "uid": "04:A3:B2:C1",
  "duration": 30,
  "note": "Card emulated. If reader didn't detect, try magic card clone."
}

// Or if library limitation:
{
  "status": "library_limitation",
  "recommendation": "Use Clone Card feature",
  "alternative": "Install libnfc for advanced emulation"
}
```

---

## 📻 **Existing RF API (Summary)**

### 433MHz Scanning

**GET /api/scan433**
Scan for 433MHz devices (30 seconds)

**POST /api/capture**
Capture raw IQ signal with RTL-SDR

**GET /api/captures**
List all saved captures

**DELETE /api/capture/{name}**
Delete a capture

**GET /api/analyze/{name}**
Analyze signal with URH

**POST /api/replay/{name}**
Replay signal via CC1101

### CC1101 Operations

**GET /api/cc1101/status**
Get CC1101 chip status

**POST /api/cc1101/capture**
Capture signal with CC1101

**POST /api/cc1101/scan**
Scan frequency range

**GET /api/cc1101/library**
List saved signals

**POST /api/cc1101/transmit/{name}**
Transmit saved signal

**DELETE /api/cc1101/library/{name}**
Delete saved signal

**GET /api/cc1101/decode/{name}**
Decode signal to binary

### TPMS & Weather

**GET /api/tpms**
Scan for TPMS tire pressure sensors (315MHz, 45s)

**GET /api/weather**
Scan for weather stations (433.92MHz, 60s)

---

## 💳 **NFC/RFID API**

### Reading

**GET /api/nfc**
Scan for NFC card (detailed info)

**POST /api/nfc/read_full**
Read full card dump (all sectors)

### Library Management

**POST /api/nfc/save**
Save NFC card to library

```json
Request:
{
  "name": "work_badge"
}
```

**GET /api/nfc/library**
List saved NFC cards

**DELETE /api/nfc/library/{name}**
Delete saved card

### Cloning

**POST /api/nfc/clone**
Clone card to magic card

**POST /api/nfc/verify**
Verify cloned card matches original

**POST /api/nfc/backup**
Backup card UID

### Emulation

**POST /api/nfc/emulate/{name}**
Get emulation info and instructions

**GET /api/nfc/clone_instructions**
Get step-by-step clone instructions

---

## 📈 **Dashboard & Stats API**

**GET /api/stats**
Get dashboard statistics

```json
Response:
{
  "total_rf_captures": 42,
  "total_nfc_reads": 15,
  "total_replays": 8,
  "total_scans": 120,
  "storage_used_mb": 145.23,
  "success_rate": 95,
  "top_frequencies": {
    "433.92": 25,
    "315.00": 10,
    "433.85": 5
  }
}
```

**GET /api/recent**
Get recent activity

**POST /api/activity**
Log user activity

---

## 🎨 **Visualization API**

**GET /api/waveform/{signal_name}**
Get ASCII waveform visualization

```json
Response:
{
  "simple_waveform": "▁▁▁███▁▁▁███▁▁▁",
  "detailed_waveform": "...",
  "timing_count": 150
}
```

**GET /api/waterfall/spectrum**
Real-time spectrum for waterfall display

**GET /api/waterfall/stream**
Server-sent events stream for continuous updates

---

## ⚙️ **System API**

**GET /api/status**
Hardware status (all components)

```json
Response:
{
  "nfc": true,
  "rtl_sdr": true,
  "cc1101": true
}
```

**GET /api/rssi**
Current RSSI from CC1101

---

## 📱 **Web Interface Routes**

**GET /**
Main Flipper-style UI

**GET /old**
Original interface

**GET /test**
Hardware test suite

**GET /nfc_test**
NFC testing page

---

## 🔧 **Usage Examples**

### Scan Bluetooth from Command Line

```bash
curl -X POST http://localhost:5000/api/bluetooth/scan \
  -H "Content-Type: application/json" \
  -d '{"type": "comprehensive", "duration": 15}'
```

### Enable WiFi Hotspot

```bash
curl -X POST http://localhost:5000/api/wifi/hotspot/enable
```

### Quick Spectrum Scan

```bash
curl -X POST http://localhost:5000/api/spectrum/scan \
  -H "Content-Type: application/json" \
  -d '{"center_freq": 433.92, "span": 2.0, "bins": 256}'
```

### Save Bluetooth Device

```bash
curl -X POST http://localhost:5000/api/bluetooth/save \
  -H "Content-Type: application/json" \
  -d '{
    "device": {
      "address": "AA:BB:CC:DD:EE:FF",
      "name": "iPhone",
      "type": "BLE"
    },
    "name": "my_iphone"
  }'
```

### Get WiFi Status

```bash
curl http://localhost:5000/api/wifi/status
```

---

## 🎯 **Rate Limiting**

No rate limiting currently implemented. Use responsibly:

- Spectrum scans: Allow 3+ seconds between scans
- Bluetooth scans: Allow 10+ seconds between scans
- WiFi mode switches: Allow 5+ seconds between switches
- NFC operations: Allow 2+ seconds between reads

---

## 🚨 **Error Responses**

All endpoints return errors in this format:

```json
{
  "error": "Error description",
  "status": "error",
  "message": "Detailed error message"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad request (missing parameters)
- `404` - Resource not found
- `500` - Internal server error (hardware issue, timeout, etc.)

---

## 📚 **Related Files**

- **bluetooth_scanner.py** - Bluetooth implementation
- **wifi_manager.py** - WiFi implementation
- **spectrum_analyzer.py** - Spectrum analysis
- **nfc_emulator.py** - NFC emulation
- **web_interface.py** - Main Flask app

---

**Total API Endpoints:** 80+
**New in This Update:** 20+ endpoints
**Last Updated:** October 3, 2025

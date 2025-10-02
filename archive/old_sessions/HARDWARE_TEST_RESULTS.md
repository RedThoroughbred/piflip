# PiFlip Hardware Test Results
**Date:** 2025-10-01
**Test Session:** Initial Hardware Verification

---

## Test Summary

| Module | Status | Details |
|--------|--------|---------|
| PN532 NFC | ✅ PASS | Firmware v1.6, I2C address 0x24 |
| RTL-SDR | ✅ PASS | Blog V4 detected, R828D tuner working |
| CC1101 | ⚠️ FAIL | SPI communication issue - wiring problem |
| Signal Capture | ✅ PASS | Successfully saved 20MB capture |
| Web Interface | ⏸️ NOT TESTED | Not currently running |

---

## Detailed Test Results

### ✅ PN532 NFC Module - WORKING

**Test Method:** I2C detection + firmware version read

**Results:**
```
I2C Address: 0x24 (detected)
Firmware Version: 1.6
Status: Fully functional
```

**Capabilities Verified:**
- I2C communication ✅
- Firmware detection ✅
- Ready for card read/write ✅

**Next Steps:**
- Test with actual NFC card
- Verify read/write operations
- Test card cloning

---

### ✅ RTL-SDR (Blog V4) - WORKING

**Test Method:** rtl_test device detection

**Results:**
```
Device: RTLSDRBlog, Blog V4
Serial: 00000001
Tuner: Rafael Micro R828D
Sample Rate: 2.048 MS/s
Gain Steps: 29 (0.0 - 49.6 dB)
```

**Notes:**
- "[R82XX] PLL not locked!" warnings are NORMAL for R828D tuner
- Successfully tested with signal capture
- Requires dump1090 to be stopped for scanning mode

**Capabilities Verified:**
- USB detection ✅
- Tuner initialization ✅
- Sample rate configuration ✅
- Signal capture (20MB test file) ✅

**Next Steps:**
- Test live 433MHz scanning
- Test TPMS reception
- Verify flight tracking

---

### ⚠️ CC1101 Module - WIRING ISSUE

**Test Method:** SPI register read

**Results:**
```
SPI Device: /dev/spidev0.0 (available)
Part Number Register: 0x0F (expected 0x00)
Version Register: 0x0F (expected 0x14)
Status: Not responding correctly
```

**Diagnosis:**
Reading `0x0F` from all registers indicates:
- SPI communication is working (can send/receive)
- CC1101 is NOT responding (likely power issue)

**Most Common Causes:**
1. **VCC not connected** (or using 5V instead of 3.3V!)
2. **GND not connected**
3. **Loose jumper wire on VCC/GND**
4. **Wrong CS pin**

**Expected Wiring:**
```
CC1101 Pin    →  Raspberry Pi Pin
────────────────────────────────
VCC           →  Pin 1 (3.3V) ⚠️ CRITICAL!
GND           →  Pin 6 or 9 (GND)
SCLK          →  Pin 23 (GPIO 11)
MOSI          →  Pin 19 (GPIO 10)
MISO          →  Pin 21 (GPIO 9)
CSN           →  Pin 24 (GPIO 8)
GDO0          →  Pin 11 (GPIO 17)
GDO2          →  Pin 31 (GPIO 6)
```

**Action Required:**
1. **Check VCC connection** - MUST be 3.3V, NOT 5V!
2. **Verify GND connection** - Essential for circuit
3. **Re-seat all jumper wires** - Ensure firm connection
4. **Retest after fixing wiring**

---

### ✅ Signal Capture System - WORKING

**Test Method:** Captured 5-second signal at 433.92 MHz

**Results:**
```
Capture Name: testNumber1
Frequency: 433.92 MHz
Duration: 5 seconds
File Size: 20 MB
Sample Rate: 2.048 MS/s
Samples: 10,240,000
Format: .cu8 (complex unsigned 8-bit)
```

**File Locations:**
```
~/piflip/captures/testNumber1.cu8   (raw IQ data)
~/piflip/captures/testNumber1.json  (metadata)
```

**Capabilities Verified:**
- rtl_sdr capture ✅
- Metadata storage ✅
- File management ✅

**Next Steps:**
- Decode with URH
- Test replay with CC1101 (once wired correctly)
- Build signal library

---

## Quick Retest Commands

### Test PN532
```bash
python3 -c "
import board, busio
from adafruit_pn532.i2c import PN532_I2C
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
print(f'PN532 v{pn532.firmware_version[1]}.{pn532.firmware_version[2]}')
"
```

### Test RTL-SDR
```bash
sudo systemctl stop dump1090-fa
rtl_test -t
```

### Test CC1101 (After Fixing Wiring)
```bash
python3 -c "
import spidev, time
spi = spidev.SpiDev()
spi.open(0, 0)
spi.xfer2([0x30])  # Reset
time.sleep(0.1)
part = spi.xfer2([0x30 | 0x80, 0x00])[1]
ver = spi.xfer2([0x31 | 0x80, 0x00])[1]
print(f'Part: 0x{part:02X}, Version: 0x{ver:02X}')
print('Expected: Part: 0x00, Version: 0x14')
spi.close()
"
```

### Test Signal Capture
```bash
# Make sure dump1090 is stopped
sudo systemctl stop dump1090-fa

# Capture 5 seconds at 433.92 MHz
rtl_sdr -f 433920000 -s 2048000 -n 10240000 ~/piflip/captures/test.cu8
ls -lh ~/piflip/captures/test.cu8
```

---

## Overall Assessment

### Working (3/4):
- ✅ PN532 NFC - Ready for use
- ✅ RTL-SDR - Ready for use
- ✅ Signal Capture - Ready for use

### Needs Attention (1/4):
- ⚠️ CC1101 - Check power wiring (VCC + GND)

### Success Rate: 75%

**Recommendation:**
1. **Priority 1:** Fix CC1101 wiring (check VCC connection!)
2. **Priority 2:** Test NFC with actual card
3. **Priority 3:** Test live 433MHz scanning
4. **Priority 4:** Install URH for signal analysis

---

## Next Session Goals

1. **Fix CC1101 wiring** → See Part: 0x00, Version: 0x14
2. **Test CC1101 transmission** → Send test signal
3. **Capture + Replay workflow** → Full loop test
4. **NFC card operations** → Read/clone test
5. **Web interface testing** → Verify all APIs

---

## Hardware Health Check

**What's Working:**
- ✅ I2C bus (PN532)
- ✅ USB (RTL-SDR)
- ✅ SPI bus (communicating, but CC1101 not responding)
- ✅ File system (captures saving)
- ✅ Python environment

**What Needs Fixing:**
- ⚠️ CC1101 power connection (critical!)

---

## Troubleshooting Tips

### CC1101 Wiring Debug Checklist:

**Step 1: Visual Inspection**
- [ ] Check VCC wire is on Pin 1 or 17 (3.3V)
- [ ] Check GND wire is on Pin 6, 9, 14, 20, 25, 30, 34, or 39
- [ ] Verify no wires on Pin 2 or 4 (5V - will damage CC1101!)
- [ ] Ensure all jumpers are firmly seated

**Step 2: Multimeter Test** (if available)
- [ ] Measure voltage on CC1101 VCC pin: Should be ~3.3V
- [ ] Measure continuity from CC1101 GND to Pi GND
- [ ] Check SPI pins for connectivity

**Step 3: Re-wire from Scratch**
- Remove all CC1101 connections
- Re-connect one wire at a time
- Double-check each connection
- Test after all wires connected

**Expected Result After Fix:**
```
Part Number: 0x00
Version: 0x14
Status: CC1101 is WORKING! ✅
```

---

**Test Conducted By:** Automated Hardware Test Suite
**Platform:** Raspberry Pi 3B
**OS:** Linux 6.1.21-v7+
**Python:** 3.9

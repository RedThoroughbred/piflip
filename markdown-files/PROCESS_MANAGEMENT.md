# PiFlip Process Management Guide

**Last Updated:** October 2, 2025

---

## 🎯 Understanding Process Conflicts

### The RTL-SDR Limitation

**KEY CONCEPT:** Only ONE process can use the RTL-SDR dongle at a time!

The RTL-SDR USB device can only be claimed by a single process. If multiple programs try to access it, you'll see:
```
usb_claim_interface error -6
EBUSY: Device or resource busy
```

---

## 🔄 Current Boot Configuration

### Services That Auto-Start:

#### 1. **piflip.service** ✅ Running
```
Status: Active (running)
Description: PiFlip Web Interface
Started: On boot
User: seth
Process: /home/seth/piflip/piflip_env/bin/python web_interface.py
Port: 5000
```

**What it does:**
- Starts Flask web server on boot
- Provides web UI at http://192.168.86.141:5000
- Does NOT claim RTL-SDR at startup
- Only uses RTL-SDR when you trigger scans/captures

#### 2. **dump1090-fa.service** ⚠️ Enabled but Stopped
```
Status: Inactive (dead)
Description: dump1090 ADS-B receiver (FlightAware)
Auto-start: Enabled (will start on next boot)
User: dump1090
Process: /usr/bin/dump1090-fa
Port: 8080 (web interface), 30001-30005 (data feeds)
```

**What it does:**
- Monitors 1090MHz for aircraft ADS-B signals
- **CLAIMS RTL-SDR EXCLUSIVELY** when running
- Serves flight map at http://192.168.86.141:8080
- Prevents 433MHz scanning while active

---

## ⚠️ The Conflict Explained

### Why They Conflict:

```
RTL-SDR USB Dongle
       |
       ├─ Option A: dump1090-fa (1090MHz flight tracking)
       |            └─ Blocks piflip from using RTL-SDR
       |
       └─ Option B: piflip (433MHz/TPMS/Weather scanning)
                    └─ Blocks dump1090 from using RTL-SDR
```

**You must choose ONE at a time:**
- **Flight Mode:** dump1090-fa running → Can track flights, CANNOT scan 433MHz
- **Scanning Mode:** dump1090-fa stopped → Can scan 433MHz, CANNOT track flights

### What Doesn't Conflict:

✅ **NFC operations** - Uses I2C (PN532), completely independent
✅ **CC1101 operations** - Uses SPI, completely independent
✅ **Web interface** - Just serves HTTP, doesn't touch hardware directly

---

## 🎛️ Controlling the Services

### Method 1: Via Web Interface (Easiest)

The web interface has a "Switch Mode" button that automatically:
- Stops dump1090-fa for scanning mode
- Starts dump1090-fa for flight mode

**API Endpoint:**
```bash
curl -X POST http://localhost:5000/api/rtlsdr/toggle
```

### Method 2: Manual Control (systemctl)

**Stop dump1090 (for 433MHz scanning):**
```bash
sudo systemctl stop dump1090-fa
```

**Start dump1090 (for flight tracking):**
```bash
sudo systemctl start dump1090-fa
```

**Check status:**
```bash
systemctl status dump1090-fa
systemctl status piflip
```

**Disable auto-start on boot:**
```bash
sudo systemctl disable dump1090-fa
```

**Enable auto-start on boot:**
```bash
sudo systemctl enable dump1090-fa
```

### Method 3: Restart Behavior

**Current boot behavior:**
- ✅ `piflip.service` → Always starts
- ⚠️ `dump1090-fa.service` → Currently enabled (will start on next reboot)

**If both try to start on boot:**
- dump1090-fa starts first (system service)
- Piflip web interface starts, but RTL-SDR scans will fail
- You'll see "RTL-SDR is busy" errors until you stop dump1090

---

## 🔧 Recommended Configuration

### Option 1: Flight Mode by Default (Current)
```bash
# dump1090 starts on boot
sudo systemctl enable dump1090-fa

# Result:
# - Boot → Flight tracking active
# - 433MHz scanning requires manual mode switch
```

**Best for:** Users who primarily want flight tracking

### Option 2: Scanning Mode by Default (Recommended for PiFlip)
```bash
# Disable dump1090 auto-start
sudo systemctl disable dump1090-fa

# Result:
# - Boot → RTL-SDR available for scanning
# - Flight tracking requires manual start
```

**Best for:** Users who primarily want RF scanning/capture

### Option 3: Manual Control Only
```bash
# Disable both from auto-starting
sudo systemctl disable dump1090-fa
sudo systemctl disable piflip

# Start manually when needed:
sudo systemctl start piflip
sudo systemctl start dump1090-fa  # Only if not using RTL-SDR for scanning
```

**Best for:** Advanced users who want full control

---

## 📊 Service Dependencies

### PiFlip Service Dependencies:

**Required:**
- ✅ Network (After=network.target)
- ✅ Python environment (/home/seth/piflip/piflip_env)
- ✅ I2C enabled (for PN532)
- ✅ SPI enabled (for CC1101)

**Optional (doesn't block startup):**
- RTL-SDR (used on-demand)
- dump1090 (toggled as needed)

### What Piflip Actually Uses:

**Always used:**
- Flask web server (port 5000)
- PN532 via I2C (if accessing NFC)
- CC1101 via SPI (if accessing RF transmit)

**Used on-demand:**
- RTL-SDR via USB (only during scans/captures)
- dump1090 API (only when checking flight mode)

---

## 🗑️ Unnecessary Services to Consider Disabling

### Services You Probably Don't Need:

```bash
# Printing services (if no printer)
sudo systemctl disable cups.service
sudo systemctl disable cups-browsed.service

# Bluetooth (if not using)
sudo systemctl disable bluetooth.service

# PostgreSQL (if not using database)
sudo systemctl disable postgresql.service

# Modem Manager (if no cellular modem)
sudo systemctl disable ModemManager.service
```

**Check what's using resources:**
```bash
systemctl list-units --type=service --state=running
```

---

## 🚀 Optimizing for PiFlip

### Recommended Boot Configuration:

1. **Enable piflip to start on boot:**
```bash
sudo systemctl enable piflip.service
```

2. **Disable dump1090 auto-start** (start manually when needed):
```bash
sudo systemctl disable dump1090-fa
```

3. **Keep essential services:**
- ssh (remote access)
- dhcpcd (networking)
- lighttpd (if using PiAware web features)

4. **Disable unnecessary services:**
```bash
# List enabled services
systemctl list-unit-files --state=enabled

# Disable ones you don't need
sudo systemctl disable <service-name>
```

---

## 🔍 Troubleshooting

### "RTL-SDR is busy" Error

**Check what's using it:**
```bash
# Check if dump1090 is running
systemctl status dump1090-fa

# Check all processes using RTL-SDR
lsusb | grep RTL
ps aux | grep dump1090
ps aux | grep rtl_
```

**Solution:**
```bash
sudo systemctl stop dump1090-fa
```

### Web Interface Won't Start

**Check service status:**
```bash
systemctl status piflip.service
journalctl -u piflip.service -n 50
```

**Common issues:**
- Virtual environment missing
- Port 5000 already in use
- Python dependencies not installed
- I2C/SPI not enabled

**Restart service:**
```bash
sudo systemctl restart piflip.service
```

### Both Services Start on Boot (Conflict)

**Disable dump1090 auto-start:**
```bash
sudo systemctl disable dump1090-fa
sudo systemctl stop dump1090-fa
```

**Or disable piflip if you prefer flight-only:**
```bash
sudo systemctl disable piflip
```

---

## 📝 Service Files Location

**Piflip service:**
```
/etc/systemd/system/piflip.service
```

**Dump1090 service:**
```
/lib/systemd/system/dump1090-fa.service
```

**View service file:**
```bash
systemctl cat piflip.service
systemctl cat dump1090-fa.service
```

**Reload after editing:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart piflip.service
```

---

## 🎯 Quick Reference

### Current Status:
```bash
systemctl status piflip dump1090-fa
```

### Switch to Scanning Mode:
```bash
sudo systemctl stop dump1090-fa
```

### Switch to Flight Mode:
```bash
sudo systemctl start dump1090-fa
```

### View Logs:
```bash
# PiFlip logs
journalctl -u piflip.service -f

# dump1090 logs
journalctl -u dump1090-fa.service -f
```

### Check RTL-SDR:
```bash
rtl_test -t
lsusb | grep RTL
```

---

## 🔒 Security Notes

**Piflip service runs as:**
- User: `seth` (your user account)
- Has access to GPIO, I2C, SPI (via groups)
- Does NOT require root

**Dump1090 service runs as:**
- User: `dump1090` (dedicated service account)
- Has access to RTL-SDR USB device
- Does NOT require root

**Sudo access needed for:**
- Starting/stopping services
- Enabling/disabling auto-start
- Not needed for web interface usage

---

## 📖 Summary

**Key Takeaways:**
1. ✅ Piflip runs on boot, provides web interface
2. ⚠️ dump1090-fa enabled but stopped (will start on reboot)
3. ⚠️ Only ONE can use RTL-SDR at a time
4. ✅ NFC and CC1101 always work (independent hardware)
5. 💡 Recommended: Disable dump1090 auto-start, enable manually when needed

**Best Practice:**
- Default to scanning mode (dump1090 disabled)
- Start dump1090 manually when tracking flights
- Use web interface to toggle modes

**Your system is well-configured!** Just decide which mode you want by default on boot.

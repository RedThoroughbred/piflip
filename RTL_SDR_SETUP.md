# RTL-SDR Setup & Troubleshooting 📻

## ✅ Current Status

Your RTL-SDR is **connected and working**:
- **Device:** RTLSDRBlog Blog V4
- **Chipset:** RTL2832U with R828D tuner
- **Status:** Detected by system
- **Service:** PiFlip web interface auto-starts on boot

---

## 🚀 Quick Start

### **Access RTL-SDR Features:**

1. **Open PiFlip Web Interface** - http://piflip.local:5000 (or Pi's IP:5000)
2. **Main Menu → Spectrum Analyzer**
3. Choose from:
   - ⚡ **Quick Scan** - Fast 433MHz snapshot
   - 🌊 **Waterfall Display** - PortaPack-style live view
   - 🎛️ **Custom Frequency Scan** - Choose your frequency
   - 🔄 **Reset RTL-SDR** - Fix stuck scans ← NEW!

---

## 🔧 RTL-SDR Reset Feature

### **When to Use:**
- Scans hang or timeout
- "RTL-SDR busy" errors
- Device not responding
- After SDR++ or other software closes

### **What It Does:**
1. Kills stuck RTL processes (rtl_power, rtl_fm, etc.)
2. Resets USB device
3. Clears device locks
4. Tests device is responsive

### **How to Use:**
```
1. Spectrum Analyzer menu
2. Click: Reset RTL-SDR
3. Confirm the reset
4. Wait 5-10 seconds
5. Device ready!
```

### **If Reset Fails:**
```
Manual reset:
1. Unplug RTL-SDR from USB
2. Wait 5 seconds
3. Plug back in
4. Try reset again
```

---

## 📊 RTL-SDR Capabilities

### **Frequency Range:**
- **24 MHz - 1.7 GHz** (wideband coverage)
- Common bands:
  - FM Radio: 88-108 MHz
  - Air Band: 108-137 MHz
  - 2m Ham: 144-148 MHz
  - Weather Satellites: 137 MHz
  - 433 MHz ISM: 433.05-434.79 MHz
  - 868 MHz ISM: 863-870 MHz
  - GPS L1: 1575.42 MHz

### **Features:**
- Real-time spectrum display
- Waterfall visualization
- Signal detection & peak finding
- Wide frequency coverage
- High sample rate (up to 2.4 MS/s)

### **Limitations:**
- **RX only** (receive, no transmit)
- Not for precise frequency decoding (use CC1101 for that)
- Best for wideband scanning and monitoring

---

## 🔍 Troubleshooting

### **Problem: "RTL-SDR busy or not available"**

**Cause:** Another program is using the RTL-SDR

**Solutions:**
1. Use **Reset RTL-SDR** button (easiest)
2. Check if SDR++ is running on your Mac
3. Kill processes manually:
   ```bash
   sudo killall -9 rtl_power rtl_fm rtl_sdr rtl_tcp
   ```

### **Problem: Scan timeouts**

**Cause:** Device locked or USB issue

**Solutions:**
1. Use **Reset RTL-SDR** button
2. Unplug/replug USB
3. Try different USB port
4. Check USB power (use powered hub if needed)

### **Problem: "No data received"**

**Cause:** Weak signals or antenna issue

**Solutions:**
1. Check antenna is connected
2. Try different frequency
3. Move antenna to better location
4. Increase integration time

### **Problem: Device not detected**

**Check device:**
```bash
# Should show: "RTLSDRBlog, Blog V4"
lsusb | grep -i rtl

# Should show: "Found 1 device"
rtl_test -t
```

**If not detected:**
1. Unplug and replug USB
2. Try different USB port
3. Check USB cable
4. Reboot Pi if needed

---

## 🆚 RTL-SDR vs CC1101

### **Use RTL-SDR when:**
- Wide frequency range (24 MHz - 1.7 GHz)
- Spectrum scanning
- Signal discovery
- Wideband monitoring
- Visualizing signals
- Verifying TX (watch CC1101 transmit)

### **Use CC1101 when:**
- Need to transmit (300-928 MHz)
- Sub-GHz capture for replay
- Precise frequency work
- Advanced TX features (fuzz, variations)

### **Use BOTH together:**
```
Perfect workflow:
1. RTL-SDR: Find signals (wideband scan)
2. CC1101: Capture signal (timing data)
3. CC1101: Replay/transmit
4. RTL-SDR: Verify transmission (waterfall)
```

---

## ⚙️ Service Configuration

### **Auto-Start on Boot:**
```bash
# Service is enabled and running:
sudo systemctl status piflip.service

# Service file location:
/etc/systemd/system/piflip.service

# Manual control:
sudo systemctl start piflip.service
sudo systemctl stop piflip.service
sudo systemctl restart piflip.service
```

### **Service Details:**
```ini
[Unit]
Description=PiFlip Web Interface
After=network.target

[Service]
Type=simple
User=seth
WorkingDirectory=/home/seth/piflip
ExecStart=/home/seth/piflip/piflip_env/bin/python /home/seth/piflip/web_interface.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**What this means:**
- PiFlip starts automatically after network is ready
- Runs as user `seth`
- Restarts automatically if crashes
- Starts on every boot

---

## 🔌 USB Extension Cable

### **Why You Might Need One:**
- RTL-SDR generates heat
- Move dongle away from Pi's heat
- Better antenna positioning
- Reduce USB interference

### **Recommendations:**
- USB 2.0 extension (USB 3.0 can cause interference)
- 1-3 feet length (too long = signal loss)
- Shielded cable (reduces noise)

### **Testing:**
```
With extension:
1. Plug RTL-SDR into extension
2. Plug extension into Pi
3. Run: rtl_test -t
4. Should still show "Found 1 device"

If not detected = cable too long or bad quality
```

---

## 📱 Web Interface Access

### **From Same Network:**
```
http://piflip.local:5000
or
http://<pi-ip-address>:5000
```

### **Check Pi's IP:**
```bash
hostname -I
```

### **Access from Mac/Phone:**
```
Make sure both devices on same WiFi
Open browser: http://piflip.local:5000
```

---

## 🎯 Common Use Cases

### **1. Find Unknown Signal:**
```
1. Spectrum Analyzer → Quick Scan
2. Press remote/transmitter
3. Note peak frequency
4. Use Custom Scan at that frequency
5. Capture with CC1101 for replay
```

### **2. Monitor ISM Band:**
```
1. Custom Scan: 433.92 MHz, Span 2 MHz
2. Waterfall Display for live view
3. Watch for activity
4. Note active frequencies
```

### **3. Verify CC1101 TX:**
```
1. SDR++ on Mac: Set to 433.92 MHz
2. PiFlip: Transmit with CC1101
3. Watch waterfall for bursts
4. Confirms TX working!
```

---

## 🛠️ Advanced: Manual Reset Methods

### **Method 1: usbreset (Already Installed)**
```bash
# Reset RTL-SDR USB device:
sudo usbreset 0bda:2838
```

### **Method 2: USB Driver Unbind/Bind**
```bash
# Unbind device:
echo "0bda 2838" | sudo tee /sys/bus/usb/drivers/dvb_usb_rtl28xxu/unbind

# Wait 2 seconds
sleep 2

# Rebind device:
echo "0bda 2838" | sudo tee /sys/bus/usb/drivers/dvb_usb_rtl28xxu/bind
```

### **Method 3: Kill All RTL Processes**
```bash
# Kill everything using RTL-SDR:
sudo killall -9 rtl_power rtl_fm rtl_sdr rtl_tcp rtl_test

# Test device:
rtl_test -t
```

---

## ✅ Installation Checklist

**Confirm everything is working:**

Hardware:
- [x] RTL-SDR plugged into USB
- [x] Antenna connected to RTL-SDR
- [ ] USB extension (optional, recommended)

Software:
- [x] RTL-SDR drivers installed
- [x] rtl-sdr tools installed (rtl_power, rtl_test)
- [x] PiFlip service enabled
- [x] Service auto-starts on boot

Web Interface:
- [x] Can access at piflip.local:5000
- [x] Spectrum Analyzer menu visible
- [x] Reset RTL-SDR button present

Testing:
- [ ] Quick Scan works
- [ ] Waterfall Display works
- [ ] Reset RTL-SDR button works
- [ ] Service survives reboot

---

## 📚 Related Documentation

- **`TX_VERIFICATION_GUIDE.md`** - How to verify TX works with SDR++
- **`SIGNAL_TYPES_EXPLAINED.md`** - RTL-SDR vs CC1101 captures
- **`ADVANCED_FEATURES_GUIDE.md`** - Advanced TX features guide
- **`WHATS_NEW.md`** - Recent feature additions

---

## 💡 Pro Tips

### **Tip 1: Keep SDR++ Handy**
```
Run SDR++ on your Mac while using PiFlip
Perfect for verifying transmissions
See TX in real-time
```

### **Tip 2: Use Reset Before Long Scans**
```
Reset RTL-SDR before important scans
Ensures clean state
Reduces timeout errors
```

### **Tip 3: USB Power Matters**
```
RTL-SDR needs good USB power
Use powered USB hub if issues
Avoid long/cheap USB extensions
```

### **Tip 4: Heat Management**
```
RTL-SDR gets hot during use
USB extension helps cooling
Don't stack near Pi's heat
```

---

## 🆘 Getting Help

**If you encounter issues:**

1. Try **Reset RTL-SDR** button first
2. Check device: `rtl_test -t`
3. Check service: `sudo systemctl status piflip`
4. Unplug/replug USB if needed
5. Reboot Pi as last resort

**Logs to check:**
```bash
# Service logs:
journalctl -u piflip.service -n 50

# RTL-SDR test:
rtl_test -t

# USB devices:
lsusb
```

---

**Your RTL-SDR is ready to use! 📻✨**

# PiFlip Installation Guide

Complete installation guide for setting up PiFlip on a fresh Raspberry Pi.

---

## 📋 Prerequisites

### Hardware Required:
- **Raspberry Pi 3B or 4** (2GB+ RAM recommended)
- **microSD card** (32GB+ recommended)
- **5V 3A power supply** (official Raspberry Pi PSU recommended)
- **RTL-SDR Blog V4** (or compatible RTL-SDR dongle)
- **CC1101 module** (433MHz transceiver)
- **PN532 NFC module** (I2C version)
- Antenna for RTL-SDR
- USB cable for RTL-SDR (extension recommended)

### Cost Breakdown:
- Raspberry Pi 3B: $35
- RTL-SDR Blog V4: $35
- CC1101 module: $3
- PN532 NFC module: $10
- microSD 32GB: $10
- 3A Power Supply: $10
- **Total: ~$103**

---

## 🚀 Quick Install (For Clean Raspberry Pi OS)

### Method 1: Automated Install Script

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/piflip.git
cd piflip

# Run installation script
./install.sh

# Reboot
sudo reboot
```

The script will:
- ✅ Install system dependencies (RTL-SDR tools, I2C, SPI)
- ✅ Enable I2C and SPI interfaces
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Set up systemd service (auto-start on boot)
- ✅ Configure sudoers (for mode switching)
- ✅ Optionally install dump1090-fa (flight tracking)

---

## 📝 Manual Installation

If you prefer manual setup or need to troubleshoot:

### 1. Install System Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install RTL-SDR tools
sudo apt-get install -y rtl-sdr librtlsdr-dev rtl-433

# Install I2C/SPI tools
sudo apt-get install -y i2c-tools python3-dev python3-smbus

# Install build tools
sudo apt-get install -y build-essential libi2c-dev libusb-1.0-0-dev cmake git

# Install Python pip
sudo apt-get install -y python3-pip python3-venv
```

### 2. Enable Hardware Interfaces

```bash
# Enable I2C and SPI
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Or manually edit /boot/config.txt:
sudo nano /boot/config.txt
# Add these lines:
# dtparam=i2c_arm=on
# dtparam=spi=on
```

### 3. Add User to Groups

```bash
sudo usermod -a -G gpio,i2c,spi,dialout $USER

# Logout and login for group changes to take effect
```

### 4. Clone Repository

```bash
cd ~
git clone https://github.com/YOUR-USERNAME/piflip.git
cd piflip
```

### 5. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv piflip_env

# Activate it
source piflip_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Install dump1090-fa (Optional - For Flight Tracking)

```bash
# Add FlightAware repository
wget -O - https://www.flightaware.com/adsb/piaware/files/flightaware.gpg.key | sudo apt-key add -
echo "deb https://www.flightaware.com/adsb/piaware/repository bookworm piaware" | sudo tee /etc/apt/sources.list.d/piaware.list

# Install
sudo apt-get update
sudo apt-get install -y dump1090-fa

# Disable auto-start (piflip will manage it)
sudo systemctl disable dump1090-fa
```

### 7. Set Up Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/piflip.service
```

Paste this content:
```ini
[Unit]
Description=PiFlip Web Interface
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/piflip
ExecStart=/home/YOUR_USERNAME/piflip/piflip_env/bin/python /home/YOUR_USERNAME/piflip/web_interface.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual username!

```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable piflip.service
```

### 8. Configure Sudoers (For Mode Switching)

```bash
# Create sudoers file
sudo nano /etc/sudoers.d/piflip
```

Paste this content (replace YOUR_USERNAME):
```
# Allow user to control dump1090-fa for PiFlip mode switching
YOUR_USERNAME ALL=(ALL) NOPASSWD: /bin/systemctl start dump1090-fa
YOUR_USERNAME ALL=(ALL) NOPASSWD: /bin/systemctl stop dump1090-fa
YOUR_USERNAME ALL=(ALL) NOPASSWD: /bin/systemctl restart dump1090-fa
YOUR_USERNAME ALL=(ALL) NOPASSWD: /bin/systemctl status dump1090-fa
```

```bash
# Set correct permissions
sudo chmod 0440 /etc/sudoers.d/piflip
```

### 9. Reboot

```bash
sudo reboot
```

---

## 🔌 Hardware Connection

### After Reboot - Connect Hardware

#### PN532 (I2C) - NFC Module

```
PN532 → Raspberry Pi
VCC   → Pin 1 (3.3V)
GND   → Pin 6 (GND)
SDA   → Pin 3 (GPIO 2)
SCL   → Pin 5 (GPIO 3)
```

**Verify connection:**
```bash
i2cdetect -y 1
# Should see device at address 0x24
```

#### CC1101 (SPI) - Sub-GHz Transceiver

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

**Verify connection:**
```bash
ls /dev/spi*
# Should see /dev/spidev0.0
```

#### RTL-SDR (USB) - Wideband Receiver

```
RTL-SDR → Pi USB port
Antenna → RTL-SDR SMA connector
```

**Verify connection:**
```bash
rtl_test -t
# Should detect RTL-SDR and show device info
```

---

## ✅ Verification

### 1. Check Service Status

```bash
systemctl status piflip
# Should show: active (running)
```

### 2. Access Web Interface

Open browser to:
```
http://YOUR_PI_IP:5000
```

Find your Pi's IP:
```bash
hostname -I
```

### 3. Run Hardware Tests

Navigate to:
```
http://YOUR_PI_IP:5000/test
```

Click "RUN ALL TESTS" - all should pass ✅

### 4. Test Individual Components

**Test NFC:**
```bash
curl http://localhost:5000/api/nfc
# Place card on reader
```

**Test RTL-SDR:**
```bash
rtl_test -t
# Should show device info with no errors
```

**Test 433MHz Scan:**
```bash
# Via web interface: RF Tools → Scan 433MHz
# Or API:
curl http://localhost:5000/api/scan433
```

---

## 🐛 Troubleshooting

### I2C Not Detected

```bash
# Check if I2C is enabled
ls /dev/i2c*
# Should see /dev/i2c-1

# If not, enable:
sudo raspi-config
# Interface Options → I2C → Enable

# Reboot
sudo reboot
```

### SPI Not Detected

```bash
# Check if SPI is enabled
ls /dev/spi*
# Should see /dev/spidev0.0 and /dev/spidev0.1

# If not, enable:
sudo raspi-config
# Interface Options → SPI → Enable

# Reboot
sudo reboot
```

### RTL-SDR "Device Busy" Error

```bash
# Check if dump1090 is running
systemctl status dump1090-fa

# If running, stop it:
sudo systemctl stop dump1090-fa
```

### PN532 Not Found (0x24 missing in i2cdetect)

**Check:**
1. Wiring is correct (SDA→Pin 3, SCL→Pin 5)
2. PN532 is in I2C mode (DIP switches on module)
3. Power connections secure
4. Try different I2C address (0x48 for some modules)

```bash
# Slow down I2C bus (some modules need this)
sudo nano /boot/config.txt
# Add: dtparam=i2c_arm_baudrate=10000
sudo reboot
```

### Under-Voltage Warning

```bash
# Check for under-voltage
vcgencmd get_throttled
# Should show: 0x0 or 0x50000

# If 0x50005 = under-voltage!
# Solution: Use 3A power supply
```

### Web Interface Won't Start

```bash
# Check logs
journalctl -u piflip.service -n 50

# Common issues:
# - Virtual environment missing: Create it
# - Port 5000 in use: Change port in web_interface.py
# - Dependencies missing: pip install -r requirements.txt
```

### Permission Denied Errors

```bash
# Make sure user is in correct groups
groups
# Should show: gpio i2c spi dialout

# If not:
sudo usermod -a -G gpio,i2c,spi,dialout $USER
# Logout and login
```

---

## 📚 Post-Installation

### Configure Default Mode

**Decide which mode you want on boot:**

**Option A: Scanning Mode (Recommended)**
```bash
# Disable dump1090 auto-start
sudo systemctl disable dump1090-fa

# Result: RTL-SDR available for 433MHz scanning by default
```

**Option B: Flight Mode**
```bash
# Enable dump1090 auto-start
sudo systemctl enable dump1090-fa

# Result: Flight tracking active by default
```

See [PROCESS_MANAGEMENT.md](PROCESS_MANAGEMENT.md) for details.

### Access Points

After installation, access:
- **Web UI:** http://YOUR_PI_IP:5000
- **Test Suite:** http://YOUR_PI_IP:5000/test
- **Flight Map:** http://YOUR_PI_IP:8080 (if dump1090 installed)

### Documentation

Read these guides:
- [README.md](../README.md) - Main documentation
- [QUICK_START.md](QUICK_START.md) - Getting started
- [INTERFACE_GUIDE.md](INTERFACE_GUIDE.md) - Using the web interface
- [PROCESS_MANAGEMENT.md](PROCESS_MANAGEMENT.md) - Service management
- [claude.md](../claude.md) - Complete project context

---

## 🔄 Updating PiFlip

```bash
cd ~/piflip

# Pull latest changes
git pull origin main

# Update dependencies
source piflip_env/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart piflip
```

---

## 🗑️ Uninstallation

```bash
# Stop and disable service
sudo systemctl stop piflip
sudo systemctl disable piflip

# Remove service file
sudo rm /etc/systemd/system/piflip.service
sudo systemctl daemon-reload

# Remove sudoers file
sudo rm /etc/sudoers.d/piflip

# Remove repository
rm -rf ~/piflip

# Optional: Remove dump1090
sudo apt-get remove --purge dump1090-fa
```

---

## 🎉 Installation Complete!

Your PiFlip is ready! Start with:
1. Web interface at http://YOUR_PI_IP:5000
2. Run hardware tests
3. Try capturing an RF signal or scanning an NFC card

**Need help?** Check [claude.md](../claude.md) for complete project overview.

**Happy hacking!** 🦊✨

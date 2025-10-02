#!/bin/bash
#
# PiFlip Installation Script
# For Raspberry Pi 3B/4 running Raspberry Pi OS
#
# Usage: ./install.sh
#

set -e  # Exit on error

echo "╔═══════════════════════════════════════╗"
echo "║   PiFlip Installation Script          ║"
echo "║   Raspberry Pi RF & NFC Multi-Tool    ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for root/sudo
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do NOT run this script as root!"
    echo "   Run as regular user. Script will use sudo when needed."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "📋 Checking prerequisites..."
echo ""

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 not found!"
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

# Check pip
if ! command_exists pip3; then
    echo "⚠️  pip3 not found, installing..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
echo "✅ pip3 installed"

# Check git
if ! command_exists git; then
    echo "⚠️  git not found, installing..."
    sudo apt-get install -y git
fi
echo "✅ git installed"

echo ""
echo "📦 Installing system dependencies..."
echo ""

# Update package list
sudo apt-get update

# Install RTL-SDR tools
echo "Installing RTL-SDR tools..."
sudo apt-get install -y \
    rtl-sdr \
    librtlsdr-dev \
    rtl-433

# Install I2C and SPI tools
echo "Installing I2C/SPI tools..."
sudo apt-get install -y \
    i2c-tools \
    python3-dev \
    python3-smbus

# Install build tools
echo "Installing build tools..."
sudo apt-get install -y \
    build-essential \
    libi2c-dev \
    libusb-1.0-0-dev \
    cmake

# Optional: Install dump1090-fa for flight tracking
read -p "Install dump1090-fa for flight tracking? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing dump1090-fa..."
    wget -O - https://www.flightaware.com/adsb/piaware/files/flightaware.gpg.key | sudo apt-key add -
    sudo sh -c 'echo "deb https://www.flightaware.com/adsb/piaware/repository bookworm piaware" > /etc/apt/sources.list.d/piaware.list'
    sudo apt-get update
    sudo apt-get install -y dump1090-fa

    # Disable auto-start (let user control it)
    sudo systemctl disable dump1090-fa
    echo "✅ dump1090-fa installed (disabled by default)"
fi

echo ""
echo "🔧 Configuring hardware interfaces..."
echo ""

# Enable I2C
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "Enabling I2C..."
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    echo "✅ I2C enabled (reboot required)"
else
    echo "✅ I2C already enabled"
fi

# Enable SPI
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "Enabling SPI..."
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "✅ SPI enabled (reboot required)"
else
    echo "✅ SPI already enabled"
fi

# Add user to groups
echo "Adding $USER to required groups..."
sudo usermod -a -G gpio,i2c,spi,dialout $USER
echo "✅ User added to groups (logout required)"

echo ""
echo "🐍 Setting up Python virtual environment..."
echo ""

# Create virtual environment
if [ ! -d "piflip_env" ]; then
    python3 -m venv piflip_env
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate and install requirements
source piflip_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

echo ""
echo "⚙️  Setting up systemd service..."
echo ""

# Create systemd service file
sudo tee /etc/systemd/system/piflip.service > /dev/null <<EOF
[Unit]
Description=PiFlip Web Interface
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/piflip_env/bin/python $(pwd)/web_interface.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable piflip.service

echo "✅ Service installed and enabled"

echo ""
echo "🔧 Configuring sudoers for mode switching..."
echo ""

# Allow user to control dump1090 without password (for mode switching)
if [ -f /usr/bin/systemctl ]; then
    sudo tee /etc/sudoers.d/piflip > /dev/null <<EOF
# Allow $USER to control dump1090-fa for PiFlip mode switching
$USER ALL=(ALL) NOPASSWD: /bin/systemctl start dump1090-fa
$USER ALL=(ALL) NOPASSWD: /bin/systemctl stop dump1090-fa
$USER ALL=(ALL) NOPASSWD: /bin/systemctl restart dump1090-fa
$USER ALL=(ALL) NOPASSWD: /bin/systemctl status dump1090-fa
EOF
    sudo chmod 0440 /etc/sudoers.d/piflip
    echo "✅ Sudoers configured for mode switching"
fi

echo ""
echo "📁 Creating data directories..."
echo ""

# Ensure directories exist
mkdir -p captures nfc_library backups rf_library decoded config

echo "✅ Data directories created"

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║   Installation Complete!              ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. REBOOT your Raspberry Pi:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, verify hardware:"
echo "   - I2C devices: i2cdetect -y 1"
echo "   - SPI devices: ls /dev/spi*"
echo "   - RTL-SDR: rtl_test -t"
echo ""
echo "3. Access web interface:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "4. Run hardware tests:"
echo "   http://$(hostname -I | awk '{print $1}'):5000/test"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Main documentation"
echo "   - markdown-files/SETUP.md - Detailed setup"
echo "   - markdown-files/PROCESS_MANAGEMENT.md - Service management"
echo "   - claude.md - Complete project context"
echo ""
echo "⚠️  Important:"
echo "   - Connect hardware AFTER reboot"
echo "   - PN532 on I2C (pins 3/5)"
echo "   - CC1101 on SPI (see docs for pinout)"
echo "   - RTL-SDR on USB"
echo "   - Use 3A power supply!"
echo ""
echo "🎉 Happy hacking!"

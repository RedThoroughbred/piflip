#!/bin/bash
# PiFlip Startup Script

echo "================================================"
echo "           PiFlip Control Center"
echo "================================================"
echo ""

# Check if dump1090-fa is running
echo "[*] Checking flight tracking service..."
if systemctl is-active --quiet dump1090-fa; then
    echo "    ✓ dump1090-fa is running"
else
    echo "    ⚠ dump1090-fa is not running"
    read -p "    Start dump1090-fa? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl start dump1090-fa
        echo "    ✓ Started dump1090-fa"
    fi
fi

echo ""
echo "[*] Starting web interface..."
echo ""

# Get IP address
IP=$(hostname -I | awk '{print $1}')

echo "================================================"
echo "  Access Points:"
echo "================================================"
echo "  Web Dashboard:  http://$IP:5000"
echo "  Flight Map:     http://$IP:8080"
echo "================================================"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

# Activate virtual environment and start Flask app
cd /home/seth/piflip
source piflip_env/bin/activate
python3 web_interface.py

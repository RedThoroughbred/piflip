# PiFlip WiFi Modes

PiFlip supports three WiFi operating modes for maximum flexibility:

## Operating Modes

### 1. 🏠 Client Mode (Home WiFi)
- **Use Case**: At home or places with known WiFi
- **Connection**: Pi connects to your WiFi network
- **Access**: `http://[pi-ip]:5000` from any device on network
- **Internet**: Available for updates, packages, etc.

### 2. 🔥 Hotspot Mode (Portable)
- **Use Case**: Hotels, field work, anywhere without WiFi
- **Connection**: Pi creates "PiFlip" WiFi network
- **Access**: `http://192.168.50.1:5000` from phone/laptop
- **Internet**: Not available (fully offline capable)
- **Credentials**:
  - SSID: `PiFlip`
  - Password: `piflip123`

### 3. 🤖 Auto Mode (Smart Switching)
- **Use Case**: Set it and forget it
- **Behavior**:
  - Connects to home WiFi when available
  - Falls back to hotspot when away from home
  - Won't interrupt active hotspot sessions
- **Configuration**: Runs automatically on boot

## Manual Control

### Check Current Status
```bash
./wifi_mode.sh status
```

### Switch to Hotspot Mode
```bash
sudo ./wifi_mode.sh hotspot
```

### Switch to Client Mode
```bash
sudo ./wifi_mode.sh client
```

### Toggle Between Modes
```bash
sudo ./wifi_mode.sh toggle
```

## Auto Mode Setup

### 1. Configure Your Home WiFi Name
Edit both scripts and replace `your_home_wifi_name` with your actual WiFi SSID:
```bash
nano wifi_mode.sh
nano wifi_auto_switch.sh
```

Find line:
```bash
HOME_WIFI_SSID="your_home_wifi_name"
```

Change to (example):
```bash
HOME_WIFI_SSID="MyHomeWiFi"
```

### 2. Install Auto-Switcher Service
```bash
sudo cp piflip-wifi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable piflip-wifi.service
sudo systemctl start piflip-wifi.service
```

### 3. Monitor Auto-Switcher
```bash
# View logs
sudo journalctl -u piflip-wifi -f

# Check status
sudo systemctl status piflip-wifi
```

## How Auto Mode Works

1. **At Home**:
   - Detects home WiFi network
   - Connects automatically
   - PiFlip accessible on home network

2. **Away from Home**:
   - Can't find home WiFi after 3 attempts
   - Automatically switches to hotspot mode
   - Creates "PiFlip" network for phone access

3. **Returning Home**:
   - Detects home WiFi is available
   - Waits for hotspot clients to disconnect
   - Switches back to home WiFi automatically

## Hotspot Configuration

### Change Hotspot Password
Edit `/etc/hostapd/hostapd.conf`:
```bash
sudo nano /etc/hostapd/hostapd.conf
```

Change:
```
wpa_passphrase=piflip123
```

Then restart:
```bash
sudo systemctl restart hostapd
```

### Change Hotspot Name (SSID)
In same file:
```
ssid=PiFlip
```

## Troubleshooting

### Hotspot won't start
```bash
# Check hostapd status
sudo systemctl status hostapd

# View logs
sudo journalctl -u hostapd -n 50
```

### Can't connect to home WiFi
```bash
# Check WiFi credentials
sudo cat /etc/wpa_supplicant/wpa_supplicant.conf

# Reconfigure
sudo wpa_cli -i wlan0 reconfigure
```

### Auto-switcher not working
```bash
# Check service status
sudo systemctl status piflip-wifi

# View detailed logs
sudo tail -f /var/log/piflip_wifi.log
```

## Power Consumption

| Mode | Power Draw | Notes |
|------|------------|-------|
| Client | ~150mA | Normal WiFi connection |
| Hotspot | ~200mA | Broadcasting WiFi network |
| Auto | ~150-200mA | Varies based on active mode |

## Security Notes

- Default hotspot password is `piflip123` - **CHANGE IT** for security
- Hotspot provides no internet access (isolated network)
- Only devices with password can connect
- Web interface has no authentication (add if deploying publicly)

## Tips

- **Battery Life**: Hotspot mode uses slightly more power than client mode
- **Range**: Hotspot range ~30ft (typical WiFi limitations)
- **Speed**: Local network speed is very fast (no internet latency)
- **Offline**: All RF/NFC tools work without internet in any mode

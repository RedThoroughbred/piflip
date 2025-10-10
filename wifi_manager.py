#!/usr/bin/env python3
"""
WiFi Manager for PiFlip
Manages WiFi modes: Client, Hotspot, and Auto-switch
Allows iPad/phone access without external network
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

class WiFiManager:
    """Manage WiFi client and hotspot modes"""

    def __init__(self):
        self.config_dir = Path.home() / 'piflip' / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'wifi_config.json'
        self.load_config()

    def load_config(self):
        """Load WiFi configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                'hotspot': {
                    'ssid': 'PiFlip-RF',
                    'password': 'piflip123',
                    'channel': 6,
                    'ip': '10.0.0.1',
                    'dhcp_range': '10.0.0.10,10.0.0.50'
                },
                'mode': 'client',  # client, hotspot, auto
                'auto_fallback_timeout': 30  # seconds
            }
            self.save_config()

    def save_config(self):
        """Save WiFi configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_current_mode(self):
        """Check current WiFi mode"""
        try:
            # Check if hostapd is running (hotspot mode)
            result = subprocess.run(
                ['systemctl', 'is-active', 'hostapd'],
                capture_output=True,
                text=True
            )

            if result.stdout.strip() == 'active':
                return 'hotspot'

            # Check if connected to WiFi (client mode)
            result = subprocess.run(
                ['iwgetid', '-r'],
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                return 'client'

            return 'disconnected'

        except Exception as e:
            return f'error: {e}'

    def get_wifi_status(self):
        """Get detailed WiFi status"""
        mode = self.get_current_mode()

        status = {
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        }

        if mode == 'client':
            # Get connected network info
            try:
                ssid_result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)
                status['connected_to'] = ssid_result.stdout.strip()

                # Get IP address
                ip_result = subprocess.run(
                    ['hostname', '-I'],
                    capture_output=True,
                    text=True
                )
                status['ip_address'] = ip_result.stdout.strip().split()[0]

            except:
                pass

        elif mode == 'hotspot':
            status['hotspot_ssid'] = self.config['hotspot']['ssid']
            status['hotspot_ip'] = self.config['hotspot']['ip']
            status['access_url'] = f"http://{self.config['hotspot']['ip']}:5000"

        return status

    def enable_hotspot(self):
        """Enable WiFi hotspot mode"""
        print("[*] Enabling WiFi hotspot mode...")

        try:
            # Create hostapd configuration
            hostapd_conf = f"""
interface=wlan0
driver=nl80211
ssid={self.config['hotspot']['ssid']}
hw_mode=g
channel={self.config['hotspot']['channel']}
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={self.config['hotspot']['password']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""

            # Write hostapd config
            with open('/tmp/hostapd_piflip.conf', 'w') as f:
                f.write(hostapd_conf)

            subprocess.run(['sudo', 'cp', '/tmp/hostapd_piflip.conf', '/etc/hostapd/hostapd.conf'])

            # Create dnsmasq configuration
            dnsmasq_conf = f"""
interface=wlan0
dhcp-range={self.config['hotspot']['dhcp_range']},255.255.255.0,24h
"""

            with open('/tmp/dnsmasq_piflip.conf', 'w') as f:
                f.write(dnsmasq_conf)

            subprocess.run(['sudo', 'cp', '/tmp/dnsmasq_piflip.conf', '/etc/dnsmasq.conf'])

            # Configure network interface
            subprocess.run(['sudo', 'ifconfig', 'wlan0', self.config['hotspot']['ip']])

            # Start services
            subprocess.run(['sudo', 'systemctl', 'start', 'hostapd'])
            subprocess.run(['sudo', 'systemctl', 'start', 'dnsmasq'])

            # Enable IP forwarding (optional - for internet sharing)
            subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'])

            time.sleep(2)

            # Update config
            self.config['mode'] = 'hotspot'
            self.save_config()

            return {
                'status': 'enabled',
                'mode': 'hotspot',
                'ssid': self.config['hotspot']['ssid'],
                'password': self.config['hotspot']['password'],
                'ip': self.config['hotspot']['ip'],
                'access_url': f"http://{self.config['hotspot']['ip']}:5000",
                'instructions': [
                    f"1. Connect to WiFi: {self.config['hotspot']['ssid']}",
                    f"2. Password: {self.config['hotspot']['password']}",
                    f"3. Open browser: http://{self.config['hotspot']['ip']}:5000",
                    "4. Use PiFlip from iPad, phone, or laptop!"
                ]
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def disable_hotspot(self):
        """Disable hotspot and return to client mode"""
        print("[*] Disabling hotspot, returning to client mode...")

        try:
            # Stop services
            subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'])
            subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'])

            # Restart networking
            subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'])

            time.sleep(2)

            # Update config
            self.config['mode'] = 'client'
            self.save_config()

            return {
                'status': 'disabled',
                'mode': 'client',
                'message': 'Hotspot disabled, reconnecting to WiFi...'
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def toggle_mode(self):
        """Toggle between client and hotspot modes"""
        current = self.get_current_mode()

        if current == 'hotspot':
            return self.disable_hotspot()
        else:
            return self.enable_hotspot()

    def scan_networks(self):
        """Scan for available WiFi networks"""
        try:
            # Make sure wlan0 is up
            subprocess.run(['sudo', 'ifconfig', 'wlan0', 'up'])

            # Scan
            result = subprocess.run(
                ['sudo', 'iwlist', 'wlan0', 'scan'],
                capture_output=True,
                text=True,
                timeout=10
            )

            networks = []
            current_network = {}

            for line in result.stdout.split('\n'):
                line = line.strip()

                if 'Cell' in line and 'Address' in line:
                    if current_network:
                        networks.append(current_network)
                    current_network = {}

                elif 'ESSID:' in line:
                    essid = line.split('ESSID:')[1].strip('"')
                    current_network['ssid'] = essid

                elif 'Quality=' in line:
                    # Parse signal quality
                    quality_part = line.split('Quality=')[1].split()[0]
                    current_network['quality'] = quality_part

                elif 'Encryption key:' in line:
                    encrypted = 'on' in line.lower()
                    current_network['encrypted'] = encrypted

            if current_network:
                networks.append(current_network)

            # Remove duplicates and empty SSIDs
            unique_networks = []
            seen = set()

            for net in networks:
                ssid = net.get('ssid', '')
                if ssid and ssid not in seen:
                    seen.add(ssid)
                    unique_networks.append(net)

            return {
                'status': 'success',
                'networks': unique_networks,
                'count': len(unique_networks)
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def connect_to_network(self, ssid, password=None):
        """Connect to a WiFi network"""
        try:
            # Create wpa_supplicant config
            if password:
                wpa_config = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""
            else:
                wpa_config = f"""
network={{
    ssid="{ssid}"
    key_mgmt=NONE
}}
"""

            # Append to wpa_supplicant config
            with open('/tmp/wpa_network.conf', 'w') as f:
                f.write(wpa_config)

            subprocess.run(['sudo', 'sh', '-c', 'cat /tmp/wpa_network.conf >> /etc/wpa_supplicant/wpa_supplicant.conf'])

            # Reconfigure wpa_supplicant
            subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])

            # Wait for connection
            time.sleep(5)

            # Check if connected
            result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)

            if ssid in result.stdout:
                return {
                    'status': 'connected',
                    'ssid': ssid,
                    'message': f'Connected to {ssid}'
                }
            else:
                return {
                    'status': 'failed',
                    'message': f'Failed to connect to {ssid}'
                }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}


class WiFiScanner:
    """WiFi network scanner and monitor"""

    def __init__(self):
        pass

    def scan_nearby_aps(self, duration=10):
        """Scan for nearby access points"""
        try:
            # Put interface in monitor mode (if supported)
            # Note: This may require specific WiFi adapter
            result = subprocess.run(
                ['sudo', 'timeout', str(duration), 'airodump-ng', 'wlan0mon', '--write-interval', '1', '-w', '/tmp/piflip_airodump', '--output-format', 'csv'],
                capture_output=True,
                text=True
            )

            # Parse airodump CSV if available
            # This is advanced - requires aircrack-ng installed

            return {
                'status': 'scan_complete',
                'note': 'Advanced WiFi scanning requires aircrack-ng and monitor mode'
            }

        except Exception as e:
            # Fallback to basic iwlist scan
            manager = WiFiManager()
            return manager.scan_networks()


if __name__ == '__main__':
    # Test WiFi manager
    manager = WiFiManager()

    print("[*] WiFi Manager Test")
    print("=" * 50)

    status = manager.get_wifi_status()
    print(f"\nCurrent mode: {status['mode']}")

    if status['mode'] == 'client':
        print(f"Connected to: {status.get('connected_to', 'N/A')}")
        print(f"IP address: {status.get('ip_address', 'N/A')}")

    print("\n[*] Scanning for networks...")
    scan_result = manager.scan_networks()

    if scan_result['status'] == 'success':
        print(f"[+] Found {scan_result['count']} networks:")
        for net in scan_result['networks'][:5]:
            print(f"  - {net['ssid']} ({net.get('quality', 'N/A')})")

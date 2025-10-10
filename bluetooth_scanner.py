#!/usr/bin/env python3
"""
Bluetooth Scanner Module for PiFlip
Supports both BLE and Bluetooth Classic scanning
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import re

class BluetoothScanner:
    """Bluetooth/BLE scanner using built-in Raspberry Pi Bluetooth"""

    def __init__(self):
        self.scan_results = []
        self.library_dir = Path.home() / 'piflip' / 'bluetooth_library'
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def check_bluetooth_available(self):
        """Check if Bluetooth is available and enabled"""
        try:
            result = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=2)
            return 'UP RUNNING' in result.stdout
        except:
            return False

    def enable_bluetooth(self):
        """Enable Bluetooth interface"""
        try:
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'], timeout=5)
            time.sleep(1)
            return True
        except:
            return False

    def reset_bluetooth(self):
        """
        Reset Bluetooth adapter completely
        Useful when scans stop working
        """
        try:
            # Kill any stuck processes
            subprocess.run(['sudo', 'killall', 'hcitool', 'btmon'],
                         stderr=subprocess.DEVNULL, timeout=3)
            time.sleep(0.5)

            # Reset adapter
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'down'], timeout=3)
            time.sleep(1)
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'], timeout=3)
            time.sleep(1)

            # Restart Bluetooth service
            subprocess.run(['sudo', 'systemctl', 'restart', 'bluetooth'], timeout=5)
            time.sleep(2)

            return {
                'status': 'success',
                'message': 'Bluetooth adapter reset successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Reset failed: {str(e)}'
            }

    def scan_ble_devices(self, duration=10):
        """
        Scan for BLE devices using hcitool
        Returns list of discovered devices with RSSI
        """
        devices = []

        try:
            # Enable Bluetooth if not already
            if not self.check_bluetooth_available():
                self.enable_bluetooth()

            print(f"[*] Starting BLE scan for {duration} seconds...")

            # Use hcitool for BLE scan
            proc = subprocess.Popen(
                ['sudo', 'timeout', str(duration), 'hcitool', 'lescan', '--duplicates'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Simultaneously get RSSI data
            time.sleep(1)  # Let scan start

            # Use bluetoothctl to get more details
            result = subprocess.run(
                ['sudo', 'timeout', str(duration - 1), 'btmon'],
                capture_output=True,
                text=True
            )

            proc.wait()

            # Parse hcitool output
            stdout, stderr = proc.communicate()

            seen_addresses = set()

            for line in stdout.split('\n'):
                if line.strip() and not line.startswith('LE Scan'):
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) >= 1:
                        addr = parts[0]
                        name = parts[1] if len(parts) > 1 else '(Unknown)'

                        if addr not in seen_addresses and ':' in addr:
                            seen_addresses.add(addr)
                            devices.append({
                                'address': addr,
                                'name': name,
                                'type': 'BLE',
                                'rssi': None,  # Will try to get this
                                'timestamp': datetime.now().isoformat()
                            })

            print(f"[+] Found {len(devices)} BLE devices")
            return {
                'status': 'success',
                'devices': devices,
                'count': len(devices),
                'scan_duration': duration,
                'type': 'BLE'
            }

        except Exception as e:
            print(f"[!] BLE scan error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'devices': [],
                'count': 0
            }

    def scan_classic_devices(self, duration=10):
        """
        Scan for Bluetooth Classic devices
        Returns list of discovered devices
        """
        devices = []

        try:
            # Enable Bluetooth if not already
            if not self.check_bluetooth_available():
                self.enable_bluetooth()

            print(f"[*] Starting Bluetooth Classic scan for {duration} seconds...")

            # Use hcitool scan
            result = subprocess.run(
                ['sudo', 'timeout', str(duration), 'hcitool', 'scan'],
                capture_output=True,
                text=True,
                timeout=duration + 5
            )

            # Parse output
            for line in result.stdout.split('\n'):
                if '\t' in line:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        addr = parts[0].strip()
                        name = parts[1].strip()

                        if ':' in addr:
                            devices.append({
                                'address': addr,
                                'name': name,
                                'type': 'Classic',
                                'timestamp': datetime.now().isoformat()
                            })

            print(f"[+] Found {len(devices)} Classic Bluetooth devices")
            return {
                'status': 'success',
                'devices': devices,
                'count': len(devices),
                'scan_duration': duration,
                'type': 'Classic'
            }

        except Exception as e:
            print(f"[!] Classic scan error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'devices': [],
                'count': 0
            }

    def scan_comprehensive(self, duration=15):
        """
        Comprehensive scan - both BLE and Classic
        """
        print("[*] Starting comprehensive Bluetooth scan...")

        # Scan BLE first (faster)
        ble_results = self.scan_ble_devices(duration // 2)

        # Then scan Classic
        classic_results = self.scan_classic_devices(duration // 2)

        all_devices = ble_results.get('devices', []) + classic_results.get('devices', [])

        return {
            'status': 'success',
            'devices': all_devices,
            'ble_count': ble_results.get('count', 0),
            'classic_count': classic_results.get('count', 0),
            'total_count': len(all_devices),
            'scan_duration': duration,
            'type': 'Comprehensive'
        }

    def get_device_info(self, address):
        """
        Get detailed information about a specific device
        """
        try:
            # Get device info using hcitool
            result = subprocess.run(
                ['sudo', 'hcitool', 'info', address],
                capture_output=True,
                text=True,
                timeout=10
            )

            info = {
                'address': address,
                'timestamp': datetime.now().isoformat()
            }

            # Parse output
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower().replace(' ', '_')] = value.strip()

            return info

        except Exception as e:
            return {'error': str(e)}

    def get_device_services(self, address, device_type='BLE'):
        """
        Enumerate services on a device
        """
        try:
            if device_type == 'BLE':
                # Use gatttool for BLE services
                result = subprocess.run(
                    ['sudo', 'timeout', '15', 'gatttool', '-b', address, '--primary'],
                    capture_output=True,
                    text=True,
                    timeout=20
                )

                services = []
                for line in result.stdout.split('\n'):
                    if 'attr handle' in line.lower():
                        services.append(line.strip())

                return {
                    'address': address,
                    'type': device_type,
                    'services': services,
                    'service_count': len(services)
                }
            else:
                # Use sdptool for Classic services
                result = subprocess.run(
                    ['sudo', 'timeout', '15', 'sdptool', 'browse', address],
                    capture_output=True,
                    text=True,
                    timeout=20
                )

                return {
                    'address': address,
                    'type': device_type,
                    'services_raw': result.stdout,
                    'status': 'success' if result.returncode == 0 else 'error'
                }

        except Exception as e:
            return {'error': str(e)}

    def monitor_device_rssi(self, address, duration=10):
        """
        Monitor RSSI (signal strength) of a device over time
        """
        rssi_data = []

        try:
            start_time = time.time()

            while time.time() - start_time < duration:
                # Get RSSI using hcitool
                result = subprocess.run(
                    ['sudo', 'hcitool', 'rssi', address],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                # Parse RSSI
                if 'RSSI return value:' in result.stdout:
                    rssi_str = result.stdout.split('RSSI return value:')[1].strip()
                    rssi = int(rssi_str)

                    rssi_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'rssi': rssi,
                        'elapsed': round(time.time() - start_time, 2)
                    })

                time.sleep(1)

            return {
                'address': address,
                'rssi_readings': rssi_data,
                'count': len(rssi_data),
                'duration': duration,
                'avg_rssi': sum(r['rssi'] for r in rssi_data) / len(rssi_data) if rssi_data else None
            }

        except Exception as e:
            return {'error': str(e)}

    def save_device(self, device_data, name):
        """Save device to library"""
        try:
            filename = f"{name}.json"
            filepath = self.library_dir / filename

            device_data['saved_name'] = name
            device_data['saved_timestamp'] = datetime.now().isoformat()

            with open(filepath, 'w') as f:
                json.dump(device_data, f, indent=2)

            return {
                'status': 'saved',
                'name': name,
                'path': str(filepath)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def list_saved_devices(self):
        """List all saved devices"""
        devices = []

        try:
            for json_file in sorted(self.library_dir.glob('*.json'),
                                   key=lambda x: x.stat().st_mtime,
                                   reverse=True):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        devices.append(data)
                except:
                    continue

            return devices
        except:
            return []

    def delete_device(self, name):
        """Delete saved device"""
        try:
            filepath = self.library_dir / f"{name}.json"
            if filepath.exists():
                filepath.unlink()
                return {'status': 'deleted', 'name': name}
            return {'status': 'error', 'message': 'Device not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


if __name__ == '__main__':
    # Test the scanner
    scanner = BluetoothScanner()

    print("[*] Testing Bluetooth Scanner...")

    if scanner.check_bluetooth_available():
        print("[+] Bluetooth is available!")
    else:
        print("[!] Enabling Bluetooth...")
        scanner.enable_bluetooth()

    # Quick BLE scan
    print("\n[*] Running quick BLE scan...")
    results = scanner.scan_ble_devices(duration=10)
    print(f"[+] Found {results['count']} BLE devices")

    for device in results['devices'][:5]:
        print(f"    - {device['address']}: {device['name']}")

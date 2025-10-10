#!/usr/bin/env python3
"""
NFC Guardian - Real-time NFC security monitoring
Detects unauthorized scan attempts and suspicious patterns
"""

import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

class NFCGuardian:
    """NFC Guardian - Monitors for unauthorized NFC scan attempts"""

    def __init__(self):
        self.data_dir = Path.home() / 'piflip' / 'guardian_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.card_catalog_file = self.data_dir / 'card_catalog.json'
        self.scan_log_file = self.data_dir / 'scan_log.json'
        self.suspicious_log_file = self.data_dir / 'suspicious_events.json'

        # Guardian settings
        self.monitoring = False
        self.monitor_thread = None
        self.suspicious_threshold = 3  # scans in 5 seconds = suspicious
        self.suspicious_window = 5  # seconds

        # Scan history
        self.scan_history = []
        self.max_history = 1000

        # Stats
        self.stats = {
            'total_scans': 0,
            'suspicious_events': 0,
            'last_scan': None,
            'monitoring_since': None
        }

        # Initialize PN532
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, address=0x24, reset=None, debug=False)
            self.pn532.SAM_configuration()
            self.available = True
        except Exception as e:
            print(f"[!] PN532 not available: {e}")
            self.available = False

        # Load existing data
        self.load_data()

    def load_data(self):
        """Load scan history and stats from disk"""
        if self.scan_log_file.exists():
            try:
                with open(self.scan_log_file, 'r') as f:
                    data = json.load(f)
                    self.scan_history = data.get('scans', [])[-100:]  # Keep last 100
                    self.stats = data.get('stats', self.stats)
            except:
                pass

    def save_data(self):
        """Save scan history and stats to disk"""
        try:
            data = {
                'scans': self.scan_history[-100:],  # Keep last 100
                'stats': self.stats
            }
            with open(self.scan_log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[!] Error saving data: {e}")

    def start_monitoring(self):
        """Start Guardian monitoring in background thread"""
        if not self.available:
            return {'status': 'error', 'message': 'PN532 not available'}

        if self.monitoring:
            return {'status': 'info', 'message': 'Already monitoring'}

        self.monitoring = True
        self.stats['monitoring_since'] = datetime.now().isoformat()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        return {'status': 'success', 'message': 'Guardian monitoring started'}

    def stop_monitoring(self):
        """Stop Guardian monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        self.save_data()
        return {'status': 'success', 'message': 'Guardian monitoring stopped'}

    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread"""
        print("[*] NFC Guardian monitoring started")

        while self.monitoring:
            try:
                # Check for NFC card presence (non-blocking, 100ms timeout)
                uid = self.pn532.read_passive_target(timeout=0.1)

                if uid:
                    # Card detected!
                    uid_hex = ''.join([f'{b:02X}' for b in uid])

                    scan_event = {
                        'timestamp': datetime.now().isoformat(),
                        'uid': uid_hex,
                        'unix_time': time.time()
                    }

                    # Add to history
                    self.scan_history.append(scan_event)
                    if len(self.scan_history) > self.max_history:
                        self.scan_history.pop(0)

                    # Update stats
                    self.stats['total_scans'] += 1
                    self.stats['last_scan'] = scan_event['timestamp']

                    # Check if suspicious
                    if self.is_suspicious_pattern(scan_event):
                        self.log_suspicious_event(scan_event)

                    print(f"[+] Guardian: Card detected - {uid_hex}")

                    # Save periodically (every 10 scans)
                    if self.stats['total_scans'] % 10 == 0:
                        self.save_data()

                    # Wait a bit after detection to avoid rapid repeats
                    time.sleep(0.5)
                else:
                    # No card, short sleep
                    time.sleep(0.1)

            except Exception as e:
                print(f"[!] Guardian monitor error: {e}")
                time.sleep(1)

        print("[*] NFC Guardian monitoring stopped")
        self.save_data()

    def is_suspicious_pattern(self, current_event):
        """
        Analyze scan patterns to detect suspicious activity

        Suspicious patterns:
        - Multiple scans in short time (3+ in 5 seconds)
        - Multiple different UIDs in short time
        - Scans at unusual times (configurable)
        """
        current_time = current_event['unix_time']

        # Get recent scans within suspicious window
        recent_scans = [
            scan for scan in self.scan_history
            if current_time - scan['unix_time'] < self.suspicious_window
        ]

        # Pattern 1: Too many scans too quickly
        if len(recent_scans) >= self.suspicious_threshold:
            return True

        # Pattern 2: Multiple different UIDs quickly (possible scanning attack)
        if len(recent_scans) >= 2:
            unique_uids = set(scan['uid'] for scan in recent_scans)
            if len(unique_uids) >= 3:  # 3+ different cards in 5 seconds
                return True

        return False

    def log_suspicious_event(self, scan_event):
        """Log a suspicious event"""
        self.stats['suspicious_events'] += 1

        # Load existing suspicious events
        suspicious_events = []
        if self.suspicious_log_file.exists():
            try:
                with open(self.suspicious_log_file, 'r') as f:
                    suspicious_events = json.load(f)
            except:
                pass

        # Add new event with context
        recent_scans = [
            scan for scan in self.scan_history
            if scan_event['unix_time'] - scan['unix_time'] < self.suspicious_window
        ]

        suspicious_event = {
            'timestamp': scan_event['timestamp'],
            'trigger_uid': scan_event['uid'],
            'reason': 'Multiple rapid scans detected',
            'recent_scan_count': len(recent_scans),
            'recent_scans': recent_scans[-5:]  # Last 5 scans for context
        }

        suspicious_events.append(suspicious_event)

        # Keep last 100 suspicious events
        suspicious_events = suspicious_events[-100:]

        # Save
        try:
            with open(self.suspicious_log_file, 'w') as f:
                json.dump(suspicious_events, f, indent=2)
        except Exception as e:
            print(f"[!] Error saving suspicious event: {e}")

        print(f"[!] SUSPICIOUS ACTIVITY DETECTED: {scan_event['uid']}")

    def get_status(self):
        """Get current Guardian status"""
        # Count recent scans (last 24 hours)
        now = time.time()
        recent_scans = [
            scan for scan in self.scan_history
            if now - scan['unix_time'] < 86400  # 24 hours
        ]

        # Count suspicious events today
        suspicious_today = 0
        if self.suspicious_log_file.exists():
            try:
                with open(self.suspicious_log_file, 'r') as f:
                    events = json.load(f)
                    today = datetime.now().date()
                    for event in events:
                        event_date = datetime.fromisoformat(event['timestamp']).date()
                        if event_date == today:
                            suspicious_today += 1
            except:
                pass

        return {
            'monitoring': self.monitoring,
            'available': self.available,
            'stats': {
                'total_scans': self.stats['total_scans'],
                'scans_today': len(recent_scans),
                'suspicious_events': self.stats['suspicious_events'],
                'suspicious_today': suspicious_today,
                'last_scan': self.stats['last_scan'],
                'monitoring_since': self.stats['monitoring_since']
            },
            'recent_scans': self.scan_history[-10:],  # Last 10 scans
            'alert_level': 'normal' if suspicious_today == 0 else 'elevated'
        }

    def get_suspicious_events(self, limit=20):
        """Get recent suspicious events"""
        if not self.suspicious_log_file.exists():
            return []

        try:
            with open(self.suspicious_log_file, 'r') as f:
                events = json.load(f)
                return events[-limit:][::-1]  # Most recent first
        except:
            return []

    def clear_history(self):
        """Clear scan history (keep stats)"""
        self.scan_history = []
        self.save_data()
        return {'status': 'success', 'message': 'History cleared'}


if __name__ == '__main__':
    # Test Guardian
    guardian = NFCGuardian()

    print("[*] Testing NFC Guardian...")
    print(f"[*] Available: {guardian.available}")

    if guardian.available:
        print("[*] Starting monitoring for 30 seconds...")
        print("[*] Try scanning NFC cards multiple times quickly")

        guardian.start_monitoring()
        time.sleep(30)
        guardian.stop_monitoring()

        status = guardian.get_status()
        print(f"\n[+] Monitoring complete!")
        print(f"[+] Total scans: {status['stats']['total_scans']}")
        print(f"[+] Suspicious events: {status['stats']['suspicious_events']}")

        if status['stats']['suspicious_events'] > 0:
            print("\n[!] Suspicious events detected:")
            for event in guardian.get_suspicious_events():
                print(f"    {event['timestamp']}: {event['reason']}")

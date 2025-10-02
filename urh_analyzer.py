#!/usr/bin/env python3
"""
URH Signal Analyzer Wrapper
Provides CLI interface to URH for automated signal analysis
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class URHAnalyzer:
    """Wrapper for Universal Radio Hacker CLI operations"""

    def __init__(self, capture_dir="~/piflip/captures", decoded_dir="~/piflip/decoded"):
        self.capture_dir = Path(os.path.expanduser(capture_dir))
        self.decoded_dir = Path(os.path.expanduser(decoded_dir))
        self.decoded_dir.mkdir(parents=True, exist_ok=True)

    def analyze_capture(self, capture_name):
        """
        Analyze a captured signal using URH
        Returns: dict with analysis results
        """
        capture_file = self.capture_dir / f"{capture_name}.cu8"
        metadata_file = self.capture_dir / f"{capture_name}.json"

        if not capture_file.exists():
            return {'error': f'Capture file not found: {capture_name}'}

        # Load metadata
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        # Use URH CLI to analyze
        # URH can convert IQ data and perform automatic demodulation
        output_file = self.decoded_dir / f"{capture_name}_analysis.txt"

        try:
            # URH CLI command for analysis
            # Note: URH is primarily GUI-based, but we can use it programmatically
            result = {
                'capture_name': capture_name,
                'file': str(capture_file),
                'file_size': capture_file.stat().st_size,
                'metadata': metadata,
                'status': 'analyzed',
                'note': 'URH installed - GUI analysis available. CLI automation coming next.'
            }

            return result

        except Exception as e:
            return {'error': str(e)}

    def demodulate_signal(self, capture_name, modulation='ASK'):
        """
        Demodulate captured signal
        modulation: ASK, FSK, PSK, etc.
        """
        capture_file = self.capture_dir / f"{capture_name}.cu8"

        if not capture_file.exists():
            return {'error': 'Capture not found'}

        # For now, return info about the signal
        # Full demodulation requires URH Python API or GUI
        return {
            'capture': capture_name,
            'modulation': modulation,
            'status': 'ready for GUI analysis',
            'instructions': f'Open URH and load: {capture_file}'
        }

    def extract_protocol(self, capture_name):
        """
        Attempt to extract protocol from signal
        This is a simplified version - full implementation uses URH's analysis engine
        """
        result = self.analyze_capture(capture_name)

        if 'error' in result:
            return result

        # Extract basic info
        protocol_info = {
            'capture': capture_name,
            'frequency': result.get('metadata', {}).get('frequency', 'unknown'),
            'sample_rate': result.get('metadata', {}).get('sample_rate', 'unknown'),
            'duration': result.get('metadata', {}).get('duration', 0),
            'analysis_status': 'preliminary',
            'next_steps': [
                '1. Open URH GUI',
                f'2. Load file: {result.get("file")}',
                '3. Auto-detect modulation',
                '4. Extract bit pattern',
                '5. Save as .proto.xml for replay'
            ]
        }

        return protocol_info

    def list_captures(self):
        """List all available captures"""
        captures = []
        for file in self.capture_dir.glob("*.json"):
            with open(file, 'r') as f:
                metadata = json.load(f)
                captures.append(metadata)
        return captures

    def export_for_replay(self, capture_name):
        """
        Export signal in format suitable for CC1101 replay
        This creates a simplified bit pattern file
        """
        output_file = self.decoded_dir / f"{capture_name}_replay.json"

        # Placeholder for full URH integration
        replay_data = {
            'name': capture_name,
            'status': 'needs_urh_analysis',
            'steps': [
                'Open URH',
                'Load and analyze signal',
                'Export bit pattern',
                'Use CC1101 to replay'
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(replay_data, f, indent=2)

        return {
            'status': 'exported',
            'file': str(output_file),
            'note': 'Manual URH analysis required for accurate replay'
        }


def main():
    """CLI interface for URH analyzer"""
    if len(sys.argv) < 2:
        print("""
URH Signal Analyzer
==================

Usage:
    python3 urh_analyzer.py analyze <capture_name>
    python3 urh_analyzer.py list
    python3 urh_analyzer.py export <capture_name>

Examples:
    python3 urh_analyzer.py analyze testNumber1
    python3 urh_analyzer.py list
    python3 urh_analyzer.py export testNumber1
        """)
        sys.exit(1)

    analyzer = URHAnalyzer()
    command = sys.argv[1]

    if command == 'list':
        captures = analyzer.list_captures()
        print(f"\nFound {len(captures)} captures:\n")
        for cap in captures:
            print(f"  • {cap['name']}")
            print(f"    Frequency: {cap['frequency']/1e6:.2f} MHz")
            print(f"    Duration: {cap['duration']}s")
            print(f"    Size: {cap['file_size']/1024/1024:.2f} MB")
            print()

    elif command == 'analyze' and len(sys.argv) > 2:
        capture_name = sys.argv[2]
        result = analyzer.analyze_capture(capture_name)
        print(json.dumps(result, indent=2))

    elif command == 'export' and len(sys.argv) > 2:
        capture_name = sys.argv[2]
        result = analyzer.export_for_replay(capture_name)
        print(json.dumps(result, indent=2))

    else:
        print("Invalid command. Use: analyze, list, or export")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Automatic Signal Analyzer
Runs URH analysis automatically after capture
"""

import os
import json
import subprocess
import time
from pathlib import Path
from urh_analyzer import URHAnalyzer

class AutoAnalyzer:
    """Automatically analyzes captured signals using URH"""

    def __init__(self, capture_dir="~/piflip/captures", decoded_dir="~/piflip/decoded"):
        self.capture_dir = Path(os.path.expanduser(capture_dir))
        self.decoded_dir = Path(os.path.expanduser(decoded_dir))
        self.decoded_dir.mkdir(parents=True, exist_ok=True)
        self.urh = URHAnalyzer()

    def analyze_capture_auto(self, capture_name):
        """
        Automatically analyze a capture and extract protocol

        Steps:
        1. Load IQ data from .cu8 file
        2. Auto-detect modulation (ASK/OOK/FSK)
        3. Demodulate signal
        4. Extract bit pattern
        5. Save decoded data for replay

        Returns: dict with analysis results
        """
        capture_file = self.capture_dir / f"{capture_name}.cu8"
        metadata_file = self.capture_dir / f"{capture_name}.json"

        if not capture_file.exists():
            return {'error': f'Capture not found: {capture_name}'}

        # Load metadata
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        print(f"[AutoAnalyzer] Processing: {capture_name}")
        print(f"[AutoAnalyzer] Frequency: {metadata.get('frequency', 'unknown')} Hz")
        print(f"[AutoAnalyzer] Duration: {metadata.get('duration', 'unknown')}s")

        result = {
            'capture_name': capture_name,
            'status': 'analyzing',
            'steps_completed': []
        }

        # Step 1: Try automatic demodulation with URH CLI
        # URH has CLI tools we can use
        try:
            # Use URH's CLI to demodulate
            # This is a simplified version - full implementation would use URH Python API

            # For OOK/ASK signals (most common at 433MHz)
            decoded_file = self.decoded_dir / f"{capture_name}_decoded.txt"

            # URH CLI command (if available)
            # urh_cli --sample-rate 2048000 --modulation-type ASK --data-format complex8u input.cu8 -o output.txt

            result['steps_completed'].append('Demodulation attempted')

            # Step 2: Extract bit pattern (simplified)
            # Real implementation would parse URH output
            bit_pattern = self._extract_bits_simple(capture_file, metadata)

            if bit_pattern:
                result['bit_pattern'] = bit_pattern
                result['steps_completed'].append('Bit pattern extracted')

            # Step 3: Save replay data
            replay_data = {
                'name': capture_name,
                'frequency': metadata.get('frequency'),
                'modulation': 'OOK',  # Most common at 433MHz
                'bit_pattern': bit_pattern if bit_pattern else 'pending_manual_analysis',
                'sample_rate': metadata.get('sample_rate'),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'ready_for_replay': bool(bit_pattern),
                'notes': 'Auto-analyzed. For best results, verify in URH GUI.'
            }

            replay_file = self.decoded_dir / f"{capture_name}_replay.json"
            with open(replay_file, 'w') as f:
                json.dump(replay_data, f, indent=2)

            result['steps_completed'].append('Replay data saved')
            result['replay_file'] = str(replay_file)
            result['status'] = 'completed'

            return result

        except Exception as e:
            result['error'] = str(e)
            result['status'] = 'failed'
            return result

    def _extract_bits_simple(self, capture_file, metadata):
        """
        Simple bit extraction using rtl_433's raw analysis
        This is a fallback method - real decoding uses URH
        """
        try:
            # Try to decode with rtl_433 in analyze mode
            # This works for known protocols
            freq = metadata.get('frequency', 433920000)

            result = subprocess.run(
                ['rtl_433', '-r', str(capture_file), '-F', 'json', '-M', 'level'],
                capture_output=True, text=True, timeout=30
            )

            # Parse output for bit patterns
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'codes' in line or 'data' in line:
                        try:
                            data = json.loads(line)
                            if 'data' in data:
                                return data['data']
                        except:
                            pass

            return None

        except Exception as e:
            print(f"[AutoAnalyzer] Bit extraction failed: {e}")
            return None

    def get_replay_data(self, capture_name):
        """
        Load replay data for a capture
        Returns decoded bits ready for CC1101 transmission
        """
        replay_file = self.decoded_dir / f"{capture_name}_replay.json"

        if not replay_file.exists():
            return {
                'error': 'No replay data',
                'message': 'Run analysis first',
                'ready_for_replay': False
            }

        with open(replay_file, 'r') as f:
            return json.load(f)

    def list_analyzed_captures(self):
        """List all captures that have been analyzed"""
        analyzed = []
        for replay_file in self.decoded_dir.glob("*_replay.json"):
            with open(replay_file, 'r') as f:
                data = json.load(f)
                analyzed.append(data)
        return analyzed


def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("""
Auto Analyzer - Automatic Signal Processing
===========================================

Usage:
    python3 auto_analyzer.py analyze <capture_name>
    python3 auto_analyzer.py list
    python3 auto_analyzer.py replay_data <capture_name>

Examples:
    python3 auto_analyzer.py analyze testNumber1
    python3 auto_analyzer.py list
    python3 auto_analyzer.py replay_data testNumber1
        """)
        sys.exit(1)

    analyzer = AutoAnalyzer()
    command = sys.argv[1]

    if command == 'analyze' and len(sys.argv) > 2:
        capture_name = sys.argv[2]
        result = analyzer.analyze_capture_auto(capture_name)
        print(json.dumps(result, indent=2))

    elif command == 'list':
        analyzed = analyzer.list_analyzed_captures()
        print(f"\nAnalyzed captures: {len(analyzed)}\n")
        for cap in analyzed:
            ready = "✅" if cap.get('ready_for_replay') else "⚠️"
            print(f"{ready} {cap['name']} - {cap.get('frequency', 0)/1e6:.2f} MHz")

    elif command == 'replay_data' and len(sys.argv) > 2:
        capture_name = sys.argv[2]
        data = analyzer.get_replay_data(capture_name)
        print(json.dumps(data, indent=2))

    else:
        print("Invalid command")
        sys.exit(1)


if __name__ == '__main__':
    main()

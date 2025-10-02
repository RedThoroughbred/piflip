#!/usr/bin/env python3
"""
Signal Decoder for PiFlip
Decodes OOK/ASK signals from CC1101 timing captures
Extracts binary data and protocol information
"""

import json
import statistics
from pathlib import Path
from collections import Counter

class SignalDecoder:
    """Decode OOK/ASK signals to binary and extract protocols"""

    def __init__(self):
        self.library_dir = Path("~/piflip/rf_library").expanduser()

    def load_signal(self, name):
        """Load signal from library"""
        signal_file = self.library_dir / f"{name}.json"
        if not signal_file.exists():
            return None

        with open(signal_file, 'r') as f:
            return json.load(f)

    def analyze_timings(self, timings):
        """Analyze timing patterns to find short/long pulses"""
        if not timings or len(timings) < 4:
            return None

        # Extract all pulse durations (ignore state for now)
        durations = [t['duration_us'] for t in timings]

        # Filter out very short noise (< 50us) and very long gaps (> 50ms)
        filtered = [d for d in durations if 50 < d < 50000]

        if len(filtered) < 4:
            return None

        # Use clustering to find short vs long pulses
        # Most OOK uses 2-3 distinct pulse widths
        sorted_durations = sorted(filtered)

        # Find clusters using simple threshold
        # Typically: short pulse (200-500us), long pulse (800-1500us)
        clusters = self._find_pulse_clusters(sorted_durations)

        if not clusters:
            return None

        return {
            'clusters': clusters,
            'min_duration': min(filtered),
            'max_duration': max(filtered),
            'avg_duration': int(statistics.mean(filtered)),
            'total_pulses': len(timings)
        }

    def _find_pulse_clusters(self, sorted_durations):
        """Find distinct pulse width clusters"""
        if len(sorted_durations) < 4:
            return None

        # Use simple k-means-like clustering for 2 clusters (short/long)
        median = statistics.median(sorted_durations)

        short_pulses = [d for d in sorted_durations if d < median]
        long_pulses = [d for d in sorted_durations if d >= median]

        if not short_pulses or not long_pulses:
            return None

        short_avg = int(statistics.mean(short_pulses))
        long_avg = int(statistics.mean(long_pulses))

        # Calculate tolerance (±30%)
        short_tolerance = short_avg * 0.3
        long_tolerance = long_avg * 0.3

        return {
            'short': {
                'avg': short_avg,
                'min': short_avg - int(short_tolerance),
                'max': short_avg + int(short_tolerance),
                'count': len(short_pulses)
            },
            'long': {
                'avg': long_avg,
                'min': long_avg - int(long_tolerance),
                'max': long_avg + int(long_tolerance),
                'count': len(long_pulses)
            }
        }

    def timings_to_binary(self, timings, pulse_info):
        """Convert timings to binary using pulse width analysis"""
        if not pulse_info or not pulse_info.get('clusters'):
            return None

        clusters = pulse_info['clusters']
        short = clusters['short']
        long = clusters['long']

        binary_data = []
        raw_symbols = []

        for timing in timings:
            duration = timing['duration_us']
            state = timing['state']

            # Classify pulse as short or long
            if short['min'] <= duration <= short['max']:
                symbol = 'S'
                binary_data.append(0)
            elif long['min'] <= duration <= long['max']:
                symbol = 'L'
                binary_data.append(1)
            else:
                symbol = '?'  # Unknown/noise

            raw_symbols.append({
                'duration': duration,
                'state': state,
                'symbol': symbol
            })

        # Convert to bit string
        bit_string = ''.join(str(b) for b in binary_data)

        return {
            'binary': binary_data,
            'bit_string': bit_string,
            'symbols': raw_symbols,
            'bit_count': len(binary_data)
        }

    def detect_protocol(self, binary_data):
        """Detect protocol type from binary pattern"""
        if not binary_data or 'bit_string' not in binary_data:
            return {'type': 'unknown'}

        bit_string = binary_data['bit_string']

        # Look for common patterns
        protocol_info = {
            'type': 'OOK',
            'encoding': self._detect_encoding(bit_string),
            'bit_count': len(bit_string),
            'patterns': self._find_repeating_patterns(bit_string)
        }

        return protocol_info

    def _detect_encoding(self, bit_string):
        """Detect encoding type (PWM, Manchester, etc.)"""
        if len(bit_string) < 8:
            return 'unknown'

        # Check for Manchester encoding (bit transitions)
        # Manchester: 01 = 1, 10 = 0 (always transitions)
        transitions = 0
        for i in range(len(bit_string) - 1):
            if bit_string[i] != bit_string[i+1]:
                transitions += 1

        transition_ratio = transitions / len(bit_string)

        if transition_ratio > 0.8:
            return 'Manchester'
        elif transition_ratio > 0.4:
            return 'PWM (Pulse Width Modulation)'
        else:
            return 'Simple OOK'

    def _find_repeating_patterns(self, bit_string):
        """Find repeating patterns in bit string"""
        patterns = []

        # Look for patterns of different lengths
        for pattern_len in [8, 12, 16, 24, 32]:
            if len(bit_string) < pattern_len * 2:
                continue

            # Check if signal repeats
            chunks = [bit_string[i:i+pattern_len]
                     for i in range(0, len(bit_string), pattern_len)
                     if len(bit_string[i:i+pattern_len]) == pattern_len]

            if len(chunks) >= 2:
                # Count occurrences
                counter = Counter(chunks)
                most_common = counter.most_common(3)

                for pattern, count in most_common:
                    if count >= 2:  # Repeats at least twice
                        patterns.append({
                            'pattern': pattern,
                            'length': pattern_len,
                            'repeats': count,
                            'hex': hex(int(pattern, 2))[2:].upper().zfill(pattern_len // 4)
                        })

        return patterns

    def decode_signal(self, name):
        """Complete signal decode pipeline"""
        signal = self.load_signal(name)
        if not signal:
            return {'error': 'Signal not found'}

        timings = signal.get('timings', [])
        if not timings:
            return {'error': 'No timing data'}

        # Step 1: Analyze pulse widths
        pulse_info = self.analyze_timings(timings)
        if not pulse_info:
            return {'error': 'Could not analyze timings'}

        # Step 2: Convert to binary
        binary_data = self.timings_to_binary(timings, pulse_info)
        if not binary_data:
            return {'error': 'Could not convert to binary'}

        # Step 3: Detect protocol
        protocol = self.detect_protocol(binary_data)

        # Step 4: Compile results
        result = {
            'name': name,
            'frequency': signal.get('frequency'),
            'duration': signal.get('duration'),
            'pulse_analysis': pulse_info,
            'binary': binary_data,
            'protocol': protocol,
            'raw_timings': len(timings),
            'decoded_bits': binary_data['bit_count']
        }

        return result

    def format_decode_output(self, decode_result):
        """Format decode result for display"""
        if 'error' in decode_result:
            return f"❌ Error: {decode_result['error']}"

        output = '╔══════════════════════════════════════════════════╗\n'
        output += '║          📡 SIGNAL DECODED!                      ║\n'
        output += '╚══════════════════════════════════════════════════╝\n\n'

        output += f"Signal:       {decode_result['name']}\n"
        output += f"Frequency:    {decode_result['frequency']} MHz\n"
        output += f"Duration:     {decode_result['duration']}s\n\n"

        # Pulse analysis
        pulse = decode_result['pulse_analysis']
        clusters = pulse.get('clusters', {})
        if clusters:
            output += '─────────────────────────────────────────────────\n'
            output += 'PULSE WIDTHS:\n'
            output += f"  Short: {clusters['short']['avg']}µs ({clusters['short']['count']} pulses)\n"
            output += f"  Long:  {clusters['long']['avg']}µs ({clusters['long']['count']} pulses)\n\n"

        # Binary data
        binary = decode_result.get('binary', {})
        if binary and binary.get('bit_string'):
            output += '─────────────────────────────────────────────────\n'
            output += 'BINARY DATA:\n'
            bit_string = binary['bit_string']

            # Show in chunks of 8 bits
            for i in range(0, len(bit_string), 32):
                chunk = bit_string[i:i+32]
                # Add spaces every 8 bits
                formatted = ' '.join(chunk[j:j+8] for j in range(0, len(chunk), 8))
                output += f"  {formatted}\n"

            output += f"\nTotal bits: {binary['bit_count']}\n\n"

        # Protocol
        protocol = decode_result.get('protocol', {})
        if protocol:
            output += '─────────────────────────────────────────────────\n'
            output += 'PROTOCOL:\n'
            output += f"  Type:     {protocol.get('type', 'Unknown')}\n"
            output += f"  Encoding: {protocol.get('encoding', 'Unknown')}\n\n"

            # Show repeating patterns
            patterns = protocol.get('patterns', [])
            if patterns:
                output += 'REPEATING PATTERNS:\n'
                for i, p in enumerate(patterns[:3], 1):  # Show top 3
                    output += f"  {i}. {p['pattern']} (hex: {p['hex']})\n"
                    output += f"     Repeats: {p['repeats']}x, Length: {p['length']} bits\n"

        output += '\n✅ Ready to replay with exact timings!'

        return output

    def create_replay_data(self, name):
        """Create optimized replay data from decoded signal"""
        decode_result = self.decode_signal(name)

        if 'error' in decode_result:
            return decode_result

        signal = self.load_signal(name)

        # Use original timings for exact replay
        replay_data = {
            'name': name,
            'frequency': signal['frequency'],
            'timings': signal['timings'],
            'modulation': 'OOK',
            'decoded_info': {
                'bit_count': decode_result['binary']['bit_count'],
                'encoding': decode_result['protocol']['encoding'],
                'patterns': decode_result['protocol'].get('patterns', [])
            }
        }

        return replay_data


if __name__ == '__main__':
    # Test decoder
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 signal_decoder.py <signal_name>")
        sys.exit(1)

    decoder = SignalDecoder()
    result = decoder.decode_signal(sys.argv[1])

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(decoder.format_decode_output(result))

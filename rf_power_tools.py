#!/usr/bin/env python3
"""
RF Power Tools for PiFlip
Advanced transmission features for security testing and research

Features:
- Signal Fuzzing (bit flipping, mutation)
- Protocol Encoder (PT2262, PT2264, HCS301, custom)
- Frequency Scanner (sweep and transmit)
- Signal Playlist (macros and sequences)
- Jamming/Noise Generator (security testing)

Educational and security research purposes only!
"""

import time
import json
import os
import random
from pathlib import Path
from cc1101_enhanced import CC1101Enhanced
from datetime import datetime

class RFPowerTools:
    """Advanced RF transmission tools"""

    def __init__(self):
        self.cc1101 = CC1101Enhanced()
        self.signal_library = Path.home() / "piflip" / "rf_library"
        self.signal_library.mkdir(exist_ok=True)
        self.captures_dir = Path.home() / "piflip" / "captures"
        self.captures_dir.mkdir(exist_ok=True)

    # =========================================================================
    # 1. SIGNAL FUZZING
    # =========================================================================

    def fuzz_signal(self, signal_name, mode='bit_flip', max_attempts=100, delay_ms=100):
        """
        Fuzz a captured signal by systematically mutating it

        Args:
            signal_name: Name of saved signal
            mode: 'bit_flip' (flip each bit), 'random' (random mutations), 'increment' (increment values)
            max_attempts: Maximum number of variations to try
            delay_ms: Delay between transmissions (milliseconds)

        Returns:
            Dict with results
        """
        # Load signal
        signal_data = self._load_signal(signal_name)
        if not signal_data:
            return {'status': 'error', 'message': f'Signal not found: {signal_name}'}

        if 'timings' not in signal_data:
            return {'status': 'error', 'message': 'Signal has no timing data. Only CC1101 captures can be fuzzed.'}

        frequency = signal_data.get('frequency', 433.92)
        if frequency > 1000:
            frequency = frequency / 1e6

        base_timings = signal_data['timings']

        # Convert timings to binary string for easier manipulation
        binary_data = self._timings_to_binary(base_timings)

        if not binary_data:
            return {'status': 'error', 'message': 'Could not convert signal to binary'}

        results = {
            'status': 'complete',
            'signal': signal_name,
            'mode': mode,
            'original_bits': len(binary_data),
            'attempts': 0,
            'variations': []
        }

        print(f"[*] Fuzzing signal '{signal_name}'")
        print(f"    Mode: {mode}")
        print(f"    Original binary: {binary_data[:50]}... ({len(binary_data)} bits)")
        print(f"    Max attempts: {max_attempts}")

        if mode == 'bit_flip':
            # Flip each bit one at a time
            attempts = min(max_attempts, len(binary_data))

            for i in range(attempts):
                # Flip bit at position i
                mutated = list(binary_data)
                mutated[i] = '0' if binary_data[i] == '1' else '1'
                mutated_binary = ''.join(mutated)

                # Convert back to timings and transmit
                mutated_timings = self._binary_to_timings(mutated_binary)

                print(f"  [+] Attempt {i+1}/{attempts}: Flipped bit {i}")

                self.cc1101.transmit_signal_enhanced(
                    {'frequency': frequency, 'timings': mutated_timings},
                    repeats=2,
                    power='max'
                )

                results['variations'].append({
                    'attempt': i + 1,
                    'mutation': f'bit_flip_{i}',
                    'binary': mutated_binary[:50] + '...'
                })

                time.sleep(delay_ms / 1000.0)
                results['attempts'] = i + 1

        elif mode == 'random':
            # Random bit flips
            for i in range(max_attempts):
                # Flip 1-5 random bits
                num_flips = random.randint(1, 5)
                mutated = list(binary_data)

                flipped_positions = []
                for _ in range(num_flips):
                    pos = random.randint(0, len(binary_data) - 1)
                    mutated[pos] = '0' if mutated[pos] == '1' else '1'
                    flipped_positions.append(pos)

                mutated_binary = ''.join(mutated)
                mutated_timings = self._binary_to_timings(mutated_binary)

                print(f"  [+] Attempt {i+1}/{max_attempts}: Flipped bits at {flipped_positions}")

                self.cc1101.transmit_signal_enhanced(
                    {'frequency': frequency, 'timings': mutated_timings},
                    repeats=2,
                    power='max'
                )

                results['variations'].append({
                    'attempt': i + 1,
                    'mutation': f'random_flip_{flipped_positions}',
                    'binary': mutated_binary[:50] + '...'
                })

                time.sleep(delay_ms / 1000.0)
                results['attempts'] = i + 1

        elif mode == 'increment':
            # Treat binary as number and increment
            try:
                base_value = int(binary_data, 2)

                for i in range(max_attempts):
                    new_value = (base_value + i) % (2 ** len(binary_data))
                    mutated_binary = format(new_value, f'0{len(binary_data)}b')
                    mutated_timings = self._binary_to_timings(mutated_binary)

                    print(f"  [+] Attempt {i+1}/{max_attempts}: Value = {new_value}")

                    self.cc1101.transmit_signal_enhanced(
                        {'frequency': frequency, 'timings': mutated_timings},
                        repeats=2,
                        power='max'
                    )

                    results['variations'].append({
                        'attempt': i + 1,
                        'mutation': f'increment_{i}',
                        'value': new_value,
                        'binary': mutated_binary[:50] + '...'
                    })

                    time.sleep(delay_ms / 1000.0)
                    results['attempts'] = i + 1

            except ValueError:
                return {'status': 'error', 'message': 'Could not parse signal as numeric value'}

        print(f"[✓] Fuzzing complete: {results['attempts']} variations transmitted")
        return results

    # =========================================================================
    # 2. PROTOCOL ENCODER
    # =========================================================================

    def encode_protocol(self, protocol, code, frequency=433.92, **kwargs):
        """
        Encode and transmit signal using known protocol

        Supported protocols:
        - PT2262 (common 433MHz remotes)
        - PT2264 (variant of PT2262)
        - HCS301 (KeeLoq rolling code)
        - custom (define your own timing)

        Args:
            protocol: Protocol name
            code: Binary code string (e.g., "101010101010")
            frequency: Transmission frequency in MHz
            **kwargs: Protocol-specific parameters

        Returns:
            Dict with result
        """
        print(f"[*] Encoding signal with {protocol} protocol")
        print(f"    Code: {code}")
        print(f"    Frequency: {frequency} MHz")

        if protocol == 'PT2262':
            timings = self._encode_pt2262(code)
        elif protocol == 'PT2264':
            timings = self._encode_pt2264(code)
        elif protocol == 'HCS301':
            timings = self._encode_hcs301(code, **kwargs)
        elif protocol == 'custom':
            timings = self._encode_custom(code, **kwargs)
        else:
            return {'status': 'error', 'message': f'Unknown protocol: {protocol}'}

        if not timings:
            return {'status': 'error', 'message': 'Failed to encode signal'}

        # Transmit
        signal_data = {
            'frequency': frequency,
            'timings': timings
        }

        print(f"[*] Transmitting encoded signal ({len(timings)} transitions)")

        self.cc1101.transmit_signal_enhanced(signal_data, repeats=5, power='max')

        return {
            'status': 'success',
            'protocol': protocol,
            'code': code,
            'frequency': frequency,
            'transitions': len(timings)
        }

    def _encode_pt2262(self, code):
        """
        Encode PT2262 protocol
        Timing: short=350us, long=1050us (1:3 ratio)
        0 = short high, long low
        1 = long high, short low
        Sync = short high, 31*short low
        """
        SHORT = 350
        LONG = 1050
        SYNC_GAP = 10850  # 31 * 350

        timings = []

        # Add preamble sync
        timings.append({'state': 1, 'duration_us': SHORT})
        timings.append({'state': 0, 'duration_us': SYNC_GAP})

        # Encode each bit
        for bit in code:
            if bit == '0':
                timings.append({'state': 1, 'duration_us': SHORT})
                timings.append({'state': 0, 'duration_us': LONG})
            elif bit == '1':
                timings.append({'state': 1, 'duration_us': LONG})
                timings.append({'state': 0, 'duration_us': SHORT})
            elif bit == 'F':  # Floating bit (tristate)
                timings.append({'state': 1, 'duration_us': SHORT})
                timings.append({'state': 0, 'duration_us': SHORT})
                timings.append({'state': 1, 'duration_us': SHORT})
                timings.append({'state': 0, 'duration_us': LONG})

        # Final sync
        timings.append({'state': 1, 'duration_us': SHORT})
        timings.append({'state': 0, 'duration_us': SYNC_GAP})

        return timings

    def _encode_pt2264(self, code):
        """PT2264 is similar to PT2262 but with different timing"""
        SHORT = 450
        LONG = 1350
        SYNC_GAP = 13950

        timings = []

        timings.append({'state': 1, 'duration_us': SHORT})
        timings.append({'state': 0, 'duration_us': SYNC_GAP})

        for bit in code:
            if bit == '0':
                timings.append({'state': 1, 'duration_us': SHORT})
                timings.append({'state': 0, 'duration_us': LONG})
            elif bit == '1':
                timings.append({'state': 1, 'duration_us': LONG})
                timings.append({'state': 0, 'duration_us': SHORT})

        timings.append({'state': 1, 'duration_us': SHORT})
        timings.append({'state': 0, 'duration_us': SYNC_GAP})

        return timings

    def _encode_hcs301(self, code, **kwargs):
        """
        HCS301 KeeLoq encoding (simplified)
        Real KeeLoq uses encryption - this is basic frame structure
        """
        # This is a simplified version - real KeeLoq requires encryption
        SHORT = 400
        LONG = 800

        timings = []

        # Preamble
        for _ in range(12):
            timings.append({'state': 1, 'duration_us': SHORT})
            timings.append({'state': 0, 'duration_us': SHORT})

        # Data bits (Manchester encoding)
        for bit in code:
            if bit == '0':
                timings.append({'state': 1, 'duration_us': SHORT})
                timings.append({'state': 0, 'duration_us': SHORT})
            else:
                timings.append({'state': 0, 'duration_us': SHORT})
                timings.append({'state': 1, 'duration_us': SHORT})

        return timings

    def _encode_custom(self, code, short_us=350, long_us=1050, **kwargs):
        """Custom encoding with user-defined timings"""
        timings = []

        for bit in code:
            if bit == '0':
                timings.append({'state': 1, 'duration_us': short_us})
                timings.append({'state': 0, 'duration_us': long_us})
            else:
                timings.append({'state': 1, 'duration_us': long_us})
                timings.append({'state': 0, 'duration_us': short_us})

        return timings

    # =========================================================================
    # 3. FREQUENCY SCANNER
    # =========================================================================

    def frequency_sweep(self, signal_name, start_freq, end_freq, step_mhz=0.05, delay_ms=500, repeats=3):
        """
        Sweep frequency range while transmitting signal
        Useful for finding unknown frequency of target device

        Args:
            signal_name: Name of signal to transmit
            start_freq: Start frequency in MHz
            end_freq: End frequency in MHz
            step_mhz: Step size in MHz
            delay_ms: Delay between frequencies
            repeats: Number of times to transmit at each frequency

        Returns:
            Dict with results
        """
        signal_data = self._load_signal(signal_name)
        if not signal_data:
            return {'status': 'error', 'message': f'Signal not found: {signal_name}'}

        if 'timings' not in signal_data:
            return {'status': 'error', 'message': 'Signal has no timing data'}

        timings = signal_data['timings']

        frequencies_tested = []
        current_freq = start_freq

        print(f"[*] Frequency Sweep: {start_freq} - {end_freq} MHz")
        print(f"    Step: {step_mhz} MHz")
        print(f"    Signal: {signal_name}")

        while current_freq <= end_freq:
            print(f"  [+] Testing {current_freq:.3f} MHz...")

            signal = {
                'frequency': current_freq,
                'timings': timings
            }

            self.cc1101.transmit_signal_enhanced(signal, repeats=repeats, power='max')

            frequencies_tested.append(current_freq)
            current_freq += step_mhz

            time.sleep(delay_ms / 1000.0)

        print(f"[✓] Sweep complete: {len(frequencies_tested)} frequencies tested")

        return {
            'status': 'complete',
            'signal': signal_name,
            'start_freq': start_freq,
            'end_freq': end_freq,
            'step': step_mhz,
            'frequencies_tested': len(frequencies_tested),
            'frequencies': frequencies_tested
        }

    # =========================================================================
    # 4. SIGNAL PLAYLIST
    # =========================================================================

    def execute_playlist(self, playlist):
        """
        Execute sequence of signal transmissions

        Args:
            playlist: List of dicts with format:
                [
                    {'signal': 'signal_name', 'delay': 1.0, 'repeats': 3},
                    {'signal': 'signal_name2', 'delay': 0.5, 'repeats': 1},
                ]

        Returns:
            Dict with results
        """
        print(f"[*] Executing playlist with {len(playlist)} steps")

        results = {
            'status': 'complete',
            'total_steps': len(playlist),
            'executed': 0,
            'steps': []
        }

        for i, step in enumerate(playlist):
            signal_name = step.get('signal')
            delay = step.get('delay', 0)
            repeats = step.get('repeats', 3)
            frequency = step.get('frequency', None)

            print(f"  [{i+1}/{len(playlist)}] Signal: {signal_name}, Delay: {delay}s")

            # Load signal
            signal_data = self._load_signal(signal_name)
            if not signal_data:
                print(f"    [!] Signal not found: {signal_name}")
                results['steps'].append({
                    'step': i + 1,
                    'signal': signal_name,
                    'status': 'error',
                    'message': 'Signal not found'
                })
                continue

            if 'timings' not in signal_data:
                print(f"    [!] No timing data for: {signal_name}")
                results['steps'].append({
                    'step': i + 1,
                    'signal': signal_name,
                    'status': 'error',
                    'message': 'No timing data'
                })
                continue

            # Use custom frequency if provided
            if frequency:
                signal_data['frequency'] = frequency

            # Transmit
            self.cc1101.transmit_signal_enhanced(signal_data, repeats=repeats, power='max')

            results['steps'].append({
                'step': i + 1,
                'signal': signal_name,
                'status': 'success',
                'repeats': repeats
            })

            results['executed'] += 1

            # Delay before next step
            if delay > 0 and i < len(playlist) - 1:
                time.sleep(delay)

        print(f"[✓] Playlist complete: {results['executed']}/{results['total_steps']} steps executed")

        return results

    def save_playlist(self, name, playlist):
        """Save playlist to file"""
        playlist_dir = Path.home() / "piflip" / "playlists"
        playlist_dir.mkdir(exist_ok=True)

        playlist_file = playlist_dir / f"{name}.json"

        with open(playlist_file, 'w') as f:
            json.dump({
                'name': name,
                'created': datetime.now().isoformat(),
                'playlist': playlist
            }, f, indent=2)

        return {'status': 'success', 'file': str(playlist_file)}

    def load_playlist(self, name):
        """Load playlist from file"""
        playlist_dir = Path.home() / "piflip" / "playlists"
        playlist_file = playlist_dir / f"{name}.json"

        if not playlist_file.exists():
            return None

        with open(playlist_file) as f:
            data = json.load(f)

        return data.get('playlist', [])

    # =========================================================================
    # 5. JAMMING / NOISE GENERATOR
    # =========================================================================

    def jam_frequency(self, frequency, duration_sec=10, mode='noise', power='max'):
        """
        Transmit noise/jamming signal on frequency

        WARNING: Use only for security testing on YOUR OWN devices
        Jamming is ILLEGAL in most jurisdictions

        Args:
            frequency: Frequency in MHz
            duration_sec: Duration in seconds
            mode: 'noise' (random), 'tone' (continuous), 'sweep' (frequency sweep)
            power: Transmission power

        Returns:
            Dict with results
        """
        print(f"[*] JAMMING MODE: {mode}")
        print(f"    Frequency: {frequency} MHz")
        print(f"    Duration: {duration_sec} seconds")
        print(f"    ⚠️  WARNING: Use responsibly and legally!")

        start_time = time.time()

        if mode == 'noise':
            # Random noise
            while time.time() - start_time < duration_sec:
                # Generate random timing pattern
                timings = []
                for _ in range(100):
                    state = random.randint(0, 1)
                    duration = random.randint(50, 500)
                    timings.append({'state': state, 'duration_us': duration})

                signal = {'frequency': frequency, 'timings': timings}
                self.cc1101.transmit_signal_enhanced(signal, repeats=1, power=power)

        elif mode == 'tone':
            # Continuous carrier
            timings = [{'state': 1, 'duration_us': 100000}]  # 100ms high
            signal = {'frequency': frequency, 'timings': timings}

            while time.time() - start_time < duration_sec:
                self.cc1101.transmit_signal_enhanced(signal, repeats=1, power=power)
                time.sleep(0.05)

        elif mode == 'sweep':
            # Sweep around frequency
            sweep_range = 1.0  # +/- 1 MHz

            while time.time() - start_time < duration_sec:
                # Sweep up
                for offset in range(0, 100, 5):
                    freq = frequency + (offset / 100.0 * sweep_range)
                    timings = [{'state': 1, 'duration_us': 10000}]
                    signal = {'frequency': freq, 'timings': timings}
                    self.cc1101.transmit_signal_enhanced(signal, repeats=1, power=power)

                    if time.time() - start_time >= duration_sec:
                        break

        elapsed = time.time() - start_time
        print(f"[✓] Jamming complete: {elapsed:.1f} seconds")

        return {
            'status': 'complete',
            'frequency': frequency,
            'mode': mode,
            'duration': elapsed
        }

    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================

    def _load_signal(self, signal_name):
        """Load signal from library or captures"""
        # Try signal library first
        signal_path = self.signal_library / f"{signal_name}.json"

        if not signal_path.exists():
            # Try captures directory
            signal_path = self.captures_dir / f"{signal_name}.json"

        if not signal_path.exists():
            return None

        with open(signal_path) as f:
            return json.load(f)

    def _timings_to_binary(self, timings):
        """Convert timing data to binary string (simplified)"""
        # Simple approach: short pulse = 0, long pulse = 1
        # This is a simplification - real protocols vary

        binary = []

        for timing in timings:
            duration = timing['duration_us']

            # Classify as short or long (threshold at 600us)
            if duration < 600:
                binary.append('0')
            else:
                binary.append('1')

        return ''.join(binary)

    def _binary_to_timings(self, binary_str):
        """Convert binary string to timing data (simplified)"""
        SHORT = 350
        LONG = 1050

        timings = []
        state = 1

        for bit in binary_str:
            if bit == '0':
                timings.append({'state': state, 'duration_us': SHORT})
            else:
                timings.append({'state': state, 'duration_us': LONG})

            state = 1 - state  # Alternate between high and low

        return timings

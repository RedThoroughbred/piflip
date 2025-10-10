#!/usr/bin/env python3
"""
Advanced RF Transmission Features for PiFlip
Educational and research purposes only!
"""

import time
import json
import os
from cc1101_enhanced import CC1101Enhanced
from pathlib import Path

class RFAdvancedTX:
    """Advanced RF transmission capabilities"""

    def __init__(self):
        self.cc1101 = CC1101Enhanced()
        self.signal_library = Path.home() / "piflip" / "signal_library"
        self.signal_library.mkdir(exist_ok=True)

    def replay_with_variations(self, signal_name, frequency_offsets=None, timing_variations=None):
        """
        Replay signal with frequency and timing variations
        Useful when exact frequency/timing is uncertain

        Args:
            signal_name: Name of saved signal
            frequency_offsets: List of MHz offsets to try (e.g., [-0.5, 0, 0.5])
            timing_variations: List of timing multipliers (e.g., [0.9, 1.0, 1.1])
        """
        if frequency_offsets is None:
            frequency_offsets = [-0.5, -0.25, 0, 0.25, 0.5]
        if timing_variations is None:
            timing_variations = [0.95, 1.0, 1.05]

        # Load signal (try signal_library first, then captures directory)
        signal_path = self.signal_library / f"{signal_name}.json"

        if not signal_path.exists():
            # Try captures directory
            captures_dir = Path.home() / "piflip" / "captures"
            signal_path = captures_dir / f"{signal_name}.json"

            if not signal_path.exists():
                return {'status': 'error', 'message': f'Signal not found: {signal_name}'}

        with open(signal_path) as f:
            signal_data = json.load(f)

        # Check if signal has timing data (CC1101 capture)
        if 'timings' not in signal_data:
            return {
                'status': 'error',
                'message': 'Signal has no timing data. Only CC1101 captures can be replayed. RTL-SDR captures are raw IQ samples.'
            }

        base_freq = signal_data.get('frequency', 433.92)
        # Handle frequency in Hz vs MHz
        if base_freq > 1000:
            base_freq = base_freq / 1e6

        base_timings = signal_data['timings']

        results = []

        print(f"[*] Replaying '{signal_name}' with variations...")
        print(f"    Base frequency: {base_freq} MHz")
        print(f"    Trying {len(frequency_offsets)} frequency offsets")
        print(f"    Trying {len(timing_variations)} timing variations")

        for freq_offset in frequency_offsets:
            test_freq = base_freq + freq_offset

            for timing_mult in timing_variations:
                # Modify timings
                modified_timings = []
                for timing in base_timings:
                    modified_timings.append({
                        'state': timing['state'],
                        'duration_us': int(timing['duration_us'] * timing_mult)
                    })

                # Create modified signal
                modified_signal = {
                    'frequency': test_freq,
                    'timings': modified_timings
                }

                print(f"  [+] TX: {test_freq:.2f} MHz, timing x{timing_mult}")

                # Transmit
                self.cc1101.transmit_signal_enhanced(
                    modified_signal,
                    repeats=3,
                    power='max'
                )

                results.append({
                    'frequency': test_freq,
                    'timing_multiplier': timing_mult,
                    'transmitted': True
                })

                time.sleep(0.5)  # Brief delay between attempts

        return {
            'status': 'success',
            'variations_tried': len(results),
            'results': results
        }

    def brute_force_codes(self, frequency, bit_length, protocol='ook'):
        """
        Brute force simple fixed codes (educational only!)
        WARNING: Only use on your own devices!

        Args:
            frequency: TX frequency in MHz
            bit_length: Number of bits to brute force (max 16 for safety)
            protocol: 'ook' (On-Off Keying) or 'fsk'
        """
        if bit_length > 16:
            return {
                'status': 'error',
                'message': 'Bit length limited to 16 for safety (65,536 combinations)'
            }

        total_codes = 2 ** bit_length
        print(f"[!] Brute forcing {total_codes} codes at {frequency} MHz")
        print(f"[!] This will take approximately {total_codes * 0.1:.1f} seconds")
        print(f"[!] Press Ctrl+C to stop")

        results = []

        try:
            for code in range(total_codes):
                # Convert code to binary string
                binary = format(code, f'0{bit_length}b')

                # Create OOK timings (simple: 1=500us high, 0=500us low)
                timings = []
                for bit in binary:
                    if bit == '1':
                        timings.append({'state': 1, 'duration_us': 500})
                        timings.append({'state': 0, 'duration_us': 500})
                    else:
                        timings.append({'state': 0, 'duration_us': 500})
                        timings.append({'state': 1, 'duration_us': 500})

                signal_data = {
                    'frequency': frequency,
                    'timings': timings
                }

                # Transmit
                self.cc1101.transmit_signal(signal_data)

                if code % 100 == 0:
                    print(f"  [*] Progress: {code}/{total_codes} ({code/total_codes*100:.1f}%)")

                time.sleep(0.1)  # Brief delay

        except KeyboardInterrupt:
            print("\n[!] Stopped by user")

        return {
            'status': 'success',
            'codes_transmitted': code + 1,
            'total_codes': total_codes
        }

    def signal_fuzzing(self, signal_name, fuzz_percentage=10, iterations=50):
        """
        Fuzz a signal by randomly varying timings
        Helps find working variants of captured signals

        Args:
            signal_name: Name of saved signal
            fuzz_percentage: How much to vary timings (% of original)
            iterations: Number of fuzzed variants to try
        """
        import random

        # Load signal (try signal_library first, then captures directory)
        signal_path = self.signal_library / f"{signal_name}.json"

        if not signal_path.exists():
            # Try captures directory
            captures_dir = Path.home() / "piflip" / "captures"
            signal_path = captures_dir / f"{signal_name}.json"

            if not signal_path.exists():
                return {'status': 'error', 'message': f'Signal not found: {signal_name}'}

        with open(signal_path) as f:
            signal_data = json.load(f)

        # Check if signal has timing data (CC1101 capture)
        if 'timings' not in signal_data:
            return {
                'status': 'error',
                'message': 'Signal has no timing data. Only CC1101 captures can be fuzzed. RTL-SDR captures are raw IQ samples.'
            }

        base_timings = signal_data['timings']
        frequency = signal_data.get('frequency', 433.92)
        # Handle frequency in Hz vs MHz
        if frequency > 1000:
            frequency = frequency / 1e6

        print(f"[*] Fuzzing signal '{signal_name}'")
        print(f"    Variations: ±{fuzz_percentage}%")
        print(f"    Iterations: {iterations}")

        for i in range(iterations):
            fuzzed_timings = []

            for timing in base_timings:
                # Random variation within percentage
                variation = random.uniform(
                    1 - fuzz_percentage/100,
                    1 + fuzz_percentage/100
                )

                fuzzed_timings.append({
                    'state': timing['state'],
                    'duration_us': int(timing['duration_us'] * variation)
                })

            fuzzed_signal = {
                'frequency': frequency,
                'timings': fuzzed_timings
            }

            print(f"  [+] Fuzzing iteration {i+1}/{iterations}")
            self.cc1101.transmit_signal(fuzzed_signal)
            time.sleep(0.3)

        return {
            'status': 'success',
            'iterations': iterations,
            'fuzz_percentage': fuzz_percentage
        }

    def continuous_jam(self, frequency, duration_seconds=10, pattern='noise'):
        """
        Continuous transmission for jamming/testing
        Educational purposes - understand jamming, don't use maliciously!

        Args:
            frequency: Frequency to jam (MHz)
            duration_seconds: How long to transmit
            pattern: 'noise' (random), 'tone' (carrier), 'pulse' (on/off)
        """
        import random

        print(f"[!] JAMMING {frequency} MHz for {duration_seconds} seconds")
        print(f"[!] Pattern: {pattern}")
        print(f"[!] WARNING: This may interfere with nearby devices!")

        self.cc1101.set_frequency(frequency)
        self.cc1101.set_tx_power('max')

        start_time = time.time()

        try:
            while time.time() - start_time < duration_seconds:
                if pattern == 'noise':
                    # Random on/off
                    duration = random.randint(100, 1000)
                    timings = [{'state': random.randint(0, 1), 'duration_us': duration}]
                elif pattern == 'tone':
                    # Continuous carrier
                    timings = [{'state': 1, 'duration_us': 10000}]
                elif pattern == 'pulse':
                    # Regular pulses
                    timings = [
                        {'state': 1, 'duration_us': 500},
                        {'state': 0, 'duration_us': 500}
                    ]

                signal = {'frequency': frequency, 'timings': timings}
                self.cc1101.transmit_signal(signal)

        except KeyboardInterrupt:
            print("\n[!] Stopped by user")

        self.cc1101.idle()

        elapsed = time.time() - start_time
        return {
            'status': 'success',
            'frequency': frequency,
            'duration': elapsed,
            'pattern': pattern
        }

    def rolling_code_capture_replay(self, frequency, capture_duration=30):
        """
        Capture and immediately replay - useful for rolling codes
        Some rolling code systems accept recent codes

        Args:
            frequency: Frequency to monitor (MHz)
            capture_duration: How long to listen for signals (seconds)
        """
        print(f"[*] Rolling code capture & replay mode")
        print(f"    Frequency: {frequency} MHz")
        print(f"    Listening for {capture_duration} seconds...")
        print(f"[!] Press your remote NOW!")

        # Capture signal
        self.cc1101.set_frequency(frequency)
        capture_result = self.cc1101.capture_signal(duration=capture_duration, freq_mhz=frequency)

        # Check if we got timings
        if not capture_result.get('timings') or len(capture_result['timings']) == 0:
            return {'status': 'error', 'message': 'No signal captured'}

        print(f"[+] Signal captured! ({len(capture_result['timings'])} transitions)")
        print(f"[*] Replaying immediately...")

        # Create signal data in format expected by transmit_signal_enhanced
        signal_data = {
            'frequency': frequency,
            'timings': capture_result['timings']
        }

        # Immediate replay (before code rolls)
        for i in range(5):
            print(f"  [+] Replay {i+1}/5")
            self.cc1101.transmit_signal_enhanced(
                signal_data,
                repeats=1,
                power='max'
            )
            time.sleep(0.5)

        return {
            'status': 'success',
            'captured': True,
            'replayed': 5,
            'timings_count': len(capture_result['timings'])
        }

    def generate_custom_signal(self, frequency, pattern_binary, bit_duration_us=500):
        """
        Generate custom signal from binary pattern

        Args:
            frequency: TX frequency (MHz)
            pattern_binary: Binary string (e.g., "101010001111")
            bit_duration_us: Duration per bit in microseconds
        """
        print(f"[*] Generating custom signal")
        print(f"    Frequency: {frequency} MHz")
        print(f"    Pattern: {pattern_binary}")
        print(f"    Bit duration: {bit_duration_us} μs")

        # Convert binary to OOK timings
        timings = []
        for bit in pattern_binary:
            if bit == '1':
                timings.append({'state': 1, 'duration_us': bit_duration_us})
            else:
                timings.append({'state': 0, 'duration_us': bit_duration_us})

        signal_data = {
            'frequency': frequency,
            'timings': timings,
            'pattern': pattern_binary,
            'generated': True
        }

        # Transmit
        self.cc1101.transmit_signal_enhanced(signal_data, repeats=3, power='max')

        return {
            'status': 'success',
            'frequency': frequency,
            'pattern': pattern_binary,
            'bit_count': len(pattern_binary)
        }

if __name__ == "__main__":
    print("PiFlip Advanced TX Module")
    print("Educational purposes only!")
    print()

    adv_tx = RFAdvancedTX()

    # Example: Replay with variations
    # adv_tx.replay_with_variations('garage_remote')

    # Example: Brute force 8-bit code
    # adv_tx.brute_force_codes(frequency=433.92, bit_length=8)

    # Example: Signal fuzzing
    # adv_tx.signal_fuzzing('car_unlock', fuzz_percentage=15, iterations=30)

    # Example: Generate custom signal
    # adv_tx.generate_custom_signal(433.92, "11110000111100001111", bit_duration_us=400)

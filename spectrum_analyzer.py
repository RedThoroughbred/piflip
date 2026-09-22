#!/usr/bin/env python3
"""
Enhanced Spectrum Analyzer for PiFlip
PortaPack-style waterfall and spectrum display
"""

import subprocess
import numpy as np
import json
import time
from datetime import datetime
from pathlib import Path

# Waterfall band presets: start/stop in MHz, step in Hz (~500-1000 bins per sweep).
# 'mode' is the demod the radio should use when a point in the band is tapped.
BAND_PRESETS = {
    'ism433':  {'name': '433 ISM',            'start': 433.0,  'stop': 434.0,  'step': 2000,  'mode': 'nfm'},
    'fm':      {'name': 'FM Broadcast',       'start': 88.0,   'stop': 108.0,  'step': 25000, 'mode': 'wfm'},
    'air':     {'name': 'Airband',            'start': 118.0,  'stop': 137.0,  'step': 25000, 'mode': 'am'},
    'ham2m':   {'name': '2m Ham',             'start': 144.0,  'stop': 148.0,  'step': 5000,  'mode': 'nfm'},
    'ham70cm': {'name': '70cm Ham',           'start': 420.0,  'stop': 450.0,  'step': 25000, 'mode': 'nfm'},
    'ism900':  {'name': '900 ISM',            'start': 902.0,  'stop': 928.0,  'step': 25000, 'mode': 'nfm'},
    'adsb':    {'name': 'ADS-B vicinity',     'start': 1085.0, 'stop': 1095.0, 'step': 10000, 'mode': 'am'},
}


def band_range(band=None, start_mhz=None, stop_mhz=None, step_hz=None):
    """Resolve a preset name and/or explicit edges to (start_hz, stop_hz, step_hz)."""
    b = BAND_PRESETS.get(band or '', {})
    start = float(start_mhz if start_mhz is not None else b.get('start', 433.0))
    stop = float(stop_mhz if stop_mhz is not None else b.get('stop', 434.0))
    if stop <= start:
        raise ValueError('stop must be above start')
    if not (24.0 <= start and stop <= 1766.0) or stop - start > 100.0:
        raise ValueError('band must be within 24-1766 MHz and at most 100 MHz wide')
    step = float(step_hz if step_hz is not None else b.get('step', max(1000, (stop - start) * 1e6 / 512)))
    step = max(1.0, min(step, 2.8e6))
    return start * 1e6, stop * 1e6, step


class SpectrumAnalyzer:
    """RTL-SDR based spectrum analyzer with waterfall"""

    @staticmethod
    def sweep(start_hz, stop_hz, step_hz=1e6, interval=0.1, gain=None, timeout=None):
        """One rtl_power pass over [start_hz, stop_hz]. Wide ranges come back as
        several hop lines; they are merged and sorted. Returns a list of
        {'frequency': MHz, 'power': dB} or None if the dongle is busy/failed."""
        span = stop_hz - start_hz
        hops = max(1, int(span / 2.0e6) + 1)
        if timeout is None:
            timeout = 3 + hops * (float(interval) + 0.15)
        cmd = ['rtl_power', '-f', '%d:%d:%d' % (int(start_hz), int(stop_hz), int(step_hz)),
               '-i', str(interval), '-1']
        if gain:
            cmd += ['-g', str(gain)]
        cmd.append('-')
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None
        if result.returncode != 0:
            return None
        rows = {}
        for line in result.stdout.splitlines():
            parts = line.split(',')
            if len(parts) < 7:
                continue
            try:
                lo, hi = float(parts[2]), float(parts[3])
                dbs = [float(x) for x in parts[6:] if x.strip() not in ('', 'nan', '-nan')]
            except ValueError:
                continue
            if not dbs:
                continue
            st = (hi - lo) / len(dbs)
            for i, db in enumerate(dbs):
                rows[round(lo + i * st)] = db
        if not rows:
            return None
        return [{'frequency': f / 1e6, 'power': rows[f]} for f in sorted(rows)]

    def __init__(self):
        self.scan_history = []
        self.max_history = 100
        self.data_dir = Path.home() / 'piflip' / 'spectrum_data'
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def quick_scan(self, center_freq=433.92, span=2.0, bins=256):
        """
        Quick spectrum scan around center frequency

        Args:
            center_freq: Center frequency in MHz
            span: Frequency span in MHz
            bins: Number of FFT bins
        """
        start_freq = (center_freq - span/2) * 1e6
        end_freq = (center_freq + span/2) * 1e6

        try:
            # Use rtl_power for quick scan
            result = subprocess.run(
                ['rtl_power', '-f', f'{int(start_freq)}:{int(end_freq)}:1M',
                 '-i', '0.1', '-1', '-'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return {
                    'status': 'error',
                    'message': 'RTL-SDR busy or not available'
                }

            # Parse rtl_power output
            lines = [l for l in result.stdout.strip().split('\n') if l]

            if not lines:
                return {'status': 'error', 'message': 'No data received'}

            parts = lines[-1].split(',')
            if len(parts) < 7:
                return {'status': 'error', 'message': 'Invalid data format'}

            # Extract power values
            db_values = [float(x) for x in parts[6:]]

            # Calculate frequencies
            freq_low = float(parts[2])
            freq_high = float(parts[3])
            freq_step = (freq_high - freq_low) / len(db_values)

            spectrum = []
            for i, db in enumerate(db_values):
                freq = freq_low + (i * freq_step)
                spectrum.append({
                    'frequency': freq / 1e6,  # MHz
                    'power': db
                })

            # Find peak
            peak_idx = db_values.index(max(db_values))
            peak_freq = freq_low + (peak_idx * freq_step)

            return {
                'status': 'success',
                'spectrum': spectrum,
                'center_freq': center_freq,
                'span': span,
                'bins': len(db_values),
                'peak': {
                    'frequency': peak_freq / 1e6,
                    'power': max(db_values)
                },
                'timestamp': time.time()
            }

        except subprocess.TimeoutExpired:
            return {'status': 'error', 'message': 'Scan timeout'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def waterfall_scan(self, center_freq=433.92, span=2.0, duration=10, interval=0.2,
                       start_mhz=None, stop_mhz=None, step_hz=None, band=None):
        """
        Continuous waterfall scan

        Args:
            center_freq: Center frequency in MHz
            span: Frequency span in MHz
            duration: Scan duration in seconds
            interval: Time between scans in seconds
            start_mhz/stop_mhz: explicit band edges (override center/span)
            step_hz: rtl_power bin size (default 1 MHz, as before)
            band: a BAND_PRESETS key (fills start/stop/step)
        """
        if band or start_mhz is not None or stop_mhz is not None:
            start_freq, end_freq, step = band_range(band, start_mhz, stop_mhz, step_hz)
            center_freq = (start_freq + end_freq) / 2e6
            span = (end_freq - start_freq) / 1e6
        else:
            start_freq = (center_freq - span/2) * 1e6
            end_freq = (center_freq + span/2) * 1e6
            step = step_hz or 1e6
        hops = max(1, int((end_freq - start_freq) / 2.0e6) + 1)

        waterfall_data = []
        frequencies = None
        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # Quick scan
                spec = self.sweep(start_freq, end_freq, step, interval,
                                  timeout=max(3, 2 + hops * (interval + 0.15)))
                if spec:
                    if frequencies is None:
                        frequencies = [p['frequency'] for p in spec]
                    if len(spec) == len(frequencies):
                        waterfall_data.append({
                            'timestamp': time.time(),
                            'powers': [p['power'] for p in spec]
                        })

                time.sleep(max(0, interval - 0.1))

            if waterfall_data:
                return {
                    'status': 'success',
                    'waterfall': waterfall_data,
                    'frequencies': frequencies,  # MHz
                    'start_mhz': start_freq / 1e6,
                    'stop_mhz': end_freq / 1e6,
                    'step_hz': step,
                    'center_freq': center_freq,
                    'span': span,
                    'duration': duration,
                    'scan_count': len(waterfall_data)
                }
            else:
                return {'status': 'error', 'message': 'No data collected'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def generate_ascii_waterfall(self, waterfall_data, width=80, height=20):
        """
        Generate ASCII art waterfall display (PortaPack style)
        """
        if not waterfall_data or 'waterfall' not in waterfall_data:
            return "No waterfall data"

        scans = waterfall_data['waterfall'][-height:]  # Last N scans
        if not scans:
            return "No scans"

        # Color gradient for power levels (dBm)
        chars = ' .:-=+*#%@'

        lines = []

        # Header
        lines.append(f"Waterfall: {waterfall_data['center_freq']} MHz ± {waterfall_data['span']/2} MHz")
        lines.append("=" * width)

        # Process each scan (newest at top)
        for scan in reversed(scans):
            powers = scan['powers']

            # Normalize to character range
            min_power = min(powers)
            max_power = max(powers)
            power_range = max_power - min_power if max_power > min_power else 1

            # Resample to width
            step = len(powers) / width
            resampled = []
            for i in range(width):
                idx = int(i * step)
                power = powers[idx]
                # Map to char index
                normalized = (power - min_power) / power_range
                char_idx = int(normalized * (len(chars) - 1))
                resampled.append(chars[char_idx])

            lines.append(''.join(resampled))

        # Footer with frequency scale
        freq_min = waterfall_data['center_freq'] - waterfall_data['span']/2
        freq_max = waterfall_data['center_freq'] + waterfall_data['span']/2
        lines.append("=" * width)
        lines.append(f"{freq_min:.2f} MHz{' ' * (width-30)}{freq_max:.2f} MHz")

        return '\n'.join(lines)

    def detect_signals(self, spectrum_data, threshold_db=-80, min_width=0.05):
        """
        Detect signals in spectrum data

        Args:
            spectrum_data: Spectrum scan result
            threshold_db: Power threshold in dBm
            min_width: Minimum signal width in MHz
        """
        if spectrum_data['status'] != 'success':
            return {'status': 'error', 'message': 'Invalid spectrum data'}

        spectrum = spectrum_data['spectrum']
        signals = []

        in_signal = False
        signal_start = None
        signal_freqs = []
        signal_powers = []

        for point in list(spectrum) + [{'frequency': None, 'power': float('-inf')}]:
            freq = point['frequency']
            power = point['power']

            if power > threshold_db:
                if not in_signal:
                    # Start of new signal
                    in_signal = True
                    signal_start = freq
                    signal_freqs = [freq]
                    signal_powers = [power]
                else:
                    # Continue signal
                    signal_freqs.append(freq)
                    signal_powers.append(power)
            else:
                if in_signal:
                    # End of signal
                    in_signal = False

                    # Check if signal is wide enough
                    signal_width = signal_freqs[-1] - signal_freqs[0]
                    if signal_width >= min_width:
                        # Calculate signal center and peak
                        center_freq = (signal_freqs[0] + signal_freqs[-1]) / 2
                        peak_power = max(signal_powers)

                        signals.append({
                            'center_freq': round(center_freq, 3),
                            'start_freq': round(signal_freqs[0], 3),
                            'end_freq': round(signal_freqs[-1], 3),
                            'bandwidth': round(signal_width, 3),
                            'peak_power': round(peak_power, 2),
                            'avg_power': round(sum(signal_powers) / len(signal_powers), 2)
                        })

        return {
            'status': 'success',
            'signals': signals,
            'count': len(signals),
            'threshold': threshold_db
        }

    def frequency_hopper_detect(self, duration=30):
        """
        Detect frequency hopping signals (Bluetooth, cordless phones, etc.)
        """
        # Scan wide range looking for hopping patterns
        # This is advanced - requires multiple scans and correlation

        scans = []
        center_freqs = [2.44, 2.45, 2.46]  # 2.4 GHz ISM band

        for freq in center_freqs:
            result = self.quick_scan(center_freq=freq, span=0.1, bins=512)
            if result['status'] == 'success':
                scans.append(result)
            time.sleep(0.5)

        # Analyze for hopping
        # Look for signals appearing/disappearing across scans

        return {
            'status': 'analysis_complete',
            'scans': len(scans),
            'note': 'Frequency hopping detection is experimental'
        }

    def save_scan(self, scan_data, name):
        """Save spectrum scan to file"""
        try:
            filename = f"{name}_{int(time.time())}.json"
            filepath = self.data_dir / filename

            scan_data['saved_name'] = name
            scan_data['saved_timestamp'] = datetime.now().isoformat()

            with open(filepath, 'w') as f:
                json.dump(scan_data, f, indent=2)

            return {
                'status': 'saved',
                'name': name,
                'path': str(filepath)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def reset_rtlsdr(self):
        """Reset RTL-SDR device - use if scans hang or fail"""
        try:
            result = {'steps': []}

            # Step 1: Kill any stuck rtl processes
            kill_result = subprocess.run(
                ['sudo', 'killall', '-9', 'rtl_power', 'rtl_fm', 'rtl_sdr', 'rtl_tcp', 'rtl_test'],
                capture_output=True,
                text=True,
                timeout=5
            )
            result['steps'].append('Killed stuck RTL-SDR processes')

            # Step 2: Reset USB device
            reset_result = subprocess.run(
                ['sudo', 'usbreset', '0bda:2838'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if reset_result.returncode == 0:
                result['steps'].append('USB device reset successful')
            else:
                # Try alternative method
                subprocess.run(
                    ['bash', '-c', 'echo "0bda 2838" | sudo tee /sys/bus/usb/drivers/dvb_usb_rtl28xxu/unbind 2>/dev/null; sleep 1; echo "0bda 2838" | sudo tee /sys/bus/usb/drivers/dvb_usb_rtl28xxu/bind 2>/dev/null'],
                    capture_output=True,
                    timeout=5
                )
                result['steps'].append('USB device rebound')

            # Step 3: Wait for device to settle
            time.sleep(2)
            result['steps'].append('Waited for device to settle')

            # Step 4: Test device
            test_result = subprocess.run(
                ['rtl_test', '-t'],
                capture_output=True,
                text=True,
                timeout=3
            )

            if 'Found 1 device' in test_result.stdout or 'Found 1 device' in test_result.stderr:
                result['steps'].append('RTL-SDR device detected')
                result['status'] = 'success'
                result['message'] = 'RTL-SDR reset successfully'
            else:
                result['status'] = 'warning'
                result['message'] = 'Reset completed but device may need replug'

            return result

        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'message': 'Reset timeout - device may be disconnected',
                'steps': result.get('steps', [])
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Reset failed: {str(e)}',
                'steps': result.get('steps', [])
            }


if __name__ == '__main__':
    # Test spectrum analyzer
    analyzer = SpectrumAnalyzer()

    print("[*] Testing Spectrum Analyzer...")
    print("=" * 60)

    # Quick scan around 433 MHz
    print("\n[*] Scanning 433 MHz ISM band...")
    result = analyzer.quick_scan(center_freq=433.92, span=2.0)

    if result['status'] == 'success':
        print(f"[+] Scan complete: {result['bins']} bins")
        print(f"[+] Peak at {result['peak']['frequency']:.2f} MHz ({result['peak']['power']:.1f} dBm)")

        # Detect signals
        signals = analyzer.detect_signals(result, threshold_db=-80)
        print(f"\n[+] Detected {signals['count']} signals:")
        for sig in signals['signals'][:5]:
            print(f"    {sig['center_freq']:.3f} MHz (BW: {sig['bandwidth']:.3f} MHz, {sig['peak_power']:.1f} dBm)")

    else:
        print(f"[!] Scan failed: {result.get('message', 'Unknown error')}")

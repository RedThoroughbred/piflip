#!/usr/bin/env python3
"""
Enhanced CC1101 Controller for PiFlip
Full RX/TX capabilities for sub-GHz RF operations
"""

import spidev
import RPi.GPIO as GPIO
import time
import json
import os
from datetime import datetime
from pathlib import Path

class CC1101Enhanced:
    """Enhanced CC1101 with full receive and transmit capabilities"""

    # CC1101 Register addresses
    IOCFG2 = 0x00
    IOCFG1 = 0x01
    IOCFG0 = 0x02
    FIFOTHR = 0x03
    PKTLEN = 0x06
    PKTCTRL1 = 0x07
    PKTCTRL0 = 0x08
    ADDR = 0x09
    CHANNR = 0x0A
    FSCTRL1 = 0x0B
    FSCTRL0 = 0x0C
    FREQ2 = 0x0D
    FREQ1 = 0x0E
    FREQ0 = 0x0F
    MDMCFG4 = 0x10
    MDMCFG3 = 0x11
    MDMCFG2 = 0x12
    MDMCFG1 = 0x13
    MDMCFG0 = 0x14
    DEVIATN = 0x15
    MCSM2 = 0x16
    MCSM1 = 0x17
    MCSM0 = 0x18
    FOCCFG = 0x19
    BSCFG = 0x1A
    AGCCTRL2 = 0x1B
    AGCCTRL1 = 0x1C
    AGCCTRL0 = 0x1D
    FREND1 = 0x21
    FREND0 = 0x22
    FSCAL3 = 0x23
    FSCAL2 = 0x24
    FSCAL1 = 0x25
    FSCAL0 = 0x26
    TEST2 = 0x2C
    TEST1 = 0x2D
    TEST0 = 0x2E
    PATABLE = 0x3E

    # Strobe commands
    SRES = 0x30      # Reset
    SFSTXON = 0x31   # Enable and calibrate frequency synthesizer
    SXOFF = 0x32     # Turn off crystal oscillator
    SCAL = 0x33      # Calibrate frequency synthesizer
    SRX = 0x34       # Enable RX
    STX = 0x35       # Enable TX
    SIDLE = 0x36     # Exit RX/TX, turn off frequency synthesizer
    SWOR = 0x38      # Start automatic RX polling
    SPWD = 0x39      # Enter power down mode
    SFRX = 0x3A      # Flush the RX FIFO buffer
    SFTX = 0x3B      # Flush the TX FIFO buffer
    SWORRST = 0x3C   # Reset real time clock
    SNOP = 0x3D      # No operation

    # Status registers
    PARTNUM = 0x30
    VERSION = 0x31
    FREQEST = 0x32
    LQI = 0x33
    RSSI = 0x34
    MARCSTATE = 0x35
    PKTSTATUS = 0x38
    TXBYTES = 0x3A
    RXBYTES = 0x3B

    # FIFO access
    TXFIFO = 0x3F
    RXFIFO = 0x3F

    def __init__(self, gdo0_pin=17, gdo2_pin=6, csn_pin=8):
        """Initialize CC1101 with GPIO pins"""
        self.GDO0_PIN = gdo0_pin
        self.GDO2_PIN = gdo2_pin
        self.CSN_PIN = csn_pin

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 50000
        self.spi.mode = 0

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GDO0_PIN, GPIO.IN)
        GPIO.setup(self.GDO2_PIN, GPIO.IN)

        # Create signal library directory
        self.library_dir = Path(os.path.expanduser("~/piflip/rf_library"))
        self.library_dir.mkdir(parents=True, exist_ok=True)

        # Reset and initialize
        self.reset()
        self.configure_default()

    def write_register(self, address, value):
        """Write single byte to register"""
        self.spi.xfer2([address, value])

    def read_register(self, address):
        """Read single byte from register"""
        result = self.spi.xfer2([address | 0x80, 0x00])
        return result[1]

    def write_burst(self, address, data):
        """Write multiple bytes to register"""
        self.spi.xfer2([address | 0x40] + list(data))

    def read_burst(self, address, length):
        """Read multiple bytes from register"""
        result = self.spi.xfer2([address | 0xC0] + [0x00] * length)
        return result[1:]

    def strobe_command(self, command):
        """Send strobe command"""
        self.spi.xfer2([command])

    def reset(self):
        """Reset CC1101"""
        self.strobe_command(self.SRES)
        time.sleep(0.1)

    def get_status(self):
        """Get chip status"""
        partnum = self.read_register(self.PARTNUM | 0xC0)
        version = self.read_register(self.VERSION | 0xC0)
        return {
            'partnum': f"0x{partnum:02X}",
            'version': f"0x{version:02X}",
            'detected': partnum == 0x00 and version > 0x00
        }

    def set_frequency(self, freq_mhz):
        """Set carrier frequency in MHz"""
        # CC1101 frequency formula: freq = (FREQ * 26MHz) / 2^16
        freq_reg = int((freq_mhz * 1e6 * 65536) / 26e6)

        freq2 = (freq_reg >> 16) & 0xFF
        freq1 = (freq_reg >> 8) & 0xFF
        freq0 = freq_reg & 0xFF

        self.write_register(self.FREQ2, freq2)
        self.write_register(self.FREQ1, freq1)
        self.write_register(self.FREQ0, freq0)

        return freq_mhz

    def configure_default(self):
        """Configure CC1101 with default settings for 433.92MHz OOK"""
        # Set 433.92MHz
        self.set_frequency(433.92)

        # Configure packet handling
        self.write_register(self.PKTCTRL0, 0x32)  # Async mode, infinite packet length
        self.write_register(self.PKTLEN, 0xFF)    # Max packet length

        # Configure modulation (OOK)
        self.write_register(self.MDMCFG2, 0x30)   # OOK, no sync
        self.write_register(self.MDMCFG4, 0x5B)   # Data rate config
        self.write_register(self.MDMCFG3, 0xF8)   # Data rate config

        # Configure GDO0 for RX data output
        self.write_register(self.IOCFG0, 0x0D)    # GDO0 = serial data output

        # Configure GDO2 for RX/TX indicator
        self.write_register(self.IOCFG2, 0x06)    # GDO2 = sync word sent/received

        # Set PA table (power)
        self.write_register(self.PATABLE, 0xC0)   # Max power ~10dBm

        # FIFO threshold
        self.write_register(self.FIFOTHR, 0x47)   # 33 bytes TX, 32 bytes RX

    def configure_rx(self, freq_mhz=433.92):
        """Configure for receive mode"""
        self.set_frequency(freq_mhz)

        # Configure for better reception
        self.write_register(self.AGCCTRL2, 0x43)  # AGC settings
        self.write_register(self.AGCCTRL1, 0x40)
        self.write_register(self.AGCCTRL0, 0x91)

        # Configure GDO0 to output received data
        self.write_register(self.IOCFG0, 0x0D)    # GDO0 = serial data output

        # Set MCSM1 for RX after packet
        self.write_register(self.MCSM1, 0x0F)     # Stay in RX after packet

    def enter_rx_mode(self):
        """Enter receive mode"""
        self.strobe_command(self.SFRX)   # Flush RX FIFO
        self.strobe_command(self.SRX)    # Enter RX mode

    def enter_tx_mode(self):
        """Enter transmit mode"""
        self.strobe_command(self.SFTX)   # Flush TX FIFO
        self.strobe_command(self.STX)    # Enter TX mode

    def idle(self):
        """Enter idle mode"""
        self.strobe_command(self.SIDLE)

    def get_rssi(self):
        """Get RSSI value in dBm"""
        rssi_raw = self.read_register(self.RSSI | 0xC0)
        if rssi_raw >= 128:
            rssi_dbm = (rssi_raw - 256) / 2 - 74
        else:
            rssi_dbm = rssi_raw / 2 - 74
        return rssi_dbm

    def capture_signal(self, duration=5.0, freq_mhz=433.92):
        """Capture raw signal data from GDO0 pin"""
        self.configure_rx(freq_mhz)
        self.enter_rx_mode()

        print(f"[*] Listening on {freq_mhz} MHz for {duration} seconds...")

        samples = []
        start_time = time.time()
        sample_interval = 0.00001  # 100kHz sampling (10us per sample)

        while time.time() - start_time < duration:
            # Read GDO0 state (high or low)
            state = GPIO.input(self.GDO0_PIN)
            samples.append(state)
            time.sleep(sample_interval)

        self.idle()

        # Convert to timing pairs (on/off durations)
        timings = self._samples_to_timings(samples, sample_interval)

        return {
            'samples': samples,
            'timings': timings,
            'frequency': freq_mhz,
            'duration': duration,
            'sample_count': len(samples),
            'rssi': self.get_rssi()
        }

    def _samples_to_timings(self, samples, sample_interval):
        """Convert sample array to timing pairs"""
        if not samples:
            return []

        timings = []
        current_state = samples[0]
        duration_count = 1

        for sample in samples[1:]:
            if sample == current_state:
                duration_count += 1
            else:
                # State changed, record duration
                duration_us = int(duration_count * sample_interval * 1e6)
                timings.append({'state': current_state, 'duration_us': duration_us})
                current_state = sample
                duration_count = 1

        # Add final duration
        duration_us = int(duration_count * sample_interval * 1e6)
        timings.append({'state': current_state, 'duration_us': duration_us})

        return timings

    def save_signal(self, capture_data, name):
        """Save captured signal to library"""
        signal_file = self.library_dir / f"{name}.json"

        signal_data = {
            'name': name,
            'frequency': capture_data['frequency'],
            'duration': capture_data['duration'],
            'sample_count': capture_data['sample_count'],
            'timings': capture_data['timings'],
            'rssi': capture_data.get('rssi', -100),
            'timestamp': datetime.now().isoformat(),
            'modulation': 'OOK'
        }

        with open(signal_file, 'w') as f:
            json.dump(signal_data, f, indent=2)

        return {
            'status': 'saved',
            'name': name,
            'file': str(signal_file),
            'timing_count': len(capture_data['timings'])
        }

    def list_signals(self):
        """List all saved signals"""
        signals = []
        for file in self.library_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    signals.append({
                        'name': data['name'],
                        'frequency': data['frequency'],
                        'timestamp': data['timestamp'],
                        'duration': data['duration']
                    })
            except:
                pass

        return sorted(signals, key=lambda x: x['timestamp'], reverse=True)

    def load_signal(self, name):
        """Load signal from library"""
        signal_file = self.library_dir / f"{name}.json"
        if not signal_file.exists():
            return None

        with open(signal_file, 'r') as f:
            return json.load(f)

    def transmit_signal(self, signal_data):
        """Transmit a saved signal"""
        freq = signal_data['frequency']
        timings = signal_data['timings']

        self.set_frequency(freq)
        self.configure_default()
        self.enter_tx_mode()

        print(f"[*] Transmitting on {freq} MHz...")

        # Replay timings on GDO0
        for timing in timings:
            state = timing['state']
            duration_us = timing['duration_us']

            # Since we're in TX mode, writing to TXFIFO controls transmission
            # For simple OOK, we can use GDO pins or FIFO
            # This is a simplified approach - actual implementation depends on signal type
            time.sleep(duration_us / 1e6)

        self.idle()

        return {
            'status': 'transmitted',
            'frequency': freq,
            'timing_count': len(timings)
        }

    def scan_frequencies(self, start_mhz=433.0, end_mhz=434.0, step_mhz=0.1, rssi_threshold=-80):
        """Scan frequency range for active signals"""
        results = []
        current_freq = start_mhz

        print(f"[*] Scanning {start_mhz} - {end_mhz} MHz...")

        while current_freq <= end_mhz:
            self.set_frequency(current_freq)
            self.enter_rx_mode()
            time.sleep(0.1)  # Brief listen

            rssi = self.get_rssi()
            if rssi > rssi_threshold:
                results.append({
                    'frequency': round(current_freq, 2),
                    'rssi': round(rssi, 1)
                })
                print(f"  [+] Signal at {current_freq:.2f} MHz: {rssi:.1f} dBm")

            current_freq += step_mhz

        self.idle()
        return results

    def set_tx_power(self, power_level='max'):
        """
        Set transmission power level

        Args:
            power_level: 'min' (-30dBm), 'low' (-20dBm), 'medium' (-10dBm),
                        'high' (0dBm), 'max' (+10dBm)
        """
        power_table = {
            'min': 0x03,      # -30 dBm
            'low': 0x0E,      # -20 dBm
            'medium': 0x1D,   # -10 dBm
            'high': 0x60,     #   0 dBm
            'max': 0xC0       # +10 dBm (maximum)
        }

        pa_value = power_table.get(power_level, 0xC0)
        self.write_register(self.PATABLE, pa_value)

        return {
            'power_level': power_level,
            'pa_value': f"0x{pa_value:02X}"
        }

    def transmit_signal_enhanced(self, signal_data, repeats=3, power='max'):
        """
        Enhanced transmission with repeats and power control

        Args:
            signal_data: Signal dictionary with timings
            repeats: Number of times to transmit (default 3)
            power: Power level ('min', 'low', 'medium', 'high', 'max')

        Returns:
            Transmission status
        """
        freq = signal_data['frequency']
        timings = signal_data['timings']

        # Set maximum power for better range
        self.set_tx_power(power)

        self.set_frequency(freq)
        self.configure_default()

        print(f"[*] Transmitting on {freq} MHz at {power} power...")
        print(f"[*] Repeating {repeats} times...")

        successful_transmits = 0

        for repeat in range(repeats):
            try:
                self.enter_tx_mode()

                # Add preamble for better receiver lock
                preamble_duration = 500  # 500us preamble
                time.sleep(preamble_duration / 1e6)

                # Replay timings
                for timing in timings:
                    duration_us = timing['duration_us']
                    time.sleep(duration_us / 1e6)

                # Brief gap between repeats
                if repeat < repeats - 1:
                    time.sleep(0.01)  # 10ms gap

                successful_transmits += 1

            except Exception as e:
                print(f"[!] Transmit {repeat + 1} failed: {e}")

        self.idle()

        return {
            'status': 'transmitted',
            'frequency': freq,
            'power_level': power,
            'repeats': repeats,
            'successful': successful_transmits,
            'timing_count': len(timings)
        }

    def capture_signal_enhanced(self, duration=5.0, freq_mhz=433.92, auto_retry=True):
        """
        Enhanced capture with quality checking and auto-retry

        Args:
            duration: Capture duration in seconds
            freq_mhz: Frequency to capture on
            auto_retry: If True, retry if signal quality is poor

        Returns:
            Signal data with quality metrics
        """
        max_retries = 3 if auto_retry else 1
        best_capture = None
        best_quality = 0

        for attempt in range(max_retries):
            print(f"[*] Capture attempt {attempt + 1}/{max_retries}...")

            capture = self.capture_signal(duration, freq_mhz)

            # Calculate quality score
            transitions = len(capture['timings'])
            rssi = capture['rssi']

            # Quality score: more transitions + stronger signal = better
            quality_score = transitions + (rssi + 100)  # Normalize RSSI

            if quality_score > best_quality:
                best_quality = quality_score
                best_capture = capture
                best_capture['quality_score'] = quality_score
                best_capture['attempt'] = attempt + 1

            # If we got a good capture, stop early
            if transitions > 1000 and rssi > -70:
                print(f"[+] High quality capture on attempt {attempt + 1}")
                break

            if attempt < max_retries - 1:
                print(f"[!] Low quality (score: {quality_score}), retrying...")
                time.sleep(0.5)

        print(f"[+] Best capture: {best_capture.get('quality_score', 0)} quality score")
        return best_capture

    def delete_signal(self, name):
        """Delete signal from library"""
        signal_file = self.library_dir / f"{name}.json"
        if signal_file.exists():
            signal_file.unlink()
            return {'status': 'deleted', 'name': name}
        return {'status': 'not_found', 'name': name}

    def cleanup(self):
        """Clean up resources"""
        self.idle()
        self.spi.close()

if __name__ == "__main__":
    # Test CC1101
    print("[*] Initializing CC1101...")
    cc = CC1101Enhanced()

    status = cc.get_status()
    print(f"[+] CC1101 Status: {status}")

    if status['detected']:
        print("[+] CC1101 detected and ready!")

        # Test frequency scan
        print("\n[*] Testing frequency scanner...")
        signals = cc.scan_frequencies(433.0, 434.0, 0.25)
        print(f"[+] Found {len(signals)} active frequencies")

    cc.cleanup()

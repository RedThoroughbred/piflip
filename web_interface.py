#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request, Response
import subprocess
import json
import os
import time
import requests
import spidev
import RPi.GPIO as GPIO
from datetime import datetime
from pathlib import Path

# Imports for PN532
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

# Import URH analyzer and auto analyzer
import sys
sys.path.insert(0, os.path.expanduser('~/piflip'))
from urh_analyzer import URHAnalyzer
from auto_analyzer import AutoAnalyzer
from nfc_enhanced import NFCEnhanced
from nfc_cloner import NFCCloner
from cc1101_enhanced import CC1101Enhanced
from signal_decoder import SignalDecoder
from nfc_emulator import NFCEmulator, MagicCardHelper
from favorites_manager import FavoritesManager
from waveform_generator import WaveformGenerator
from bluetooth_scanner import BluetoothScanner
from wifi_manager import WiFiManager, WiFiScanner
from spectrum_analyzer import SpectrumAnalyzer
from rf_advanced_tx import RFAdvancedTX
from nfc_guardian import NFCGuardian
from card_catalog import CardCatalog
from rfid_wallet_tester import RFIDWalletTester

app = Flask(__name__)

# --- Global Controllers ---
pn532_controller = None
nfc_enhanced = None
cc1101_controller = None
cc1101_enhanced = None

class CC1101Controller:
    """CC1101 controller for sub-GHz RF operations"""
    def __init__(self):
        self.GDO0_PIN = 17
        self.GDO2_PIN = 6
        self.CSN_PIN = 8

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 50000
        self.spi.mode = 0

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GDO0_PIN, GPIO.IN)
        GPIO.setup(self.GDO2_PIN, GPIO.IN)

        self.reset()
        self.configure_433mhz()

    def write_register(self, address, value):
        self.spi.xfer2([address, value])

    def read_register(self, address):
        result = self.spi.xfer2([address | 0x80, 0x00])
        return result[1]

    def strobe_command(self, command):
        self.spi.xfer2([command])

    def reset(self):
        self.strobe_command(0x30)  # SRES
        time.sleep(0.1)

    def configure_433mhz(self):
        """Configure for 433.92MHz OOK"""
        self.write_register(0x0D, 0x10)  # FREQ2
        self.write_register(0x0E, 0xA7)  # FREQ1
        self.write_register(0x0F, 0x62)  # FREQ0
        self.write_register(0x12, 0x03)  # MDMCFG2 - OOK modulation
        self.write_register(0x10, 0x5B)  # MDMCFG4
        self.write_register(0x11, 0xF8)  # MDMCFG3
        self.write_register(0x3E, 0xC0)  # PATABLE

    def get_version_info(self):
        partnum = self.read_register(0x30)
        version = self.read_register(0x31)
        return f"Part: 0x{partnum:02X}, Version: 0x{version:02X}"

    def cleanup(self):
        self.spi.close()

def initialize_pn532():
    """Initializes the PN532 controller if not already done."""
    global pn532_controller
    if pn532_controller is None:
        print("[+] Initializing PN532 Controller for Web App...")
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            pn532_controller = PN532_I2C(i2c, debug=False)
            ic, ver, rev, support = pn532_controller.firmware_version
            print(f"[+] Found PN532 with firmware version: {ver}.{rev}")
            pn532_controller.SAM_configuration()
        except Exception as e:
            print(f"[!] PN532 Web App Init Error: {e}")
            pn532_controller = None
    return pn532_controller

def initialize_nfc_enhanced():
    """Initialize enhanced NFC controller"""
    global nfc_enhanced
    if nfc_enhanced is None:
        print("[+] Initializing Enhanced NFC Controller for Web App...")
        try:
            nfc_enhanced = NFCEnhanced()
            print(f"[+] Enhanced NFC initialized successfully")
        except Exception as e:
            print(f"[!] Enhanced NFC Init Error: {e}")
            nfc_enhanced = None
    return nfc_enhanced

def initialize_cc1101():
    """Initializes the CC1101 controller if not already done."""
    global cc1101_controller
    if cc1101_controller is None:
        print("[+] Initializing CC1101 Controller for Web App...")
        try:
            cc1101_controller = CC1101Controller()
            print(f"[+] CC1101 initialized: {cc1101_controller.get_version_info()}")
        except Exception as e:
            print(f"[!] CC1101 Web App Init Error: {e}")
            cc1101_controller = None
    return cc1101_controller

def initialize_cc1101_enhanced():
    """Initialize enhanced CC1101 controller with RX/TX"""
    global cc1101_enhanced
    if cc1101_enhanced is None:
        print("[+] Initializing Enhanced CC1101 Controller for Web App...")
        try:
            cc1101_enhanced = CC1101Enhanced()
            status = cc1101_enhanced.get_status()
            print(f"[+] Enhanced CC1101 initialized: {status}")
        except Exception as e:
            print(f"[!] Enhanced CC1101 Init Error: {e}")
            cc1101_enhanced = None
    return cc1101_enhanced

# --- Web App Routes ---

@app.route('/')
def index():
    initialize_pn532()
    import time
    return render_template('flipper_ui.html', cache_bust=int(time.time()))

@app.route('/old')
def old_interface():
    # Add timestamp to bust cache
    import time
    return render_template('index.html', cache_bust=int(time.time()))

@app.route('/test')
def test_suite():
    return render_template('test_suite.html')

@app.route('/nfc_test')
def nfc_test():
    return render_template('nfc_test.html')

@app.route('/api/status')
def status():
    """Get status of all hardware components"""
    status_info = {
        'nfc': False,
        'rtl_sdr': False,
        'cc1101': False
    }

    # Check PN532 NFC
    try:
        if pn532_controller is None:
            initialize_pn532()
        status_info['nfc'] = pn532_controller is not None
    except:
        status_info['nfc'] = False

    # Check RTL-SDR (check if device is present)
    try:
        result = subprocess.run(['rtl_test', '-t'], capture_output=True,
                              text=True, timeout=2)
        status_info['rtl_sdr'] = 'Found' in result.stdout
    except:
        status_info['rtl_sdr'] = False

    # Check CC1101 (try to initialize and read chip version)
    try:
        if cc1101_enhanced is None:
            initialize_cc1101_enhanced()
        status_info['cc1101'] = cc1101_enhanced is not None
    except:
        status_info['cc1101'] = False

    return jsonify(status_info)

@app.route('/api/scan433')
def scan433():
    """Scan for 433MHz devices using rtl_433 - wider scan with hop"""
    # Use frequency hopping to scan 433-434MHz range
    # This catches more devices: doorbells, remotes, sensors, weather stations, etc.
    # Use higher gain for better reception
    result = subprocess.run(
        ['timeout', '30', 'rtl_433', '-f', '433.92M', '-g', '40', '-H', '15', '-F', 'json'],
        capture_output=True, text=True
    )

    # Check if RTL-SDR is busy
    if 'usb_claim_interface error -6' in result.stderr or 'usb_claim_interface error -6' in result.stdout:
        return jsonify({
            'error': 'RTL-SDR is in use',
            'message': 'RTL-SDR is currently being used by another program. Please close the other program first.',
            'devices': [],
            'count': 0,
            'raw_output': result.stderr
        })

    devices = []
    for line in result.stdout.split('\n'):
        if line.strip():
            try:
                data = json.loads(line)
                devices.append(data)
            except:
                pass

    # Also capture any error/info messages
    info_lines = [line for line in result.stderr.split('\n') if line.strip() and not line.startswith('rtl_433')]

    return jsonify({
        'devices': devices,
        'count': len(devices),
        'scan_duration': '30 seconds',
        'frequency': '433.92MHz with hopping',
        'info': info_lines[:5] if info_lines else [],
        'raw_output': result.stderr if len(devices) == 0 else ''
    })

@app.route('/api/capture', methods=['POST'])
def capture():
    """Capture raw RF signal with rtl_sdr"""
    data = request.get_json()
    frequency = data.get('frequency', 433920000)  # Default 433.92MHz
    sample_rate = data.get('sample_rate', 2048000)  # 2.048 MS/s
    duration = data.get('duration', 5)  # seconds
    name = data.get('name', f'capture_{int(time.time())}')

    # Calculate number of samples
    num_samples = int(sample_rate * duration)

    # Create captures directory
    capture_dir = os.path.expanduser("~/piflip/captures")
    os.makedirs(capture_dir, exist_ok=True)

    filename = f"{name}.cu8"
    filepath = os.path.join(capture_dir, filename)

    # Capture using rtl_sdr with high gain for better signal strength
    result = subprocess.run(
        ['rtl_sdr', '-f', str(frequency), '-s', str(sample_rate),
         '-g', '40', '-n', str(num_samples), filepath],
        capture_output=True, text=True, timeout=duration + 5
    )

    if 'usb_claim_interface error -6' in result.stderr:
        return jsonify({
            'error': 'RTL-SDR is in use',
            'message': 'Close other programs using RTL-SDR first'
        }), 500

    # Save metadata
    metadata = {
        'name': name,
        'filename': filename,
        'frequency': frequency,
        'sample_rate': sample_rate,
        'duration': duration,
        'num_samples': num_samples,
        'timestamp': datetime.now().isoformat(),
        'file_size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
    }

    metadata_file = os.path.join(capture_dir, f"{name}.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    # Automatically analyze the capture in background
    try:
        analyzer = AutoAnalyzer()
        analysis_result = analyzer.analyze_capture_auto(name)
        metadata['auto_analysis'] = analysis_result
    except Exception as e:
        metadata['auto_analysis'] = {'error': str(e), 'status': 'analysis_failed'}

    return jsonify({
        'status': 'success',
        'message': f'Captured {duration} seconds at {frequency/1e6:.2f} MHz',
        'metadata': metadata,
        'auto_analyzed': True
    })

@app.route('/api/captures')
def list_captures():
    """List all saved signal captures"""
    capture_dir = os.path.expanduser("~/piflip/captures")
    if not os.path.exists(capture_dir):
        return jsonify({'captures': []})

    captures = []
    for file in os.listdir(capture_dir):
        if file.endswith('.json'):
            filepath = os.path.join(capture_dir, file)
            try:
                with open(filepath, 'r') as f:
                    metadata = json.load(f)
                    captures.append(metadata)
            except:
                pass

    # Sort by timestamp, newest first
    captures.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify({'captures': captures, 'count': len(captures)})

@app.route('/api/capture/<name>', methods=['DELETE'])
def delete_capture(name):
    """Delete a signal capture"""
    capture_dir = os.path.expanduser("~/piflip/captures")

    # Delete both .cu8 and .json files
    cu8_file = os.path.join(capture_dir, f"{name}.cu8")
    json_file = os.path.join(capture_dir, f"{name}.json")

    deleted = []
    if os.path.exists(cu8_file):
        os.remove(cu8_file)
        deleted.append(f"{name}.cu8")
    if os.path.exists(json_file):
        os.remove(json_file)
        deleted.append(f"{name}.json")

    return jsonify({
        'status': 'deleted',
        'files': deleted
    })

@app.route('/api/nfc')
def nfc():
    """Scan for NFC card with detailed information"""
    controller = initialize_nfc_enhanced()
    if not controller:
        return jsonify({'status': 'Error', 'message': 'NFC not initialized'}), 500
    try:
        card_data = controller.read_card_detailed(timeout=0.5)
        if card_data is None:
            return jsonify({'status': 'No card found', 'card_present': False})
        return jsonify({**card_data, 'card_present': True})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/nfc/save', methods=['POST'])
def nfc_save():
    """Save NFC card to library"""
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'status': 'Error', 'message': 'Name required'}), 400

    controller = initialize_nfc_enhanced()
    if not controller:
        return jsonify({'status': 'Error', 'message': 'NFC not initialized'}), 500

    try:
        # Read card with longer timeout
        card_data = controller.read_card_detailed(timeout=3.0)
        if card_data is None:
            return jsonify({'status': 'Error', 'message': 'No card found. Keep card on reader for 3 seconds.'}), 404

        # Save to library
        result = controller.save_card(card_data, name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/nfc/library')
def nfc_library():
    """List saved NFC cards"""
    controller = initialize_nfc_enhanced()
    if not controller:
        return jsonify({'status': 'Error', 'message': 'NFC not initialized'}), 500

    try:
        cards = controller.list_saved_cards()
        return jsonify({'cards': cards, 'count': len(cards)})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/nfc/library/<name>', methods=['DELETE'])
def nfc_delete(name):
    """Delete saved NFC card"""
    controller = initialize_nfc_enhanced()
    if not controller:
        return jsonify({'status': 'Error', 'message': 'NFC not initialized'}), 500

    try:
        result = controller.delete_card(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/nfc/read_full', methods=['POST'])
def nfc_read_full():
    """Read full card dump (all sectors)"""
    try:
        cloner = NFCCloner()
        dump = cloner.read_full_card()
        return jsonify(dump)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nfc/clone', methods=['POST'])
def nfc_clone():
    """Clone a card to magic card"""
    data = request.get_json()
    source_dump = data.get('dump')

    if not source_dump:
        return jsonify({'error': 'No dump provided'}), 400

    try:
        cloner = NFCCloner()
        result = cloner.write_to_magic_card(source_dump)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nfc/verify', methods=['POST'])
def nfc_verify():
    """Verify cloned card matches original"""
    data = request.get_json()
    original_dump = data.get('dump')

    if not original_dump:
        return jsonify({'error': 'No dump provided'}), 400

    try:
        cloner = NFCCloner()
        result = cloner.verify_clone(original_dump)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tpms')
def tpms():
    """Scan for TPMS tire pressure sensors - comprehensive scan"""
    # Scan both 315MHz and 433MHz (some TPMS use 433MHz)
    # Extended time for better detection
    # Use higher gain for better TPMS detection
    result = subprocess.run(
        ['timeout', '45', 'rtl_433', '-f', '315M', '-g', '40', '-H', '10', '-F', 'json', '-R', '59', '-R', '60', '-R', '88', '-R', '89'],
        capture_output=True, text=True
    )

    # Check if RTL-SDR is busy
    if 'usb_claim_interface error -6' in result.stderr:
        return jsonify({
            'error': 'RTL-SDR is in use',
            'message': 'RTL-SDR is being used by another program. Close it first or click "Switch Mode".',
            'sensors': [],
            'count': 0
        })

    sensors = []
    for line in result.stdout.split('\n'):
        if line.strip():
            try:
                sensors.append(json.loads(line))
            except:
                pass

    return jsonify({
        'sensors': sensors,
        'count': len(sensors),
        'scan_duration': '45 seconds',
        'frequency': '315MHz (TPMS)',
        'protocols': 'TPMS sensors: Toyota, Ford, Schrader, etc.',
        'note': 'Drive near the Pi or roll your car to activate TPMS sensors',
        'raw_output': result.stderr if len(sensors) == 0 else ''
    })

@app.route('/api/weather')
def weather():
    """Scan for weather stations - comprehensive scan"""
    # Scan multiple common weather station protocols
    # Many weather stations transmit every 30-60 seconds
    # Use higher gain for better weather station detection
    result = subprocess.run(
        ['timeout', '60', 'rtl_433', '-f', '433.92M', '-g', '40', '-H', '15', '-F', 'json',
         '-R', '40', '-R', '41', '-R', '44', '-R', '73', '-R', '74', '-R', '113'],
        capture_output=True, text=True
    )

    # Check if RTL-SDR is busy
    if 'usb_claim_interface error -6' in result.stderr:
        return jsonify({
            'error': 'RTL-SDR is in use',
            'message': 'RTL-SDR is being used by another program. Close it first or click "Switch Mode".',
            'stations': [],
            'count': 0
        })

    stations = []
    for line in result.stdout.split('\n'):
        if line.strip():
            try:
                data = json.loads(line)
                stations.append(data)
            except:
                pass

    return jsonify({
        'stations': stations,
        'count': len(stations),
        'scan_duration': '60 seconds',
        'frequency': '433.92MHz',
        'protocols': 'Acurite, Ambient Weather, LaCrosse, Oregon Scientific, etc.',
        'note': 'Weather stations typically transmit every 30-60 seconds',
        'raw_output': result.stderr if len(stations) == 0 else ''
    })

@app.route('/api/nfc/backup', methods=['POST'])
def backup_nfc():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'status': 'Error', 'message': 'Backup name not provided.'}), 400
    controller = initialize_pn532()
    if not controller:
        return jsonify({'status': 'Error', 'message': 'PN532 not initialized or not found.'}), 500
    try:
        uid = controller.read_passive_target(timeout=1.0)
        if uid is None:
            return jsonify({'status': 'Error', 'message': 'No card found to back up.'})
        uid_hex = ''.join([f'{i:02X}' for i in uid])
        readable_uid = ':'.join(uid_hex[i:i+2] for i in range(0, len(uid_hex), 2))
        backup_dir = os.path.expanduser("~/piflip/backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"{name}.json")
        backup_data = {
            "uid": uid_hex,
            "readable": readable_uid,
            "timestamp": datetime.now().isoformat(),
            "name": name
        }
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        return jsonify({'status': 'Success', 'message': f'Card UID {readable_uid} backed up to {name}.json'})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/cc1101/status')
def cc1101_status():
    """Get CC1101 status"""
    controller = initialize_cc1101()
    if not controller:
        return jsonify({'status': 'Error', 'message': 'CC1101 not initialized'}), 500
    try:
        version_info = controller.get_version_info()
        return jsonify({'status': 'OK', 'info': version_info})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/api/analyze/<capture_name>')
def analyze_signal(capture_name):
    """Analyze a captured signal with URH and generate visualization"""
    try:
        analyzer = URHAnalyzer()
        result = analyzer.analyze_capture(capture_name)

        # Load signal data for visualization
        capture_dir = Path(os.path.expanduser("~/piflip/captures"))
        signal_file = capture_dir / f"{capture_name}.json"

        if signal_file.exists():
            with open(signal_file, 'r') as f:
                signal_data = json.load(f)

            # Add ASCII waveform if we have timings
            if 'timings' in signal_data:
                result['waveform_ascii'] = analyzer.generate_ascii_waveform(signal_data, width=60, height=8)
                result['timings'] = signal_data['timings']

            # Add decoded binary if available
            if 'decoded_binary' in signal_data:
                result['decoded_binary'] = signal_data['decoded_binary']

            # Add frequency and sample rate
            if 'frequency' in signal_data:
                result['frequency'] = signal_data['frequency']
            if 'sample_rate' in signal_data:
                result['sample_rate'] = signal_data['sample_rate']

        result['status'] = 'success'
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/replay/<capture_name>', methods=['POST'])
def replay_signal(capture_name):
    """Replay a captured signal using CC1101"""
    try:
        # Load metadata
        capture_dir = Path(os.path.expanduser("~/piflip/captures"))
        metadata_file = capture_dir / f"{capture_name}.json"

        if not metadata_file.exists():
            return jsonify({'error': 'Capture not found'}), 404

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Transmit using CC1101
        freq = metadata['frequency']

        # Simple test transmission
        result = subprocess.run([
            'python3', '-c', f'''
import spidev, time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 50000
spi.mode = 0

# Configure for transmission
spi.xfer2([0x0D, 0x10])  # FREQ2
spi.xfer2([0x0E, 0xA7])  # FREQ1
spi.xfer2([0x0F, 0x62])  # FREQ0
spi.xfer2([0x12, 0x03])  # OOK mode

# Enter TX mode
spi.xfer2([0x35])  # STX
time.sleep(0.5)  # Transmit for 500ms

# Back to idle
spi.xfer2([0x36])  # SIDLE

spi.close()
print("Transmitted test burst on {freq/1e6:.2f} MHz")
'''
        ], capture_output=True, text=True)

        return jsonify({
            'status': 'transmitted',
            'message': f'Test transmission on {freq/1e6:.2f} MHz',
            'note': 'Basic burst transmission. Full signal replay requires URH decoding.',
            'capture': capture_name,
            'output': result.stdout
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- CC1101 Enhanced API Routes ---

@app.route('/api/cc1101/capture', methods=['POST'])
def cc1101_capture():
    """Capture signal with CC1101"""
    data = request.get_json()
    duration = data.get('duration', 5.0)
    frequency = data.get('frequency', 433.92)
    name = data.get('name')

    controller = initialize_cc1101_enhanced()
    if not controller:
        return jsonify({'error': 'CC1101 not initialized'}), 500

    try:
        # Capture signal
        capture_data = controller.capture_signal(duration=duration, freq_mhz=frequency)

        # Auto-save if name provided
        if name:
            save_result = controller.save_signal(capture_data, name)
            return jsonify({
                'status': 'captured_and_saved',
                'capture': capture_data,
                'save': save_result
            })

        return jsonify({
            'status': 'captured',
            'capture': capture_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cc1101/scan', methods=['POST'])
def cc1101_scan():
    """Scan frequency range for signals"""
    data = request.get_json()
    start_freq = data.get('start', 433.0)
    end_freq = data.get('end', 434.0)
    step = data.get('step', 0.1)
    threshold = data.get('threshold', -80)

    controller = initialize_cc1101_enhanced()
    if not controller:
        return jsonify({'error': 'CC1101 not initialized'}), 500

    try:
        results = controller.scan_frequencies(
            start_mhz=start_freq,
            end_mhz=end_freq,
            step_mhz=step,
            rssi_threshold=threshold
        )
        return jsonify({
            'status': 'scan_complete',
            'signals': results,
            'count': len(results),
            'range': f"{start_freq}-{end_freq} MHz"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cc1101/library')
def cc1101_library():
    """List saved RF signals"""
    controller = initialize_cc1101_enhanced()
    if not controller:
        return jsonify({'error': 'CC1101 not initialized'}), 500

    try:
        signals = controller.list_signals()
        return jsonify({
            'signals': signals,
            'count': len(signals)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cc1101/transmit/<name>', methods=['POST'])
def cc1101_transmit(name):
    """Transmit saved signal with enhanced power and repeats"""
    controller = initialize_cc1101_enhanced()
    if not controller:
        return jsonify({'error': 'CC1101 not initialized'}), 500

    try:
        # Get request parameters
        data = request.get_json() or {}
        repeats = data.get('repeats', 3)  # Default 3 repeats
        power = data.get('power', 'max')  # Default max power

        # Load signal
        signal_data = controller.load_signal(name)
        if not signal_data:
            return jsonify({'error': 'Signal not found'}), 404

        # Transmit with enhancements
        result = controller.transmit_signal_enhanced(signal_data, repeats=repeats, power=power)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cc1101/library/<name>', methods=['DELETE'])
def cc1101_delete(name):
    """Delete saved signal"""
    controller = initialize_cc1101_enhanced()
    if not controller:
        return jsonify({'error': 'CC1101 not initialized'}), 500

    try:
        result = controller.delete_signal(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cc1101/status')
def cc1101_enhanced_status():
    """Get CC1101 enhanced status"""
    controller = initialize_cc1101_enhanced()
    if not controller:
        return jsonify({'error': 'CC1101 not initialized'}), 500

    try:
        status = controller.get_status()
        rssi = controller.get_rssi()
        return jsonify({
            'status': 'OK',
            'chip': status,
            'current_rssi': rssi
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cc1101/decode/<name>')
def cc1101_decode_signal(name):
    """Decode signal to binary and extract protocol"""
    try:
        decoder = SignalDecoder()
        result = decoder.decode_signal(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nfc/emulate/<name>', methods=['POST'])
def nfc_emulate_card(name):
    """Attempt to emulate card (shows magic card recommendation)"""
    try:
        emulator = NFCEmulator()
        card_data = emulator.load_card(name)

        if not card_data:
            return jsonify({'error': 'Card not found'}), 404

        # Check if can emulate
        emulation_info = emulator.can_emulate(card_data)

        # Get virtual badge instructions
        instructions = emulator.virtual_badge_mode(name)

        return jsonify({
            'emulation_info': emulation_info,
            'instructions': instructions,
            'recommendation': 'Use Clone Card feature for best results'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nfc/clone_instructions')
def nfc_clone_instructions():
    """Get clone instructions for work badges"""
    try:
        instructions = MagicCardHelper.get_clone_instructions()
        return jsonify(instructions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Favorites & Stats API ---

@app.route('/api/favorites')
def get_favorites():
    """Get all favorites"""
    try:
        fm = FavoritesManager()
        favorites = fm.get_favorites()
        return jsonify(favorites)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites/<item_type>/<name>', methods=['POST'])
def add_favorite(item_type, name):
    """Add item to favorites"""
    try:
        fm = FavoritesManager()
        data = request.get_json() or {}
        metadata = data.get('metadata', {})
        result = fm.add_favorite(item_type, name, metadata)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites/<item_type>/<name>', methods=['DELETE'])
def remove_favorite(item_type, name):
    """Remove item from favorites"""
    try:
        fm = FavoritesManager()
        result = fm.remove_favorite(item_type, name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard endpoints moved to end of file (before if __name__)

@app.route('/api/waveform/<signal_name>')
def get_waveform(signal_name):
    """Get waveform visualization for signal"""
    try:
        # Load signal from CC1101 library
        controller = initialize_cc1101_enhanced()
        if not controller:
            return jsonify({'error': 'CC1101 not initialized'}), 500

        signal_data = controller.load_signal(signal_name)
        if not signal_data:
            return jsonify({'error': 'Signal not found'}), 404

        timings = signal_data.get('timings', [])

        # Generate waveforms
        gen = WaveformGenerator()
        simple = gen.generate_ascii_waveform(timings, width=60)
        detailed = gen.generate_detailed_waveform(timings, width=60, height=3)

        return jsonify({
            'simple_waveform': simple,
            'detailed_waveform': detailed,
            'timing_count': len(timings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/waterfall/spectrum')
def waterfall_spectrum():
    """Get real-time spectrum data for waterfall display"""
    start_freq = request.args.get('start', '433000000')  # 433 MHz default
    end_freq = request.args.get('end', '434000000')      # 434 MHz default
    bins = request.args.get('bins', '256')                # FFT bins

    try:
        # Use rtl_power for quick spectrum scan
        # -f start:end:step -i interval -1 (single scan)
        result = subprocess.run(
            ['rtl_power', '-f', f'{start_freq}:{end_freq}:1M', '-i', '0.1', '-1', '-'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode != 0 or 'usb_claim_interface' in result.stderr:
            return jsonify({
                'error': 'RTL-SDR busy or not available',
                'spectrum': []
            })

        # Parse rtl_power output
        # Format: date, time, Hz low, Hz high, Hz step, samples, dB, dB, dB...
        lines = [l for l in result.stdout.strip().split('\n') if l]

        if not lines:
            return jsonify({'error': 'No data', 'spectrum': []})

        # Parse last line (most recent scan)
        parts = lines[-1].split(',')
        if len(parts) < 7:
            return jsonify({'error': 'Invalid data', 'spectrum': []})

        # Extract dB values (skip first 6 metadata fields)
        db_values = [float(x) for x in parts[6:]]

        # Calculate frequencies for each bin
        freq_low = float(parts[2])
        freq_high = float(parts[3])
        freq_step = (freq_high - freq_low) / len(db_values)

        spectrum = []
        for i, db in enumerate(db_values):
            freq = freq_low + (i * freq_step)
            spectrum.append({
                'frequency': freq / 1e6,  # Convert to MHz
                'power': db
            })

        return jsonify({
            'spectrum': spectrum,
            'freq_range': [freq_low / 1e6, freq_high / 1e6],
            'timestamp': time.time()
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout', 'spectrum': []})
    except Exception as e:
        return jsonify({'error': str(e), 'spectrum': []})

@app.route('/api/waterfall/stream')
def waterfall_stream():
    """Server-sent events stream for continuous waterfall updates"""
    def generate():
        import time
        start_freq = request.args.get('start', '433000000')
        end_freq = request.args.get('end', '434000000')

        while True:
            try:
                # Quick spectrum scan
                result = subprocess.run(
                    ['rtl_power', '-f', f'{start_freq}:{end_freq}:1M', '-i', '0.05', '-1', '-'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )

                if result.returncode == 0:
                    lines = [l for l in result.stdout.strip().split('\n') if l]
                    if lines:
                        parts = lines[-1].split(',')
                        if len(parts) >= 7:
                            db_values = [float(x) for x in parts[6:]]
                            freq_low = float(parts[2])
                            freq_high = float(parts[3])
                            freq_step = (freq_high - freq_low) / len(db_values)

                            spectrum = []
                            for i, db in enumerate(db_values):
                                freq = freq_low + (i * freq_step)
                                spectrum.append([freq / 1e6, db])

                            data = json.dumps({'spectrum': spectrum, 'timestamp': time.time()})
                            yield f"data: {data}\n\n"

                time.sleep(0.2)  # 5 updates per second

            except:
                time.sleep(0.5)
                continue

    return Response(generate(), mimetype='text/event-stream')

# --- Dashboard API Routes ---

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        captures_dir = Path.home() / 'piflip' / 'captures'
        nfc_dir = Path.home() / 'piflip' / 'nfc_library'

        # Count RF captures
        rf_captures = list(captures_dir.glob('*.json')) if captures_dir.exists() else []

        # Count NFC cards
        nfc_cards = list(nfc_dir.glob('*.json')) if nfc_dir.exists() else []

        # Calculate storage used
        total_size = 0
        if captures_dir.exists():
            for file in captures_dir.iterdir():
                if file.is_file():
                    total_size += file.stat().st_size

        # Load activity log if exists
        activity_file = Path.home() / 'piflip' / 'activity.json'
        total_replays = 0
        total_scans = 0

        if activity_file.exists():
            try:
                with open(activity_file, 'r') as f:
                    activities = json.load(f)
                    total_replays = sum(1 for a in activities if a.get('action') == 'replay')
                    total_scans = sum(1 for a in activities if a.get('action') == 'scan')
            except:
                pass

        # Frequency breakdown
        freq_count = {}
        for capture in rf_captures:
            try:
                with open(capture, 'r') as f:
                    data = json.load(f)
                    freq = data.get('frequency', 'unknown')
                    if freq != 'unknown':
                        freq_mhz = f"{float(freq)/1e6:.2f}" if freq > 1000 else f"{freq:.2f}"
                        freq_count[freq_mhz] = freq_count.get(freq_mhz, 0) + 1
            except:
                continue

        return jsonify({
            'total_rf_captures': len(rf_captures),
            'total_nfc_reads': len(nfc_cards),
            'total_replays': total_replays,
            'total_scans': total_scans,
            'storage_used_mb': round(total_size / (1024 * 1024), 2),
            'success_rate': 95,  # Placeholder - could track actual success/failure
            'top_frequencies': dict(sorted(freq_count.items(), key=lambda x: x[1], reverse=True)[:5])
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent')
def get_recent():
    """Get recent activity"""
    try:
        captures_dir = Path.home() / 'piflip' / 'captures'
        nfc_dir = Path.home() / 'piflip' / 'nfc_library'

        recent = []

        # Get recent RF captures
        if captures_dir.exists():
            for json_file in sorted(captures_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        recent.append({
                            'type': 'rf_capture',
                            'name': json_file.stem,
                            'frequency': data.get('frequency', 'unknown'),
                            'duration': data.get('duration', 'unknown'),
                            'timestamp': data.get('timestamp', json_file.stat().st_mtime),
                            'size_kb': round(json_file.stat().st_size / 1024, 2)
                        })
                except:
                    continue

        # Get recent NFC reads
        if nfc_dir.exists():
            for json_file in sorted(nfc_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        recent.append({
                            'type': 'nfc_read',
                            'name': json_file.stem,
                            'uid': data.get('uid', 'unknown'),
                            'card_type': data.get('card_type', 'unknown'),
                            'timestamp': data.get('timestamp', json_file.stat().st_mtime)
                        })
                except:
                    continue

        # Sort all by timestamp
        recent.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

        return jsonify(recent[:15])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity', methods=['POST'])
def log_activity():
    """Log user activity for dashboard"""
    try:
        activity_file = Path.home() / 'piflip' / 'activity.json'

        # Load existing activities
        activities = []
        if activity_file.exists():
            try:
                with open(activity_file, 'r') as f:
                    activities = json.load(f)
            except:
                activities = []

        # Add new activity
        new_activity = request.get_json()
        new_activity['timestamp'] = datetime.now().isoformat()
        activities.append(new_activity)

        # Keep only last 100 activities
        activities = activities[-100:]

        # Save
        with open(activity_file, 'w') as f:
            json.dump(activities, f, indent=2)

        return jsonify({'status': 'logged'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rssi')
def get_rssi():
    """Get current RSSI (signal strength) from CC1101"""
    try:
        controller = initialize_cc1101_enhanced()
        if not controller:
            return jsonify({'error': 'CC1101 not initialized'}), 500

        # Put CC1101 in RX mode to read RSSI
        controller.strobe_command(controller.SRX)
        time.sleep(0.01)  # Brief delay for RSSI to settle

        # Read RSSI
        rssi_data = controller.read_rssi()

        return jsonify(rssi_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Bluetooth API Routes ---

@app.route('/api/bluetooth/scan', methods=['POST'])
def bluetooth_scan():
    """Scan for Bluetooth devices"""
    try:
        scanner = BluetoothScanner()
        data = request.get_json() or {}
        scan_type = data.get('type', 'comprehensive')  # ble, classic, comprehensive
        duration = data.get('duration', 15)

        if scan_type == 'ble':
            result = scanner.scan_ble_devices(duration)
        elif scan_type == 'classic':
            result = scanner.scan_classic_devices(duration)
        else:
            result = scanner.scan_comprehensive(duration)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/device/<address>/info')
def bluetooth_device_info(address):
    """Get detailed device information"""
    try:
        scanner = BluetoothScanner()
        result = scanner.get_device_info(address)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/device/<address>/services')
def bluetooth_device_services(address):
    """Enumerate device services"""
    try:
        scanner = BluetoothScanner()
        device_type = request.args.get('type', 'BLE')
        result = scanner.get_device_services(address, device_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/device/<address>/rssi', methods=['POST'])
def bluetooth_monitor_rssi(address):
    """Monitor device RSSI"""
    try:
        scanner = BluetoothScanner()
        data = request.get_json() or {}
        duration = data.get('duration', 10)
        result = scanner.monitor_device_rssi(address, duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/library')
def bluetooth_library():
    """List saved Bluetooth devices"""
    try:
        scanner = BluetoothScanner()
        devices = scanner.list_saved_devices()
        return jsonify({'devices': devices, 'count': len(devices)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/save', methods=['POST'])
def bluetooth_save():
    """Save Bluetooth device"""
    try:
        scanner = BluetoothScanner()
        data = request.get_json()
        device_data = data.get('device')
        name = data.get('name')
        result = scanner.save_device(device_data, name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/library/<name>', methods=['DELETE'])
def bluetooth_delete(name):
    """Delete saved Bluetooth device"""
    try:
        scanner = BluetoothScanner()
        result = scanner.delete_device(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bluetooth/reset', methods=['POST'])
def bluetooth_reset():
    """Reset Bluetooth adapter"""
    try:
        scanner = BluetoothScanner()
        result = scanner.reset_bluetooth()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- WiFi API Routes ---

@app.route('/api/wifi/status')
def wifi_status():
    """Get WiFi status"""
    try:
        manager = WiFiManager()
        status = manager.get_wifi_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/hotspot/enable', methods=['POST'])
def wifi_enable_hotspot():
    """Enable WiFi hotspot mode"""
    try:
        manager = WiFiManager()
        result = manager.enable_hotspot()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/hotspot/disable', methods=['POST'])
def wifi_disable_hotspot():
    """Disable WiFi hotspot"""
    try:
        manager = WiFiManager()
        result = manager.disable_hotspot()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/toggle', methods=['POST'])
def wifi_toggle():
    """Toggle WiFi mode"""
    try:
        manager = WiFiManager()
        result = manager.toggle_mode()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/scan')
def wifi_scan():
    """Scan for WiFi networks"""
    try:
        manager = WiFiManager()
        result = manager.scan_networks()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi/connect', methods=['POST'])
def wifi_connect():
    """Connect to WiFi network"""
    try:
        manager = WiFiManager()
        data = request.get_json()
        ssid = data.get('ssid')
        password = data.get('password')
        result = manager.connect_to_network(ssid, password)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Spectrum Analyzer API Routes ---

@app.route('/api/spectrum/scan', methods=['POST'])
def spectrum_scan():
    """Quick spectrum scan"""
    try:
        analyzer = SpectrumAnalyzer()
        data = request.get_json() or {}
        center_freq = data.get('center_freq', 433.92)
        span = data.get('span', 2.0)
        bins = data.get('bins', 256)
        result = analyzer.quick_scan(center_freq, span, bins)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spectrum/waterfall', methods=['POST'])
def spectrum_waterfall():
    """Waterfall scan"""
    try:
        analyzer = SpectrumAnalyzer()
        data = request.get_json() or {}
        center_freq = data.get('center_freq', 433.92)
        span = data.get('span', 2.0)
        duration = data.get('duration', 10)
        interval = data.get('interval', 0.2)
        result = analyzer.waterfall_scan(center_freq, span, duration, interval)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spectrum/detect', methods=['POST'])
def spectrum_detect():
    """Detect signals in spectrum"""
    try:
        analyzer = SpectrumAnalyzer()
        data = request.get_json()
        spectrum_data = data.get('spectrum_data')
        threshold = data.get('threshold', -80)
        min_width = data.get('min_width', 0.05)
        result = analyzer.detect_signals(spectrum_data, threshold, min_width)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spectrum/save', methods=['POST'])
def spectrum_save():
    """Save spectrum scan"""
    try:
        analyzer = SpectrumAnalyzer()
        data = request.get_json()
        scan_data = data.get('scan_data')
        name = data.get('name')
        result = analyzer.save_scan(scan_data, name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spectrum/reset', methods=['POST'])
def spectrum_reset():
    """Reset RTL-SDR device"""
    try:
        analyzer = SpectrumAnalyzer()
        result = analyzer.reset_rtlsdr()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hardware/status')
def hardware_status():
    """Check hardware status (CC1101, PN532, RTL-SDR)"""
    status = {
        'cc1101': False,
        'pn532': False,
        'rtl_sdr': False
    }

    try:
        # Check CC1101
        from cc1101_enhanced import CC1101Enhanced
        cc = CC1101Enhanced()
        status['cc1101'] = True
    except:
        pass

    try:
        # Check PN532
        from nfc_emulator import NFCEmulator
        nfc = NFCEmulator()
        status['pn532'] = True
    except:
        pass

    try:
        # Check RTL-SDR with quick timeout
        result = subprocess.run(
            ['rtl_test', '-t'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if 'Found 1 device' in result.stdout or 'Found 1 device' in result.stderr:
            status['rtl_sdr'] = True
    except:
        pass

    return jsonify(status)

# --- Enhanced NFC Emulation Route ---

@app.route('/api/nfc/emulate_real/<name>', methods=['POST'])
def nfc_emulate_real(name):
    """Actually emulate NFC card (experimental)"""
    try:
        emulator = NFCEmulator()
        card_data = emulator.load_card(name)

        if not card_data:
            return jsonify({'error': 'Card not found'}), 404

        data = request.get_json() or {}
        duration = data.get('duration', 30)

        result = emulator.emulate_card(card_data, duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# ADVANCED TX FEATURES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/tx/replay_variations/<signal_name>', methods=['POST'])
def tx_replay_variations(signal_name):
    """Replay signal with frequency and timing variations"""
    try:
        adv_tx = RFAdvancedTX()
        data = request.get_json() or {}

        freq_offsets = data.get('frequency_offsets', [-0.5, -0.25, 0, 0.25, 0.5])
        timing_variations = data.get('timing_variations', [0.95, 1.0, 1.05])

        result = adv_tx.replay_with_variations(
            signal_name,
            frequency_offsets=freq_offsets,
            timing_variations=timing_variations
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tx/brute_force', methods=['POST'])
def tx_brute_force():
    """Brute force simple fixed codes (educational only!)"""
    try:
        adv_tx = RFAdvancedTX()
        data = request.get_json()

        frequency = data.get('frequency', 433.92)
        bit_length = data.get('bit_length', 8)

        if bit_length > 16:
            return jsonify({'error': 'Bit length limited to 16 for safety'}), 400

        result = adv_tx.brute_force_codes(frequency, bit_length)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tx/fuzz/<signal_name>', methods=['POST'])
def tx_fuzz_signal(signal_name):
    """Fuzz signal by varying timings"""
    try:
        adv_tx = RFAdvancedTX()
        data = request.get_json() or {}

        fuzz_percentage = data.get('fuzz_percentage', 10)
        iterations = data.get('iterations', 50)

        result = adv_tx.signal_fuzzing(signal_name, fuzz_percentage, iterations)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tx/jam', methods=['POST'])
def tx_jam_frequency():
    """Continuous transmission for jamming/testing (educational only!)"""
    try:
        adv_tx = RFAdvancedTX()
        data = request.get_json()

        frequency = data.get('frequency', 433.92)
        duration = data.get('duration', 10)
        pattern = data.get('pattern', 'noise')

        result = adv_tx.continuous_jam(frequency, duration, pattern)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tx/rolling_code', methods=['POST'])
def tx_rolling_code():
    """Capture and immediately replay for rolling codes"""
    try:
        adv_tx = RFAdvancedTX()
        data = request.get_json()

        frequency = data.get('frequency', 433.92)
        capture_duration = data.get('capture_duration', 30)

        result = adv_tx.rolling_code_capture_replay(frequency, capture_duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tx/custom_signal', methods=['POST'])
def tx_custom_signal():
    """Generate and transmit custom signal from binary pattern"""
    try:
        adv_tx = RFAdvancedTX()
        data = request.get_json()

        frequency = data.get('frequency', 433.92)
        pattern = data.get('pattern', '101010')
        bit_duration = data.get('bit_duration_us', 500)

        result = adv_tx.generate_custom_signal(frequency, pattern, bit_duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# NFC GUARDIAN API ROUTES
# ═══════════════════════════════════════════════════════════════

# Global guardian instance
guardian = None
card_catalog = None
wallet_tester = None

def get_guardian():
    """Get or create guardian instance"""
    global guardian
    if guardian is None:
        guardian = NFCGuardian()
    return guardian

def get_card_catalog():
    """Get or create card catalog instance"""
    global card_catalog
    if card_catalog is None:
        card_catalog = CardCatalog()
    return card_catalog

def get_wallet_tester():
    """Get or create wallet tester instance"""
    global wallet_tester
    if wallet_tester is None:
        wallet_tester = RFIDWalletTester()
    return wallet_tester

@app.route('/api/guardian/status')
def guardian_status():
    """Get Guardian monitoring status"""
    try:
        g = get_guardian()
        return jsonify(g.get_status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guardian/start', methods=['POST'])
def guardian_start():
    """Start Guardian monitoring"""
    try:
        g = get_guardian()
        result = g.start_monitoring()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guardian/stop', methods=['POST'])
def guardian_stop():
    """Stop Guardian monitoring"""
    try:
        g = get_guardian()
        result = g.stop_monitoring()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guardian/suspicious')
def guardian_suspicious():
    """Get suspicious events"""
    try:
        g = get_guardian()
        limit = request.args.get('limit', 20, type=int)
        events = g.get_suspicious_events(limit=limit)
        return jsonify({'events': events})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guardian/clear_history', methods=['POST'])
def guardian_clear_history():
    """Clear scan history"""
    try:
        g = get_guardian()
        result = g.clear_history()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# CARD CATALOG API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/catalog/cards')
def catalog_list_cards():
    """Get all cards in catalog"""
    try:
        catalog = get_card_catalog()
        cards = catalog.get_all_cards()
        return jsonify({'cards': cards})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/card/<uid>')
def catalog_get_card(uid):
    """Get specific card by UID"""
    try:
        catalog = get_card_catalog()
        card = catalog.get_card(uid)
        if card:
            return jsonify({'card': card})
        else:
            return jsonify({'error': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/add', methods=['POST'])
def catalog_add_card():
    """Add card to catalog by scanning"""
    try:
        catalog = get_card_catalog()
        data = request.get_json()
        
        name = data.get('name', 'Unnamed Card')
        card_type = data.get('type', 'unknown')
        protected = data.get('protected', False)
        notes = data.get('notes', '')
        
        result = catalog.add_card(name, card_type, protected, notes)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/register', methods=['POST'])
def catalog_register_card():
    """Register card by UID without scanning"""
    try:
        catalog = get_card_catalog()
        data = request.get_json()
        
        uid = data.get('uid')
        if not uid:
            return jsonify({'error': 'UID required'}), 400
            
        name = data.get('name', 'Unnamed Card')
        card_type = data.get('type', 'unknown')
        protected = data.get('protected', False)
        notes = data.get('notes', '')
        
        result = catalog.register_card_by_uid(uid, name, card_type, protected, notes)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/update/<uid>', methods=['POST'])
def catalog_update_card(uid):
    """Update card information"""
    try:
        catalog = get_card_catalog()
        data = request.get_json()
        result = catalog.update_card(uid, **data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/delete/<uid>', methods=['DELETE'])
def catalog_delete_card(uid):
    """Delete card from catalog"""
    try:
        catalog = get_card_catalog()
        result = catalog.delete_card(uid)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/identify', methods=['POST'])
def catalog_identify():
    """Scan and identify card"""
    try:
        catalog = get_card_catalog()
        result = catalog.identify_scanned_card()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/stats')
def catalog_stats():
    """Get catalog statistics"""
    try:
        catalog = get_card_catalog()
        stats = catalog.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# WALLET TESTER API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/wallet/quick_test', methods=['POST'])
def wallet_quick_test():
    """Quick wallet blocking test"""
    try:
        tester = get_wallet_tester()
        data = request.get_json() or {}
        duration = data.get('duration', 3)
        result = tester.quick_test(test_duration=duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet/full_test', methods=['POST'])
def wallet_full_test():
    """Full wallet effectiveness test"""
    try:
        tester = get_wallet_tester()
        data = request.get_json() or {}
        duration = data.get('duration', 10)
        result = tester.test_blocking_effectiveness(duration=duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# SYSTEM POWER MANAGEMENT
# =============================================================================

@app.route('/api/system/shutdown', methods=['POST'])
def system_shutdown():
    """Safely shutdown the Raspberry Pi"""
    try:
        import subprocess
        # Shutdown now (use 'now' instead of time offset)
        subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
        return jsonify({
            'status': 'success',
            'message': 'System shutting down now...'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/reboot', methods=['POST'])
def system_reboot():
    """Safely reboot the Raspberry Pi"""
    try:
        import subprocess
        # Schedule reboot in 5 seconds to allow response to be sent
        subprocess.Popen(['sudo', 'reboot'])
        return jsonify({
            'status': 'success',
            'message': 'System rebooting in 5 seconds...'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("[*] Starting PiFlip Web Interface...")
    print("[*] Initializing hardware...")
    initialize_pn532()
    # Note: CC1101 initialization postponed until needed (requires SPI wiring)
    print("[*] Web interface available at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

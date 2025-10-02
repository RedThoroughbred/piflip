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
            'message': 'RTL-SDR is currently being used by another program (likely dump1090-fa or GQRX). Please close the other program first, or click "Switch Mode" at the top of the page.',
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

@app.route('/api/flights')
def flights():
    """Get flight data from dump1090"""
    try:
        response = requests.get('http://localhost:8080/data/aircraft.json', timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e), 'aircraft': []}), 500

@app.route('/api/flights/stats')
def flight_stats():
    """Get flight tracking statistics"""
    try:
        response = requests.get('http://localhost:8080/data/aircraft.json', timeout=2)
        data = response.json()
        aircraft = data.get('aircraft', [])

        stats = {
            'total_aircraft': len(aircraft),
            'with_position': len([a for a in aircraft if 'lat' in a and 'lon' in a]),
            'with_altitude': len([a for a in aircraft if 'altitude' in a]),
            'messages': data.get('messages', 0),
            'timestamp': data.get('now', 0)
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        # Read card
        card_data = controller.read_card_detailed(timeout=1.0)
        if card_data is None:
            return jsonify({'status': 'Error', 'message': 'No card found'}), 404

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
    """Analyze a captured signal with URH"""
    try:
        analyzer = URHAnalyzer()
        result = analyzer.analyze_capture(capture_name)
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

@app.route('/api/rtlsdr/mode')
def rtlsdr_mode():
    """Check current RTL-SDR mode (flights vs scanning)"""
    result = subprocess.run(['systemctl', 'is-active', 'dump1090-fa'],
                          capture_output=True, text=True)
    is_active = result.stdout.strip() == 'active'

    return jsonify({
        'mode': 'flights' if is_active else 'scanning',
        'dump1090_active': is_active,
        'message': 'Flight tracking enabled' if is_active else 'RTL-SDR available for 433MHz/TPMS/Weather scanning'
    })

@app.route('/api/rtlsdr/toggle', methods=['POST'])
def rtlsdr_toggle():
    """Toggle RTL-SDR between flight mode and scanning mode"""
    # Check current state
    result = subprocess.run(['systemctl', 'is-active', 'dump1090-fa'],
                          capture_output=True, text=True)
    is_active = result.stdout.strip() == 'active'

    if is_active:
        # Stop dump1090 to free RTL-SDR for scanning
        subprocess.run(['sudo', 'systemctl', 'stop', 'dump1090-fa'])
        return jsonify({
            'mode': 'scanning',
            'message': 'Switched to SCANNING mode. You can now use 433MHz, TPMS, and Weather scanning.',
            'dump1090_active': False
        })
    else:
        # Start dump1090 for flight tracking
        subprocess.run(['sudo', 'systemctl', 'start', 'dump1090-fa'])
        time.sleep(2)  # Give it time to start
        return jsonify({
            'mode': 'flights',
            'message': 'Switched to FLIGHT TRACKING mode. 433MHz/TPMS/Weather scanning disabled.',
            'dump1090_active': True
        })

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

@app.route('/api/stats')
def get_stats():
    """Get usage statistics"""
    try:
        fm = FavoritesManager()
        stats = fm.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent')
def get_recent():
    """Get recent activity"""
    try:
        fm = FavoritesManager()
        recent = fm.get_recent(limit=10)
        return jsonify({'activities': recent})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity', methods=['POST'])
def add_activity():
    """Add activity to recent list"""
    try:
        fm = FavoritesManager()
        data = request.get_json()
        activity = fm.add_activity(
            data['action'],
            data['type'],
            data['name'],
            data.get('result', 'success')
        )
        return jsonify(activity)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    print("[*] Starting PiFlip Web Interface...")
    print("[*] Initializing hardware...")
    initialize_pn532()
    # Note: CC1101 initialization postponed until needed (requires SPI wiring)
    print("[*] Web interface available at http://0.0.0.0:5000")
    print("[*] Flight map available at http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=5000, debug=True)

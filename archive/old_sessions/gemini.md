# PiFlip Project Setup Summary

This document summarizes the complete setup process for the PiFlip project on your Raspberry Pi.

## 1. Project Files & Structure

All project files are located in `/home/seth/piflip/`.

```
/home/seth/piflip/
├── piflip_env/              # Python virtual environment for this project
├── captures/                # Directory for saving captured signals
├── scripts/                 # (empty) For future helper scripts
├── web/                     # (empty) For future web assets
├── config/                  # (empty) For future configuration files
├── CC1101/                  # Cloned library for the CC1101 module
├── piflip_core.py           # Main command-line interface script
├── web_interface.py         # Flask web server script
├── cc1101_controller.py     # Python script to control the CC1101 module
└── status.sh                # Script to check the system status
```

## 2. System Configuration

### Hardware Interfaces
The following interfaces were enabled via `raspi-config`:
- **SPI** (for the CC1101 module)
- **I2C** (for the OLED display and/or NFC module)
- **Serial**

### System Service (piflip.service)
- **File:** `/etc/systemd/system/piflip.service`
- **Purpose:** To automatically start the web interface (`web_interface.py`) when the Raspberry Pi boots up.
- **Status:** Enabled.

### RTL-SDR Driver Configuration
- **Udev Rule:** `/etc/udev/rules.d/20-rtlsdr.rules` was created to allow non-root access to the RTL-SDR USB device.
- **Blacklist:** `/etc/modprobe.d/blacklist-rtl.conf` was created to prevent the default TV drivers from interfering with the SDR tools.

## 3. Software & Libraries

### System Packages (Installed via `apt`)
- `git`
- `python3-pip`, `python3-dev`, `python3-venv`
- `build-essential`, `cmake`
- `libusb-1.0-0-dev`, `i2c-tools`, `python3-smbus`
- `libnfc-dev`, `libnfc-bin`
- `spi-tools`, `python3-spidev`, `python3-rpi.gpio`
- `rtl-sdr`, `librtlsdr-dev`
- `libjpeg-dev`, `zlib1g-dev` (to fix build issues with Pillow)

### Compiled from Source
- **rtl_433:** The latest version was compiled and installed from its GitHub repository. The executable is at `/usr/local/bin/rtl_433`.

### Python Environment (`piflip_env`)
The following packages were installed via `pip` into the virtual environment at `/home/seth/piflip/piflip_env/`:
- `pyrtlsdr`
- `numpy`
- `matplotlib`
- `flask`
- `adafruit-circuitpython-ssd1306`
- `pillow`
- `spidev`
- `RPi.GPIO`
- `nfcpy`
- `pynfc`

## 4. How to Use

### Web Interface
- **URL:** [http://192.168.86.141:5000](http://192.168.86.141:5000)
- **To Start/Stop Manually:**
  - `sudo systemctl start piflip`
  - `sudo systemctl stop piflip`
  - `sudo systemctl restart piflip`

### Command-Line Interface
To use the CLI, open a terminal and run:
```bash
# Activate the virtual environment first
source /home/seth/piflip/piflip_env/bin/activate

# Run the core script
python3 /home/seth/piflip/piflip_core.py
```

### Status Check
To see a quick summary of the system status, run:
```bash
/home/seth/piflip/status.sh
```

# PiFlip Dependency Audit

**Generated:** October 2, 2025
**Purpose:** Identify what's actually being used by web_interface.py

---

## ✅ ACTIVELY USED FILES (Keep These)

### Core Application Files
- **web_interface.py** (36KB) - Main Flask web application
- **app.py** (13KB) - Older web interface? (check if still needed)

### Python Modules IMPORTED by web_interface.py
These are all **REQUIRED** and actively used:

1. **urh_analyzer.py** (6KB) - URH signal analysis integration
2. **auto_analyzer.py** (7KB) - Auto-analysis for captures
3. **nfc_enhanced.py** (9KB) - Enhanced NFC features
4. **nfc_cloner.py** (10KB) - NFC card cloning
5. **cc1101_enhanced.py** (17KB) - Enhanced CC1101 RX/TX
6. **signal_decoder.py** (12KB) - Signal decoding to binary
7. **nfc_emulator.py** (8KB) - NFC emulation & magic card helper
8. **favorites_manager.py** (7KB) - Favorites & stats tracking
9. **waveform_generator.py** (7KB) - Waveform visualization

**Total: 9 Python modules = ~83KB**

### External Commands Used by web_interface.py
These system commands are called via subprocess:

- `rtl_433` - 433MHz scanning (scan433, tpms, weather endpoints)
- `rtl_sdr` - Raw IQ capture
- `rtl_power` - Spectrum waterfall
- `rtl_test` - Hardware status check
- `systemctl` - dump1090 mode switching
- `requests` → `http://localhost:8080/data/aircraft.json` (dump1090 API)

### Shell Scripts (potentially used)
- **start_piflip.sh** (1KB) - Start script for web interface
- **status.sh** (566B) - Hardware status check

### Essential Directories
- **templates/** (164KB) - Flask HTML templates (flipper_ui.html, etc.)
- **captures/** (40MB) - User RF signal captures
- **nfc_library/** (12KB) - Saved NFC cards
- **rf_library/** (15MB) - Saved RF signals
- **backups/** (16KB) - NFC card backups
- **piflip_env/** (113MB) - Python virtual environment **[KEEP]**
- **config/** (4KB) - Configuration files
- **__pycache__/** (88KB) - Python cache **[CAN DELETE]**

---

## ❌ UNUSED FILES (Can Delete)

### Old/Obsolete Python Files (NOT imported by web_interface.py)

**Test Files (15 files):**
1. `simple_nfc_test.py` (1KB)
2. `pi_nfc_test.py` (1KB)
3. `arduino_style_test.py` (1KB)
4. `minimal_test.py` (448B)
5. `debug_pn532.py` (1KB)
6. `proper_pn532_test.py` (2KB)
7. `chunked_pn532_test.py` (2KB)
8. `test_nfc.py` (864B)
9. `gentle_nfc_test.py` (1KB)
10. `test_cc1101_transmit.py` (5KB)
11. `test_cc1101_simple_tx.py` (3KB)
12. `test_cc1101_strong_signal.py` (5KB)
13. `test_transmission_visibility.py` (8KB)
14. `test_magic_card.py` (9KB)
15. `verify_keyfob_transmission.py` (6KB)

**Old Application Files:**
- `piflip_core.py` (4KB) - Old core (replaced by web_interface.py)
- `piflip_modern.py` (16KB) - Old version
- `pi-flipper.py` (31KB) - Old version
- `raspi-flipper.py` (31KB) - Old version
- `raspi-blinka.py` (7KB) - Old test
- `cc1101_controller.py` (864B) - Replaced by cc1101_enhanced.py

**Old Replay Scripts:**
- `replay_keyfob_pattern.py` (5KB)
- `replay_keyfob_with_timing.py` (12KB)
- `replay_exact_capture.py` (7KB)

**Total obsolete Python files: ~200KB**

### Unused Shell Scripts
- `capture_keyfob.sh` (886B) - Manual test script
- `test_flight_reception.sh` (3KB) - Manual test script
- `test_keyfob_mac_settings.sh` (5KB) - Manual test script
- `test_keyfob_now.sh` (2KB) - Manual test script

**Total: ~11KB**

### Other Files
- `piaware-repository_3.8.1_all.deb` - Installer package (not needed)
- `fm_scan.csv` - Old scan data
- `web_interface.log` - Log file (can delete if old)
- `sdrpp_error.log` - Error log
- `stats.json`, `favorites.json`, `recent_activity.json` - Generated at runtime

---

## 🤔 NEEDS INVESTIGATION

### dump1090 Directory (107MB)
**Current Status:**
- dump1090-fa is **installed** (`/usr/bin/dump1090-fa`)
- Currently **inactive** (in scanning mode)
- Web interface uses it via systemctl and localhost:8080

**The `/home/seth/piflip/dump1090/` directory contains:**
- Source code for dump1090
- 107MB of C code, build files, etc.

**Question:** Is this a git clone or build directory?

**Answer:** Since dump1090-fa is already installed at `/usr/bin/dump1090-fa`, the source directory is **NOT NEEDED** for running the application.

**Recommendation:** ✅ **SAFE TO DELETE** (saves 107MB)

### app.py (13KB)
- There's both `web_interface.py` and `app.py`
- Need to check if `app.py` is still used or just an old version

---

## 📚 DOCUMENTATION FILES (24 MD files)

### Current Documentation
Many of these may be outdated or redundant. Here's the list:

1. README.md - **KEEP** (main docs)
2. SETUP.md
3. ROADMAP.md - **KEEP**
4. QUICK_START.md
5. QUICK_REFERENCE.md
6. HARDWARE_TEST_RESULTS.md
7. HARDWARE_TEST_RESULTS_FINAL.md ← Duplicate?
8. HARDWARE_STRATEGY.md
9. HARDWARE_CAPABILITIES.md ← Can merge with HARDWARE_STRATEGY
10. SESSION_SUMMARY.md - Old session notes
11. INTERFACE_GUIDE.md - **KEEP**
12. SIGNAL_WORKFLOW_EXPLAINED.md - **KEEP**
13. WHATS_NEW_UI.md - Old changelog
14. WHATS_NEW.md - Old changelog
15. WEB_INTERFACE_TEST_GUIDE.md
16. FLIGHT_TRACKING_GUIDE.md - **KEEP**
17. RTL-SDR-CONFLICT.md
18. POWER_ISSUE_DIAGNOSIS.md - Historical
19. MULTIMETER_POWER_TEST.md - Historical
20. MAC_PI_WORKFLOW.md - Historical
21. KEYFOB_SETTINGS.md
22. CC1101_RECEIVE_GUIDE.md
23. PHASE1_PROGRESS.md - Old progress notes
24. gemini.md - Old AI notes

**Recommendation:** Consolidate into 5-6 essential docs

---

## 💾 ESTIMATED SPACE SAVINGS

### Safe Deletions:
- dump1090/ directory: **107MB**
- __pycache__/: **88KB**
- Obsolete Python test files: **~200KB**
- Old shell scripts: **~11KB**
- piaware .deb file: **~3MB**
- Old logs: **~100KB**

**Total Safe Deletion: ~110MB (40% reduction!)**

### Aggressive Cleanup (if consolidating docs):
- Old MD files: **~100KB**
- Old Python versions: **~100KB**

**Total Aggressive: ~110.2MB**

---

## 🎯 RECOMMENDED ACTIONS

### Phase 1: Safe Cleanup (110MB)
1. ✅ Delete `dump1090/` directory (107MB) - source code not needed
2. ✅ Delete `__pycache__/` directories (88KB)
3. ✅ Delete `piaware-repository_3.8.1_all.deb` (3MB)
4. ✅ Delete old logs (web_interface.log, sdrpp_error.log)
5. ✅ Delete `fm_scan.csv`

### Phase 2: Test File Cleanup (~55KB)
6. ✅ Delete all 15 NFC/CC1101 test files (they're standalone tests)
7. ✅ Delete manual test shell scripts (4 scripts)

### Phase 3: Old App Cleanup (~85KB)
8. ❓ Check if `app.py` is still needed, then delete
9. ✅ Delete old app versions (piflip_core.py, piflip_modern.py, etc.)
10. ✅ Delete old replay scripts

### Phase 4: Documentation Consolidation
11. Merge redundant MD files
12. Archive historical docs

---

## 📝 FILES TO KEEP (Core Application)

### Python (Required by web_interface.py)
```
web_interface.py          ← Main app
urh_analyzer.py
auto_analyzer.py
nfc_enhanced.py
nfc_cloner.py
cc1101_enhanced.py
signal_decoder.py
nfc_emulator.py
favorites_manager.py
waveform_generator.py
```

### Directories
```
templates/           ← Flask HTML
piflip_env/         ← Python venv
captures/           ← User data
nfc_library/        ← User data
rf_library/         ← User data
backups/           ← User data
config/            ← Configuration
```

### Documentation (Essential)
```
README.md
ROADMAP.md
INTERFACE_GUIDE.md
SIGNAL_WORKFLOW_EXPLAINED.md
FLIGHT_TRACKING_GUIDE.md
```

**Total Core Size: ~128MB (after cleanup)**

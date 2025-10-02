# Archive Directory

This directory contains historical files that are no longer actively used but preserved for reference.

**Archived:** October 2, 2025

---

## 📁 Directory Structure

### `/old_sessions/`
Session notes and progress logs from development:
- `gemini.md` - Early AI assistant notes
- `SESSION_SUMMARY.md` - Old session summary
- `HARDWARE_TEST_RESULTS.md` - Initial hardware tests (superseded by HARDWARE_TEST_RESULTS_FINAL.md)
- `WHATS_NEW.md` / `WHATS_NEW_UI.md` - Old changelogs
- `PHASE1_PROGRESS.md` - Phase 1 completion notes

### `/historical_docs/`
Troubleshooting and workflow documentation from development:
- `POWER_ISSUE_DIAGNOSIS.md` - Power supply troubleshooting (resolved with 3A PSU)
- `MULTIMETER_POWER_TEST.md` - Power testing methodology (issue resolved)
- `MAC_PI_WORKFLOW.md` - Development workflow notes
- `KEYFOB_SETTINGS.md` - Specific keyfob test settings
- `HARDWARE_CAPABILITIES.md` - Hardware capabilities (merged into HARDWARE_STRATEGY.md)

### `/deprecated_code/`
Old application code superseded by current implementation:
- `app.py` - Old CLI-based PiFlip interface (replaced by web_interface.py)

---

## 📚 Current Documentation (Active)

The main repo now has clean, essential docs:

**Core Documentation:**
- `README.md` - Main project documentation
- `claude.md` - AI assistant context and project overview
- `SETUP.md` - Installation and setup guide

**Usage Guides:**
- `INTERFACE_GUIDE.md` - Web interface features and usage
- `SIGNAL_WORKFLOW_EXPLAINED.md` - How capture/analyze/replay works
- `FLIGHT_TRACKING_GUIDE.md` - ADS-B flight tracking setup
- `CC1101_RECEIVE_GUIDE.md` - CC1101 receiver operations
- `QUICK_START.md` - Getting started quickly
- `QUICK_REFERENCE.md` - Command reference

**Technical:**
- `HARDWARE_STRATEGY.md` - Hardware decisions and capabilities
- `HARDWARE_TEST_RESULTS_FINAL.md` - Final hardware test results
- `RTL-SDR-CONFLICT.md` - RTL-SDR mode switching explanation
- `WEB_INTERFACE_TEST_GUIDE.md` - Testing the web interface

**Project Management:**
- `ROADMAP.md` - Future features and plans
- `DEPENDENCY_AUDIT.md` - What files are used/needed
- `CLEANUP_SUMMARY.md` - Recent cleanup results

---

## 🗑️ Why These Were Archived

**Old Sessions:** Development logs from initial build (Sep 28 - Oct 1, 2025). Project is now stable and documented.

**Historical Docs:** Troubleshooting docs for issues that have been resolved (power supply, hardware setup, etc.). Kept for reference.

**Deprecated Code:** `app.py` was a CLI-based interface. The project now uses `web_interface.py` which provides a full Flask web application with REST API.

---

## 📦 Archive Policy

Files are archived rather than deleted to:
1. Preserve development history
2. Reference past solutions if similar issues arise
3. Track project evolution
4. Maintain complete documentation trail

**These files are NOT needed for running PiFlip** but may be useful for understanding the development process.

---

**Last Updated:** October 2, 2025

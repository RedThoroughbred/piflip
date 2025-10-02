# 🎯 PiFlip Quick Reference

## Your Hardware (on Pi):

### 📡 CC1101 - RF Transceiver
**Can TX/RX:** 300-928 MHz
**Already works:** ✅ Transmit at 433.92 MHz
**Not tested yet:** ⚠️ Receive mode
**Cool factor:** 🔥🔥🔥🔥🔥

**What it does:**
- Replay garage remotes
- Control wireless lights
- Send/receive custom RF
- Analyze wireless protocols

---

### 💳 PN532 - NFC Reader/Writer
**Can read:** Most NFC/RFID cards
**Can write:** NFC tags, some cards
**Already works:** ✅ Read card UID
**Not tested yet:** ⚠️ Write, clone, emulate
**Cool factor:** 🔥🔥🔥🔥

**What it does:**
- Read access cards
- Write NFC tags (URLs, WiFi, etc)
- Clone cards (where legal)
- Smart business cards

---

## Web Interface Ideas:

### Option 1: Signal Library 📚
Store and replay RF captures
- Capture signals → save with name
- Browse library
- One-click replay
- **Effort:** Medium
- **Usefulness:** High

### Option 2: NFC Tag Programmer ✏️
Program blank NFC tags
- Write URLs
- Write WiFi passwords
- Write contact info
- **Effort:** Low
- **Usefulness:** Medium-High

### Option 3: Universal Remote 🎮
Web-based RF remote control
- Capture all your remotes
- Control from phone/computer
- Schedule transmissions
- **Effort:** Medium-High
- **Usefulness:** Very High

### Option 4: Card Cloner 📋
Clone access cards
- Read card
- Save dump
- Write to blank
- **Effort:** Medium
- **Usefulness:** Medium (limited use cases)

### Option 5: Combined Tool 🔧
Everything in one interface
- RF + NFC together
- Automation workflows
- Complete toolkit
- **Effort:** High
- **Usefulness:** Very High

---

## Recommended: Start with Universal Remote

**Why:**
- Most practical
- Use it daily
- Showcases RF capabilities
- Can expand later

**Features:**
1. Capture signals from remotes
2. Save to library with names/icons
3. Replay from web interface
4. Mobile-friendly buttons
5. Bonus: NFC tags as physical buttons

**Implementation:**
- Database to store signals
- Web UI with big buttons
- API endpoint for replay
- ~2-3 hours of work

---

## Quick Decision Guide:

**Want something practical you'll use daily?**
→ Universal Remote

**Want to impress people?**
→ NFC Tag Programmer (smart business cards)

**Want to learn the most?**
→ Combined Tool (everything)

**Want quick wins?**
→ Signal Library + NFC Tag Writer

**What do you want to build?**

# GitHub Setup Instructions

**Status:** ✅ Git repository initialized locally
**Branch:** main
**Commit:** Initial commit created (59 files, 17,400+ lines)

---

## 🎯 What's Done

✅ Git repository initialized
✅ `.gitignore` created (excludes user data, cache, venv)
✅ `requirements.txt` created (all dependencies documented)
✅ `.gitkeep` files for directory structure
✅ Initial commit made with full codebase
✅ Repository is clean and ready to push

---

## 📦 What's Included in Repo

### Code (will be pushed):
- `web_interface.py` - Main Flask application
- 9 core Python modules (nfc_enhanced, cc1101_enhanced, etc.)
- `templates/` - Web UI templates
- `CC1101/` - CC1101 library code
- Shell scripts (start_piflip.sh, status.sh)
- Configuration files
- Archive of historical docs
- Complete documentation in `markdown-files/`

### User Data (excluded by .gitignore):
- `piflip_env/` - Virtual environment
- `captures/*.cu8` and `captures/*.json` - Your RF captures
- `nfc_library/*.json` - Your saved NFC cards
- `backups/*.json` - Your NFC backups
- Runtime data (favorites.json, stats.json, etc.)

---

## 🚀 Next Steps: Push to GitHub

### 1. Create GitHub Repository

Go to: https://github.com/new

**Recommended settings:**
- **Repository name:** `piflip` (or your choice)
- **Description:** "PiFlip - Raspberry Pi RF & NFC Multi-Tool (Flipper Zero Alternative)"
- **Visibility:**
  - ✅ **Public** - if you want to share with community
  - ⚠️ **Private** - if keeping it personal
- **DO NOT initialize with:**
  - ❌ README (we already have one)
  - ❌ .gitignore (we already have one)
  - ❌ License (add later if desired)

Click "Create repository"

### 2. Add Remote and Push

GitHub will show you commands. Use these:

```bash
cd ~/piflip

# Add GitHub as remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/piflip.git

# Push to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/redthoroughbreds/piflip.git
git push -u origin main
```

### 3. Enter GitHub Credentials

When prompted:
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (not your password!)

**To create token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Classic"
3. Give it a name: "PiFlip Raspberry Pi"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

---

## 🔐 Alternative: SSH Key (Recommended)

Instead of token, use SSH for easier pushing:

### 1. Generate SSH key on Pi:
```bash
ssh-keygen -t ed25519 -C "redthoroughbreds@gmail.com"
# Press Enter for default location
# Press Enter for no passphrase (or set one)
```

### 2. Copy public key:
```bash
cat ~/.ssh/id_ed25519.pub
# Copy the entire output
```

### 3. Add to GitHub:
1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Title: "Raspberry Pi - PiFlip"
4. Paste the public key
5. Click "Add SSH key"

### 4. Change remote to SSH:
```bash
cd ~/piflip
git remote remove origin
git remote add origin git@github.com:YOUR-USERNAME/piflip.git
git push -u origin main
```

---

## 📝 Future Git Workflow

After initial push, your workflow will be:

```bash
# Make changes to code
# ...

# Check what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Add new feature: X"

# Push to GitHub
git push
```

---

## 🎨 Recommended Repository Settings

After pushing, configure on GitHub:

### About Section (right sidebar):
- Description: "Flipper Zero alternative built with Raspberry Pi 3B. RF capture/replay (RTL-SDR + CC1101), NFC operations (PN532), and flight tracking (ADS-B)"
- Website: http://192.168.86.141:5000 (or your domain)
- Topics: `raspberry-pi`, `rtl-sdr`, `nfc`, `flipper-zero`, `rf-tools`, `sdr`, `cc1101`, `pn532`, `ads-b`, `hardware-hacking`

### Add License (optional):
- Go to: Add file → Create new file
- Filename: `LICENSE`
- Click "Choose a license template"
- Recommended: MIT (permissive) or GPL-3.0 (copyleft)

### GitHub Actions (optional):
Could add automated tests, but not critical for now.

---

## ⚠️ Important Notes

### Security:
- ✅ User data (captures, NFC cards) is excluded via .gitignore
- ✅ Virtual environment excluded (too large)
- ✅ No credentials or secrets in repo
- ⚠️ Be careful not to accidentally commit `captures/` if you modify .gitignore

### Privacy:
- If making **public**: Anyone can see your code
- If making **private**: Only you (and collaborators) can see it
- **Recommendation:** Start private, make public later if desired

### Collaboration:
- If you want others to contribute: Make public + add CONTRIBUTING.md
- If just for backup: Keep private

---

## 📊 Repository Stats

**Current commit:**
- Files: 59
- Lines of code: 17,400+
- Size: ~400 KB (excluding user data and venv)
- Full size with venv: ~134 MB (but venv not pushed)

**Clean repository:**
- No generated files
- No user data
- No cache files
- Ready for cloning on another machine

---

## 🔄 Cloning on Another Machine

Once pushed to GitHub, you can clone it anywhere:

```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/piflip.git
cd piflip

# Install dependencies
python3 -m venv piflip_env
source piflip_env/bin/activate
pip install -r requirements.txt

# Configure hardware (I2C, SPI)
# Connect RTL-SDR, CC1101, PN532

# Run
python3 web_interface.py
```

---

## ✅ Ready to Push!

Your local repository is ready. Just:
1. Create GitHub repo
2. Add remote
3. Push!

Let me know if you need help with any step!

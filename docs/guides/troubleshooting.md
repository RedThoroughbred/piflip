# PN532 NFC Not Connected - Troubleshooting 🔧

## ⚠️ Current Status

**PN532 NFC module is NOT detected**
- I2C device expected at address: **0x24**
- I2C bus is working (enabled and loaded)
- Device not responding at 0x24

---

## 🔍 Quick Diagnosis

### **What We Know:**
```
✅ I2C is enabled in /boot/config.txt
✅ I2C modules loaded (i2c_bcm2835, i2c_dev)
✅ I2C device file exists (/dev/i2c-1)
❌ PN532 not detected at address 0x24
```

### **Most Likely Causes:**
1. **Loose wire** - I2C connection not making contact
2. **Wrong mode** - PN532 not in I2C mode (switch settings)
3. **Power issue** - PN532 not getting 3.3V power
4. **Damaged module** - Less common but possible

---

## 🔧 Step-by-Step Fixes

### **Step 1: Check Physical Connections**

**PN532 I2C Wiring (verify each wire):**
```
PN532 → Raspberry Pi GPIO
==================
VCC   → Pin 1  (3.3V)     [RED wire typically]
GND   → Pin 6  (GND)      [BLACK wire]
SDA   → Pin 3  (GPIO 2)   [BLUE/GREEN wire]
SCL   → Pin 5  (GPIO 3)   [YELLOW/WHITE wire]
```

**Check each connection:**
```
1. Power off Pi completely
2. Disconnect and reconnect each wire
3. Ensure wires are FULLY seated in pins
4. Check for bent pins or damaged wires
5. Power on Pi and test
```

### **Step 2: Verify PN532 Mode Switches**

**PN532 has TWO small switches (DIP switches or jumpers):**

**For I2C mode, switches should be:**
```
Switch 0: OFF (down)
Switch 1: ON  (up)

Visual:
┌─────────┐
│  0  1   │
│ ↓   ↑   │  ← This is I2C mode
└─────────┘
OFF  ON
```

**If switches are different:**
1. Power off Pi
2. Set switches to: 0=OFF, 1=ON
3. Power on Pi
4. Test again

### **Step 3: Test I2C Bus**

**Quick I2C scan (safe, read-only):**
```bash
# This should complete in <5 seconds
# If it hangs = hardware problem
sudo i2cdetect -y 1

# Expected result if PN532 connected:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 20: -- -- -- -- 24 -- -- -- -- -- -- -- -- -- -- --
#                  ^^
#                  PN532 at 0x24
```

**If scan hangs:**
```
1. Power off Pi
2. Disconnect PN532 completely
3. Power on Pi
4. Run scan again (should be fast with no devices)
5. If still hangs = I2C bus issue, not PN532
```

### **Step 4: Check Power**

**Measure PN532 power:**
```
With multimeter:
1. Power on Pi
2. Measure between PN532 VCC and GND
3. Should read: 3.3V (±0.2V)

If less than 3.0V:
- Weak power supply
- Too many devices on 3.3V rail
- Bad wire connection
```

**Visual power check:**
```
Some PN532 boards have LED
- If LED lit = has power
- If LED off = no power (check VCC/GND)
```

### **Step 5: Try Different I2C Pins (Advanced)**

**Pi has alternate I2C buses:**
```bash
# Enable I2C bus 0 (GPIO 0/1):
# Edit /boot/config.txt:
sudo nano /boot/config.txt

# Add line:
dtoverlay=i2c0

# Reboot
sudo reboot

# After reboot, scan bus 0:
sudo i2cdetect -y 0
```

---

## 🛠️ Common Issues & Solutions

### **Issue 1: i2cdetect hangs/times out**

**Cause:** Short circuit or damaged I2C bus

**Fix:**
```
1. Power off completely
2. Remove PN532 wires
3. Check for bare wire touching metal
4. Check for bent GPIO pins
5. Reconnect carefully
```

### **Issue 2: PN532 detected at wrong address**

**Some PN532 modules use 0x48 instead of 0x24**

**Check:**
```bash
sudo i2cdetect -y 1

# If you see 48 instead of 24:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
```

**Solution:** Edit nfc_emulator.py:
```python
# Change:
self.pn532 = PN532_I2C(i2c, address=0x24)

# To:
self.pn532 = PN532_I2C(i2c, address=0x48)
```

### **Issue 3: Worked before, stopped working**

**Likely causes:**
```
1. Wire came loose (most common)
2. PN532 mode switch bumped
3. Something else using I2C
4. Pi GPIO damaged (rare)
```

**Quick fix:**
```
1. Reseat all 4 wires
2. Check mode switches
3. Reboot Pi
4. Test again
```

### **Issue 4: Never worked, brand new module**

**Checklist:**
```
1. Mode switches in I2C mode?
2. Wires to correct GPIO pins?
3. 3.3V NOT 5V? (5V will damage PN532!)
4. All 4 wires connected (VCC, GND, SDA, SCL)?
5. Good quality jumper wires?
```

---

## 🧪 Diagnostic Commands

### **Full I2C Diagnostic:**
```bash
# 1. Check I2C enabled:
ls -l /dev/i2c-*
# Should show: /dev/i2c-1

# 2. Check modules loaded:
lsmod | grep i2c
# Should show: i2c_bcm2835, i2c_dev

# 3. Quick scan:
sudo i2cdetect -y 1
# Should show 24 if PN532 connected

# 4. Test Python library:
python3 << EOF
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
print(f"I2C bus: {i2c}")
while not i2c.try_lock():
    pass
devices = i2c.scan()
i2c.unlock()
print(f"Devices found: {[hex(d) for d in devices]}")
EOF
```

### **Expected Output (Working):**
```
I2C bus: <busio.I2C object at 0x...>
Devices found: ['0x24']
```

### **Expected Output (Not Working):**
```
I2C bus: <busio.I2C object at 0x...>
Devices found: []
```

---

## 📋 Wiring Verification Table

**Use this to verify each connection:**

| PN532 Pin | Wire Color (typical) | Pi GPIO Pin | Function | Voltage | Connected? |
|-----------|---------------------|-------------|----------|---------|------------|
| VCC       | Red                 | Pin 1       | 3.3V     | 3.3V    | [ ]        |
| GND       | Black               | Pin 6       | Ground   | 0V      | [ ]        |
| SDA       | Blue/Green          | Pin 3       | Data     | 3.3V    | [ ]        |
| SCL       | Yellow/White        | Pin 5       | Clock    | 3.3V    | [ ]        |

**How to verify:**
1. Power off Pi
2. Check each wire visually
3. Gentle tug test (should not come out easily)
4. Check GPIO pin numbers match
5. Power on and test

---

## 🔄 Reset Procedure

**If all else fails, complete reset:**

```bash
# 1. Power off Pi completely:
sudo shutdown -h now
# Wait for all LEDs off

# 2. Disconnect PN532:
# Remove all 4 wires from Pi

# 3. Power on Pi (without PN532):
# Boot up normally

# 4. Test I2C bus is clean:
sudo i2cdetect -y 1
# Should show all "--" (no devices)

# 5. Power off again:
sudo shutdown -h now

# 6. Reconnect PN532 carefully:
# VCC → Pin 1 (3.3V)
# GND → Pin 6 (GND)
# SDA → Pin 3 (GPIO 2)
# SCL → Pin 5 (GPIO 3)

# 7. Verify mode switches:
# 0=OFF, 1=ON (I2C mode)

# 8. Power on Pi:
# Boot up

# 9. Test:
sudo i2cdetect -y 1
# Should show "24"

# 10. Test Python:
python3 -c "
from pathlib import Path
import sys
sys.path.append('/home/seth/piflip')
from nfc_emulator import NFCEmulator
nfc = NFCEmulator()
print('✅ PN532 connected!')
"
```

---

## 🛡️ Safety Reminders

### **IMPORTANT:**
```
⚠️ PN532 is 3.3V ONLY!
   DO NOT connect to 5V pins!
   5V will DAMAGE the module!

✅ Use Pin 1 or Pin 17 for VCC (3.3V)
❌ Never use Pin 2 or Pin 4 (5V)

⚠️ Power off Pi before wiring!
   Don't hot-plug I2C devices
```

---

## 📞 Quick Reference

### **Pi GPIO Pinout (looking at Pi from above):**
```
        3.3V  [1] [2]  5V       ← PN532 VCC here (Pin 1)
SDA (GPIO2)  [3] [4]  5V       ← PN532 SDA here (Pin 3)
SCL (GPIO3)  [5] [6]  GND      ← PN532 SCL (5), GND (6)
     GPIO4   [7] [8]  GPIO14
         GND [9] [10] GPIO15
    ...
```

### **PN532 I2C Address:**
```
Default: 0x24 (most common)
Alternative: 0x48 (some modules)
```

### **Mode Switch Settings:**
```
I2C mode:   Switch 0=OFF, Switch 1=ON
UART mode:  Switch 0=OFF, Switch 1=OFF
SPI mode:   Switch 0=ON,  Switch 1=OFF
```

---

## ✅ After Fixing

**Once PN532 is detected:**

```bash
# 1. Verify detection:
sudo i2cdetect -y 1
# Should show: 24

# 2. Test Python:
python3 -c "
from pathlib import Path
import sys
sys.path.append('/home/seth/piflip')
from nfc_emulator import NFCEmulator
nfc = NFCEmulator()
print('✅ NFC working!')
"

# 3. Restart PiFlip service:
sudo systemctl restart piflip.service

# 4. Check web interface:
# Open: http://piflip.local:5000
# NFC menu should work
```

---

## 💡 Pro Tips

**Tip 1: Use quality wires**
```
Cheap jumper wires are #1 cause of I2C issues
Invest in good female-to-female jumpers
Or solder connections for permanence
```

**Tip 2: Short wires are better**
```
Long I2C wires = more resistance & interference
Keep wires under 6 inches if possible
Twist SDA and SCL together to reduce noise
```

**Tip 3: Test after any changes**
```
After moving Pi or touching wires:
sudo i2cdetect -y 1
Quick check confirms still connected
```

**Tip 4: Photo your wiring**
```
Take a clear photo of working setup
If wires come loose, recreate from photo
Saves hours of troubleshooting!
```

---

## 🎓 Understanding I2C

**What is I2C?**
```
I2C = Inter-Integrated Circuit
Two-wire communication protocol
SDA = Data line
SCL = Clock line

Multiple devices can share same bus
Each device has unique address (0x24, 0x48, etc.)
```

**Why PN532 uses I2C:**
```
✅ Only 2 wires needed (plus power/ground)
✅ Simple to connect
✅ Well supported on Pi
✅ Can share bus with other I2C devices
```

---

## 🆘 Still Not Working?

**If you've tried everything:**

1. **Test with different PN532 module** (if available)
   - Confirms if module is faulty

2. **Test on different I2C bus** (I2C bus 0)
   - Confirms if I2C-1 is damaged

3. **Try UART mode instead of I2C**
   - Uses TX/RX pins instead
   - Requires code changes

4. **Check for fake/clone modules**
   - Some cheap clones don't work correctly
   - Original NXP PN532 recommended

**Last resort:**
```
The PN532 module may be:
- Damaged from 5V (if accidentally connected)
- Defective from factory
- Incompatible clone

Consider purchasing replacement from:
- Adafruit (original, reliable)
- Reliable electronics supplier
```

---

**Good luck! The most common fix is just reseating the wires. 🔌✨**

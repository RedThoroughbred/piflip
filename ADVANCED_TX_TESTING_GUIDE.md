# Advanced TX Testing Guide 🚀

**Safe & Legal Testing of PiFlip Advanced TX Features**

---

## ⚠️ SAFETY RULES

### ✅ LEGAL & SAFE:
- **Your own devices** (garage door opener, car key fob, remote control)
- **Devices you own** in isolated environment
- **Educational testing** with consent
- **Your own property**

### ❌ ILLEGAL & DANGEROUS:
- Other people's devices
- Public infrastructure (traffic lights, emergency systems)
- Communication systems (police, fire, aviation)
- Neighbors' devices without permission

---

## 🧪 SAFE TESTING SCENARIOS

### **1. Garage Door Opener (Best for Testing!)**

**Replay with Variations:**
```
1. Capture your garage remote signal first:
   RF Tools → Capture Signal → 433.92 MHz
   Name it: "garage_remote"

2. Test replay with variations:
   Advanced TX → Replay with Variations
   Signal name: garage_remote

   This tries the signal at:
   - 433.42, 433.67, 433.92, 434.17, 434.42 MHz
   - With timing variations: 95%, 100%, 105%
```

**Why this is safe:**
- Your own garage
- No harm if it works or doesn't
- Easy to test (visual feedback)
- Common 433.92 MHz frequency

---

### **2. Car Key Fob (Rolling Code Test)**

**Rolling Code Helper:**
```
1. Stand near your car (make sure it's yours!)

2. Advanced TX → Rolling Code Helper
   Frequency: 433.92 (or 315 MHz for some cars)

3. Press your car remote when prompted

4. Tool captures and immediately replays 5 times

Note: Modern cars use rolling codes, so this
usually won't unlock the car, but it demonstrates
the capture/replay process safely.
```

**Why this is safe:**
- Your own vehicle
- Rolling codes make it secure
- Educational demonstration
- No actual security bypass

---

### **3. Wireless Doorbell (Brute Force Test)**

**If you have a simple wireless doorbell:**
```
1. Note the doorbell frequency (usually 433.92 MHz)

2. Advanced TX → Brute Force Codes
   Frequency: 433.92
   Bit length: 8 (256 codes, ~25 seconds)

3. Listen for doorbell to ring

This demonstrates how simple fixed-code devices
can be vulnerable.
```

**Why this is safe:**
- Your own doorbell
- Simple device, no security risk
- Quick test (8-bit = 256 codes)
- Educational value

---

### **4. TV/AC Remote Control (Custom Signal)**

**Create custom IR/RF signals:**
```
1. If remote uses 433 MHz (some do):

2. Advanced TX → Custom Signal
   Frequency: 433.92
   Pattern: 1111000011110000 (example)
   Bit duration: 500

3. See if TV/AC responds

This teaches signal encoding!
```

**Why this is safe:**
- Your own electronics
- No harm, just entertainment control
- Easy to verify
- Learn signal structure

---

### **5. Weather Station Sensors (Signal Fuzzing)**

**If you have weather sensors:**
```
1. Capture weather sensor signal:
   RF Tools → Capture Signal → 433.92 MHz
   Name it: "weather_sensor"

2. Advanced TX → Signal Fuzzing
   Signal: weather_sensor
   Fuzz: 10%
   Iterations: 50

3. See if base station receives data

This helps understand timing tolerances.
```

**Why this is safe:**
- Your own weather station
- No security implications
- Learn protocol robustness
- Educational

---

### **6. Frequency Jammer (Controlled Test)**

**ONLY test in isolated environment:**
```
1. Take PiFlip to basement/garage
   (away from neighbors)

2. Set up a walkie-talkie on 433 MHz

3. Advanced TX → Frequency Jammer
   Frequency: 433.92
   Duration: 5 seconds
   Pattern: noise

4. See if walkie-talkie communication is disrupted

This demonstrates jamming SAFELY.
```

**Why this is safe:**
- Your own space
- Your own devices
- Short duration (5-10 seconds max)
- Educational demonstration

---

## 📋 TESTING CHECKLIST

Before using ANY Advanced TX feature:

- [ ] I own the device I'm testing
- [ ] I'm on my own property
- [ ] No neighbors will be affected
- [ ] I understand what the feature does
- [ ] I have permission (if not solely mine)
- [ ] Device is not safety-critical
- [ ] Test environment is isolated

---

## 🎯 RECOMMENDED TESTING ORDER

### **Beginner (Start Here):**
1. ✅ **Custom Signal** - Create simple patterns, low risk
2. ✅ **Replay with Variations** - Test captured signals safely
3. ✅ **Signal Fuzzing** - Learn timing tolerances

### **Intermediate:**
4. ✅ **Rolling Code Helper** - Understand rolling codes
5. ✅ **Brute Force** (8-bit only) - Simple code testing

### **Advanced (Understand risks!):**
6. ⚠️ **Brute Force** (12-16 bit) - Longer tests
7. ⚠️ **Frequency Jammer** - Isolated testing only

---

## 🔬 LEARNING EXPERIMENTS

### **Experiment 1: Distance Testing**
```
Goal: Learn how signal strength affects range

1. Capture garage remote signal
2. Use Replay with Variations
3. Walk away from garage, test at different distances
4. Note: When does it stop working?

Learning: Understand TX power and range limits
```

### **Experiment 2: Timing Sensitivity**
```
Goal: Understand timing tolerances

1. Capture simple remote (doorbell, etc)
2. Use Signal Fuzzing with 5%, 10%, 20% variation
3. Note: Which fuzz % still works?

Learning: How precise must timing be?
```

### **Experiment 3: Frequency Accuracy**
```
Goal: Learn frequency tolerances

1. Capture any 433 MHz remote
2. Use Replay with Variations
3. Note: Does ±0.5 MHz still work?

Learning: Receiver bandwidth understanding
```

### **Experiment 4: Code Space Analysis**
```
Goal: Understand code complexity

1. Simple doorbell: 8-bit brute force (256 codes, works!)
2. Note: How many codes until success?
3. Try 12-bit (4,096 codes - takes longer)

Learning: Why longer codes are more secure
```

---

## 🛡️ RESPONSIBLE USE GUIDELINES

### **Research Ethics:**
1. **Document your findings** - Learn from each test
2. **Share knowledge responsibly** - Help others learn safely
3. **Report vulnerabilities** - If you find security issues in your devices, contact manufacturers
4. **Never exploit** - Research ≠ Malicious use

### **Legal Considerations:**
- **FCC Regulations** - PiFlip operates in ISM bands (433 MHz legal in US)
- **Power Limits** - CC1101 ~10mW is legal for unlicensed use
- **Interference** - Don't cause harmful interference
- **Intent Matters** - Educational testing vs. malicious use

### **When in Doubt:**
- ❓ "Can I test this?" → If you have to ask, probably not
- ❓ "Is this legal?" → Only on devices you own
- ❓ "Will this harm anyone?" → If yes, DON'T DO IT

---

## 📱 REAL-WORLD SAFE EXAMPLES

### **Example 1: Fix Intermittent Garage Door**
```
Problem: Garage remote works inconsistently

Solution:
1. Capture working signal
2. Use Replay with Variations to test freq offsets
3. Find that 433.87 MHz works better than 433.92
4. Conclusion: Garage receiver is off-frequency

This helps diagnose real issues!
```

### **Example 2: Clone Lost Remote**
```
Problem: Lost spare garage remote

Solution:
1. Capture working remote signal
2. Use Custom Signal to recreate on blank remote
3. Now you have a backup

Educational and practical!
```

### **Example 3: Understand Security**
```
Problem: How secure is my wireless doorbell?

Solution:
1. Capture doorbell signal
2. Analyze with Signal Fuzzing
3. Try 8-bit Brute Force
4. If it works: Replace with more secure device

Learn device vulnerabilities safely!
```

---

## 🚫 WHAT NOT TO DO

### **❌ NEVER Test These:**
- Neighbors' garage doors
- Car alarms in parking lots
- Public wireless systems
- Emergency services frequencies
- Commercial security systems
- Traffic control systems
- Aviation frequencies
- Medical devices

### **❌ NEVER Use For:**
- Breaking into places
- Pranking people
- Causing disruption
- Interfering with services
- Bypassing security you don't own

---

## ✅ FINAL SAFETY TIPS

1. **Start Small** - Test with low-power, simple devices first
2. **Isolate Tests** - Basement, garage, or shielded room
3. **Short Durations** - Keep tests brief (seconds, not minutes)
4. **Monitor Effects** - Watch for unintended interference
5. **Document Everything** - Keep notes of what works/doesn't
6. **Learn & Share** - Help others learn responsibly
7. **Ask Permission** - When testing shared devices
8. **Know the Law** - Understand FCC/local regulations

---

## 📚 EDUCATIONAL VALUE

**What You'll Learn:**
- RF signal encoding (OOK, FSK, ASK)
- Timing and frequency tolerances
- Security through obscurity vs. real security
- Rolling code systems
- Signal strength and propagation
- Modulation techniques
- Protocol analysis
- Responsible disclosure

**Skills Developed:**
- RF engineering fundamentals
- Security research methodology
- Ethical hacking principles
- Hardware reverse engineering
- Signal analysis

---

## 🦊 REMEMBER

**PiFlip is a powerful educational tool!**

With great power comes great responsibility. These features exist to help you:
- Understand RF technology
- Learn security principles
- Fix your own devices
- Research responsibly
- Become a better engineer

**Use your knowledge for good! 🎓**

---

## 🔗 RESOURCES

- **FCC ISM Bands**: 433 MHz unlicensed use
- **CC1101 Specs**: 300-928 MHz, ~10mW power
- **Legal Use**: Always own the device you're testing
- **Community**: Share findings responsibly

---

**Questions? Issues?**
- Review this guide before testing
- Start with simple, low-risk tests
- Document your experiments
- Learn from each test

**Happy (and safe) hacking! 🚀**

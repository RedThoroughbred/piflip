# PiFlip AI Integration Guide

## Overview
PiFlip now features Google Gemini AI integration for intelligent signal analysis, natural language control, and cloud storage.

## Features

### 1. **Smart Signal Analysis**
AI automatically identifies signal types, modulation, and security:
```python
from gemini_helper import GeminiHelper

ai = GeminiHelper()
result = ai.analyze_signal(signal_data, frequency=433.92, duration=0.5)
# Returns: type, modulation, security assessment, URH parameters
```

### 2. **Natural Language Commands**
Control PiFlip with plain English:
- "Capture the garage door signal"
- "Find all car key captures from last week"
- "Compare these two signals"

### 3. **Cloud Storage Integration**
Upload signals to GCP, keep only metadata locally:
```python
ai.upload_signal_to_cloud('test_capture.cu8', metadata={...})
# Signal stored in cloud, 40MB → 2KB on Pi
```

### 4. **AI-Powered Search**
Searchable index with AI-generated tags:
```python
ai.create_signal_index('signal.cu8')
# Creates: tags, description, confidence scores
```

### 5. **Troubleshooting Assistant**
AI diagnoses hardware issues:
```python
ai.troubleshoot("NFC reader not detected", context={...})
# Returns: diagnosis, step-by-step fixes, prevention tips
```

### 6. **Signal Comparison**
Compare two signals intelligently:
```python
ai.compare_signals(signal1, signal2)
# Identifies: same device?, rolling code?, which is more secure?
```

## Setup

### 1. Install Dependencies
```bash
cd ~/piflip
source piflip_env/bin/activate
pip install google-generativeai google-cloud-storage
```

### 2. Get Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Create API key
3. Set environment variable:
```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Configure GCP Storage (Optional)
For cloud storage features:
```bash
# Set up GCP credentials
export GCP_PROJECT="your-project-id"
export GCS_BUCKET="piflip-signals"

# Download service account key
gcloud iam service-accounts keys create ~/piflip-gcp-key.json \
    --iam-account=piflip@your-project.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS=~/piflip-gcp-key.json
```

### 4. Create GCS Bucket
```bash
gsutil mb gs://piflip-signals
gsutil lifecycle set lifecycle.json gs://piflip-signals
```

Lifecycle policy (lifecycle.json):
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

## Usage Examples

### Analyze Captured Signal
```python
from gemini_helper import GeminiHelper
import json

ai = GeminiHelper()

# Load your signal
with open('captures/garage_remote.json', 'r') as f:
    signal_data = json.load(f)

# Analyze with AI
analysis = ai.analyze_signal(
    signal_data,
    frequency=433.92,
    duration=0.5
)

print(f"Type: {analysis['type']}")
print(f"Confidence: {analysis['confidence']}%")
print(f"Security: {analysis['security']}")
print(f"Suggested URH params: {analysis['urh_params']}")
```

### Natural Language Commands
```python
# User types: "capture garage door signal on 433MHz"
command = ai.natural_language_command(user_input)

if command['action'] == 'capture_signal':
    frequency = command['parameters']['frequency']
    name = command['parameters']['name']
    # Execute capture...
```

### Cloud Storage Workflow
```python
# 1. Capture signal (40MB .cu8 file)
signal_path = 'captures/test_1234.cu8'

# 2. Create AI index (2KB metadata)
index = ai.create_signal_index(signal_path)

# 3. Upload to cloud
result = ai.upload_signal_to_cloud(signal_path, metadata=index)

# 4. Delete local .cu8 file, keep index
os.remove(signal_path)
with open(signal_path.replace('.cu8', '.index.json'), 'w') as f:
    json.dump(index, f)

# Pi now stores 2KB instead of 40MB!
```

### Troubleshooting with AI
```python
error = "PN532 initialization failed"
context = {
    "gpio_status": "enabled",
    "i2c_devices": ["0x24"],
    "last_working": "2 days ago"
}

diagnosis = ai.troubleshoot(error, context)

print("Likely Cause:", diagnosis['cause'])
print("\nFix:")
for step in diagnosis['fix_steps']:
    print(f"  {step}")
```

## Web Interface Integration

### Dashboard AI Stats
The dashboard now shows AI-powered insights:
- Signal type breakdown (garage: 15, car: 8, unknown: 3)
- Security analysis (fixed codes vs rolling codes)
- Most active frequencies
- AI confidence scores

### "Ask AI" Feature
Chat interface in web app:
```
You: "What's the best frequency for garage doors?"
AI: "Most garage door openers use 310-390MHz (older) or
     433.92MHz (modern). Start with 433.92MHz."
```

### Auto-Tag System
AI automatically tags all captures:
- `garage` `433mhz` `ook` `fixed-code` `insecure`
- Searchable, filterable, sortable

## Storage Savings

### Before AI Cloud Integration:
- 100 captures × 40MB = 4GB on Pi SD card
- Search: manual grep through JSON files
- Analysis: manual URH configuration

### After AI Cloud Integration:
- 100 captures × 2KB index = 200KB on Pi
- 100 captures × 40MB = 4GB in GCS (cheap, unlimited)
- Search: instant AI-powered semantic search
- Analysis: automatic AI recommendations

**SD card savings: 99.95%**

## Cost Estimate

### Gemini API (Free Tier):
- 15 requests/minute
- 1 million tokens/month
- **Cost: $0/month** for typical PiFlip usage

### GCP Cloud Storage:
- Storage: $0.020/GB/month
- 100 signals (4GB) = $0.08/month
- Download: $0.12/GB (rarely needed)
- **Cost: ~$0.10/month**

## Privacy & Security

### What's Sent to AI:
- Signal metadata (frequency, duration, samples count)
- No raw RF data uploaded to Gemini
- NFC card UIDs (hashed for privacy)

### What's NOT Sent:
- Raw .cu8 waveform files
- Personal information
- Location data

### Cloud Storage:
- Encrypted at rest (Google-managed keys)
- Private bucket (not public)
- Access controlled by service account
- Auto-delete after 1 year

## Advanced Features

### Batch Analysis
Analyze all existing captures:
```bash
python3 << 'EOF'
from gemini_helper import GeminiHelper
from pathlib import Path
import json

ai = GeminiHelper()

for capture in Path('captures').glob('*.json'):
    with open(capture) as f:
        data = json.load(f)

    analysis = ai.analyze_signal(data,
                                  data.get('frequency'),
                                  data.get('duration'))

    print(f"{capture.stem}: {analysis['type']} ({analysis['confidence']}%)")
EOF
```

### Signal Recommendations
AI suggests similar signals to try:
```python
current_signal = load_signal('garage.json')
suggestions = ai.get_similar_signals(current_signal)
# Suggests: "Try 310MHz (older garage openers)"
```

### Learning Mode
AI learns your specific devices:
```python
# Tag known signals
ai.tag_signal('toyota_key.json', 'my_car')

# Later, AI recognizes similar patterns
new_signal = capture_signal()
match = ai.match_known_device(new_signal)
# "90% match to 'my_car' (different button?)"
```

## Troubleshooting

### "AI not configured" Error
```bash
# Check API key
echo $GEMINI_API_KEY

# If empty, set it:
export GEMINI_API_KEY="your-key-here"
```

### "GCP storage not configured"
```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test access
gsutil ls gs://piflip-signals
```

### Rate Limiting
Gemini free tier: 15 requests/minute
If you hit limit:
```python
import time
# Add delay between AI calls
time.sleep(4)  # 15 requests/min = 1 every 4 seconds
```

## Future Enhancements

- [ ] Voice control ("Hey PiFlip, scan 433MHz")
- [ ] Image recognition (point camera at remote, AI identifies type)
- [ ] Anomaly detection (alert on unusual signals)
- [ ] Collaborative database (share known signals anonymously)
- [ ] Predictive analysis (AI predicts next rolling code)
- [ ] Multi-language support
- [ ] Offline AI mode (local LLM on Pi 5)

## Resources

- [Gemini API Docs](https://ai.google.dev/docs)
- [GCP Storage Docs](https://cloud.google.com/storage/docs)
- [PiFlip GitHub](https://github.com/yourusername/piflip)

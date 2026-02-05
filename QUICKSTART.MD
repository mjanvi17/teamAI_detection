# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the API Server
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 3: Test the API

**Option A: Using Web Interface**
- Open `index.html` in your browser
- Enter API key: `my-secret-key`
- Upload an audio file
- Click "Detect Voice"

**Option B: Using Python**
```python
import requests
import base64

API_KEY = "my-secret-key"
API_URL = "http://localhost:8000"

# Read audio file
with open("your_audio.mp3", "rb") as f:
    audio_data = f.read()

# Encode to base64
audio_base64 = base64.b64encode(audio_data).decode()

# Send request
response = requests.post(
    f"{API_URL}/detect",
    json={
        "audio_base64": audio_base64,
        "audio_format": "mp3",
        "language": "english"
    },
    headers={"x_api_key": API_KEY}
)

# View result
print(response.json())
```

**Option C: Using cURL**
```bash
# Convert audio to base64 first
BASE64_AUDIO=$(base64 < audio.mp3 | tr -d '\n')

# Send request
curl -X POST "http://localhost:8000/detect" \
  -H "x_api_key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d "{'audio_base64':'$BASE64_AUDIO','audio_format':'mp3','language':'english'}"
```

---

## API Endpoints at a Glance

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/detect` | POST | **Detect AI/Human voice** |
| `/supported-languages` | GET | List supported languages |
| `/stats` | GET | API information |

All endpoints (except `/`) require header: `x_api_key: my-secret-key`

---

## Running Tests

```bash
python test_api.py
```

Expected output:
```
====================================================
AI VOICE DETECTION API - TEST SUITE
====================================================

[TEST] Health Check
Status: 200
Response: {'status': 'healthy', 'version': '1.0.0'}

[TEST] Supported Languages
Status: 200
Response: {'status': 'success', 'supported_languages': [...]}

...
====================================================
TEST RESULTS SUMMARY
====================================================
Health Check: ✅ PASSED
Supported Languages: ✅ PASSED
API Stats: ✅ PASSED
Invalid API Key: ✅ PASSED
Unsupported Language: ✅ PASSED

Total: 5/5 tests passed
```

---

## File Structure Explained

```
ai-voice-detection/
├── main.py              # 🎯 FastAPI application (START HERE)
├── model.py             # 🧠 AI model & feature extraction
├── test_api.py          # ✅ Test suite
├── index.html           # 🖥️ Web UI for testing
├── requirements.txt     # 📦 Python dependencies
├── .env.example         # ⚙️ Configuration template
└── README.md            # 📖 Full documentation
```

---

## Supported Languages

- 🇬🇧 English
- 🇮🇳 Tamil
- 🇮🇳 Hindi
- 🇮🇳 Malayalam
- 🇮🇳 Telugu

---

## Common Issues & Solutions

### ❌ "ModuleNotFoundError: No module named 'librosa'"
```bash
pip install librosa
```

### ❌ "Address already in use" (port 8000)
```bash
# Use a different port
uvicorn main:app --port 8001
```

### ❌ "Audio file too large"
Maximum file size is 25MB. Compress your audio before uploading.

### ❌ "CORS error when using web interface"
The API has CORS enabled. Make sure:
1. API is running on localhost:8000
2. Open index.html from file system or local server

---

## Next Steps

1. **Read Full Documentation**: See `README.md` for complete API reference
2. **Customize Model**: Edit `model.py` to improve detection accuracy
3. **Deploy**: See README for Docker/cloud deployment options
4. **Add Features**: Implement batch processing, webhooks, database storage

---

## Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Check if port 8000 is available
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process on port 8000
kill -9 $(lsof -ti :8000)  # macOS/Linux

# Run API in background
nohup python main.py &

# View API documentation in browser
open http://localhost:8000/docs
```

---

## Example Request & Response

### Request
```json
POST http://localhost:8000/detect
Header: x_api_key: my-secret-key

{
  "audio_base64": "SUQzBAAAAAAAI1RTU0U...",
  "audio_format": "mp3",
  "language": "english",
  "user_id": "user_123"
}
```

### Response (Human)
```json
{
  "status": "success",
  "classification": "HUMAN",
  "confidence_score": 0.87,
  "language": "english",
  "timestamp": "2024-02-05T10:30:45.123456",
  "message": "Audio classified as HUMAN with 87.0% confidence"
}
```

### Response (AI)
```json
{
  "status": "success",
  "classification": "AI_GENERATED",
  "confidence_score": 0.92,
  "language": "english",
  "timestamp": "2024-02-05T10:30:45.123456",
  "message": "Audio classified as AI_GENERATED with 92.0% confidence"
}
```

---

## Performance Tips

- **Faster API**: Run with multiple workers
  ```bash
  uvicorn main:app --workers 4
  ```

- **Reduce Audio Processing Time**: Limit audio duration in `model.py`
  ```python
  y, sr = librosa.load(path, sr=16000, duration=10)  # Max 10 seconds
  ```

- **Cache Results**: Implement caching for identical requests

---

## Security Reminder ⚠️

**Default API Key is: `my-secret-key`**

Change this in production:
```bash
export API_KEY="your-secret-key-here"
python main.py
```

---

Need help? Check `README.md` for detailed documentation!

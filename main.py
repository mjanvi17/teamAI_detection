import base64
import uuid
import os
import json
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from model import predict_voice

API_KEY = os.getenv("API_KEY", "teamAI_123")

app = FastAPI(
    title="AI Voice Detection API",
    description="Detects whether voice samples are AI-generated or human",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------- 
# Configuration
# --------------------------------- 

API_KEY = os.getenv("API_KEY", "teamAI_123")
UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --------------------------------- 
# Authentication Dependency
# --------------------------------- 

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

# Supported languages
SUPPORTED_LANGUAGES = ["tamil", "english", "hindi", "malayalam", "telugu"]

# --------------------------------- 
# Pydantic Models
# --------------------------------- 

class AudioRequest(BaseModel):
    """Request model for voice detection"""
    audio_base64: str = Field(..., description="Base64-encoded audio file")
    audio_format: str = Field(default="mp3", description="Audio format (mp3, wav, etc.)")
    language: str = Field(default="english", description="Language of the audio")
    user_id: Optional[str] = Field(default=None, description="Optional user identifier")

class DetectionResponse(BaseModel):
    """Response model for detection results"""
    status: str
    classification: str
    confidence_score: float
    language: str
    timestamp: str
    message: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str

# --------------------------------- 
# Utility Functions
# --------------------------------- 

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate incoming API key"""
    if not api_key:
        return False
    return api_key == API_KEY

def validate_language(language: str) -> bool:
    """Validate language is supported"""
    return language.lower() in SUPPORTED_LANGUAGES

def cleanup_file(path: str) -> None:
    """Safely remove temporary file"""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Warning: Could not cleanup file {path}: {e}")

# --------------------------------- 
# HTML Frontend
# --------------------------------- 

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Voice Detection</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .config-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }

        input[type="text"],
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }

        .upload-area:hover {
            background: #f0f4ff;
            border-color: #764ba2;
        }

        .upload-area.dragover {
            background: #e8f0ff;
            border-color: #667eea;
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }

        .upload-text {
            color: #666;
            font-size: 16px;
        }

        input[type="file"] {
            display: none;
        }

        .file-info {
            background: #e8f0ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }

        .file-info.active {
            display: block;
        }

        .file-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .file-size {
            color: #666;
            font-size: 14px;
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }

        button:hover:not(:disabled) {
            transform: translateY(-2px);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .result {
            margin-top: 30px;
            padding: 25px;
            border-radius: 10px;
            display: none;
        }

        .result.active {
            display: block;
        }

        .result.success {
            background: #d4edda;
            border: 2px solid #28a745;
        }

        .result.error {
            background: #f8d7da;
            border: 2px solid #dc3545;
        }

        .result-title {
            font-weight: 700;
            font-size: 18px;
            margin-bottom: 15px;
        }

        .result.success .result-title {
            color: #155724;
        }

        .result.error .result-title {
            color: #721c24;
        }

        .result-details {
            display: grid;
            gap: 10px;
        }

        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }

        .result-label {
            font-weight: 600;
            color: #333;
        }

        .result-value {
            color: #666;
        }

        .confidence-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 10px;
        }

        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 AI Voice Detection</h1>
        <p class="subtitle">Upload an audio file to detect if it's AI-generated or human</p>

        <div class="config-section">
            <div class="form-group">
                <label for="apiKey">API Key</label>
                <input type="text" id="apiKey" value="my-secret-key" placeholder="Enter your API key">
            </div>

            <div class="form-group">
                <label for="language">Language</label>
                <select id="language">
                    <option value="english">English</option>
                    <option value="tamil">Tamil</option>
                    <option value="hindi">Hindi</option>
                    <option value="malayalam">Malayalam</option>
                    <option value="telugu">Telugu</option>
                </select>
            </div>
        </div>

        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Click to upload or drag and drop</div>
            <div class="upload-text" style="font-size: 12px; margin-top: 5px;">MP3, WAV, OGG, FLAC (Max 25MB)</div>
        </div>

        <input type="file" id="fileInput" accept="audio/*">

        <div class="file-info" id="fileInfo">
            <div class="file-name" id="fileName"></div>
            <div class="file-size" id="fileSize"></div>
        </div>

        <button id="detectBtn" disabled>Analyze Audio</button>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing audio...</p>
        </div>

        <div class="result" id="result">
            <div class="result-title" id="resultTitle"></div>
            <div class="result-details" id="resultDetails"></div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const detectBtn = document.getElementById('detectBtn');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const resultTitle = document.getElementById('resultTitle');
        const resultDetails = document.getElementById('resultDetails');
        const apiKey = document.getElementById('apiKey');
        const language = document.getElementById('language');

        let selectedFile = null;

        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.type.startsWith('audio/')) {
                alert('Please upload an audio file');
                return;
            }

            selectedFile = file;
            fileName.textContent = file.name;
            fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
            fileInfo.classList.add('active');
            detectBtn.disabled = false;
            result.classList.remove('active');
        }

        detectBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            const key = apiKey.value.trim();

            if (!key) {
                showError('Please enter API Key');
                return;
            }

            detectBtn.disabled = true;
            loading.classList.add('active');
            result.classList.remove('active');

            try {
                const base64Audio = await fileToBase64(selectedFile);
                const fileExt = selectedFile.name.split('.').pop().toLowerCase();

                const response = await fetch('/detect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-api-key': key
                    },
                    body: JSON.stringify({
                        audio_base64: base64Audio,
                        audio_format: fileExt,
                        language: language.value
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showSuccess(data);
                } else {
                    showError(data.detail || 'Detection failed');
                }
            } catch (error) {
                showError(`Error: ${error.message}`);
            } finally {
                loading.classList.remove('active');
                detectBtn.disabled = false;
            }
        });

        function fileToBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
        }

        function showSuccess(data) {
            result.className = 'result active success';
            resultTitle.textContent = `✅ ${data.message}`;
            
            const confidence = Math.round(data.confidence_score * 100);
            
            resultDetails.innerHTML = `
                <div class="result-item">
                    <span class="result-label">Classification:</span>
                    <span class="result-value">${data.classification.toUpperCase()}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Language:</span>
                    <span class="result-value">${data.language.toUpperCase()}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Timestamp:</span>
                    <span class="result-value">${new Date(data.timestamp).toLocaleString()}</span>
                </div>
                <div style="padding: 10px; background: white; border-radius: 5px;">
                    <div class="result-label" style="margin-bottom: 10px;">Confidence Score</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%">${confidence}%</div>
                    </div>
                </div>
            `;
        }

        function showError(message) {
            result.className = 'result active error';
            resultTitle.textContent = '❌ Error';
            resultDetails.innerHTML = `
                <div class="result-item">
                    <span class="result-value">${message}</span>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

# --------------------------------- 
# API Endpoints
# --------------------------------- 

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )

@app.post("/predict")
def predict_voice_api(
    file: UploadFile = File(...),
    _: str = Depends(verify_api_key)
):
    try:
        # Create unique filename to avoid collisions
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else "wav"
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = f"{UPLOAD_DIR}/{filename}"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        label, confidence = predict_voice(file_path)

        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "label": label,
            "confidence": round(confidence, 3)
        }
    except Exception as e:
        # Cleanup on error if file exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.post("/detect", response_model=DetectionResponse)
async def detect(
    data: AudioRequest,
    x_api_key: str = Header(None)
):
    """
    Detect whether audio is AI-generated or human-spoken.
    
    Headers:
        x_api_key: Your API key (required)
    
    Request Body:
        - audio_base64: Base64-encoded audio file
        - audio_format: Format of audio (default: mp3)
        - language: Language code (tamil, english, hindi, malayalam, telugu)
        - user_id: Optional user identifier
    
    Returns:
        Detection result with classification and confidence score
    """
    
    if not validate_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    
    if not validate_language(data.language):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
        )
    
    if not data.audio_base64:
        raise HTTPException(
            status_code=400,
            detail="audio_base64 cannot be empty"
        )
    
    file_path = None
    try:
        try:
            audio_bytes = base64.b64decode(data.audio_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 encoding: {str(e)}"
            )
        
        if len(audio_bytes) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Audio file too large (max 25MB)"
            )
        
        if len(audio_bytes) < 1024:
            raise HTTPException(
                status_code=400,
                detail="Audio file too small"
            )
        
        filename = f"{uuid.uuid4()}.{data.audio_format}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        
        try:
            label, confidence = predict_voice(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Audio processing failed: {str(e)}"
            )
        
        return DetectionResponse(
            status="success",
            classification=label,
            confidence_score=confidence,
            language=data.language.lower(),
            timestamp=datetime.utcnow().isoformat(),
            message=f"Audio classified as {label} with {confidence*100:.1f}% confidence"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        if file_path:
            cleanup_file(file_path)


@app.get("/supported-languages")
async def get_supported_languages(x_api_key: str = Header(None)):
    """Get list of supported languages"""
    if not validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return {
        "status": "success",
        "supported_languages": SUPPORTED_LANGUAGES
    }

@app.get("/stats")
async def get_stats(x_api_key: str = Header(None)):
    """Get API statistics"""
    if not validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return {
        "status": "success",
        "version": "1.0.0",
        "supported_languages": SUPPORTED_LANGUAGES,
        "max_file_size_mb": 25,
        "supported_formats": ["mp3", "wav", "ogg", "flac"]
    }



@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
    )



import os
import io
from fastapi.testclient import TestClient
from unittest.mock import patch

# Set env var before importing main to match default behavior if needed
os.environ["API_KEY"] = "teamAI_123"

from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}
    print("✅ /health check passed")

def test_predict_auth_missing():
    response = client.post("/predict")
    # Should be 401 or 422 depending on implementation of Header(...), likely 422 if missing, but we implemented verify_api_key manually.
    # Actually Header(...) acts as required, so if missing it might return 422 (Validation Error) from FastAPI or 401 if our logic catches it.
    # Our verify_api_key defaults: x_api_key: str = Header(...)
    # If missing, FastAPI returns 422.
    assert response.status_code == 422
    print("✅ /predict missing auth passed (422)")

def test_predict_auth_invalid():
    response = client.post(
        "/predict",
        headers={"x-api-key": "wrong_key"},
        files={"file": ("test.wav", b"dummy content", "audio/wav")}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"
    print("✅ /predict invalid auth passed (401)")

@patch("main.predict_voice")
def test_predict_success(mock_predict):
    # Mock the simplified return from model
    mock_predict.return_value = ("AI_GENERATED", 0.9876)

    # Create dummy file
    file_content = b"fake audio content for mock"
    
    response = client.post(
        "/predict",
        headers={"x-api-key": "teamAI_123"},
        files={"file": ("sample.wav", file_content, "audio/wav")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "AI_GENERATED"
    assert data["confidence"] == 0.988  # round(0.9876, 3) -> 0.988
    
    # Verify mock was called
    mock_predict.assert_called_once()
    
    # Check if temp file was cleaned up (hard to check inside the test as it happens inside the function, 
    # but we can trust the logic if no error raised)
    print("✅ /predict success flow passed")

def run_tests():
    print("Running verification tests...")
    try:
        test_health()
        test_predict_auth_missing()
        test_predict_auth_invalid()
        test_predict_success()
        print("\n🎉 All verification tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_tests()

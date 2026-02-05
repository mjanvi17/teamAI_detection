#!/usr/bin/env python3
"""
Test All Endpoints
Complete test suite for AI Voice Detection API
"""

import requests
import base64
from time import sleep

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "my-secret-key"

def print_section(title):
    """Print a nice section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Test 1: API is running"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Version: {data.get('version')}")
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ FAILED - Cannot connect to API")
        print(f"   Make sure to run: python main.py")
        return False

def test_languages():
    """Test 2: Get supported languages"""
    print_section("TEST 2: Supported Languages")
    
    try:
        headers = {"x_api_key": API_KEY}
        response = requests.get(
            f"{API_URL}/supported-languages",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            languages = data.get('supported_languages', [])
            
            print(f"Status: {response.status_code}")
            print(f"Found {len(languages)} languages:")
            for lang in languages:
                print(f"  ✓ {lang}")
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_api_key_valid():
    """Test 3: Valid API key accepted"""
    print_section("TEST 3: Valid API Key")
    
    try:
        headers = {"x_api_key": API_KEY}
        response = requests.get(
            f"{API_URL}/supported-languages",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"Status: {response.status_code}")
            print("Valid API key accepted")
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_api_key_invalid():
    """Test 4: Invalid API key rejected"""
    print_section("TEST 4: Invalid API Key Rejected")
    
    try:
        headers = {"x_api_key": "wrong-secret-key"}
        response = requests.get(
            f"{API_URL}/supported-languages",
            headers=headers
        )
        
        if response.status_code == 401:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Error: {data.get('detail')}")
            print("Invalid key correctly rejected")
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED - Invalid key was not rejected")
            print(f"   Got status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_language_validation():
    """Test 5: Invalid language rejected"""
    print_section("TEST 5: Language Validation")
    
    try:
        # Create dummy audio
        dummy_audio = b"test"
        audio_base64 = base64.b64encode(dummy_audio).decode()
        
        headers = {"x_api_key": API_KEY}
        payload = {
            "audio_base64": audio_base64,
            "audio_format": "mp3",
            "language": "invalid_language"
        }
        
        response = requests.post(
            f"{API_URL}/detect",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Error: {data.get('detail')}")
            print("Invalid language correctly rejected")
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED - Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_stats():
    """Test 6: Get API statistics"""
    print_section("TEST 6: API Statistics")
    
    try:
        headers = {"x_api_key": API_KEY}
        response = requests.get(
            f"{API_URL}/stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Version: {data.get('version')}")
            print(f"Max file size: {data.get('max_file_size_mb')} MB")
            print(f"Supported formats: {', '.join(data.get('supported_formats', []))}")
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AI VOICE DETECTION API - COMPLETE TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health()))
    sleep(0.5)
    
    results.append(("Supported Languages", test_languages()))
    sleep(0.5)
    
    results.append(("Valid API Key", test_api_key_valid()))
    sleep(0.5)
    
    results.append(("Invalid API Key Rejected", test_api_key_invalid()))
    sleep(0.5)
    
    results.append(("Language Validation", test_language_validation()))
    sleep(0.5)
    
    results.append(("API Statistics", test_stats()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API is working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    print("="*70)

if __name__ == "__main__":
    main()

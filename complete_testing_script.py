#!/usr/bin/env python3
"""
AI Voice Detection API - Complete Testing Script
This script tests the API and detects if audio is AI-generated or human

Author: Claude
Date: February 5, 2024
Version: 1.0.0
"""

import requests
import base64
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000"
API_KEY = "my-secret-key"
RESULTS_FILE = "detection_results.json"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text, char="="):
    """Print a formatted header"""
    width = 70
    print("\n" + char * width)
    print(f" {text}")
    print(char * width)

def print_section(text, char="-"):
    """Print a section divider"""
    width = 70
    print("\n" + char * width)
    print(f" {text}")
    print(char * width)

def print_success(message):
    """Print success message"""
    print(f"✓ {message}")

def print_error(message):
    """Print error message"""
    print(f"✗ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ {message}")

def check_api_connection():
    """Check if API is running and accessible"""
    print_section("Checking API Connection")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is running on {API_URL}")
            print_info(f"API Version: {data.get('version', 'Unknown')}")
            print_info(f"Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print_error(f"API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {API_URL}")
        print_info("Make sure to start the API with: python main.py")
        return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False

def get_supported_languages():
    """Get list of supported languages from API"""
    try:
        response = requests.get(
            f"{API_URL}/supported-languages",
            headers={"x_api_key": API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            languages = data.get('supported_languages', [])
            return languages
    except Exception as e:
        print_error(f"Error getting languages: {str(e)}")
    
    return []

def get_api_stats():
    """Get API statistics"""
    try:
        response = requests.get(
            f"{API_URL}/stats",
            headers={"x_api_key": API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print_error(f"Error getting stats: {str(e)}")
    
    return None

def validate_audio_file(file_path):
    """Validate audio file exists and size is acceptable"""
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    if file_size_mb > 25:
        print_error(f"File too large: {file_size_mb:.2f} MB (max 25 MB)")
        return False
    
    if file_size_mb < 0.1:
        print_error(f"File too small: {file_size_mb:.2f} MB (min 0.1 MB)")
        return False
    
    return True

def get_file_extension(file_path):
    """Get file extension"""
    return file_path.split('.')[-1].lower()

def detect_voice(audio_file_path, language="english"):
    """
    Send audio to API for detection
    
    Args:
        audio_file_path: Path to audio file
        language: Language code (english, tamil, hindi, malayalam, telugu)
    
    Returns:
        dict: API response or None if error
    """
    
    # Validate file
    if not validate_audio_file(audio_file_path):
        return None
    
    # Get file info
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    file_name = os.path.basename(audio_file_path)
    file_ext = get_file_extension(audio_file_path)
    
    print_section("Processing Audio File")
    print_info(f"File: {file_name}")
    print_info(f"Size: {file_size_mb:.2f} MB")
    print_info(f"Format: {file_ext.upper()}")
    print_info(f"Language: {language.upper()}")
    
    try:
        # Read audio file
        print_section("Reading Audio File", "-")
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        print_success(f"File read successfully ({len(audio_data)} bytes)")
        
        # Encode to base64
        print_section("Encoding to Base64", "-")
        audio_base64 = base64.b64encode(audio_data).decode()
        print_success(f"Encoding complete ({len(audio_base64)} characters)")
        
        # Prepare request
        print_section("Preparing Request", "-")
        payload = {
            "audio_base64": audio_base64,
            "audio_format": file_ext,
            "language": language
        }
        print_success("Request prepared")
        
        # Send to API
        print_section("Sending to API", "-")
        print_info(f"Endpoint: POST {API_URL}/detect")
        print_info("Sending request...")
        
        response = requests.post(
            f"{API_URL}/detect",
            json=payload,
            headers={"x_api_key": API_KEY},
            timeout=30
        )
        
        # Handle response
        if response.status_code == 200:
            print_success("API response received")
            return response.json()
        else:
            data = response.json()
            detail = data.get('detail', 'Unknown error')
            print_error(f"API Error ({response.status_code}): {detail}")
            return None
    
    except requests.exceptions.Timeout:
        print_error("Request timed out (>30 seconds)")
        print_info("Audio file might be too large or API is slow")
        return None
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API")
        print_info("Make sure API is running: python main.py")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def display_result(result):
    """Display and save detection result"""
    if not result:
        print_error("No result to display")
        return
    
    classification = result.get('classification', 'UNKNOWN')
    confidence = result.get('confidence_score', 0)
    language = result.get('language', 'unknown')
    timestamp = result.get('timestamp', '')
    message = result.get('message', '')
    status = result.get('status', 'unknown')
    
    # Display result
    print_section("DETECTION RESULT")
    
    if status == "success":
        print_success(f"Status: {status.upper()}")
    else:
        print_error(f"Status: {status.upper()}")
    
    # Classification
    print("\n" + "-" * 70)
    if classification == "AI_GENERATED":
        print(f"Classification: 🤖 AI GENERATED")
        print(f"Confidence:     {confidence * 100:.1f}%")
    elif classification == "HUMAN":
        print(f"Classification: 👤 HUMAN VOICE")
        print(f"Confidence:     {confidence * 100:.1f}%")
    else:
        print(f"Classification: ❓ {classification}")
        print(f"Confidence:     {confidence * 100:.1f}%")
    
    print(f"Language:       {language.upper()}")
    print(f"Timestamp:      {timestamp}")
    print(f"Message:        {message}")
    print("-" * 70)
    
    return result

def save_results(audio_file, result):
    """Save results to JSON file"""
    try:
        # Read existing results
        results = []
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
        
        # Add new result
        entry = {
            "file": audio_file,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        results.append(entry)
        
        # Save results
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        
        print_success(f"Results saved to {RESULTS_FILE}")
    except Exception as e:
        print_error(f"Could not save results: {str(e)}")

def run_diagnostics():
    """Run full diagnostic test"""
    print_header("AI VOICE DETECTION - DIAGNOSTIC TEST")
    
    # Check API connection
    if not check_api_connection():
        print_error("Cannot proceed without API connection")
        return False
    
    # Get API stats
    print_section("Getting API Statistics")
    stats = get_api_stats()
    if stats:
        print_success("API Statistics retrieved")
        print_info(f"Version: {stats.get('version')}")
        print_info(f"Max file size: {stats.get('max_file_size_mb')} MB")
        print_info(f"Supported formats: {', '.join(stats.get('supported_formats', []))}")
    
    # Get languages
    print_section("Getting Supported Languages")
    languages = get_supported_languages()
    if languages:
        print_success("Languages retrieved")
        for i, lang in enumerate(languages, 1):
            print_info(f"{i}. {lang.upper()}")
    else:
        print_error("Could not get supported languages")
    
    print_section("Diagnostic Complete", "=")
    return True

def interactive_detection():
    """Interactive detection mode"""
    print_header("INTERACTIVE AUDIO DETECTION MODE")
    
    # Get audio file
    print_section("Input")
    audio_file = input("\nEnter audio file path: ").strip()
    
    if not audio_file:
        print_error("No file provided")
        return
    
    # Get language
    languages = get_supported_languages()
    if languages:
        print("\nAvailable languages:")
        for i, lang in enumerate(languages, 1):
            print(f"  {i}. {lang}")
        
        lang_input = input(f"Select language (1-{len(languages)}) [default: 1]: ").strip()
        
        try:
            lang_idx = int(lang_input) - 1 if lang_input else 0
            if 0 <= lang_idx < len(languages):
                language = languages[lang_idx]
            else:
                language = languages[0]
        except:
            language = languages[0]
    else:
        language = "english"
    
    # Detect
    result = detect_voice(audio_file, language)
    
    if result:
        display_result(result)
        
        # Save results
        save_choice = input("\nSave results? (y/n) [default: y]: ").strip().lower()
        if save_choice != 'n':
            save_results(audio_file, result)
    else:
        print_error("Detection failed")

def batch_detection(directory):
    """Batch detection on multiple files"""
    print_header(f"BATCH DETECTION - {directory}")
    
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    audio_files = []
    
    # Find audio files
    print_section("Finding Audio Files")
    for ext in audio_extensions:
        audio_files.extend(Path(directory).glob(f"*{ext}"))
        audio_files.extend(Path(directory).glob(f"*{ext.upper()}"))
    
    if not audio_files:
        print_error(f"No audio files found in {directory}")
        return
    
    print_success(f"Found {len(audio_files)} audio file(s)")
    
    # Process each file
    results = []
    for i, audio_file in enumerate(audio_files, 1):
        print_section(f"Processing {i}/{len(audio_files)}")
        result = detect_voice(str(audio_file), "english")
        if result:
            display_result(result)
            results.append({
                "file": str(audio_file),
                "result": result
            })
    
    # Save batch results
    if results:
        batch_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_file, 'w') as f:
            json.dump(results, f, indent=2)
        print_success(f"Batch results saved to {batch_file}")

def main():
    """Main function"""
    print_header("🎙️  AI VOICE DETECTION - TESTING SCRIPT 🎙️", "=")
    
    # Show menu
    print("\nChoose an option:")
    print("  1. Run diagnostics")
    print("  2. Detect single audio file")
    print("  3. Batch detection (folder)")
    print("  4. Interactive mode")
    print("  5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        run_diagnostics()
    
    elif choice == "2":
        if len(sys.argv) > 1:
            audio_file = sys.argv[1]
            language = sys.argv[2] if len(sys.argv) > 2 else "english"
        else:
            audio_file = input("Enter audio file path: ").strip()
            language = input("Enter language [default: english]: ").strip() or "english"
        
        result = detect_voice(audio_file, language)
        if result:
            display_result(result)
            save_results(audio_file, result)
    
    elif choice == "3":
        directory = input("Enter directory path: ").strip()
        batch_detection(directory)
    
    elif choice == "4":
        interactive_detection()
    
    elif choice == "5":
        print("\nGoodbye! 👋")
        sys.exit(0)
    
    else:
        print_error("Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

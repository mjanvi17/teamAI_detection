#!/usr/bin/env python3
"""
Test 1: Health Check
Checks if the API server is running
"""

import requests

# Configuration
API_URL = "http://localhost:8000"

print("Testing API Health Check...")
print("="*60)

try:
    response = requests.get(f"{API_URL}/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ API is running!")
    else:
        print("\n❌ API is not responding correctly")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API")
    print("Make sure to run: python main.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("="*60)

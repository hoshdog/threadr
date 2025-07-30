#!/usr/bin/env python3
"""
Test Railway Deployment
Verifies that the Railway deployment is working correctly after fixes
"""

import requests
import json
import time

BASE_URL = "https://threadr-production.up.railway.app"

def test_endpoint(endpoint, expected_status=200, method="GET", data=None):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        success = response.status_code == expected_status
        status_symbol = "✓" if success else "✗"
        
        print(f"{status_symbol} {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                if endpoint == "/health":
                    print(f"    Environment: {json_data.get('environment', 'unknown')}")
                    print(f"    OpenAI: {json_data.get('services', {}).get('openai', 'unknown')}")
                elif endpoint == "/debug/startup":
                    print(f"    Python: {json_data.get('python_version', 'unknown')[:20]}...")
                    print(f"    Port: {json_data.get('port', 'unknown')}")
                    print(f"    Working Dir: {json_data.get('process_info', {}).get('working_directory', 'unknown')}")
            except:
                pass
        
        return success, response
        
    except requests.exceptions.RequestException as e:
        print(f"✗ {method} {endpoint} - Error: {str(e)}")
        return False, None

def test_api_functionality():
    """Test core API functionality"""
    print("\n" + "="*60)
    print("  TESTING API FUNCTIONALITY")
    print("="*60)
    
    # Test thread generation with text
    test_data = {
        "text": "This is a test message to verify that the API can generate Twitter threads correctly. The API should split this into appropriate tweet-sized chunks."
    }
    
    success, response = test_endpoint("/api/generate", method="POST", data=test_data)
    
    if success and response:
        try:
            json_data = response.json()
            if json_data.get("success"):
                thread = json_data.get("thread", [])
                print(f"    ✓ Generated {len(thread)} tweets")
                if thread:
                    print(f"    First tweet: {thread[0].get('content', '')[:50]}...")
            else:
                print(f"    ✗ API returned success=false: {json_data.get('error', 'unknown error')}")
        except:
            print("    ✗ Invalid JSON response")

def main():
    print("="*60)
    print("  RAILWAY DEPLOYMENT TEST")
    print("="*60)
    print(f"Testing deployment at: {BASE_URL}")
    print()
    
    # Test basic endpoints
    endpoints = [
        "/",
        "/health", 
        "/readiness",
        "/debug/startup",
        "/api/test"
    ]
    
    print("Testing basic endpoints...")
    all_passed = True
    
    for endpoint in endpoints:
        success, _ = test_endpoint(endpoint)
        if not success:
            all_passed = False
    
    # Test API functionality
    test_api_functionality()
    
    # Summary
    print("\n" + "="*60)
    print("  DEPLOYMENT TEST SUMMARY")
    print("="*60)
    
    if all_passed:
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("All endpoints are responding correctly.")
        print("The 502 error has been resolved.")
    else:
        print("❌ DEPLOYMENT ISSUES DETECTED")
        print("Some endpoints are not responding correctly.")
        print("Check Railway logs for more details:")
        print("  railway logs --tail 100")
    
    print(f"\nDirect URL: {BASE_URL}")
    print("API Documentation: https://threadr-production.up.railway.app/docs")

if __name__ == "__main__":
    main()
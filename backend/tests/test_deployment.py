#!/usr/bin/env python3
"""
Railway Deployment Test Script
Tests the deployed backend to verify all functionality is working
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://threadr-production.up.railway.app"

def test_endpoint(url, method="GET", data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        print(f"Testing {method} {url}...")
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"  SUCCESS")
            try:
                json_data = response.json()
                print(f"  Response: {json.dumps(json_data, indent=2)[:200]}...")
                return True, json_data
            except:
                print(f"  Response: {response.text[:200]}...")
                return True, response.text
        else:
            print(f"  FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"  Error: {response.text[:200]}...")
            return False, response.text
            
    except requests.exceptions.ConnectionError as e:
        print(f"  CONNECTION ERROR: {str(e)}")
        return False, str(e)
    except requests.exceptions.Timeout as e:
        print(f"  TIMEOUT ERROR: {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"  UNEXPECTED ERROR: {str(e)}")
        return False, str(e)

def main():
    """Run comprehensive backend tests"""
    print(f"Testing Railway Backend Deployment")
    print(f"URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Health Check
    print("\n1. HEALTH CHECK")
    success, data = test_endpoint(f"{BASE_URL}/health")
    tests.append(("Health Check", success))
    
    # Test 2: Root Endpoint
    print("\n2. ROOT ENDPOINT")
    success, data = test_endpoint(f"{BASE_URL}/")
    tests.append(("Root Endpoint", success))
    
    # Test 3: Debug Startup (if available)
    print("\n3. DEBUG STARTUP")
    success, data = test_endpoint(f"{BASE_URL}/debug/startup")
    tests.append(("Debug Startup", success))
    
    # Test 4: API Test Endpoint
    print("\n4. API TEST ENDPOINT")
    success, data = test_endpoint(f"{BASE_URL}/api/test")  
    tests.append(("API Test", success))
    
    # Test 5: Rate Limit Status
    print("\n5. RATE LIMIT STATUS")
    success, data = test_endpoint(f"{BASE_URL}/api/rate-limit-status")
    tests.append(("Rate Limit Status", success))
    
    # Test 6: Generate Thread with Text
    print("\n6. GENERATE THREAD (TEXT)")
    test_data = {
        "text": "This is a test article about artificial intelligence. AI is transforming many industries and creating new opportunities for innovation. Companies are investing heavily in AI research and development to stay competitive in the market."
    }
    success, data = test_endpoint(f"{BASE_URL}/api/generate", method="POST", data=test_data)
    tests.append(("Generate Thread (Text)", success))
    
    # Test 7: Generate Thread with URL
    print("\n7. GENERATE THREAD (URL)")
    test_data = {
        "url": "https://example.com"
    }
    success, data = test_endpoint(f"{BASE_URL}/api/generate", method="POST", data=test_data, expected_status=400)  # May fail due to URL scraping
    tests.append(("Generate Thread (URL)", success))
    
    # Test 8: CORS Headers
    print("\n8. CORS HEADERS")
    try:
        response = requests.options(f"{BASE_URL}/api/generate", headers={
            "Origin": "https://threadr.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        cors_success = "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
        print(f"  Status: {response.status_code}")
        print(f"  CORS Headers: {cors_success}")
        tests.append(("CORS Configuration", cors_success))
    except Exception as e:
        print(f"  ❌ CORS test failed: {e}")
        tests.append(("CORS Configuration", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\nALL TESTS PASSED - Backend is ready for frontend integration!")
    elif passed > total/2:
        print("\nPARTIAL SUCCESS - Some functionality working, check failed tests")
    else:
        print("\nMAJOR ISSUES - Backend needs fixes before frontend integration")
    
    print("\nFRONTEND INTEGRATION NOTES:")
    print("- CORS Origins configured for: https://threadr.vercel.app")
    print("- Base API URL: https://threadr-production.up.railway.app")
    print("- Main endpoint: POST /api/generate")
    print("- Rate limiting: 10 requests per hour per IP")

if __name__ == "__main__":
    main()
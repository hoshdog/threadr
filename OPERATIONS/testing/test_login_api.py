#!/usr/bin/env python3
"""
Test script to verify login API functionality and CORS configuration
for Threadr backend deployed on Railway.

This script tests:
1. CORS preflight requests from Vercel frontend
2. Login endpoint POST requests
3. Error responses for invalid credentials
4. Response format validation
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL
BACKEND_URL = "https://threadr-production.up.railway.app"
FRONTEND_ORIGIN = "https://threadr-plum.vercel.app"

def test_cors_preflight():
    """Test CORS preflight request for login endpoint"""
    print("Testing CORS preflight request...")
    
    url = f"{BACKEND_URL}/api/auth/login"
    headers = {
        "Origin": FRONTEND_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Check CORS headers
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        cors_methods = response.headers.get("Access-Control-Allow-Methods")
        cors_headers = response.headers.get("Access-Control-Allow-Headers")
        cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
        
        print(f"   CORS Origin: {cors_origin}")
        print(f"   CORS Methods: {cors_methods}")
        print(f"   CORS Headers: {cors_headers}")
        print(f"   CORS Credentials: {cors_credentials}")
        
        # Validate CORS configuration
        if cors_origin == FRONTEND_ORIGIN or cors_origin == "*":
            print("   PASS: CORS Origin configured correctly")
        else:
            print(f"   FAIL: CORS Origin issue: Expected {FRONTEND_ORIGIN}, got {cors_origin}")
            
        if cors_methods and "POST" in cors_methods:
            print("   PASS: POST method allowed")
        else:
            print(f"   FAIL: POST method not allowed: {cors_methods}")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: CORS preflight failed: {e}")
        return False

def test_login_with_invalid_credentials():
    """Test login endpoint with invalid credentials"""
    print("\nTesting login with invalid credentials...")
    
    url = f"{BACKEND_URL}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_ORIGIN
    }
    
    # Test payload with invalid credentials
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword",
        "remember_me": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response Text: {response.text}")
        
        # Check expected 401 status for invalid credentials
        if response.status_code == 401:
            print("   PASS: Returns 401 for invalid credentials")
        else:
            print(f"   FAIL: Expected 401, got {response.status_code}")
            
        # Check CORS headers in response
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        if cors_origin:
            print(f"   PASS: CORS headers present in response: {cors_origin}")
        else:
            print("   FAIL: No CORS headers in response")
            
        return response.status_code == 401
        
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: Login request failed: {e}")
        return False

def test_login_with_malformed_payload():
    """Test login endpoint with malformed payload"""
    print("\nTesting login with malformed payload...")
    
    url = f"{BACKEND_URL}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_ORIGIN
    }
    
    # Test payload with missing required fields
    payload = {
        "email": "not-an-email",  # Invalid email format
        "password": ""            # Empty password
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response Text: {response.text}")
        
        # Check expected 422 status for validation errors
        if response.status_code == 422:
            print("   PASS: Returns 422 for validation errors")
        else:
            print(f"   FAIL: Expected 422, got {response.status_code}")
            
        return response.status_code == 422
        
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: Malformed request failed: {e}")
        return False

def test_health_endpoint():
    """Test basic connectivity with health endpoint"""
    print("\nTesting basic connectivity...")
    
    url = f"{BACKEND_URL}/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Health Status: {data.get('status', 'unknown')}")
                print("   PASS: Backend is accessible")
                return True
            except:
                print("   PASS: Backend responded (non-JSON)")
                return True
        else:
            print(f"   FAIL: Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: Health check failed: {e}")
        return False

def run_curl_examples():
    """Print curl command examples for manual testing"""
    print("\nManual curl commands for testing:")
    
    print("\n1. CORS Preflight Test:")
    print(f'curl -X OPTIONS "{BACKEND_URL}/api/auth/login" \\')
    print(f'  -H "Origin: {FRONTEND_ORIGIN}" \\')
    print('  -H "Access-Control-Request-Method: POST" \\')
    print('  -H "Access-Control-Request-Headers: Content-Type" \\')
    print('  -v')
    
    print("\n2. Login Test with Invalid Credentials:")
    print(f'curl -X POST "{BACKEND_URL}/api/auth/login" \\')
    print(f'  -H "Origin: {FRONTEND_ORIGIN}" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "test@example.com", "password": "wrongpassword"}\' \\')
    print('  -v')
    
    print("\n3. Login Test with Malformed Data:")
    print(f'curl -X POST "{BACKEND_URL}/api/auth/login" \\')
    print(f'  -H "Origin: {FRONTEND_ORIGIN}" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "not-an-email", "password": ""}\' \\')
    print('  -v')

def main():
    """Run all tests"""
    print("Threadr Login API Test Suite")
    print("="*50)
    
    results = []
    
    # Test basic connectivity first
    results.append(("Health Check", test_health_endpoint()))
    
    # Test CORS configuration
    results.append(("CORS Preflight", test_cors_preflight()))
    
    # Test login functionality
    results.append(("Invalid Credentials", test_login_with_invalid_credentials()))
    results.append(("Malformed Payload", test_login_with_malformed_payload()))
    
    # Print summary
    print("\nTest Results Summary:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Login API is properly configured.")
    else:
        print("Some tests failed. Check the details above.")
    
    # Print manual testing commands
    run_curl_examples()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test if authentication deployment has been successful
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://threadr-pw0s.onrender.com"
TEST_USER = {
    "email": f"test_{int(time.time())}@example.com",
    "password": "Test123!",
    "full_name": "Test User"
}

def test_health():
    """Test backend health"""
    print("\n[TEST] Testing Backend Health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = response.json()
        print(f"[OK] Backend is {data['status']}")
        print(f"   - Redis: {data['services']['redis']}")
        print(f"   - Routes: {data['services']['routes']}")
        print(f"   - Environment: {data['environment']}")
        return True
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints availability"""
    print("\n[TEST] Testing Authentication Endpoints...")
    
    endpoints = [
        ("/api/auth/register", "POST"),
        ("/api/auth/login", "POST"),
        ("/api/auth/me", "GET"),
    ]
    
    available = []
    unavailable = []
    
    for endpoint, method in endpoints:
        try:
            if method == "POST":
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    json={},  # Empty JSON to test endpoint existence
                    timeout=5
                )
            else:
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    timeout=5
                )
            
            if response.status_code == 404:
                unavailable.append(endpoint)
                print(f"[FAIL] {endpoint}: Not Found (404)")
            elif response.status_code in [422, 401, 400]:
                # These errors mean the endpoint exists but needs proper data
                available.append(endpoint)
                print(f"[OK] {endpoint}: Available (expecting data)")
            else:
                available.append(endpoint)
                print(f"[OK] {endpoint}: Available ({response.status_code})")
                
        except Exception as e:
            unavailable.append(endpoint)
            print(f"[FAIL] {endpoint}: Error - {e}")
    
    return len(available), len(unavailable)

def test_registration():
    """Test user registration"""
    print("\n[TEST] Testing User Registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Registration successful!")
            print(f"   - Token: {data.get('access_token', 'N/A')[:20]}...")
            return data.get('access_token')
        elif response.status_code == 404:
            print(f"[FAIL] Registration endpoint not found (404)")
            print("   AUTH ROUTERS NOT INITIALIZED!")
            return None
        else:
            print(f"[FAIL] Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Registration error: {e}")
        return None

def test_openapi_docs():
    """Check OpenAPI documentation"""
    print("\n[TEST] Checking OpenAPI Documentation...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            auth_paths = [p for p in paths if "/auth/" in p]
            print(f"[OK] OpenAPI docs available")
            print(f"   - Total endpoints: {len(paths)}")
            print(f"   - Auth endpoints: {len(auth_paths)}")
            
            if auth_paths:
                print("   Auth endpoints found:")
                for path in auth_paths[:5]:  # Show first 5
                    print(f"     • {path}")
            else:
                print("   [WARNING] No auth endpoints in OpenAPI spec!")
                
            return len(auth_paths) > 0
        else:
            print(f"[FAIL] OpenAPI docs not available: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking OpenAPI: {e}")
        return False

def main():
    print("=" * 60)
    print("THREADR AUTHENTICATION DEPLOYMENT TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print("=" * 60)
    
    # Run tests
    health_ok = test_health()
    available, unavailable = test_auth_endpoints()
    has_openapi_auth = test_openapi_docs()
    token = test_registration()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if health_ok and available > 0 and token:
        print("[SUCCESS] AUTHENTICATION DEPLOYED SUCCESSFULLY!")
        print(f"   - {available} auth endpoints available")
        print("   - Registration working")
        print("   - Ready for premium upgrade flow")
    elif health_ok and unavailable > 0:
        print("[FAIL] AUTHENTICATION NOT DEPLOYED YET")
        print(f"   - {unavailable} auth endpoints missing")
        print("   - Deployment may still be in progress")
        print("   - Wait 2-3 minutes and retry")
        
        if not has_openapi_auth:
            print("\n[CRITICAL] Auth routers not initialized!")
            print("   The authentication fix needs to be deployed.")
    else:
        print("[WARNING] PARTIAL DEPLOYMENT")
        print("   Some components working, others failing")
    
    print("\nNEXT STEPS:")
    if not token:
        print("1. Check Render deployment logs")
        print("2. Verify environment variables are set")
        print("3. Ensure latest code is deployed")
        print("4. Check for initialization errors in logs")
    else:
        print("1. Test premium upgrade flow")
        print("2. Verify Stripe integration")
        print("3. Test full user journey")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple Authentication Testing Script for Threadr Application
============================================================

This script tests authentication flows without Unicode characters for Windows compatibility.
"""

import requests
import json
import sys
import uuid
from datetime import datetime

# Backend URLs to try
BACKEND_URLS = [
    "https://threadr-pw0s.onrender.com",
    "https://threadr-production.up.railway.app"
]

FRONTEND_ORIGIN = "https://threadr-plum.vercel.app"

def find_backend_url():
    """Find working backend URL"""
    for url in BACKEND_URLS:
        try:
            print(f"Testing backend URL: {url}")
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print(f"[SUCCESS] Backend found at: {url}")
                return url
        except Exception as e:
            print(f"[FAILED] {url}: {e}")
            continue
    
    raise Exception("No working backend URL found")

def test_registration(backend_url):
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    
    unique_id = str(uuid.uuid4())[:8]
    email = f"test+{unique_id}@threadr-test.com"
    password = "TestPassword123!"
    
    url = f"{backend_url}/api/auth/register"
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_ORIGIN
    }
    
    payload = {
        "email": email,
        "password": password,
        "confirm_password": password
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"[SUCCESS] Registration successful for {email}")
            
            if "access_token" in data:
                print("[SUCCESS] JWT token received")
                return email, password, data["access_token"]
            else:
                print("[WARNING] No access token in response")
                return email, password, None
        else:
            try:
                error_data = response.json()
                print(f"[FAILED] Registration failed: {error_data}")
            except:
                print(f"[FAILED] Registration failed with status {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"[ERROR] Registration request failed: {e}")
        return None, None, None

def test_login(backend_url, email, password):
    """Test user login"""
    print("\n=== Testing User Login ===")
    
    url = f"{backend_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_ORIGIN
    }
    
    payload = {
        "email": email,
        "password": password,
        "remember_me": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Login successful for {email}")
            
            if "access_token" in data:
                print("[SUCCESS] JWT token received")
                return data["access_token"]
            else:
                print("[WARNING] No access token in response")
                return None
        else:
            try:
                error_data = response.json()
                print(f"[FAILED] Login failed: {error_data}")
            except:
                print(f"[FAILED] Login failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Login request failed: {e}")
        return None

def test_invalid_login(backend_url, email):
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Login ===")
    
    url = f"{backend_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_ORIGIN
    }
    
    payload = {
        "email": email,
        "password": "wrongpassword123",
        "remember_me": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("[SUCCESS] Correctly rejected invalid credentials")
            return True
        else:
            print(f"[FAILED] Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Invalid login test failed: {e}")
        return False

def test_protected_endpoint_without_token(backend_url):
    """Test protected endpoint without token"""
    print("\n=== Testing Protected Endpoint Without Token ===")
    
    url = f"{backend_url}/api/auth/me"
    headers = {"Origin": FRONTEND_ORIGIN}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("[SUCCESS] Correctly rejected request without token")
            return True
        else:
            print(f"[FAILED] Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Protected endpoint test failed: {e}")
        return False

def test_user_profile(backend_url, token, email):
    """Test authenticated user profile access"""
    print("\n=== Testing User Profile Access ===")
    
    if not token:
        print("[SKIPPED] No token available")
        return False
    
    url = f"{backend_url}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": FRONTEND_ORIGIN
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Profile data retrieved")
            
            if data.get("email") == email:
                print("[SUCCESS] Email matches registered user")
                return True
            else:
                print(f"[WARNING] Email mismatch: expected {email}, got {data.get('email')}")
                return False
        else:
            print(f"[FAILED] Profile access failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Profile access failed: {e}")
        return False

def test_thread_save(backend_url, token):
    """Test saving a thread"""
    print("\n=== Testing Thread Save ===")
    
    if not token:
        print("[SKIPPED] No token available")
        return False
    
    url = f"{backend_url}/api/threads/save"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Origin": FRONTEND_ORIGIN
    }
    
    thread_data = {
        "title": "Test Thread - Auth Testing",
        "original_content": "This is a test thread created during authentication testing.",
        "tweets": [
            "Testing the Threadr authentication system!",
            "This thread was created automatically during testing.",
            "All systems working correctly!"
        ],
        "metadata": {
            "source": "auth_test",
            "test_timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(url, json=thread_data, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("[SUCCESS] Thread saved successfully")
                return True
            else:
                print("[FAILED] Thread save response indicates failure")
                return False
        else:
            try:
                error_data = response.json()
                print(f"[FAILED] Thread save failed: {error_data}")
            except:
                print(f"[FAILED] Thread save failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Thread save failed: {e}")
        return False

def test_thread_history(backend_url, token):
    """Test retrieving thread history"""
    print("\n=== Testing Thread History ===")
    
    if not token:
        print("[SKIPPED] No token available")
        return False
    
    url = f"{backend_url}/api/threads"
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": FRONTEND_ORIGIN
    }
    
    params = {"page": 1, "page_size": 10}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "threads" in data:
                thread_count = len(data["threads"])
                print(f"[SUCCESS] Retrieved {thread_count} threads")
                return True
            else:
                print("[FAILED] No threads array in response")
                return False
        else:
            try:
                error_data = response.json()
                print(f"[FAILED] Thread history failed: {error_data}")
            except:
                print(f"[FAILED] Thread history failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Thread history failed: {e}")
        return False

def generate_curl_commands(backend_url, email, password, token):
    """Generate curl commands for manual testing"""
    print(f"""
=== Manual Testing Commands ===

1. Registration:
curl -X POST "{backend_url}/api/auth/register" \\
  -H "Content-Type: application/json" \\
  -H "Origin: {FRONTEND_ORIGIN}" \\
  -d '{{"email": "{email}", "password": "{password}", "confirm_password": "{password}"}}'

2. Login:
curl -X POST "{backend_url}/api/auth/login" \\
  -H "Content-Type: application/json" \\
  -H "Origin: {FRONTEND_ORIGIN}" \\
  -d '{{"email": "{email}", "password": "{password}", "remember_me": false}}'

3. User Profile (replace TOKEN):
curl -X GET "{backend_url}/api/auth/me" \\
  -H "Authorization: Bearer TOKEN" \\
  -H "Origin: {FRONTEND_ORIGIN}"

4. Save Thread (replace TOKEN):
curl -X POST "{backend_url}/api/threads/save" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer TOKEN" \\
  -H "Origin: {FRONTEND_ORIGIN}" \\
  -d '{{"title": "Test Thread", "original_content": "Test", "tweets": ["Tweet 1"], "metadata": {{}}}}'

5. Thread History (replace TOKEN):
curl -X GET "{backend_url}/api/threads?page=1&page_size=10" \\
  -H "Authorization: Bearer TOKEN" \\
  -H "Origin: {FRONTEND_ORIGIN}"
""")

def main():
    """Main test function"""
    print("Threadr Authentication Test Suite")
    print("=" * 50)
    
    try:
        # Find working backend
        backend_url = find_backend_url()
        
        # Track results
        results = []
        
        # Test registration
        email, password, token = test_registration(backend_url)
        results.append(("Registration", bool(email and password)))
        
        # Test login if registration failed
        if not token and email and password:
            token = test_login(backend_url, email, password)
            results.append(("Login", bool(token)))
        
        # Test invalid login
        if email:
            invalid_result = test_invalid_login(backend_url, email)
            results.append(("Invalid Login", invalid_result))
        
        # Test protected endpoint without token
        no_token_result = test_protected_endpoint_without_token(backend_url)
        results.append(("Protected Without Token", no_token_result))
        
        # Test authenticated endpoints
        if token:
            profile_result = test_user_profile(backend_url, token, email)
            results.append(("User Profile", profile_result))
            
            thread_save_result = test_thread_save(backend_url, token)
            results.append(("Thread Save", thread_save_result))
            
            thread_history_result = test_thread_history(backend_url, token)
            results.append(("Thread History", thread_history_result))
        
        # Print summary
        print(f"\n{'='*50}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*50}")
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "PASS" if success else "FAIL"
            print(f"{test_name:<25} {status}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Generate curl commands
        if email and password:
            generate_curl_commands(backend_url, email, password, token or "YOUR_TOKEN_HERE")
        
        return 0 if passed == total else 1
        
    except Exception as e:
        print(f"Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
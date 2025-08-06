#!/usr/bin/env python3
"""
Test script to verify user registration and login flow
"""

import requests
import json
import sys
import time
import uuid

# Backend URL
BACKEND_URL = "https://threadr-production.up.railway.app"
FRONTEND_ORIGIN = "https://threadr-plum.vercel.app"

def test_user_registration():
    """Test user registration with a unique email"""
    print("Testing user registration...")
    
    # Generate unique email for testing
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"test+{unique_id}@example.com"
    test_password = "TestPassword123!"
    
    url = f"{BACKEND_URL}/api/auth/register"
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_ORIGIN
    }
    
    payload = {
        "email": test_email,
        "password": test_password,
        "confirm_password": test_password
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response Text: {response.text}")
        
        if response.status_code == 201:
            print("   PASS: User registration successful")
            return test_email, test_password, response_data
        else:
            print(f"   FAIL: Registration failed with status {response.status_code}")
            return None, None, None
            
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: Registration request failed: {e}")
        return None, None, None

def test_user_login(email, password):
    """Test user login with valid credentials"""
    print(f"\nTesting user login with {email}...")
    
    url = f"{BACKEND_URL}/api/auth/login"
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
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response Text: {response.text}")
        
        # Check CORS headers
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        print(f"   CORS Origin: {cors_origin}")
        
        if response.status_code == 200:
            print("   PASS: Login successful")
            return True, response_data
        else:
            print(f"   FAIL: Login failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: Login request failed: {e}")
        return False, None

def test_authenticated_request(token):
    """Test an authenticated request using the login token"""
    print(f"\nTesting authenticated request...")
    
    url = f"{BACKEND_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": FRONTEND_ORIGIN
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            print("   PASS: Authenticated request successful")
            return True
        else:
            print(f"   FAIL: Authenticated request failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   FAIL: Authenticated request failed: {e}")
        return False

def main():
    """Run the complete registration and login test"""
    print("Threadr Registration and Login Test")
    print("="*50)
    
    # Test registration
    email, password, registration_data = test_user_registration()
    if not email:
        print("\nRegistration failed, cannot proceed with login test")
        return False
    
    # Wait a moment for the registration to be processed
    time.sleep(1)
    
    # Test login
    login_success, login_data = test_user_login(email, password)
    if not login_success:
        print("\nLogin failed")
        return False
    
    # Extract token and test authenticated request
    if login_data and 'access_token' in login_data:
        token = login_data['access_token']
        auth_success = test_authenticated_request(token)
        
        print(f"\nTest Results Summary:")
        print("="*50)
        print(f"Registration: PASS")
        print(f"Login:        PASS")
        print(f"Auth Request: {'PASS' if auth_success else 'FAIL'}")
        
        if auth_success:
            print("\nAll tests passed! Authentication flow is working correctly.")
        else:
            print("\nAuthenticated request failed, but login is working.")
            
        return True
    else:
        print("\nLogin succeeded but no access token returned")
        return False

def print_manual_test_commands():
    """Print manual curl commands for testing"""
    print("\nManual Registration Test:")
    print(f'curl -X POST "{BACKEND_URL}/api/auth/register" \\')
    print(f'  -H "Origin: {FRONTEND_ORIGIN}" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "your-test@example.com", "password": "YourPassword123!", "confirm_password": "YourPassword123!"}\' \\')
    print('  -v')
    
    print("\nManual Login Test (after registration):")
    print(f'curl -X POST "{BACKEND_URL}/api/auth/login" \\')
    print(f'  -H "Origin: {FRONTEND_ORIGIN}" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "your-test@example.com", "password": "YourPassword123!"}\' \\')
    print('  -v')

if __name__ == "__main__":
    try:
        success = main()
        print_manual_test_commands()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
#!/usr/bin/env python3
"""
Debug script to test registration endpoint and identify the specific issue
"""

import requests
import json
import sys

def test_registration():
    """Test registration endpoint with detailed error reporting"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    
    # Test data
    test_user = {
        "email": "test.user@example.com",
        "password": "TestPass123",
        "confirm_password": "TestPass123"
    }
    
    print("Testing Threadr Registration Endpoint")
    print("=" * 50)
    
    # 1. Test backend health
    print("\n1. Backend Health Check:")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {health_response.status_code}")
        health_data = health_response.json()
        print(f"   Health: {health_data.get('status', 'unknown')}")
        print(f"   Services: {health_data.get('services', {})}")
    except Exception as e:
        print(f"   ERROR: Health check failed: {e}")
        return
    
    # 2. Test registration endpoint
    print("\n2. Registration Endpoint Test:")
    print(f"   URL: {base_url}/api/auth/register")
    print(f"   Data: {json.dumps(test_user, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=test_user,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Raw Response: {response.text}")
            
        # Analyze the error
        if response.status_code == 400:
            print("\nERROR: HTTP 400 Bad Request - Validation or business logic error")
        elif response.status_code == 422:
            print("\nERROR: HTTP 422 Unprocessable Entity - Pydantic validation error")
        elif response.status_code == 500:
            print("\nERROR: HTTP 500 Internal Server Error - Server-side exception")
        elif response.status_code == 201:
            print("\nSUCCESS: Registration successful!")
        else:
            print(f"\nUNKNOWN: Unexpected status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed: {e}")
        return
    
    # 3. Test with different validation scenarios
    print("\n3. Testing Edge Cases:")
    
    # Test invalid email
    invalid_email_user = test_user.copy()
    invalid_email_user["email"] = "invalid-email"
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=invalid_email_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Invalid email: {response.status_code} - {response.text[:100]}")
    except:
        print("   Invalid email test failed")
    
    # Test weak password
    weak_password_user = test_user.copy()
    weak_password_user["password"] = "weak"
    weak_password_user["confirm_password"] = "weak"
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=weak_password_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Weak password: {response.status_code} - {response.text[:100]}")
    except:
        print("   Weak password test failed")
    
    # Test password mismatch
    mismatch_user = test_user.copy()
    mismatch_user["confirm_password"] = "DifferentPass123"
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=mismatch_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Password mismatch: {response.status_code} - {response.text[:100]}")
    except:
        print("   Password mismatch test failed")

if __name__ == "__main__":
    test_registration()
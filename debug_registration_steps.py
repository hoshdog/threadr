#!/usr/bin/env python3
"""
Step-by-step debugging of registration flow to identify exact failure point
"""

import requests
import json
import uuid
from datetime import datetime

def debug_registration_flow():
    """Debug each step of registration process"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    
    print("DEBUGGING THREADR REGISTRATION FLOW")
    print("=" * 50)
    
    # Generate unique email to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"test.{unique_id}@example.com"
    
    test_data = {
        "email": test_email,
        "password": "TestPass123",
        "confirm_password": "TestPass123"
    }
    
    print(f"\nTest Email: {test_email}")
    print(f"Password: {test_data['password']}")
    
    # Step 1: Verify backend is healthy
    print("\n1. Backend Health Check:")
    try:
        health_resp = requests.get(f"{base_url}/health", timeout=10)
        health_data = health_resp.json()
        
        print(f"   Status: {health_resp.status_code}")
        print(f"   Health: {health_data.get('status')}")
        print(f"   Redis: {health_data.get('services', {}).get('redis')}")
        print(f"   Database: {health_data.get('services', {}).get('database')}")
        print(f"   Routes: {health_data.get('services', {}).get('routes')}")
        
        if health_resp.status_code != 200:
            print("   ERROR: Backend not healthy - stopping")
            return
            
    except Exception as e:
        print(f"   ERROR: Health check failed: {e}")
        return
    
    # Step 2: Test auth endpoint exists
    print("\n2. Testing Auth Endpoint Availability:")
    try:
        # Try to access auth root - this should exist even if it returns an error
        auth_resp = requests.get(f"{base_url}/api/auth/", timeout=10)
        print(f"   Auth root status: {auth_resp.status_code}")
        
        if auth_resp.status_code == 404:
            print("   ERROR: Auth routes not properly registered")
            return
        elif auth_resp.status_code in [200, 405, 422]:
            print("   SUCCESS: Auth routes are registered")
        
    except Exception as e:
        print(f"   ERROR: Auth endpoint test failed: {e}")
    
    # Step 3: Test with minimal data first
    print("\n3. Testing with minimal data:")
    minimal_data = {
        "email": test_email,
        "password": "TestPass123",
        "confirm_password": "TestPass123"
    }
    
    try:
        resp = requests.post(
            f"{base_url}/api/auth/register",
            json=minimal_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {resp.status_code}")
        print(f"   Headers: {dict(resp.headers)}")
        
        try:
            resp_data = resp.json()
            print(f"   Response: {json.dumps(resp_data, indent=2)}")
        except:
            print(f"   Raw response: {resp.text}")
            
        # Analyze the response
        if resp.status_code == 400:
            print("\n   ANALYSIS: HTTP 400 - Business logic error")
            print("   - Could be Redis connection failure")
            print("   - Could be user storage failure") 
            print("   - Could be JWT token creation failure")
            print("   - Could be generic exception handler catching specific error")
        elif resp.status_code == 422:
            print("\n   ANALYSIS: HTTP 422 - Validation error")
            print("   - Pydantic model validation failed")
        elif resp.status_code == 500:
            print("\n   ANALYSIS: HTTP 500 - Server error")
            print("   - Unhandled exception in registration flow")
        elif resp.status_code == 201:
            print("\n   SUCCESS: Registration worked!")
        
    except Exception as e:
        print(f"   ERROR: Registration request failed: {e}")
    
    # Step 4: Test different edge cases to isolate issue
    print("\n4. Testing Edge Cases:")
    
    # Test with different email to rule out "user exists" error
    edge_cases = [
        {
            "name": "Different email",
            "data": {
                "email": f"different.{unique_id}@example.com",
                "password": "TestPass123",
                "confirm_password": "TestPass123"
            }
        },
        {
            "name": "Simpler password", 
            "data": {
                "email": f"simple.{unique_id}@example.com",
                "password": "Test123A",
                "confirm_password": "Test123A"
            }
        }
    ]
    
    for case in edge_cases:
        print(f"\n   Testing: {case['name']}")
        try:
            resp = requests.post(
                f"{base_url}/api/auth/register",
                json=case['data'],
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            print(f"     Status: {resp.status_code}")
            if resp.status_code != 201:
                try:
                    error_data = resp.json()
                    print(f"     Error: {error_data.get('detail', 'No detail')}")
                except:
                    print(f"     Raw: {resp.text[:100]}")
            else:
                print("     SUCCESS!")
        except Exception as e:
            print(f"     ERROR: {e}")

if __name__ == "__main__":
    debug_registration_flow()
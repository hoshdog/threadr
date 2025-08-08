#!/usr/bin/env python3
"""
Check backend environment variables and Redis connection
"""

import requests
import json

def check_backend_environment():
    """Check if required environment variables are set on backend"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    
    print("CHECKING BACKEND ENVIRONMENT")
    print("=" * 40)
    
    # 1. Check Redis connection via health endpoint
    print("\n1. Redis Connection Check:")
    try:
        health_resp = requests.get(f"{base_url}/health", timeout=10)
        health_data = health_resp.json()
        
        redis_status = health_data.get('services', {}).get('redis')
        redis_ping = health_data.get('services', {}).get('redis_ping')
        
        print(f"   Redis Available: {redis_status}")
        print(f"   Redis Ping: {redis_ping}")
        
        if not redis_status or redis_ping != "ok":
            print("   ERROR: Redis connection failed")
        else:
            print("   SUCCESS: Redis is working")
            
    except Exception as e:
        print(f"   ERROR: Could not check Redis: {e}")
    
    # 2. Test a simple endpoint that requires JWT creation
    print("\n2. Testing Session Status (no auth required):")
    try:
        session_resp = requests.get(f"{base_url}/api/auth/session/status", timeout=10)
        print(f"   Status: {session_resp.status_code}")
        
        if session_resp.status_code == 200:
            session_data = session_resp.json()
            print(f"   Authenticated: {session_data.get('authenticated')}")
            print(f"   Session IP: {session_data.get('session', {}).get('ip')}")
            print("   SUCCESS: Auth routes are functional")
        else:
            print(f"   ERROR: Session status failed: {session_resp.text}")
            
    except Exception as e:
        print(f"   ERROR: Session status check failed: {e}")
    
    # 3. Check if the issue is user already exists
    print("\n3. Testing with unique email:")
    import uuid
    unique_email = f"test.{uuid.uuid4().hex[:8]}@example.com"
    
    test_data = {
        "email": unique_email,
        "password": "TestPass123", 
        "confirm_password": "TestPass123"
    }
    
    try:
        reg_resp = requests.post(
            f"{base_url}/api/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Unique email: {unique_email}")
        print(f"   Status: {reg_resp.status_code}")
        
        if reg_resp.status_code == 201:
            print("   SUCCESS: Registration worked!")
            try:
                reg_data = reg_resp.json()
                print(f"   User created: {reg_data.get('user', {}).get('email')}")
                print(f"   Token type: {reg_data.get('token_type')}")
            except:
                pass
        elif reg_resp.status_code == 400:
            print("   ERROR: Still getting HTTP 400")
            try:
                error_data = reg_resp.json()
                print(f"   Error detail: {error_data.get('detail')}")
            except:
                print(f"   Raw response: {reg_resp.text}")
        else:
            print(f"   UNEXPECTED: Status {reg_resp.status_code}")
            print(f"   Response: {reg_resp.text}")
            
    except Exception as e:
        print(f"   ERROR: Registration test failed: {e}")

    # 4. Test password mismatch (should get 422 or proper error)
    print("\n4. Testing password mismatch validation:")
    mismatch_data = {
        "email": f"mismatch.{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestPass123",
        "confirm_password": "DifferentPass456"
    }
    
    try:
        resp = requests.post(
            f"{base_url}/api/auth/register",
            json=mismatch_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 422:
            print("   SUCCESS: Validation error as expected")
        elif resp.status_code == 500:
            print("   ERROR: Still getting HTTP 500 - validation issue in backend")
        elif resp.status_code == 400:
            print("   UNEXPECTED: Getting HTTP 400 instead of 422")
            
        try:
            error_data = resp.json()
            print(f"   Error: {error_data.get('detail', 'No detail')}")
        except:
            print(f"   Raw: {resp.text}")
            
    except Exception as e:
        print(f"   ERROR: Password mismatch test failed: {e}")

if __name__ == "__main__":
    check_backend_environment()
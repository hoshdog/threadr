#!/usr/bin/env python3
"""
Authentication diagnosis test - check what's failing in registration.
"""

import httpx
import json
import sys
import time

BASE_URL = "https://threadr-pw0s.onrender.com"

def test_auth_diagnosis():
    """Comprehensive authentication diagnosis."""
    print("🔍 AUTHENTICATION DIAGNOSIS")
    print("=" * 50)
    
    try:
        # Test 1: Check backend health
        print("\n1️⃣ Backend Health Check")
        health_response = httpx.get(f"{BASE_URL}/health", timeout=10.0)
        print(f"Status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            services = health_data.get("services", {})
            print(f"Redis: {services.get('redis', False)}")
            print(f"Database: {services.get('database', False)}")
            print(f"Routes: {services.get('routes', False)}")
        else:
            print(f"Health check failed: {health_response.text}")
            return
        
        # Test 2: Check auth endpoints exist
        print("\n2️⃣ Auth Endpoint Check")
        try:
            # Test empty registration (should get validation error, not 404)
            reg_response = httpx.post(f"{BASE_URL}/api/auth/register", 
                                    json={}, timeout=10.0)
            print(f"Empty registration status: {reg_response.status_code}")
            print(f"Response: {reg_response.text[:200]}")
        except Exception as e:
            print(f"Auth endpoint error: {e}")
        
        # Test 3: Test password validation
        print("\n3️⃣ Password Validation Test")
        try:
            test_data = {
                "email": "test@example.com",
                "password": "TestPass123",
                "confirm_password": "DifferentPass"
            }
            pwd_response = httpx.post(f"{BASE_URL}/api/auth/register",
                                    json=test_data, timeout=10.0)
            print(f"Password mismatch status: {pwd_response.status_code}")
            print(f"Response: {pwd_response.text[:200]}")
        except Exception as e:
            print(f"Password validation error: {e}")
        
        # Test 4: Test valid registration  
        print("\n4️⃣ Valid Registration Test")
        try:
            import secrets
            random_suffix = secrets.token_hex(4)
            test_data = {
                "email": f"test.{random_suffix}@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!"
            }
            valid_response = httpx.post(f"{BASE_URL}/api/auth/register",
                                      json=test_data, timeout=15.0)
            print(f"Valid registration status: {valid_response.status_code}")
            print(f"Response: {valid_response.text[:500]}")
            
            if valid_response.status_code == 201:
                print("✅ Registration SUCCESS!")
                return True
            else:
                print("❌ Registration FAILED")
                
        except Exception as e:
            print(f"Valid registration error: {e}")
        
        # Test 5: Check diagnostic endpoints (if they exist)
        print("\n5️⃣ Diagnostic Endpoint Check")
        try:
            diag_response = httpx.get(f"{BASE_URL}/api/auth/debug/storage", timeout=10.0)
            print(f"Storage diagnostic status: {diag_response.status_code}")
            if diag_response.status_code == 200:
                print(f"Storage info: {diag_response.text}")
            else:
                print(f"Storage diagnostic response: {diag_response.text[:200]}")
        except Exception as e:
            print(f"Diagnostic endpoint error: {e}")
    
    except Exception as e:
        print(f"Overall test error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("🚀 Starting Authentication Diagnosis")
    success = test_auth_diagnosis()
    
    print("\n" + "="*50)
    if success:
        print("🎉 AUTHENTICATION WORKING!")
    else:
        print("🔧 AUTHENTICATION NEEDS FIXES")
        print("\nNext steps:")
        print("1. Check authentication service logs")
        print("2. Verify database user table exists")
        print("3. Test Redis connectivity")
        print("4. Check import paths for auth service")
    print("="*50)
    
    sys.exit(0 if success else 1)
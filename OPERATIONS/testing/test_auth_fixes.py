#!/usr/bin/env python3
"""
Test script to verify authentication registration fixes
Tests storage components, registration flow, and error handling
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL - Updated for Render.com deployment
BASE_URL = "https://threadr-pw0s.onrender.com"

async def test_auth_fixes():
    """Test authentication fixes comprehensively"""
    async with aiohttp.ClientSession() as session:
        
        print("=" * 70)
        print("TESTING AUTHENTICATION REGISTRATION FIXES")
        print("=" * 70)
        
        # Test 1: Storage Components Diagnostic
        print("\n1. TESTING STORAGE COMPONENTS DIAGNOSTIC")
        print("-" * 50)
        
        try:
            async with session.get(f"{BASE_URL}/api/auth/debug/storage") as resp:
                print(f"Status Code: {resp.status}")
                print(f"Expected: 200 (OK)")
                
                if resp.status == 200:
                    response_data = await resp.json()
                    print(f"Storage Diagnostics:")
                    storage_info = response_data.get("storage_diagnostics", {})
                    print(f"  Redis Manager: {storage_info.get('redis_manager', 'Unknown')}")
                    print(f"  Redis Client: {storage_info.get('redis_client', 'Unknown')}")
                    print(f"  Redis Executor: {storage_info.get('redis_executor', 'Unknown')}")
                    print(f"  PostgreSQL DBUser: {storage_info.get('postgres_dbuser', 'Unknown')}")
                    print(f"  PostgreSQL get_async_db: {storage_info.get('postgres_get_async_db', 'Unknown')}")
                    print(f"  PostgreSQL Connection: {storage_info.get('postgres_connection', 'Unknown')}")
                    
                    if storage_info.get('redis_error'):
                        print(f"  Redis Error: {storage_info['redis_error']}")
                    if storage_info.get('postgres_error'):
                        print(f"  PostgreSQL Error: {storage_info['postgres_error']}")
                else:
                    response_text = await resp.text()
                    print(f"Diagnostic Failed: {response_text}")
                    
        except Exception as e:
            print(f"Storage diagnostic request failed: {e}")
        
        # Test 2: Password Mismatch (Should return HTTP 400, not 500)
        print("\n\n2. TESTING PASSWORD MISMATCH ERROR HANDLING")
        print("-" * 50)
        
        test1_data = {
            "email": "test1@example.com",
            "password": "ValidPassword123",
            "confirm_password": "DifferentPassword123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/auth/register", 
                                  json=test1_data,
                                  headers={"Content-Type": "application/json"}) as resp:
                print(f"Status Code: {resp.status}")
                print(f"Expected: 400 (Bad Request)")
                print(f"Issue: {'FIXED' if resp.status == 400 else 'EXISTS - HTTP 500 Error'}")
                
                response_text = await resp.text()
                try:
                    response_data = json.loads(response_text)
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"Raw Response: {response_text}")
                    
        except Exception as e:
            print(f"Request failed: {e}")
        
        # Test 3: Valid Registration (Should succeed with new storage methods)
        print("\n\n3. TESTING VALID REGISTRATION WITH ENHANCED STORAGE")
        print("-" * 50)
        
        test2_data = {
            "email": f"validuser_{int(datetime.now().timestamp())}@example.com",
            "password": "ValidPassword123",
            "confirm_password": "ValidPassword123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/auth/register", 
                                  json=test2_data,
                                  headers={"Content-Type": "application/json"}) as resp:
                print(f"Status Code: {resp.status}")
                print(f"Expected: 201 (Created)")
                print(f"Issue: {'FIXED' if resp.status == 201 else 'EXISTS - Registration Failed'}")
                
                response_text = await resp.text()
                try:
                    response_data = json.loads(response_text)
                    if resp.status == 201:
                        print(f"SUCCESS: User registered with access_token")
                        print(f"User ID: {response_data.get('user', {}).get('user_id', 'N/A')}")
                        print(f"Email: {response_data.get('user', {}).get('email', 'N/A')}")
                        print(f"Token Type: {response_data.get('token_type', 'N/A')}")
                    else:
                        print(f"Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"Raw Response: {response_text}")
                    
        except Exception as e:
            print(f"Request failed: {e}")
        
        # Test 4: Duplicate Email Registration (Should return HTTP 409)
        print("\n\n4. TESTING DUPLICATE EMAIL REGISTRATION")
        print("-" * 50)
        
        duplicate_email = "duplicate@example.com"
        duplicate_data = {
            "email": duplicate_email,
            "password": "ValidPassword123",
            "confirm_password": "ValidPassword123"
        }
        
        # First registration
        try:
            async with session.post(f"{BASE_URL}/api/auth/register", 
                                  json=duplicate_data,
                                  headers={"Content-Type": "application/json"}) as resp:
                first_status = resp.status
                print(f"First Registration Status: {first_status}")
                
                if first_status == 201:
                    print("First registration successful, attempting duplicate...")
                    
                    # Second registration with same email
                    async with session.post(f"{BASE_URL}/api/auth/register", 
                                          json=duplicate_data,
                                          headers={"Content-Type": "application/json"}) as resp2:
                        print(f"Duplicate Registration Status: {resp2.status}")
                        print(f"Expected: 409 (Conflict)")
                        print(f"Working: {'YES' if resp2.status == 409 else 'NO'}")
                        
                        response_text = await resp2.text()
                        try:
                            response_data = json.loads(response_text)
                            print(f"Response: {json.dumps(response_data, indent=2)}")
                        except:
                            print(f"Raw Response: {response_text}")
                else:
                    print(f"First registration failed with status {first_status}, skipping duplicate test")
                    
        except Exception as e:
            print(f"Duplicate email test failed: {e}")

        print("\n" + "=" * 70)
        print("AUTHENTICATION FIX TEST COMPLETE")
        print("=" * 70)
        print("\nSUMMARY:")
        print("1. Storage diagnostics should show available storage methods")
        print("2. Password mismatch should return HTTP 400 (not 500)")
        print("3. Valid registration should return HTTP 201 with tokens")
        print("4. Duplicate email should return HTTP 409 (conflict)")

if __name__ == "__main__":
    asyncio.run(test_auth_fixes())
#!/usr/bin/env python3
"""
Debug script to test authentication registration issues
Tests both password mismatch (Issue 1) and valid registration (Issue 2)
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL - Updated for Render.com deployment
BASE_URL = "https://threadr-pw0s.onrender.com"

async def test_registration_issues():
    """Test both registration issues"""
    async with aiohttp.ClientSession() as session:
        
        print("=" * 60)
        print("TESTING AUTHENTICATION REGISTRATION ISSUES")
        print("=" * 60)
        
        # Test Issue 1: Password Mismatch (Should return HTTP 400, not 500)
        print("\n1. TESTING ISSUE 1: Password Mismatch Error Handling")
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
        
        # Test Issue 2: Valid Registration (Should succeed, not return HTTP 400)
        print("\n\n2. TESTING ISSUE 2: Valid Registration Failure")
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
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"Raw Response: {response_text}")
                    
        except Exception as e:
            print(f"Request failed: {e}")
        
        # Test Edge Case: Weak Password (Should return HTTP 400 with proper validation message)
        print("\n\n3. TESTING EDGE CASE: Weak Password Validation")
        print("-" * 50)
        
        test3_data = {
            "email": "test3@example.com", 
            "password": "weak",
            "confirm_password": "weak"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/auth/register", 
                                  json=test3_data,
                                  headers={"Content-Type": "application/json"}) as resp:
                print(f"Status Code: {resp.status}")
                print(f"Expected: 400 (Bad Request)")
                print(f"Working: {'YES' if resp.status == 400 else 'NO'}")
                
                response_text = await resp.text()
                try:
                    response_data = json.loads(response_text)
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"Raw Response: {response_text}")
                    
        except Exception as e:
            print(f"Request failed: {e}")

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_registration_issues())
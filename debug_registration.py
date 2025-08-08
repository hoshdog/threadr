#!/usr/bin/env python3
"""
Debug Registration Issues - Test specific validation scenarios
"""

import asyncio
import aiohttp
import json
import secrets
import time

async def test_registration_scenarios():
    """Test different registration scenarios to identify the exact issue"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Test data variations
        test_scenarios = [
            {
                "name": "Valid Strong Password",
                "data": {
                    "email": f"test-{int(time.time())}-{secrets.token_hex(4)}@example.com",
                    "password": "StrongPass123!",
                    "confirm_password": "StrongPass123!"
                }
            },
            {
                "name": "Simple Valid Password",
                "data": {
                    "email": f"test-{int(time.time())}-{secrets.token_hex(4)}@example.com",
                    "password": "TestPass1",
                    "confirm_password": "TestPass1"
                }
            },
            {
                "name": "Password Mismatch",
                "data": {
                    "email": f"test-{int(time.time())}-{secrets.token_hex(4)}@example.com",
                    "password": "TestPass123",
                    "confirm_password": "DifferentPass123"
                }
            },
            {
                "name": "Weak Password",
                "data": {
                    "email": f"test-{int(time.time())}-{secrets.token_hex(4)}@example.com",
                    "password": "weakpass",
                    "confirm_password": "weakpass"
                }
            },
            {
                "name": "Missing Fields",
                "data": {
                    "email": f"test-{int(time.time())}-{secrets.token_hex(4)}@example.com",
                    "password": "TestPass123"
                    # Missing confirm_password
                }
            }
        ]
        
        print("=== REGISTRATION DEBUG TESTS ===\n")
        
        for scenario in test_scenarios:
            print(f"Testing: {scenario['name']}")
            print(f"Data: {json.dumps(scenario['data'], indent=2)}")
            
            try:
                async with session.post(
                    f"{base_url}/api/auth/register",
                    json=scenario['data'],
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    status = response.status
                    print(f"Status Code: {status}")
                    
                    try:
                        response_data = await response.json()
                        print(f"Response: {json.dumps(response_data, indent=2)}")
                    except:
                        response_text = await response.text()
                        print(f"Response Text: {response_text}")
                    
                    if status == 201:
                        print("SUCCESS - Registration worked!")
                    elif status == 400:
                        print("BAD REQUEST - Validation error")
                    elif status == 409:
                        print("CONFLICT - User already exists")
                    elif status == 422:
                        print("VALIDATION ERROR - Pydantic validation failed")
                    else:
                        print(f"OTHER ERROR - Status {status}")
                        
            except Exception as e:
                print(f"EXCEPTION: {str(e)}")
            
            print("-" * 50)
            
        # Test with exact data from the test suite
        print("\n=== TESTING WITH EXACT TEST SUITE DATA ===")
        
        random_id = secrets.token_hex(4)
        timestamp = int(time.time())
        
        exact_test_data = {
            "email": f"test-{timestamp}-{random_id}@example.com",
            "password": f"TestPass123!{random_id}",
            "confirm_password": f"TestPass123!{random_id}"
        }
        
        print(f"Exact Test Data: {json.dumps(exact_test_data, indent=2)}")
        
        try:
            async with session.post(
                f"{base_url}/api/auth/register",
                json=exact_test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                status = response.status
                print(f"Status Code: {status}")
                
                try:
                    response_data = await response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                except:
                    response_text = await response.text()
                    print(f"Response Text: {response_text}")
                
                if status == 201:
                    print("SUCCESS - Registration worked with exact test suite data!")
                else:
                    print(f"FAILED - Even exact test suite data failed with status {status}")
                    
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_registration_scenarios())
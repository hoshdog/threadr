#!/usr/bin/env python3
"""
Test specific validation issues in isolation
"""

import asyncio
import aiohttp
import json

BASE_URL = "https://threadr-pw0s.onrender.com"

async def test_specific_validations():
    async with aiohttp.ClientSession() as session:
        
        print("TESTING SPECIFIC VALIDATION ISSUES")
        print("=" * 50)
        
        # Test 1: Only test password mismatch with otherwise perfect data
        print("\n1. Testing ONLY password mismatch (everything else perfect):")
        test1_data = {
            "email": "perfect@gmail.com",  # Simple, standard email
            "password": "Perfect123Pass!",  # Strong password 
            "confirm_password": "Different123!"  # Different password
        }
        
        async with session.post(f"{BASE_URL}/api/auth/register", json=test1_data) as resp:
            print(f"   Status: {resp.status}")
            try:
                response_data = await resp.json()
                print(f"   Response: {response_data}")
            except:
                response_text = await resp.text()
                print(f"   Raw: {response_text}")
        
        # Test 2: Test with empty passwords (different validation path)
        print("\n2. Testing empty passwords:")
        test2_data = {
            "email": "test@gmail.com",
            "password": "",  # Empty
            "confirm_password": ""  # Empty
        }
        
        async with session.post(f"{BASE_URL}/api/auth/register", json=test2_data) as resp:
            print(f"   Status: {resp.status}")
            try:
                response_data = await resp.json()
                print(f"   Response: {response_data}")
            except:
                response_text = await resp.text()
                print(f"   Raw: {response_text}")
        
        # Test 3: Test with invalid email format
        print("\n3. Testing invalid email:")
        test3_data = {
            "email": "not-an-email",
            "password": "ValidPass123!",
            "confirm_password": "ValidPass123!"
        }
        
        async with session.post(f"{BASE_URL}/api/auth/register", json=test3_data) as resp:
            print(f"   Status: {resp.status}")
            try:
                response_data = await resp.json()
                print(f"   Response: {response_data}")
            except:
                response_text = await resp.text()
                print(f"   Raw: {response_text}")

        # Test 4: Test minimal but completely valid data
        print("\n4. Testing minimal valid registration:")
        test4_data = {
            "email": f"valid{int(asyncio.get_event_loop().time())}@test.com",
            "password": "ValidPass123",
            "confirm_password": "ValidPass123"
        }
        
        async with session.post(f"{BASE_URL}/api/auth/register", json=test4_data) as resp:
            print(f"   Status: {resp.status}")
            try:
                response_data = await resp.json()
                print(f"   Response: {response_data}")
            except:
                response_text = await resp.text()
                print(f"   Raw: {response_text}")

if __name__ == "__main__":
    asyncio.run(test_specific_validations())
#!/usr/bin/env python3
"""
Test auth service health and capabilities
"""

import asyncio
import aiohttp
import json

BASE_URL = "https://threadr-pw0s.onrender.com"

async def test_auth_health():
    async with aiohttp.ClientSession() as session:
        print("Testing auth service health...")
        
        # Test 1: Get auth router status
        try:
            async with session.get(f"{BASE_URL}/api/auth/") as resp:
                print(f"Auth Router Status: {resp.status}")
                try:
                    data = await resp.json()
                    print(f"Auth Router Response: {data}")
                except:
                    text = await resp.text()
                    print(f"Auth Router Raw: {text}")
        except Exception as e:
            print(f"Auth router test failed: {e}")
        
        # Test 2: Try to trigger our model validation in the simplest way possible
        # Send a request that should hit field validation before any service logic
        print("\nTesting password field validation (empty password):")
        try:
            test_data = {
                "email": "test@example.com",
                "password": "",  # This should trigger field validation
                "confirm_password": ""
            }
            async with session.post(f"{BASE_URL}/api/auth/register", json=test_data) as resp:
                print(f"Empty password status: {resp.status}")
                if resp.status == 422:
                    print("✓ Field validation is working")
                else:
                    print("✗ Field validation might not be working")
        except Exception as e:
            print(f"Field validation test failed: {e}")
        
        # Test 3: Try a completely malformed request to see if we can get any different response
        print("\nTesting malformed request:")
        try:
            async with session.post(f"{BASE_URL}/api/auth/register", json={"invalid": "data"}) as resp:
                print(f"Malformed request status: {resp.status}")
                try:
                    data = await resp.json()
                    print(f"Malformed request response: {data}")
                except:
                    text = await resp.text()
                    print(f"Malformed request raw: {text[:200]}")
        except Exception as e:
            print(f"Malformed request test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_health())
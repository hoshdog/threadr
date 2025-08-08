#!/usr/bin/env python3
"""
Check backend health and get logs
"""

import asyncio
import aiohttp
import json

BASE_URL = "https://threadr-pw0s.onrender.com"

async def check_health():
    async with aiohttp.ClientSession() as session:
        print("Checking backend health...")
        
        try:
            async with session.get(f"{BASE_URL}/health") as resp:
                print(f"Health Status: {resp.status}")
                response_text = await resp.text()
                try:
                    health_data = json.loads(response_text)
                    print(f"Health Response: {json.dumps(health_data, indent=2)}")
                except:
                    print(f"Raw Health Response: {response_text}")
        except Exception as e:
            print(f"Health check failed: {e}")
        
        # Also test a simple endpoint
        try:
            async with session.get(f"{BASE_URL}/") as resp:
                print(f"\nRoot endpoint Status: {resp.status}")
                root_text = await resp.text()[:500]  # First 500 chars
                print(f"Root Response: {root_text}")
        except Exception as e:
            print(f"Root endpoint failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_health())
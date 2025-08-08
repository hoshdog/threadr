#!/usr/bin/env python3
"""
Quick deployment status check for authentication fixes
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import time

BASE_URL = "https://threadr-pw0s.onrender.com"

async def check_deployment_status():
    """Check if deployment has the latest changes"""
    async with aiohttp.ClientSession() as session:
        
        print("DEPLOYMENT STATUS CHECK")
        print("=" * 40)
        
        # 1. Health Check
        print("\n1. Health Check:")
        try:
            async with session.get(f"{BASE_URL}/health") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    print(f"   Status: {health_data.get('status', 'Unknown')}")
                    print(f"   Timestamp: {health_data.get('timestamp', 'Unknown')}")
                    print(f"   Services: {health_data.get('services', {})}")
                else:
                    print(f"   Health check failed: {resp.status}")
        except Exception as e:
            print(f"   Health check error: {e}")
        
        # 2. Storage Diagnostic (New endpoint)
        print("\n2. Storage Diagnostic (New Feature):")
        try:
            async with session.get(f"{BASE_URL}/api/auth/debug/storage") as resp:
                if resp.status == 200:
                    print("   SUCCESS: DEPLOYMENT UPDATED - New endpoint available")
                    storage_data = await resp.json()
                    diagnostics = storage_data.get("storage_diagnostics", {})
                    print(f"   Redis Manager: {diagnostics.get('redis_manager', 'Unknown')}")
                    print(f"   Redis Client: {diagnostics.get('redis_client', 'Unknown')}")
                    print(f"   Redis Executor: {diagnostics.get('redis_executor', 'Unknown')}")
                    print(f"   PostgreSQL: DBUser={diagnostics.get('postgres_dbuser', 'Unknown')}, get_async_db={diagnostics.get('postgres_get_async_db', 'Unknown')}")
                elif resp.status == 404:
                    print("   FAILED: DEPLOYMENT NOT UPDATED - Endpoint not found")
                else:
                    print(f"   WARNING: Endpoint exists but failed: {resp.status}")
                    response_text = await resp.text()
                    print(f"   Response: {response_text[:200]}...")
        except Exception as e:
            print(f"   Storage diagnostic error: {e}")
        
        # 3. Quick Registration Test
        print("\n3. Registration Test:")
        test_data = {
            "email": f"deploytest_{int(time.time())}@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/auth/register", 
                                  json=test_data,
                                  headers={"Content-Type": "application/json"}) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 201:
                    print("   SUCCESS: Registration working!")
                elif resp.status == 400:
                    response_data = await resp.json()
                    detail = response_data.get('detail', 'Unknown error')
                    if detail == "Registration failed":
                        print("   FAILED: Still has storage issues")
                    else:
                        print(f"   WARNING: Different validation error: {detail}")
                elif resp.status == 500:
                    print("   FAILED: Still getting 500 errors")
                else:
                    print(f"   WARNING: Unexpected status: {resp.status}")
                    
        except Exception as e:
            print(f"   Registration test error: {e}")
        
        print("\n" + "=" * 40)
        print("Status check complete")

if __name__ == "__main__":
    asyncio.run(check_deployment_status())
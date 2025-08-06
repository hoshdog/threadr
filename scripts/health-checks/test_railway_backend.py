#!/usr/bin/env python3
"""Test Railway backend endpoints to diagnose health issues"""

import httpx
import json
import asyncio
import sys
from datetime import datetime

# Fix Windows encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BACKEND_URL = "https://threadr-production.up.railway.app"

async def test_endpoints():
    """Test all critical backend endpoints"""
    
    print(f"🔍 Testing Railway Backend: {BACKEND_URL}")
    print(f"⏰ Time: {datetime.now().isoformat()}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint
        print("1️⃣ Testing /health endpoint...")
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 503:
                print("   ⚠️ Backend is degraded but running")
            print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test readiness endpoint
        print("2️⃣ Testing /readiness endpoint...")
        try:
            response = await client.get(f"{BACKEND_URL}/readiness")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test root endpoint
        print("3️⃣ Testing / endpoint...")
        try:
            response = await client.get(f"{BACKEND_URL}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test API generate endpoint (without auth)
        print("4️⃣ Testing /api/generate endpoint (no auth)...")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/generate",
                json={"content": "Test thread"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Auth required (expected)")
            print(f"   Response: {response.json()}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test with API key
        print("5️⃣ Testing /api/generate with API key...")
        api_key = "test-api-key"  # Replace with actual key
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/generate",
                json={"content": "Test thread generation"},
                headers={"X-API-Key": api_key}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ API working!")
            print(f"   Response: {response.json()[:200] if response.text else 'Empty'}...\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")

    print("\n📊 Summary:")
    print("- Check if backend URL is correct")
    print("- Verify environment variables in Railway")
    print("- Look for 'degraded' status (Redis/DB not connected)")
    print("- Ensure API keys match between frontend and backend")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
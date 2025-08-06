#!/usr/bin/env python3
"""Quick health check for Railway backend"""

import httpx
import asyncio
import json
import sys

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def check_health():
    """Check backend health status"""
    url = "https://threadr-production.up.railway.app"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Check health endpoint
            print(f"🔍 Checking {url}/health...")
            response = await client.get(f"{url}/health")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Status: {data.get('status', 'unknown')}")
                print(f"🔧 Services: {json.dumps(data.get('services', {}), indent=2)}")
                
                # Test generate endpoint
                print(f"\n🧪 Testing {url}/api/generate...")
                test_response = await client.post(
                    f"{url}/api/generate",
                    json={"content": "Test thread generation from quick check"}
                )
                print(f"📊 Generate Status: {test_response.status_code}")
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"✅ Success! Generated {len(result.get('tweets', []))} tweets")
                else:
                    print(f"❌ Error: {test_response.text}")
                    
            elif response.status_code == 503:
                data = response.json()
                print(f"⚠️ Service Degraded: {data.get('status', 'unknown')}")
                print(f"🔧 Services: {json.dumps(data.get('services', {}), indent=2)}")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except httpx.ConnectError:
            print(f"🔴 Cannot connect to backend - deployment may still be in progress")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Railway Backend Quick Health Check")
    print("=" * 60)
    asyncio.run(check_health())
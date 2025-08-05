#!/usr/bin/env python3
"""Monitor Railway deployment until healthy"""

import httpx
import asyncio
import sys
from datetime import datetime
import json

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BACKEND_URL = "https://threadr-production.up.railway.app"
CHECK_INTERVAL = 30  # seconds

async def check_deployment():
    """Check if deployment is healthy"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Check health endpoint
            response = await client.get(f"{BACKEND_URL}/health")
            data = response.json()
            
            status = data.get("status", "unknown")
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if status == "healthy":
                print(f"\n✅ [{timestamp}] Deployment SUCCESSFUL!")
                print(f"   Status: {status}")
                print(f"   Services: {json.dumps(data.get('services', {}), indent=2)}")
                
                # Test generate endpoint
                print("\n🧪 Testing /api/generate endpoint...")
                test_response = await client.post(
                    f"{BACKEND_URL}/api/generate",
                    json={"content": "Test thread generation"}
                )
                if test_response.status_code == 200:
                    print("   ✅ Thread generation working!")
                    result = test_response.json()
                    print(f"   Generated {len(result.get('tweets', []))} tweets")
                else:
                    print(f"   ❌ Generate returned: {test_response.status_code}")
                
                return True
            else:
                print(f"⏳ [{timestamp}] Status: {status} - Waiting for deployment...")
                if response.status_code == 503:
                    services = data.get("services", {})
                    issues = [k for k, v in services.items() if not v]
                    if issues:
                        print(f"   Issues: {', '.join(issues)}")
                return False
                
        except httpx.ConnectError:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"🔄 [{timestamp}] Cannot connect - deployment in progress...")
            return False
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"❌ [{timestamp}] Error: {e}")
            return False

async def monitor_deployment():
    """Monitor deployment until healthy"""
    print("🚀 Monitoring Railway Deployment")
    print(f"📍 URL: {BACKEND_URL}")
    print(f"⏱️  Checking every {CHECK_INTERVAL} seconds...")
    print("-" * 50)
    
    attempt = 0
    while True:
        attempt += 1
        print(f"\n🔍 Check #{attempt}")
        
        if await check_deployment():
            print("\n🎉 Deployment Complete and Healthy!")
            print("\n📋 Next Steps:")
            print("1. Deploy Next.js to Vercel")
            print("2. Configure environment variables")
            print("3. Test end-to-end functionality")
            break
        
        print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds before next check...")
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("=" * 50)
    print("   Railway Deployment Monitor")
    print("=" * 50)
    
    try:
        asyncio.run(monitor_deployment())
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
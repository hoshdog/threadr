#!/usr/bin/env python3
"""Monitor Railway deployment after Dockerfile removal"""

import httpx
import asyncio
import json
import sys
from datetime import datetime
import time

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BACKEND_URL = "https://threadr-production.up.railway.app"

async def check_deployment():
    """Check if new deployment is active"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Check root endpoint
            print("\n🔍 Checking root endpoint...")
            response = await client.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check what deployment we have
                if data.get("app") == "Threadr Minimal":
                    print("✅ SUCCESS! Running main_minimal.py")
                    print(f"   Version: {data.get('version')}")
                    print(f"   Deployment: {data.get('deployment', 'main_minimal.py')}")
                    return True
                elif data.get("message") == "Threadr API" and data.get("version") == "2.0.0":
                    print("❌ Still running OLD main.py")
                    print("   Waiting for new deployment...")
                    return False
                else:
                    print("❓ Unknown deployment")
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    return False
            else:
                print(f"⚠️  Status: {response.status_code}")
                return False
                
        except httpx.ConnectError:
            print("🔄 Cannot connect - deployment in progress...")
            return False
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            return False

async def test_endpoints():
    """Test if endpoints are working"""
    print("\n🧪 Testing endpoints...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health: {data.get('status')} - App: {data.get('app', 'unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health error: {e}")
            
        # Test generate
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/generate",
                json={"content": "Test nixpacks deployment"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Generate: Working! Generated {len(data.get('tweets', []))} tweets")
            else:
                print(f"❌ Generate failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Generate error: {e}")

async def monitor_deployment():
    """Monitor until deployment succeeds"""
    print("=" * 60)
    print("🚀 Railway Nixpacks Deployment Monitor")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {BACKEND_URL}")
    print("\nMonitoring deployment (checking every 30 seconds)...")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    attempt = 0
    start_time = time.time()
    
    while True:
        attempt += 1
        elapsed = int(time.time() - start_time)
        print(f"\n📍 Check #{attempt} - Elapsed: {elapsed}s")
        
        if await check_deployment():
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("   Railway is now using nixpacks.toml")
            print("   main_minimal.py is deployed")
            
            await test_endpoints()
            
            print("\n✅ Next Steps:")
            print("1. Deploy Next.js to Vercel")
            print("2. Configure environment variables")
            print("3. Test end-to-end functionality")
            break
            
        if elapsed > 600:  # 10 minutes timeout
            print("\n⏱️ Timeout after 10 minutes")
            print("   Check Railway dashboard for build errors")
            print("   Consider using alternative deployment (Render.com)")
            break
            
        print("\n⏳ Waiting 30 seconds...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_deployment())
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
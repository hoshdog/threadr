#!/usr/bin/env python3
"""Monitor Railway deployment after TOML fix"""

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
    """Check deployment status"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Check root endpoint
            response = await client.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check deployment type
                if data.get("app") == "Threadr Minimal":
                    return "success", data
                elif data.get("message") == "Threadr API" and data.get("version") == "2.0.0":
                    return "old", data
                else:
                    return "unknown", data
            else:
                return "error", {"status_code": response.status_code}
                
        except httpx.ConnectError:
            return "deploying", {"message": "Cannot connect - deployment in progress"}
        except Exception as e:
            return "error", {"error": str(e)}

async def test_functionality():
    """Test if main_minimal.py endpoints work"""
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            results.append({
                "endpoint": "/health",
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            })
        except Exception as e:
            results.append({"endpoint": "/health", "error": str(e)})
            
        # Test generate
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/generate",
                json={"content": "Testing TOML fix deployment"}
            )
            results.append({
                "endpoint": "/api/generate",
                "status": response.status_code,
                "success": response.status_code == 200
            })
        except Exception as e:
            results.append({"endpoint": "/api/generate", "error": str(e)})
            
    return results

async def monitor_deployment():
    """Monitor deployment with detailed status"""
    print("=" * 60)
    print("🚀 Railway Deployment Monitor - TOML Fix")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {BACKEND_URL}")
    print("\n📋 What we fixed:")
    print("   - Changed [providers] to providers = ['python']")
    print("   - Added Python 3.11 configuration")
    print("   - Fixed TOML syntax error")
    print("\nMonitoring deployment...")
    print("-" * 60)
    
    attempt = 0
    start_time = time.time()
    last_status = None
    
    while True:
        attempt += 1
        elapsed = int(time.time() - start_time)
        
        print(f"\n🔍 Check #{attempt} - {datetime.now().strftime('%H:%M:%S')} (elapsed: {elapsed}s)")
        
        status, data = await check_deployment()
        
        if status != last_status:
            print("   📌 Status changed!")
            last_status = status
        
        if status == "success":
            print("   ✅ SUCCESS! main_minimal.py is deployed!")
            print(f"   App: {data.get('app')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Deployment: {data.get('deployment', 'main_minimal.py')}")
            
            print("\n🧪 Testing functionality...")
            test_results = await test_functionality()
            for result in test_results:
                if "error" in result:
                    print(f"   ❌ {result['endpoint']}: {result['error']}")
                else:
                    status_icon = "✅" if result.get('status') == 200 else "❌"
                    print(f"   {status_icon} {result['endpoint']}: {result.get('status')}")
                    if result.get('data'):
                        app_type = result['data'].get('app', 'unknown')
                        print(f"      App type: {app_type}")
            
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("\n📌 Next Steps:")
            print("1. Deploy Next.js to Vercel")
            print("2. Configure environment variables")
            print("3. Test full stack functionality")
            break
            
        elif status == "old":
            print("   ⏳ Still running OLD deployment (main.py)")
            print("   Waiting for new deployment to activate...")
            
        elif status == "deploying":
            print("   🔄 Deployment in progress...")
            print("   Railway is building with fixed nixpacks.toml")
            
        elif status == "error":
            print(f"   ❌ Error: {data}")
            
        else:
            print(f"   ❓ Unknown status: {data}")
        
        # Timeout after 15 minutes
        if elapsed > 900:
            print("\n⏱️ Timeout after 15 minutes")
            print("\n💡 Troubleshooting steps:")
            print("1. Check Railway dashboard for build logs")
            print("2. Look for any error messages")
            print("3. Try redeploying from Railway dashboard")
            print("4. Consider using railway.json instead")
            break
            
        print("\n⏳ Waiting 30 seconds...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    print("Railway TOML Fix Monitor")
    print("This will check every 30 seconds until deployment succeeds")
    print("Press Ctrl+C to stop\n")
    
    try:
        asyncio.run(monitor_deployment())
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
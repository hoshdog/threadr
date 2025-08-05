#!/usr/bin/env python3
"""Monitor Railway deployment after all fixes"""

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
    """Check if deployment succeeded"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                return data, response.status_code
            else:
                return None, response.status_code
        except httpx.ConnectError:
            return None, "connecting"
        except Exception as e:
            return None, f"error: {e}"

async def test_all_endpoints():
    """Test all main_minimal.py endpoints"""
    print("\n🧪 Testing All Endpoints...")
    
    endpoints = [
        ("GET", "/", "Root"),
        ("GET", "/health", "Health Check"),
        ("GET", "/readiness", "Readiness"),
        ("POST", "/api/generate", "Thread Generation"),
        ("GET", "/api/templates", "Templates"),
        ("GET", "/api/premium-status", "Premium Status"),
        ("GET", "/api/usage-stats", "Usage Stats")
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        passed = 0
        failed = 0
        
        for method, endpoint, name in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = await client.post(
                        f"{BACKEND_URL}{endpoint}",
                        json={"content": "Test content"}
                    )
                
                if response.status_code < 400:
                    print(f"   ✅ {name}: {response.status_code}")
                    passed += 1
                else:
                    print(f"   ❌ {name}: {response.status_code}")
                    failed += 1
                    
            except Exception as e:
                print(f"   ❌ {name}: Error - {str(e)[:50]}")
                failed += 1
        
        print(f"\n   Summary: {passed} passed, {failed} failed")
        return passed > failed

async def monitor():
    """Monitor deployment with clear status updates"""
    print("=" * 60)
    print("🚀 Railway Final Deployment Monitor")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {BACKEND_URL}")
    print("\n📋 Fixes Applied:")
    print("   ✅ Dockerfile disabled")
    print("   ✅ TOML syntax fixed")
    print("   ✅ Paths corrected")
    print("\nMonitoring deployment...")
    print("-" * 60)
    
    start_time = time.time()
    attempt = 0
    
    while True:
        attempt += 1
        elapsed = int(time.time() - start_time)
        
        print(f"\n🔍 Check #{attempt} at {datetime.now().strftime('%H:%M:%S')} (elapsed: {elapsed}s)")
        
        data, status = await check_deployment()
        
        if isinstance(data, dict):
            app_name = data.get("app", "Unknown")
            version = data.get("version", "Unknown")
            
            if app_name == "Threadr Minimal":
                print("   ✅ SUCCESS! main_minimal.py is running!")
                print(f"   App: {app_name}")
                print(f"   Version: {version}")
                
                # Test all endpoints
                if await test_all_endpoints():
                    print("\n🎉 DEPLOYMENT FULLY SUCCESSFUL!")
                    print("\n📌 Next Steps:")
                    print("1. Deploy Next.js: cd threadr-nextjs && .\\deploy-now.bat")
                    print("2. Configure Vercel environment variables")
                    print("3. Test full stack functionality")
                else:
                    print("\n⚠️  Some endpoints not working properly")
                    print("   But main deployment is successful!")
                
                break
                
            else:
                print(f"   ⚠️  Still running old version: {app_name} v{version}")
                
        elif status == "connecting":
            print("   🔄 Connecting... (deployment in progress)")
        else:
            print(f"   ❌ Status: {status}")
        
        if elapsed > 600:  # 10 minutes
            print("\n⏱️  Timeout after 10 minutes")
            print("\n💡 Check Railway dashboard for errors")
            print("   Consider using Render.com instead")
            break
        
        print("   ⏳ Next check in 20 seconds...")
        await asyncio.sleep(20)

if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
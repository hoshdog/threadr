#!/usr/bin/env python3
"""Verify Railway cache clear and deployment success"""

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

async def verify_deployment():
    """Comprehensive verification of Railway deployment"""
    print("🔍 Railway Deployment Verification")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BACKEND_URL}")
    print("=" * 60)
    
    results = {
        "cache_cleared": False,
        "correct_file": False,
        "endpoints_working": False,
        "deployment_time": None
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Check if deployment is recent
        print("\n1️⃣ CHECKING DEPLOYMENT FRESHNESS")
        print("-" * 40)
        try:
            response = await client.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                
                # Check for our deployment markers
                if data.get("app") == "Threadr Minimal":
                    print("✅ Found NEW deployment (main_minimal.py)")
                    results["correct_file"] = True
                    results["cache_cleared"] = True
                elif data.get("message") == "Threadr API" and data.get("version") == "2.0.0":
                    print("❌ Still running OLD deployment (main.py)")
                    print("   Cache clear may not have worked!")
                else:
                    print("❓ Unknown deployment version")
                
                print(f"   Response: {json.dumps(data, indent=2)}")
                
        except Exception as e:
            print(f"❌ Error checking root: {e}")
            
        # Test 2: Check health endpoint
        print("\n2️⃣ CHECKING HEALTH ENDPOINT")
        print("-" * 40)
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("app") == "minimal":
                    print("✅ Health check confirms NEW deployment")
                    results["endpoints_working"] = True
                else:
                    print("❌ Health check shows OLD deployment")
                print(f"Response: {json.dumps(data, indent=2)}")
            elif response.status_code == 503:
                print("⚠️ Service degraded - OLD deployment still active")
                
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            
        # Test 3: Check specific endpoints
        print("\n3️⃣ CHECKING ENDPOINT AVAILABILITY")
        print("-" * 40)
        
        # These endpoints only exist in certain versions
        test_endpoints = [
            ("/api/templates", "Should work in main_simple.py or main.py"),
            ("/api/generate", "Core functionality test"),
            ("/api/revenue/dashboard", "Only in main_simple.py"),
        ]
        
        working_endpoints = 0
        for endpoint, description in test_endpoints:
            try:
                if endpoint == "/api/generate":
                    response = await client.post(
                        f"{BACKEND_URL}{endpoint}",
                        json={"content": "Cache clear verification test"}
                    )
                else:
                    response = await client.get(f"{BACKEND_URL}{endpoint}")
                    
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Working")
                    working_endpoints += 1
                else:
                    print(f"❌ {endpoint} - Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
                
        if working_endpoints >= 2:
            results["endpoints_working"] = True
            
    # Final diagnosis
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS")
    print("=" * 60)
    
    if results["cache_cleared"] and results["correct_file"]:
        print("✅ SUCCESS! Cache was cleared and new deployment is active")
        print("   - Running main_minimal.py")
        print("   - All systems operational")
        print("\n🎉 Railway deployment fixed!")
        
    elif not results["correct_file"]:
        print("❌ PROBLEM: Cache clear didn't work or deployment failed")
        print("\n🔧 NEXT STEPS:")
        print("1. Try Method 2: Force rebuild with environment variable")
        print("2. Check Railway dashboard for build errors")
        print("3. Try deleting and recreating the service")
        print("4. Consider deploying to Render.com instead")
        
    else:
        print("⚠️ PARTIAL SUCCESS: Some issues remain")
        print("   Check Railway logs for details")
        
    # Provide quick commands
    print("\n" + "=" * 60)
    print("🛠️ QUICK FIX COMMANDS")
    print("=" * 60)
    print("""
# If using Railway CLI:
railway up --force

# Force rebuild by updating nixpacks.toml:
echo "# Force rebuild $(date)" >> nixpacks.toml
git add nixpacks.toml && git commit -m "Force Railway rebuild" && git push

# Test the deployment:
curl https://threadr-production.up.railway.app/health
""")

async def monitor_deployment():
    """Monitor deployment status until successful"""
    print("\n🔄 MONITORING MODE")
    print("Checking every 30 seconds until deployment is fixed...")
    print("Press Ctrl+C to stop\n")
    
    attempt = 0
    while True:
        attempt += 1
        print(f"\n--- Check #{attempt} at {datetime.now().strftime('%H:%M:%S')} ---")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{BACKEND_URL}/")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("app") == "Threadr Minimal":
                        print("✅ NEW DEPLOYMENT DETECTED!")
                        print("🎉 Cache clear successful!")
                        break
                    else:
                        print("⏳ Still running old deployment...")
                else:
                    print(f"⚠️ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
        await asyncio.sleep(30)

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Verify Railway deployment")
    parser.add_argument("--monitor", "-m", action="store_true", 
                       help="Monitor mode - check every 30 seconds")
    args = parser.parse_args()
    
    if args.monitor:
        try:
            asyncio.run(monitor_deployment())
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
    else:
        asyncio.run(verify_deployment())

if __name__ == "__main__":
    main()
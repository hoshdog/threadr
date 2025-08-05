#!/usr/bin/env python3
"""Verify which backend is deployed on Railway"""

import httpx
import asyncio
import json
import sys
from datetime import datetime

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def verify_deployment():
    """Check which backend version is deployed"""
    base_url = "https://threadr-production.up.railway.app"
    
    print("🔍 Verifying Railway Deployment")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check root endpoint
        try:
            response = await client.get(f"{base_url}/")
            data = response.json()
            
            print(f"📍 Root Endpoint Response:")
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            # Check for deployment identifier
            if "deployment" in data:
                print(f"\n✅ Deployment Type: {data['deployment']}")
            elif data.get("message") == "Threadr API":
                if data.get("version") == "2.0.0":
                    print(f"\n⚠️ Running OLD main.py (version 2.0.0)")
                else:
                    print(f"\n❓ Unknown deployment version: {data.get('version')}")
            elif data.get("app") == "Threadr Minimal":
                print(f"\n✅ Running NEW main_minimal.py!")
            else:
                print(f"\n❓ Unknown deployment")
                
        except Exception as e:
            print(f"❌ Error checking root: {e}")
            
        # Check health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            data = response.json()
            
            print(f"\n📍 Health Endpoint Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Health Status: {data.get('status')}")
            
            if "app" in data and data["app"] == "minimal":
                print(f"   ✅ Confirmed: Running main_minimal.py")
            elif "services" in data:
                print(f"   ⚠️ Confirmed: Running old main.py")
                print(f"   Services: {json.dumps(data.get('services'), indent=2)}")
                
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            
        # Test generate endpoint
        try:
            response = await client.post(
                f"{base_url}/api/generate",
                json={"content": "Test deployment verification"}
            )
            
            print(f"\n📍 Generate Endpoint Test:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Working! Generated {data.get('count', 0)} tweets")
            else:
                print(f"   ❌ Not working: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Error testing generate: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Railway Deployment Verification")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    asyncio.run(verify_deployment())
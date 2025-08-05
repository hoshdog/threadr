#!/usr/bin/env python3
"""Deep diagnostic of Railway backend to check route loading"""

import httpx
import json
import asyncio
import sys
from datetime import datetime

# Fix Windows encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BACKEND_URL = "https://threadr-production.up.railway.app"

async def test_all_routes():
    """Test all route endpoints to see what's actually loaded"""
    
    print(f"🔍 Deep Diagnostic: Railway Backend Routes")
    print(f"🌐 URL: {BACKEND_URL}")
    print(f"⏰ Time: {datetime.now().isoformat()}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test template routes
        print("📋 Testing Template Routes...")
        try:
            response = await client.get(f"{BACKEND_URL}/api/templates")
            print(f"   GET /api/templates: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Template routes loaded!")
                print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test auth routes
        print("🔐 Testing Auth Routes...")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/auth/login",
                json={"email": "test@example.com", "password": "test"}
            )
            print(f"   POST /api/auth/login: {response.status_code}")
            if response.status_code in [400, 401, 422]:
                print("   ✅ Auth routes loaded (validation working)")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test analytics routes
        print("📊 Testing Analytics Routes...")
        try:
            response = await client.get(f"{BACKEND_URL}/api/analytics/dashboard")
            print(f"   GET /api/analytics/dashboard: {response.status_code}")
            if response.status_code in [200, 401]:
                print("   ✅ Analytics routes loaded")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test revenue routes
        print("💰 Testing Revenue Routes...")
        try:
            response = await client.get(f"{BACKEND_URL}/api/revenue/dashboard")
            print(f"   GET /api/revenue/dashboard: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Revenue routes loaded!")
                print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test thread routes
        print("🧵 Testing Thread Routes...")
        try:
            response = await client.get(f"{BACKEND_URL}/api/threads")
            print(f"   GET /api/threads: {response.status_code}")
            if response.status_code in [200, 401]:
                print("   ✅ Thread routes loaded")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Test subscription routes
        print("💳 Testing Subscription Routes...")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/stripe/webhook",
                json={"test": "data"}
            )
            print(f"   POST /api/stripe/webhook: {response.status_code}")
            if response.status_code in [400, 401]:
                print("   ✅ Subscription routes loaded")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Check docs endpoint
        print("📚 Testing Documentation...")
        try:
            response = await client.get(f"{BACKEND_URL}/docs")
            print(f"   GET /docs: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ FastAPI docs available!")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # Re-check health with detailed output
        print("🏥 Final Health Check...")
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            print(f"   Status: {response.status_code}")
            health_data = response.json()
            print(f"   Health Status: {health_data['status']}")
            print(f"   Services: {json.dumps(health_data['services'], indent=2)}")
            
            # Analyze the results
            print("\n📊 Diagnostic Summary:")
            if health_data['services']['routes']:
                print("   ✅ Routes are loaded correctly")
            else:
                print("   ❌ Health check reports routes not loaded")
                print("   🤔 But individual route tests may show otherwise")
            
            if not health_data['services']['redis']:
                print("   ⚠️ Redis not connected (rate limiting disabled)")
            
            if not health_data['services']['database']:
                print("   ⚠️ Database not connected (expected if BYPASS_DATABASE=true)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}\n")

    print("\n🔍 Diagnostic Complete!")
    print("Check Railway logs for specific import errors if routes still failing")

if __name__ == "__main__":
    asyncio.run(test_all_routes())
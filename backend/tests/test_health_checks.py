#!/usr/bin/env python3
"""
Test script to verify health checks and API endpoints work correctly
Run this to test the FastAPI application locally before deploying
"""

import asyncio
import httpx
import time
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = "http://localhost:8000"

async def test_endpoints():
    """Test all health check and basic endpoints"""
    print("Testing Threadr API health checks and endpoints...")
    print(f"Base URL: {BASE_URL}")
    
    endpoints_to_test = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/readiness", "Readiness check"),
        ("/debug/startup", "Debug startup info"),
        ("/api/test", "API test endpoint")
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint, description in endpoints_to_test:
            try:
                print(f"\n🔍 Testing {description} ({endpoint})...")
                response = await client.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description}: OK")
                    
                    # Show key information
                    if endpoint == "/health":
                        print(f"   Status: {data.get('status')}")
                        services = data.get('services', {})
                        print(f"   API: {services.get('api')}")
                        print(f"   OpenAI: {services.get('openai')}")
                    elif endpoint == "/readiness":
                        print(f"   Status: {data.get('status')}")
                        checks = data.get('checks', {})
                        print(f"   Basic functionality: {checks.get('basic_functionality')}")
                        print(f"   OpenAI service: {checks.get('openai_service')}")
                    elif endpoint == "/debug/startup":
                        print(f"   Environment: {data.get('environment')}")
                        print(f"   Port: {data.get('port')}")
                        print(f"   OpenAI available: {data.get('openai_available')}")
                    elif endpoint == "/api/test":
                        print(f"   Status: {data.get('status')}")
                        test_result = data.get('test_result', {})
                        print(f"   Tweets generated: {test_result.get('tweets_generated')}")
                        print(f"   OpenAI status: {data.get('openai_status')}")
                        
                else:
                    print(f"❌ {description}: HTTP {response.status_code}")
                    print(f"   Response: {response.text[:200]}...")
                    
            except httpx.RequestError as e:
                print(f"❌ {description}: Connection error - {e}")
            except Exception as e:
                print(f"❌ {description}: Unexpected error - {e}")
    
    # Test a simple generate request
    print(f"\n🔍 Testing thread generation...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            test_data = {
                "text": "This is a test article about the importance of proper API design. Good APIs should be well-documented, consistent, and easy to use. They should handle errors gracefully and provide clear feedback to developers."
            }
            
            response = await client.post(f"{BASE_URL}/api/generate", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Thread generation: OK")
                print(f"   Success: {data.get('success')}")
                print(f"   Thread length: {len(data.get('thread', []))} tweets")
                print(f"   Source type: {data.get('source_type')}")
            else:
                print(f"❌ Thread generation: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Thread generation: Error - {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("Threadr API Health Check Test")
    print("=" * 60)
    
    try:
        asyncio.run(test_endpoints())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("If all tests pass, the API should work on Railway.")
    print("=" * 60)

if __name__ == "__main__":
    main()
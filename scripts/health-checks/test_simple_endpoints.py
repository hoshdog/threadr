#!/usr/bin/env python3
"""Test simplified backend endpoints"""

import httpx
import asyncio
import json
import sys

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def test_endpoints():
    """Test all simplified backend endpoints"""
    base_url = "https://threadr-production.up.railway.app"
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/readiness", "Readiness check"),
        ("GET", "/api/templates", "Templates list"),
        ("GET", "/api/revenue/dashboard", "Revenue dashboard"),
        ("GET", "/api/premium-status", "Premium status"),
        ("GET", "/api/usage-stats", "Usage stats"),
        ("POST", "/api/generate", "Thread generation", {"content": "Test content for thread generation"}),
        ("POST", "/api/capture-email", "Email capture", {"email": "test@example.com"})
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            method = endpoint[0]
            path = endpoint[1]
            desc = endpoint[2]
            data = endpoint[3] if len(endpoint) > 3 else None
            
            print(f"\n{'='*60}")
            print(f"Testing: {desc}")
            print(f"Endpoint: {method} {path}")
            
            try:
                if method == "GET":
                    response = await client.get(f"{base_url}{path}")
                else:
                    response = await client.post(f"{base_url}{path}", json=data)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code < 400:
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"Response: {response.text[:200]}...")
                else:
                    print(f"Error: {response.text[:200]}...")
                    
            except httpx.ConnectError:
                print("❌ Connection failed - endpoint not reachable")
            except Exception as e:
                print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("🧪 Testing Simplified Backend Endpoints")
    print("=" * 60)
    asyncio.run(test_endpoints())
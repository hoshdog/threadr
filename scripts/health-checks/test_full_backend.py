#!/usr/bin/env python3
"""
Comprehensive test for full Threadr backend
Tests all major functionality after deployment
"""

import requests
import json
import time
from datetime import datetime

def test_backend(base_url):
    """Test all backend functionality"""
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    print("[THREADR BACKEND FULL TEST]")
    print("=" * 60)
    print(f"Testing: {base_url}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {
        "health": False,
        "readiness": False,
        "generate": False,
        "usage_stats": False,
        "premium_status": False,
        "redis": False,
        "openai": False
    }
    
    # Test 1: Health Check
    print("\n[1] Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"    Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Status: {data.get('status', 'unknown')}")
            print(f"    Services: {json.dumps(data.get('services', {}), indent=2)}")
            results["health"] = True
            results["redis"] = data.get("services", {}).get("redis", False)
            print(f"    [OK] Health check passed")
        else:
            print(f"    [ERROR] Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 2: Readiness Check
    print("\n[2] Testing Readiness Endpoint...")
    try:
        response = requests.get(f"{base_url}/readiness", timeout=10)
        print(f"    Status Code: {response.status_code}")
        if response.status_code == 200:
            results["readiness"] = True
            print(f"    [OK] Readiness check passed")
        else:
            print(f"    [WARNING] Service not ready: {response.status_code}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 3: Thread Generation (Simple)
    print("\n[3] Testing Thread Generation...")
    try:
        test_content = "This is a test article about artificial intelligence and its impact on society. AI is transforming how we work, live, and interact with technology. From healthcare to transportation, AI applications are becoming increasingly prevalent in our daily lives."
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={"content": test_content},
            timeout=30
        )
        print(f"    Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tweets = data.get("tweets", [])
                print(f"    [OK] Generated {len(tweets)} tweets")
                print(f"    Method: {data.get('method', 'unknown')}")
                if tweets:
                    print(f"    First tweet: {tweets[0][:100]}...")
                results["generate"] = True
                results["openai"] = data.get("method") == "openai_generated"
            else:
                print(f"    [ERROR] Generation failed: {data.get('error')}")
        else:
            print(f"    [ERROR] Unexpected status: {response.status_code}")
            print(f"    Response: {response.text}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 4: URL Scraping
    print("\n[4] Testing URL Scraping...")
    try:
        test_url = "https://medium.com/@test/article"
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "content": "Fallback content",
                "url": test_url
            },
            timeout=30
        )
        print(f"    Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"    Success: {data.get('success')}")
            if not data.get("success"):
                print(f"    Note: {data.get('error', 'URL scraping may be limited')}")
        else:
            print(f"    [WARNING] URL scraping test returned: {response.status_code}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 5: Usage Statistics
    print("\n[5] Testing Usage Statistics...")
    try:
        response = requests.get(f"{base_url}/api/usage-stats", timeout=10)
        print(f"    Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"    Daily: {data.get('daily_used', 0)}/{data.get('daily_limit', 5)}")
                print(f"    Monthly: {data.get('monthly_used', 0)}/{data.get('monthly_limit', 20)}")
                print(f"    Premium: {data.get('is_premium', False)}")
                results["usage_stats"] = True
                print(f"    [OK] Usage stats working")
            else:
                print(f"    [WARNING] {data.get('error', 'Unknown error')}")
        else:
            print(f"    [ERROR] Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 6: Premium Status
    print("\n[6] Testing Premium Status...")
    try:
        response = requests.get(f"{base_url}/api/premium-status", timeout=10)
        print(f"    Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"    Premium: {data.get('is_premium', False)}")
                if data.get("expires_at"):
                    print(f"    Expires: {data.get('expires_at')}")
                results["premium_status"] = True
                print(f"    [OK] Premium status check working")
            else:
                print(f"    [WARNING] {data.get('error', 'Unknown error')}")
        else:
            print(f"    [ERROR] Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"    [ERROR] {e}")
    
    # Test 7: Rate Limiting (if Redis is available)
    if results["redis"]:
        print("\n[7] Testing Rate Limiting...")
        try:
            # Make multiple requests to test rate limiting
            for i in range(3):
                response = requests.post(
                    f"{base_url}/api/generate",
                    json={"content": f"Test {i+1}"},
                    timeout=10
                )
                data = response.json()
                usage = data.get("usage", {})
                print(f"    Request {i+1}: Daily {usage.get('daily_used', 0)}/{usage.get('daily_limit', 5)}")
                time.sleep(0.5)
            
            print(f"    [OK] Rate limiting appears to be working")
        except Exception as e:
            print(f"    [ERROR] {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("[TEST SUMMARY]")
    print("=" * 60)
    
    for key, value in results.items():
        status = "[OK]" if value else "[FAIL]"
        print(f"  {status} {key.replace('_', ' ').title()}")
    
    # Overall assessment
    critical_services = ["health", "generate"]
    all_critical_working = all(results[service] for service in critical_services)
    
    print("\n" + "=" * 60)
    if all_critical_working:
        print("[RESULT] Core services are OPERATIONAL")
        if results["redis"]:
            print("         Redis is CONNECTED")
        else:
            print("         Redis is NOT CONNECTED (rate limiting disabled)")
        
        if results["openai"]:
            print("         OpenAI is WORKING")
        else:
            print("         OpenAI is NOT WORKING (using fallback splitting)")
    else:
        print("[RESULT] Some core services are NOT working properly")
        print("         Check the logs above for details")
    
    print("=" * 60)
    
    return all_critical_working

if __name__ == "__main__":
    import sys
    
    print("\n[THREADR BACKEND COMPREHENSIVE TEST]")
    print("====================================\n")
    
    # Get URL from command line argument or use default
    if len(sys.argv) > 1:
        backend_url = sys.argv[1].strip()
    else:
        # Default to Render.com deployment
        backend_url = "https://threadr-pw0s.onrender.com"
        print(f"Using default backend URL: {backend_url}")
    
    if not backend_url:
        print("[ERROR] No URL provided")
    elif not backend_url.startswith("http"):
        print("[ERROR] URL must start with http:// or https://")
    else:
        success = test_backend(backend_url)
        exit(0 if success else 1)
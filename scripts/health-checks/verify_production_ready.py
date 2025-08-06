#!/usr/bin/env python3
"""
Production Readiness Verification Script
Tests all critical services after JWT_SECRET_KEY is added
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    print(f"{RED}[ERROR] {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}[WARNING] {text}{RESET}")

def print_info(text):
    print(f"   {text}")

def test_health_endpoint(base_url: str) -> Dict[str, Any]:
    """Test the health endpoint"""
    print("\n[TEST] Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Health check passed - Status: {data.get('status')}")
            
            services = data.get('services', {})
            if services.get('redis'):
                print_success("Redis is connected")
            else:
                print_error("Redis is not connected")
            
            if services.get('routes'):
                print_success("All routes loaded")
            else:
                print_error("Routes not loaded properly")
                
            return {"success": True, "data": data}
        else:
            print_error(f"Health check failed - Status: {response.status_code}")
            return {"success": False, "error": f"Status {response.status_code}"}
            
    except Exception as e:
        print_error(f"Health check error: {e}")
        return {"success": False, "error": str(e)}

def test_openai_generation(base_url: str) -> Dict[str, Any]:
    """Test OpenAI thread generation"""
    print("\n[TEST] OpenAI Integration...")
    
    test_content = """
    Artificial intelligence is transforming healthcare through early disease detection, 
    personalized treatment plans, and accelerated drug discovery. Machine learning 
    algorithms can now analyze medical images with remarkable accuracy.
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"content": test_content.strip()},
            timeout=30
        )
        data = response.json()
        
        if data.get('success'):
            tweets = data.get('tweets', [])
            
            # Check if using OpenAI or fallback
            if data.get('error') and 'quota' in str(data.get('error')):
                print_error("OpenAI quota exceeded - Using fallback splitting")
                return {"success": False, "error": "OpenAI quota issue"}
            elif len(tweets) > 1 or (tweets and len(tweets[0]) < len(test_content.strip())):
                print_success(f"OpenAI generation working - Generated {len(tweets)} tweets")
                print_info(f"First tweet: {tweets[0][:100]}...")
                return {"success": True, "tweets": tweets}
            else:
                print_warning("Using simple fallback splitting (OpenAI may not be working)")
                return {"success": False, "error": "Fallback mode"}
        else:
            print_error(f"Generation failed: {data.get('error')}")
            return {"success": False, "error": data.get('error')}
            
    except Exception as e:
        print_error(f"Thread generation error: {e}")
        return {"success": False, "error": str(e)}

def test_rate_limiting(base_url: str) -> Dict[str, Any]:
    """Test rate limiting and usage tracking"""
    print("\n[TEST] Rate Limiting...")
    
    try:
        response = requests.get(f"{base_url}/api/usage-stats", timeout=10)
        data = response.json()
        
        if data.get('success'):
            print_success("Usage tracking is working")
            print_info(f"Daily: {data.get('daily_used')}/{data.get('daily_limit')}")
            print_info(f"Monthly: {data.get('monthly_used')}/{data.get('monthly_limit')}")
            print_info(f"Premium: {data.get('is_premium', False)}")
            return {"success": True, "data": data}
        else:
            print_error(f"Usage stats failed: {data.get('error')}")
            return {"success": False, "error": data.get('error')}
            
    except Exception as e:
        print_error(f"Rate limiting test error: {e}")
        return {"success": False, "error": str(e)}

def test_premium_status(base_url: str) -> Dict[str, Any]:
    """Test premium status endpoint"""
    print("\n[TEST] Premium Status...")
    
    try:
        response = requests.get(f"{base_url}/api/premium-status", timeout=10)
        data = response.json()
        
        if data.get('success'):
            print_success("Premium status check working")
            print_info(f"Premium: {data.get('is_premium', False)}")
            if data.get('expires_at'):
                print_info(f"Expires: {data.get('expires_at')}")
            return {"success": True, "data": data}
        else:
            print_warning(f"Premium status issue: {data.get('error')}")
            return {"success": False, "error": data.get('error')}
            
    except Exception as e:
        print_error(f"Premium status test error: {e}")
        return {"success": False, "error": str(e)}

def test_cors_headers(base_url: str) -> Dict[str, Any]:
    """Test CORS headers for frontend integration"""
    print("\n[TEST] CORS Configuration...")
    
    try:
        response = requests.options(
            f"{base_url}/api/generate",
            headers={
                'Origin': 'https://threadr-plum.vercel.app',
                'Access-Control-Request-Method': 'POST'
            },
            timeout=10
        )
        
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if cors_headers:
            print_success(f"CORS configured - Origin: {cors_headers}")
            return {"success": True, "cors": cors_headers}
        else:
            print_warning("CORS headers not found - Frontend may have issues")
            return {"success": False, "error": "No CORS headers"}
            
    except Exception as e:
        print_warning(f"CORS test inconclusive: {e}")
        return {"success": False, "error": str(e)}

def main():
    print_header("THREADR PRODUCTION READINESS TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "https://threadr-pw0s.onrender.com"
    print(f"Testing: {base_url}")
    
    # Track results
    results = {
        "health": False,
        "redis": False,
        "openai": False,
        "rate_limiting": False,
        "premium": False,
        "cors": False
    }
    
    # Run tests
    health_result = test_health_endpoint(base_url)
    if health_result["success"]:
        results["health"] = True
        services = health_result["data"].get("services", {})
        results["redis"] = services.get("redis", False)
    
    openai_result = test_openai_generation(base_url)
    results["openai"] = openai_result["success"]
    
    rate_result = test_rate_limiting(base_url)
    results["rate_limiting"] = rate_result["success"]
    
    premium_result = test_premium_status(base_url)
    results["premium"] = premium_result["success"]
    
    cors_result = test_cors_headers(base_url)
    results["cors"] = cors_result["success"]
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\nPassed: {passed_tests}/{total_tests} tests")
    print()
    
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name.replace('_', ' ').title()}")
        else:
            print_error(f"{test_name.replace('_', ' ').title()}")
    
    # Final assessment
    print_header("PRODUCTION READINESS")
    
    critical_services = ["health", "redis", "rate_limiting"]
    all_critical = all(results[service] for service in critical_services)
    
    if all_critical and results["openai"]:
        print_success("FULLY PRODUCTION READY!")
        print_info("All critical services operational with AI generation")
    elif all_critical:
        print_warning("PRODUCTION READY (OpenAI needs attention)")
        print_info("Core services working, but check OpenAI configuration")
    else:
        print_error("NOT PRODUCTION READY")
        print_info("Critical services need attention")
    
    # Recommendations
    if not results["openai"]:
        print("\n[ACTION] OpenAI Fix Needed:")
        print_info("1. Verify OPENAI_API_KEY in Render environment")
        print_info("2. Check credits at platform.openai.com/account/billing")
        print_info("3. Ensure API key has no extra spaces/quotes")
    
    if not results["cors"]:
        print("\n[ACTION] CORS Configuration:")
        print_info("Add CORS_ORIGINS=https://threadr-plum.vercel.app to Render")
    
    if not results["redis"]:
        print("\n[ACTION] Redis Connection:")
        print_info("Check REDIS_URL in Render environment variables")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print("Test completed!")
    
    return all_critical

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
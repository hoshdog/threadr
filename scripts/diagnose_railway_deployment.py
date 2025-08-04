#!/usr/bin/env python3
"""
Railway Deployment Diagnostic Script
Helps identify why the backend is returning 502 Bad Gateway
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://threadr-production.up.railway.app"
FRONTEND_URL = "https://threadr-plum.vercel.app"

def test_endpoint(url, description, expected_status=200, timeout=10):
    """Test an endpoint and return detailed results"""
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=timeout)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == expected_status:
            print("✅ SUCCESS")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                return True, data
            except:
                print(f"Response (text): {response.text[:500]}")
                return True, response.text
        else:
            print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2)}")
                return False, error_data
            except:
                print(f"Error Response (text): {response.text[:500]}")
                return False, response.text
                
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - No response within {timeout} seconds")
        return False, "timeout"
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR - {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR - {str(e)}")
        return False, str(e)

def diagnose_railway_deployment():
    """Run comprehensive deployment diagnostics"""
    print("=" * 60)
    print("RAILWAY DEPLOYMENT DIAGNOSTICS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Basic health check
    success, data = test_endpoint(f"{BACKEND_URL}/health", "Backend Health Check")
    results["health"] = {"success": success, "data": data}
    
    # Test 2: Root endpoint
    success, data = test_endpoint(f"{BACKEND_URL}/", "Backend Root Endpoint", expected_status=404)
    results["root"] = {"success": success, "data": data}
    
    # Test 3: Subscription plans
    success, data = test_endpoint(f"{BACKEND_URL}/api/subscription/plans", "Subscription Plans")
    results["subscription_plans"] = {"success": success, "data": data}
    
    # Test 4: Webhook endpoint (should be accessible)
    try:
        response = requests.post(f"{BACKEND_URL}/api/subscription/webhook", 
                               json={}, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        print(f"\n🔍 Testing: Stripe Webhook Endpoint (POST)")
        print(f"URL: {BACKEND_URL}/api/subscription/webhook")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [400, 401]:  # Expected - missing signature
            print("✅ SUCCESS - Endpoint accessible (signature validation working)")
            results["webhook"] = {"success": True, "data": response.text}
        else:
            print(f"❌ UNEXPECTED STATUS - {response.status_code}")
            results["webhook"] = {"success": False, "data": response.text}
            
    except Exception as e:
        print(f"❌ WEBHOOK TEST FAILED - {str(e)}")
        results["webhook"] = {"success": False, "data": str(e)}
    
    # Test 5: Frontend accessibility
    success, data = test_endpoint(FRONTEND_URL, "Frontend Accessibility")
    results["frontend"] = {"success": success, "data": type(data).__name__ if data else None}
    
    # Test 6: CORS preflight
    try:
        print(f"\n🔍 Testing: CORS Preflight Request")
        response = requests.options(f"{BACKEND_URL}/api/subscription/plans",
                                  headers={
                                      "Origin": FRONTEND_URL,
                                      "Access-Control-Request-Method": "GET"
                                  })
        print(f"Status: {response.status_code}")
        print(f"CORS Headers: {[k for k in response.headers.keys() if 'cors' in k.lower() or 'access-control' in k.lower()]}")
        
        if response.status_code in [200, 204]:
            print("✅ CORS preflight successful")
            results["cors"] = {"success": True}
        else:
            print(f"❌ CORS preflight failed - {response.status_code}")
            results["cors"] = {"success": False}
            
    except Exception as e:
        print(f"❌ CORS TEST FAILED - {str(e)}")
        results["cors"] = {"success": False, "error": str(e)}
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r.get("success", False))
    
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    
    if results.get("health", {}).get("success"):
        print("✅ Backend is responding - deployment successful")
    else:
        print("❌ Backend is not responding - CRITICAL DEPLOYMENT ISSUE")
        print("\nLikely causes:")
        print("- Missing OPENAI_API_KEY environment variable")
        print("- Missing REDIS_URL environment variable") 
        print("- Application startup failure")
        print("- Import errors in Python code")
        
        print(f"\nImmediate action required:")
        print("1. Check Railway environment variables")
        print("2. View Railway deployment logs: railway logs --tail 50")
        print("3. Verify all required environment variables are set")
        print("4. Redeploy after fixing missing variables")
    
    if not results.get("cors", {}).get("success"):
        print("⚠️  CORS configuration may need attention")
    
    return results

if __name__ == "__main__":
    results = diagnose_railway_deployment()
    
    # Save results to file
    with open("railway_diagnostic_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"\nDiagnostic results saved to: railway_diagnostic_results.json")
#!/usr/bin/env python3
"""
Subscription Deployment Verification Script
Runs after Railway deployment is fixed to verify all subscription features
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://threadr-production.up.railway.app"
FRONTEND_URL = "https://threadr-plum.vercel.app"

def test_endpoint(method, url, description, expected_status=200, timeout=10, headers=None, data=None):
    """Test an endpoint and return detailed results"""
    print(f"\nTesting: {description}")
    print(f"URL: {url}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout, headers=headers or {})
        elif method.upper() == "POST":
            response = requests.post(url, timeout=timeout, headers=headers or {}, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("SUCCESS")
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                return True, result
            except:
                print(f"Response (text): {response.text[:200]}")
                return True, response.text
        else:
            print(f"FAILED - Expected {expected_status}, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
                return False, error_data
            except:
                print(f"Error (text): {response.text[:200]}")
                return False, response.text
                
    except Exception as e:
        print(f"ERROR - {str(e)}")
        return False, str(e)

def verify_subscription_deployment():
    """Verify all subscription system components"""
    print("=" * 60)
    print("SUBSCRIPTION DEPLOYMENT VERIFICATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Backend Health
    print("\n1. BACKEND HEALTH CHECK")
    success, data = test_endpoint("GET", f"{BACKEND_URL}/health", "Backend Health")
    results["health"] = success
    
    if not success:
        print("\nCRITICAL: Backend is not responding. Stopping verification.")
        print("Fix the Railway deployment first!")
        return results
    
    # Test 2: Subscription Plans
    print("\n2. SUBSCRIPTION PLANS")
    success, data = test_endpoint("GET", f"{BACKEND_URL}/api/subscription/plans", "Subscription Plans")
    results["plans"] = success
    
    if success and isinstance(data, dict):
        plans = data.get("plans", [])
        print(f"Found {len(plans)} subscription plans")
        for plan in plans:
            print(f"  - {plan.get('name')}: ${plan.get('price', 0)}/{plan.get('interval', 'month')}")
    
    # Test 3: Stripe Webhook (should be accessible but reject invalid signatures)
    print("\n3. STRIPE WEBHOOK ENDPOINT")
    success, data = test_endpoint("POST", f"{BACKEND_URL}/api/subscription/webhook", 
                                 "Stripe Webhook", expected_status=400,
                                 headers={"Content-Type": "application/json"}, 
                                 data={})
    results["webhook"] = success
    
    # Test 4: Authentication Endpoints
    print("\n4. AUTHENTICATION SYSTEM")
    
    # Test registration endpoint
    test_user = {
        "email": f"test-{int(time.time())}@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    success, data = test_endpoint("POST", f"{BACKEND_URL}/api/auth/register", 
                                 "User Registration", expected_status=201,
                                 headers={"Content-Type": "application/json"}, 
                                 data=test_user)
    results["auth_register"] = success
    
    if success:
        # Test login endpoint
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        success, login_response = test_endpoint("POST", f"{BACKEND_URL}/api/auth/login", 
                                               "User Login", expected_status=200,
                                               headers={"Content-Type": "application/json"}, 
                                               data=login_data)
        results["auth_login"] = success
        
        if success and isinstance(login_response, dict):
            token = login_response.get("access_token")
            if token:
                print(f"JWT Token received: {token[:20]}...")
                
                # Test subscription status with token
                print("\n5. SUBSCRIPTION STATUS (AUTHENTICATED)")
                auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                success, data = test_endpoint("GET", f"{BACKEND_URL}/api/subscription/status", 
                                             "Subscription Status", 
                                             headers=auth_headers)
                results["subscription_status"] = success
                
                # Test create checkout session
                print("\n6. CREATE CHECKOUT SESSION")
                checkout_data = {
                    "price_id": "price_starter_monthly",  # This might not exist yet
                    "success_url": f"{FRONTEND_URL}/success",
                    "cancel_url": f"{FRONTEND_URL}/cancel"
                }
                
                success, data = test_endpoint("POST", f"{BACKEND_URL}/api/subscription/create-checkout", 
                                             "Create Checkout Session",
                                             headers=auth_headers,
                                             data=checkout_data)
                results["create_checkout"] = success
    
    # Test 7: CORS Configuration
    print("\n7. CORS CONFIGURATION")
    try:
        response = requests.options(f"{BACKEND_URL}/api/subscription/plans",
                                  headers={
                                      "Origin": FRONTEND_URL,
                                      "Access-Control-Request-Method": "GET",
                                      "Access-Control-Request-Headers": "Content-Type"
                                  })
        
        cors_headers = [k for k in response.headers.keys() if 'access-control' in k.lower()]
        print(f"CORS Headers: {cors_headers}")
        
        if response.status_code in [200, 204] and cors_headers:
            print("SUCCESS - CORS configured correctly")
            results["cors"] = True
        else:
            print(f"FAILED - CORS issues detected (status: {response.status_code})")
            results["cors"] = False
            
    except Exception as e:
        print(f"CORS test failed: {e}")
        results["cors"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    critical_tests = ["health", "plans", "webhook", "auth_register", "auth_login"]
    critical_passed = sum(1 for test in critical_tests if results.get(test, False))
    
    print(f"Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
    
    if critical_passed == len(critical_tests):
        print("\nSUCCESS: Core subscription system is functional!")
        print("Ready for frontend integration testing.")
    else:
        print("\nISSUES DETECTED: Some core features are not working.")
        failed_tests = [test for test in critical_tests if not results.get(test, False)]
        print(f"Failed tests: {failed_tests}")
    
    return results

def test_frontend_integration():
    """Test frontend integration with backend"""
    print("\n" + "=" * 60)
    print("FRONTEND INTEGRATION TEST")
    print("=" * 60)
    
    print("\nPlease run the following in your browser console at:")
    print(f"{FRONTEND_URL}")
    print("\n--- Browser Console Commands ---")
    
    print("""
// Test 1: Backend connectivity
fetch('https://threadr-production.up.railway.app/health')
  .then(r => r.json())
  .then(d => console.log('Health:', d))
  .catch(e => console.error('Health failed:', e));

// Test 2: Subscription plans
fetch('https://threadr-production.up.railway.app/api/subscription/plans', {
  mode: 'cors',
  credentials: 'omit'
})
  .then(r => r.json())
  .then(d => console.log('Plans:', d))
  .catch(e => console.error('Plans failed:', e));

// Test 3: Check for CORS errors (should not see any in Network tab)
""")

if __name__ == "__main__":
    results = verify_subscription_deployment()
    
    # Save results
    output_file = f"subscription_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "backend_url": BACKEND_URL,
            "frontend_url": FRONTEND_URL
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Frontend integration guidance
    if results.get("health", False):
        test_frontend_integration()
    else:
        print("\nSkipping frontend integration test - backend not responding")
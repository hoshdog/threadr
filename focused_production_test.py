#!/usr/bin/env python3
"""
Focused Production Test Suite for Threadr
Tests public endpoints and validates authentication requirements
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import httpx

# Production URLs
BACKEND_URL = "https://threadr-production.up.railway.app"
FRONTEND_URL = "https://threadr-plum.vercel.app"

class FocusedThreadrTester:
    def __init__(self):
        self.results = []
        
    def log_test(self, test_name: str, status: str, details: Dict[str, Any], response_time: float = None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "response_time_ms": response_time
        }
        self.results.append(result)
        
        # Color coding for console output
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        reset = "\033[0m"
        
        print(f"{color}[{status}]{reset} {test_name}")
        if response_time:
            print(f"   Response time: {response_time:.0f}ms")
        if details.get("error"):
            print(f"   Error: {details['error']}")
        if details.get("message"):
            print(f"   Message: {details['message'][:100]}..." if len(str(details['message'])) > 100 else f"   Message: {details['message']}")
        print()

    async def test_public_endpoints(self):
        """Test all public endpoints that should work without API keys"""
        print("TESTING PUBLIC ENDPOINTS (No Authentication Required)")
        print("=" * 70)
        
        public_endpoints = [
            ("/health", "Basic health check"),
            ("/", "Root endpoint"),
            ("/readiness", "Readiness probe"),
            ("/api/test", "Test endpoint"),
            ("/api/rate-limit-status", "Rate limit status"),
            ("/api/cache/stats", "Cache statistics"),
            ("/api/monitor/health", "Comprehensive health"),
            ("/api/premium/check", "Premium status check"),
            ("/api/usage/status", "Usage status"),
            ("/api/payment/config", "Payment configuration")
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint, description in public_endpoints:
                start_time = time.time()
                try:
                    response = await client.get(f"{BACKEND_URL}{endpoint}")
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            self.log_test(
                                f"Public API - {description}",
                                "PASS",
                                {
                                    "status_code": response.status_code,
                                    "has_json_response": True,
                                    "endpoint": endpoint,
                                    "response_keys": list(data.keys()) if isinstance(data, dict) else None
                                },
                                response_time
                            )
                        except json.JSONDecodeError:
                            self.log_test(
                                f"Public API - {description}",
                                "PASS",
                                {
                                    "status_code": response.status_code,
                                    "has_json_response": False,
                                    "endpoint": endpoint,
                                    "content_length": len(response.text)
                                },
                                response_time
                            )
                    else:
                        try:
                            error_data = response.json()
                        except:
                            error_data = {"raw_response": response.text[:200]}
                            
                        self.log_test(
                            f"Public API - {description}",
                            "FAIL",
                            {
                                "status_code": response.status_code,
                                "error_data": error_data,
                                "endpoint": endpoint
                            },
                            response_time
                        )
                        
                except Exception as e:
                    self.log_test(
                        f"Public API - {description}",
                        "FAIL",
                        {
                            "error": str(e),
                            "endpoint": endpoint
                        }
                    )

    async def test_protected_endpoints_without_auth(self):
        """Test protected endpoints to verify they properly require authentication"""
        print("TESTING AUTHENTICATION REQUIREMENTS")
        print("=" * 70)
        
        protected_endpoints = [
            ("/api/generate", "POST", {"input_type": "text", "content": "Test content"}),
            ("/api/subscribe", "POST", {"email": "test@example.com"}),
            ("/api/emails/stats", "GET", None),
            ("/api/premium/grant", "POST", {"email": "test@example.com", "expires_at": "2025-08-31T00:00:00Z"}),
            ("/api/usage/analytics", "GET", None)
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint, method, payload in protected_endpoints:
                start_time = time.time()
                try:
                    if method == "POST":
                        response = await client.post(
                            f"{BACKEND_URL}{endpoint}",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        )
                    else:
                        response = await client.get(f"{BACKEND_URL}{endpoint}")
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 401:
                        try:
                            data = response.json()
                            self.log_test(
                                f"Auth Check - {endpoint}",
                                "PASS",
                                {
                                    "status_code": response.status_code,
                                    "message": "Correctly requires authentication",
                                    "auth_message": data.get("detail", "No detail provided"),
                                    "endpoint": endpoint
                                },
                                response_time
                            )
                        except json.JSONDecodeError:
                            self.log_test(
                                f"Auth Check - {endpoint}",
                                "PASS",
                                {
                                    "status_code": response.status_code,
                                    "message": "Correctly requires authentication (no JSON)",
                                    "endpoint": endpoint
                                },
                                response_time
                            )
                    else:
                        try:
                            error_data = response.json()
                        except:
                            error_data = {"raw_response": response.text[:200]}
                            
                        self.log_test(
                            f"Auth Check - {endpoint}",
                            "FAIL",
                            {
                                "status_code": response.status_code,
                                "error": f"Expected 401, got {response.status_code}",
                                "response_data": error_data,
                                "endpoint": endpoint
                            },
                            response_time
                        )
                        
                except Exception as e:
                    self.log_test(
                        f"Auth Check - {endpoint}",
                        "FAIL",
                        {
                            "error": str(e),
                            "endpoint": endpoint
                        }
                    )

    async def test_development_endpoints_blocked(self):
        """Test that development-only endpoints return 404 in production"""
        print("TESTING DEVELOPMENT ENDPOINT BLOCKING")
        print("=" * 70)
        
        dev_endpoints = [
            "/api/security/config",
            "/api/test/url-check",
            "/api/test/railway-network"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in dev_endpoints:
                start_time = time.time()
                try:
                    if endpoint == "/api/test/url-check":
                        # This is a POST endpoint
                        response = await client.post(
                            f"{BACKEND_URL}{endpoint}",
                            json={"url": "https://example.com"}
                        )
                    else:
                        response = await client.get(f"{BACKEND_URL}{endpoint}")
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 404:
                        self.log_test(
                            f"Dev Blocking - {endpoint}",
                            "PASS",
                            {
                                "status_code": response.status_code,
                                "message": "Correctly blocked in production",
                                "endpoint": endpoint
                            },
                            response_time
                        )
                    else:
                        try:
                            error_data = response.json()
                        except:
                            error_data = {"raw_response": response.text[:200]}
                            
                        self.log_test(
                            f"Dev Blocking - {endpoint}",
                            "FAIL",
                            {
                                "status_code": response.status_code,
                                "error": f"Expected 404, got {response.status_code}",
                                "response_data": error_data,
                                "endpoint": endpoint
                            },
                            response_time
                        )
                        
                except Exception as e:
                    self.log_test(
                        f"Dev Blocking - {endpoint}",
                        "FAIL",
                        {
                            "error": str(e),
                            "endpoint": endpoint
                        }
                    )

    async def test_cors_configuration(self):
        """Test CORS configuration with the production frontend"""
        print("TESTING CORS CONFIGURATION")
        print("=" * 70)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Origin": "https://threadr-plum.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            start_time = time.time()
            try:
                # Test preflight request for the main API endpoint
                response = await client.options(f"{BACKEND_URL}/api/generate", headers=headers)
                response_time = (time.time() - start_time) * 1000
                
                cors_headers = {
                    key.lower(): value for key, value in response.headers.items() 
                    if key.lower().startswith("access-control-")
                }
                
                allow_origin = cors_headers.get("access-control-allow-origin")
                allow_methods = cors_headers.get("access-control-allow-methods")
                allow_headers = cors_headers.get("access-control-allow-headers")
                
                if response.status_code in [200, 204]:
                    cors_working = bool(allow_origin and ("*" in allow_origin or "threadr-plum.vercel.app" in allow_origin))
                    
                    self.log_test(
                        "CORS Configuration",
                        "PASS" if cors_working else "FAIL",
                        {
                            "status_code": response.status_code,
                            "cors_working": cors_working,
                            "allow_origin": allow_origin,
                            "allow_methods": allow_methods,
                            "allow_headers": allow_headers,
                            "all_cors_headers": cors_headers
                        },
                        response_time
                    )
                else:
                    self.log_test(
                        "CORS Configuration",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": f"Expected 200/204, got {response.status_code}",
                            "cors_headers": cors_headers
                        },
                        response_time
                    )
                    
            except Exception as e:
                self.log_test(
                    "CORS Configuration",
                    "FAIL",
                    {"error": str(e)}
                )

    async def test_frontend_integration(self):
        """Test frontend accessibility and integration"""
        print("TESTING FRONTEND INTEGRATION")
        print("=" * 70)
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            start_time = time.time()
            try:
                response = await client.get(FRONTEND_URL)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for key frontend technologies and features
                    checks = {
                        "has_threadr_title": "threadr" in content,
                        "has_alpine_js": "alpine" in content or "x-data" in content,
                        "has_tailwind": "tailwind" in content or "bg-" in content or "text-" in content,
                        "has_api_endpoint": BACKEND_URL.replace("https://", "") in content,
                        "has_form_elements": "input" in content and "button" in content,
                        "has_usage_display": "usage" in content or "remaining" in content or "limit" in content,
                        "has_payment_modal": "stripe" in content or "payment" in content or "premium" in content
                    }
                    
                    passed_checks = sum(checks.values())
                    total_checks = len(checks)
                    
                    self.log_test(
                        "Frontend Integration",
                        "PASS" if passed_checks >= total_checks * 0.7 else "FAIL",
                        {
                            "status_code": response.status_code,
                            "content_length": len(response.text),
                            "checks_passed": f"{passed_checks}/{total_checks}",
                            "integration_score": f"{(passed_checks/total_checks)*100:.1f}%",
                            "checks": checks
                        },
                        response_time
                    )
                else:
                    self.log_test(
                        "Frontend Integration",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": f"Expected 200, got {response.status_code}"
                        },
                        response_time
                    )
                    
            except Exception as e:
                self.log_test(
                    "Frontend Integration",
                    "FAIL",
                    {"error": str(e)}
                )

    async def test_api_usage_limits_display(self):
        """Test that usage limit information is properly displayed"""
        print("TESTING USAGE LIMITS DISPLAY")
        print("=" * 70)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test usage status endpoint
            start_time = time.time()
            try:
                response = await client.get(f"{BACKEND_URL}/api/usage/status")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    required_fields = [
                        "daily_usage", "daily_limit", "daily_remaining",
                        "monthly_usage", "monthly_limit", "monthly_remaining",
                        "has_premium", "free_tier_enabled"
                    ]
                    
                    has_all_fields = all(field in data for field in required_fields)
                    
                    # Validate data makes sense
                    valid_data = (
                        data.get("daily_limit", 0) == 5 and
                        data.get("monthly_limit", 0) == 20 and
                        data.get("daily_remaining", -1) >= 0 and
                        data.get("monthly_remaining", -1) >= 0
                    )
                    
                    self.log_test(
                        "Usage Limits Display",
                        "PASS" if has_all_fields and valid_data else "FAIL",
                        {
                            "status_code": response.status_code,
                            "has_all_fields": has_all_fields,
                            "valid_data": valid_data,
                            "daily_limit": data.get("daily_limit"),
                            "monthly_limit": data.get("monthly_limit"),
                            "daily_remaining": data.get("daily_remaining"),
                            "monthly_remaining": data.get("monthly_remaining"),
                            "missing_fields": [f for f in required_fields if f not in data]
                        },
                        response_time
                    )
                else:
                    self.log_test(
                        "Usage Limits Display",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": f"Expected 200, got {response.status_code}"
                        },
                        response_time
                    )
                    
            except Exception as e:
                self.log_test(
                    "Usage Limits Display",
                    "FAIL",
                    {"error": str(e)}
                )
            
            # Test premium check endpoint
            start_time = time.time()
            try:
                response = await client.get(f"{BACKEND_URL}/api/premium/check")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required premium fields
                    premium_fields = ["has_premium", "needs_payment", "premium_price", "message"]
                    has_premium_fields = all(field in data for field in premium_fields)
                    
                    # Check that message is user-friendly
                    message = data.get("message", "")
                    user_friendly = "thread" in message.lower() and ("remaining" in message.lower() or "limit" in message.lower())
                    
                    self.log_test(
                        "Premium Check Display",
                        "PASS" if has_premium_fields and user_friendly else "FAIL",
                        {
                            "status_code": response.status_code,
                            "has_premium_fields": has_premium_fields,
                            "user_friendly_message": user_friendly,
                            "premium_price": data.get("premium_price"),
                            "message_preview": message[:100] + "..." if len(message) > 100 else message
                        },
                        response_time
                    )
                else:
                    self.log_test(
                        "Premium Check Display",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": f"Expected 200, got {response.status_code}"
                        },
                        response_time
                    )
                    
            except Exception as e:
                self.log_test(
                    "Premium Check Display",
                    "FAIL",
                    {"error": str(e)}
                )

    async def test_stripe_configuration(self):
        """Test Stripe payment configuration"""
        print("TESTING STRIPE PAYMENT CONFIGURATION")
        print("=" * 70)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.time()
            try:
                response = await client.get(f"{BACKEND_URL}/api/payment/config")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required payment config fields
                    required_fields = [
                        "stripe_configured", "webhook_configured", "premium_price",
                        "display_price", "currency", "payment_methods"
                    ]
                    
                    has_all_fields = all(field in data for field in required_fields)
                    
                    # Validate configuration
                    valid_config = (
                        data.get("stripe_configured") is True and
                        data.get("webhook_configured") is True and
                        data.get("premium_price") == 4.99 and
                        data.get("currency") == "USD" and
                        "stripe_payment_links" in data.get("payment_methods", [])
                    )
                    
                    self.log_test(
                        "Stripe Configuration",
                        "PASS" if has_all_fields and valid_config else "FAIL",
                        {
                            "status_code": response.status_code,
                            "has_all_fields": has_all_fields,
                            "valid_config": valid_config,
                            "stripe_configured": data.get("stripe_configured"),
                            "webhook_configured": data.get("webhook_configured"),
                            "premium_price": data.get("premium_price"),
                            "payment_methods": data.get("payment_methods"),
                            "missing_fields": [f for f in required_fields if f not in data]
                        },
                        response_time
                    )
                else:
                    self.log_test(
                        "Stripe Configuration",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": f"Expected 200, got {response.status_code}"
                        },
                        response_time
                    )
                    
            except Exception as e:
                self.log_test(
                    "Stripe Configuration",
                    "FAIL",
                    {"error": str(e)}
                )

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("FOCUSED PRODUCTION TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        
        print(f"\nTEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
        
        # Performance metrics
        response_times = [r["response_time_ms"] for r in self.results if r["response_time_ms"]]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"\nPERFORMANCE METRICS")
            print(f"Average Response Time: {avg_response_time:.0f}ms")
            print(f"Fastest Response: {min_response_time:.0f}ms")
            print(f"Slowest Response: {max_response_time:.0f}ms")
        
        # Category analysis
        categories = {}
        for result in self.results:
            category = result["test_name"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"pass": 0, "fail": 0}
            
            if result["status"] == "PASS":
                categories[category]["pass"] += 1
            else:
                categories[category]["fail"] += 1
        
        print(f"\nTEST CATEGORIES")
        for category, stats in categories.items():
            total = stats["pass"] + stats["fail"]
            success_rate = (stats["pass"] / total * 100) if total > 0 else 0
            print(f"{category}: {stats['pass']}/{total} passed ({success_rate:.1f}%)")
        
        # Failed tests details
        failed_results = [r for r in self.results if r["status"] == "FAIL"]
        if failed_results:
            print(f"\nFAILED TESTS DETAILS")
            for result in failed_results:
                print(f"- {result['test_name']}")
                if result["details"].get("error"):
                    print(f"  Error: {result['details']['error']}")
                if result["details"].get("status_code"):
                    print(f"  Status Code: {result['details']['status_code']}")
        
        # Key findings
        print(f"\nKEY FINDINGS")
        
        public_api_working = any("Public API" in r["test_name"] and r["status"] == "PASS" for r in self.results)
        auth_working = any("Auth Check" in r["test_name"] and r["status"] == "PASS" for r in self.results)
        cors_working = any("CORS" in r["test_name"] and r["status"] == "PASS" for r in self.results)
        frontend_working = any("Frontend" in r["test_name"] and r["status"] == "PASS" for r in self.results)
        stripe_working = any("Stripe" in r["test_name"] and r["status"] == "PASS" for r in self.results)
        
        if public_api_working:
            print("SUCCESS: Public API endpoints are working correctly")
        
        if auth_working:
            print("SUCCESS: Authentication requirements are properly enforced")
        
        if cors_working:
            print("SUCCESS: CORS is configured correctly for frontend integration")
        
        if frontend_working:
            print("SUCCESS: Frontend is accessible and properly integrated")
        
        if stripe_working:
            print("SUCCESS: Stripe payment configuration is set up correctly")
        
        if response_times and avg_response_time < 1000:
            print("SUCCESS: Excellent response times (< 1 second average)")
        elif response_times and avg_response_time < 3000:
            print("GOOD: Good response times (< 3 seconds average)")
        elif response_times:
            print("WARNING: Slow response times - consider optimization")
        
        print(f"\nTESTED SYSTEMS")
        print(f"Backend: {BACKEND_URL}")
        print(f"Frontend: {FRONTEND_URL}")
        
        # Save detailed results
        report_file = f"focused_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0
                },
                "performance": {
                    "average_response_time_ms": avg_response_time if response_times else None,
                    "max_response_time_ms": max_response_time if response_times else None,
                    "min_response_time_ms": min_response_time if response_times else None
                },
                "categories": categories,
                "test_results": self.results,
                "timestamp": datetime.now().isoformat(),
                "backend_url": BACKEND_URL,
                "frontend_url": FRONTEND_URL
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {report_file}")

    async def run_all_tests(self):
        """Run all focused tests"""
        print("STARTING FOCUSED THREADR PRODUCTION TESTS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        try:
            await self.test_public_endpoints()
            await self.test_protected_endpoints_without_auth()
            await self.test_development_endpoints_blocked()
            await self.test_cors_configuration()
            await self.test_frontend_integration()
            await self.test_api_usage_limits_display()
            await self.test_stripe_configuration()
            
        except KeyboardInterrupt:
            print("\nWARNING: Tests interrupted by user")
        except Exception as e:
            print(f"\nERROR: Unexpected error during testing: {e}")
        finally:
            self.generate_report()

async def main():
    """Main test runner"""
    tester = FocusedThreadrTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
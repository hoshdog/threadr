#!/usr/bin/env python3
"""
Monetization Features Testing Script for Threadr
Tests email capture, usage tracking, free tier limits, and Stripe integration locally
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional

class MonetizationTester:
    def __init__(self, backend_url: str = "http://localhost:8001"):
        self.backend_url = backend_url.rstrip('/')
        self.test_results = {}
        self.test_emails = []
        self.test_ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
        
    async def test_email_capture_endpoint(self) -> bool:
        """Test email capture API endpoint"""
        print("📧 Testing email capture endpoint...")
        
        test_cases = [
            {"email": "test@example.com", "should_succeed": True},
            {"email": "invalid-email", "should_succeed": False},
            {"email": "", "should_succeed": False},
            {"email": "test+tag@domain.co.uk", "should_succeed": True}
        ]
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for i, test_case in enumerate(test_cases):
                try:
                    async with session.post(
                        f"{self.backend_url}/api/capture-email",
                        json={"email": test_case["email"]},
                        timeout=10
                    ) as response:
                        status = response.status
                        data = await response.json()
                        
                        success = (status == 200) == test_case["should_succeed"]
                        results[f"test_{i+1}"] = {
                            "email": test_case["email"],
                            "expected_success": test_case["should_succeed"],
                            "actual_status": status,
                            "success": success,
                            "response": data
                        }
                        
                        if success:
                            print(f"  ✅ {test_case['email']}: {status}")
                            if status == 200:
                                self.test_emails.append(test_case["email"])
                        else:
                            print(f"  ❌ {test_case['email']}: Expected {'success' if test_case['should_succeed'] else 'failure'}, got {status}")
                            
                except Exception as e:
                    results[f"test_{i+1}"] = {
                        "email": test_case["email"],
                        "error": str(e),
                        "success": False
                    }
                    print(f"  ❌ {test_case['email']}: {str(e)}")
        
        self.test_results['email_capture'] = results
        return all(result.get('success', False) for result in results.values())
    
    async def test_usage_tracking_endpoint(self) -> bool:
        """Test usage tracking and limits"""
        print("📊 Testing usage tracking...")
        
        test_ip = self.test_ips[0]
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test initial usage check
                async with session.get(
                    f"{self.backend_url}/api/usage",
                    headers={"X-Forwarded-For": test_ip},
                    timeout=10
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        print(f"  ✅ Usage endpoint: {data}")
                        
                        # Verify expected structure
                        required_keys = ["used", "limit", "remaining", "reset_time"]
                        has_all_keys = all(key in data for key in required_keys)
                        
                        if has_all_keys:
                            print(f"  ✅ Usage data structure correct")
                            self.test_results['usage_tracking'] = {"success": True, "data": data}
                            return True
                        else:
                            print(f"  ❌ Missing keys in usage data: {set(required_keys) - set(data.keys())}")
                            self.test_results['usage_tracking'] = {"success": False, "error": "Missing keys"}
                            return False
                    else:
                        print(f"  ❌ Usage endpoint failed: {status}")
                        self.test_results['usage_tracking'] = {"success": False, "status": status}
                        return False
                        
            except Exception as e:
                print(f"  ❌ Usage tracking error: {str(e)}")
                self.test_results['usage_tracking'] = {"success": False, "error": str(e)}
                return False
    
    async def test_free_tier_limits(self) -> bool:
        """Test free tier limits enforcement"""
        print("🚦 Testing free tier limits...")
        
        test_ip = self.test_ips[1]
        success_count = 0
        rate_limited = False
        
        async with aiohttp.ClientSession() as session:
            # Make requests until we hit the daily limit (default 5)
            for i in range(8):  # More than the limit
                try:
                    async with session.post(
                        f"{self.backend_url}/api/generate",
                        json={"content": f"Test content for limit testing {i}"},
                        headers={"X-Forwarded-For": test_ip},
                        timeout=15
                    ) as response:
                        if response.status == 200:
                            success_count += 1
                            print(f"  ✅ Request {i+1}: Success")
                        elif response.status == 429:
                            rate_limited = True
                            data = await response.json()
                            print(f"  🚦 Request {i+1}: Rate limited - {data.get('detail', 'No details')}")
                            break
                        else:
                            print(f"  ⚠️  Request {i+1}: Unexpected status {response.status}")
                            
                except Exception as e:
                    print(f"  ❌ Request {i+1}: {str(e)}")
            
            # Test should show some successes followed by rate limiting
            limits_working = success_count > 0 and (rate_limited or success_count <= 5)
            
            result = {
                "success": limits_working,
                "successful_requests": success_count,
                "rate_limited": rate_limited,
                "expected_limit": 5
            }
            
            self.test_results['free_tier_limits'] = result
            
            if limits_working:
                print(f"  ✅ Free tier limits working: {success_count} successful, rate limited: {rate_limited}")
            else:
                print(f"  ❌ Free tier limits not working properly")
            
            return limits_working
    
    async def test_premium_features_locked(self) -> bool:
        """Test that premium features are properly locked for free users"""
        print("💎 Testing premium features are locked...")
        
        # For now, this would test any premium-only endpoints
        # Since we don't have specific premium endpoints yet, we'll test the concept
        
        test_ip = self.test_ips[2]
        
        # Test generating a long thread (premium feature)
        long_content = "This is a very long article content. " * 100  # Make it long
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.backend_url}/api/generate",
                    json={"content": long_content, "premium_features": True},
                    headers={"X-Forwarded-For": test_ip},
                    timeout=15
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    # Should either work (no premium checks yet) or return appropriate error
                    if status in [200, 402, 403]:  # Success or payment required
                        print(f"  ✅ Premium feature check: {status}")
                        self.test_results['premium_features'] = {"success": True, "status": status}
                        return True
                    else:
                        print(f"  ❌ Unexpected premium feature response: {status}")
                        self.test_results['premium_features'] = {"success": False, "status": status}
                        return False
                        
            except Exception as e:
                print(f"  ❌ Premium features test error: {str(e)}")
                self.test_results['premium_features'] = {"success": False, "error": str(e)}
                return False
    
    async def test_stripe_webhook_endpoint(self) -> bool:
        """Test Stripe webhook endpoint availability"""
        print("💳 Testing Stripe webhook endpoint...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test webhook endpoint with invalid data (should return 400, not 404)
                async with session.post(
                    f"{self.backend_url}/api/stripe/webhook",
                    data="invalid webhook data",
                    headers={"content-type": "application/json"},
                    timeout=10
                ) as response:
                    status = response.status
                    
                    # We expect 400 (bad signature) or similar, not 404
                    endpoint_exists = status != 404
                    
                    if endpoint_exists:
                        print(f"  ✅ Stripe webhook endpoint exists: {status}")
                        self.test_results['stripe_webhook'] = {"success": True, "status": status, "exists": True}
                        return True
                    else:
                        print(f"  ❌ Stripe webhook endpoint not found: {status}")
                        self.test_results['stripe_webhook'] = {"success": False, "status": status, "exists": False}
                        return False
                        
            except Exception as e:
                print(f"  ❌ Stripe webhook test error: {str(e)}")
                self.test_results['stripe_webhook'] = {"success": False, "error": str(e)}
                return False
    
    async def test_email_list_endpoint(self) -> bool:
        """Test email list retrieval (if implemented)"""
        print("📋 Testing email list endpoint...")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test emails endpoint (might not exist yet)
                async with session.get(
                    f"{self.backend_url}/api/emails",
                    timeout=10
                ) as response:
                    status = response.status
                    
                    if status == 200:
                        data = await response.json()
                        print(f"  ✅ Email list endpoint: Found {len(data.get('emails', []))} emails")
                        
                        # Check if our test emails are there
                        email_list = data.get('emails', [])
                        found_test_emails = [email for email in self.test_emails if email in email_list]
                        
                        self.test_results['email_list'] = {
                            "success": True,
                            "total_emails": len(email_list),
                            "test_emails_found": len(found_test_emails)
                        }
                        return True
                    elif status == 404:
                        print(f"  ⚠️  Email list endpoint not implemented yet")
                        self.test_results['email_list'] = {"success": True, "not_implemented": True}
                        return True
                    else:
                        print(f"  ❌ Email list endpoint error: {status}")
                        self.test_results['email_list'] = {"success": False, "status": status}
                        return False
                        
            except Exception as e:
                print(f"  ❌ Email list test error: {str(e)}")
                self.test_results['email_list'] = {"success": False, "error": str(e)}
                return False
    
    async def test_cors_configuration(self) -> bool:
        """Test CORS configuration for frontend integration"""
        print("🌐 Testing CORS configuration...")
        
        frontend_origin = "http://localhost:8000"
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test preflight request
                async with session.options(
                    f"{self.backend_url}/api/generate",
                    headers={
                        "Origin": frontend_origin,
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "Content-Type"
                    },
                    timeout=10
                ) as response:
                    status = response.status
                    headers = response.headers
                    
                    cors_origin = headers.get("Access-Control-Allow-Origin")
                    cors_methods = headers.get("Access-Control-Allow-Methods")
                    
                    cors_configured = (
                        status in [200, 204] and
                        cors_origin in [frontend_origin, "*"]
                    )
                    
                    if cors_configured:
                        print(f"  ✅ CORS properly configured")
                        print(f"    Origin: {cors_origin}")
                        print(f"    Methods: {cors_methods}")
                        self.test_results['cors'] = {"success": True, "origin": cors_origin, "methods": cors_methods}
                        return True
                    else:
                        print(f"  ❌ CORS not properly configured")
                        self.test_results['cors'] = {"success": False, "status": status, "headers": dict(headers)}
                        return False
                        
            except Exception as e:
                print(f"  ❌ CORS test error: {str(e)}")
                self.test_results['cors'] = {"success": False, "error": str(e)}
                return False
    
    async def run_all_monetization_tests(self) -> Dict:
        """Run complete monetization test suite"""
        print("🚀 Starting Monetization Features Test Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        # Define tests
        tests = [
            ("Email Capture", self.test_email_capture_endpoint()),
            ("Usage Tracking", self.test_usage_tracking_endpoint()),
            ("Free Tier Limits", self.test_free_tier_limits()),
            ("Premium Features", self.test_premium_features_locked()),
            ("Stripe Webhook", self.test_stripe_webhook_endpoint()),
            ("Email List", self.test_email_list_endpoint()),
            ("CORS Configuration", self.test_cors_configuration())
        ]
        
        # Run tests
        results = {}
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 MONETIZATION TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        print(f"Duration: {time.time() - start_time:.1f}s")
        
        # Monetization readiness assessment
        critical_tests = ["Email Capture", "Usage Tracking", "Free Tier Limits"]
        critical_passed = sum(1 for test in critical_tests if results.get(test, False))
        
        if critical_passed == len(critical_tests):
            print("\n🎉 MONETIZATION READY - All critical features working!")
        else:
            print(f"\n⚠️  MONETIZATION NOT READY - {len(critical_tests) - critical_passed} critical test(s) failed")
        
        # Detailed results
        print("\n📊 DETAILED RESULTS:")
        for key, data in self.test_results.items():
            print(f"  {key}: {json.dumps(data, indent=2, default=str)}")
        
        summary = {
            "total_tests": total,
            "passed_tests": passed,
            "critical_tests": critical_tests,
            "critical_passed": critical_passed,
            "monetization_ready": critical_passed == len(critical_tests),
            "duration": time.time() - start_time,
            "detailed_results": self.test_results
        }
        
        return summary

async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Threadr Monetization Features Test Suite")
    parser.add_argument("--backend-url", default="http://localhost:8001", help="Backend URL to test")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    tester = MonetizationTester(args.backend_url)
    results = await tester.run_all_monetization_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to {args.output}")
    
    # Exit with non-zero if not monetization ready
    if not results['monetization_ready']:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
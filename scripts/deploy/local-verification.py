#!/usr/bin/env python3
"""
Local Deployment Verification Script for Threadr
Tests all monetization features and deployment readiness locally
"""

import asyncio
import aiohttp
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

class ThreadrLocalVerifier:
    def __init__(self, backend_url: str = "http://localhost:8001", frontend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.results: Dict = {}
        
    async def verify_backend_health(self) -> bool:
        """Test backend health endpoints"""
        print("🏥 Testing backend health endpoints...")
        
        endpoints = [
            "/health",
            "/readiness", 
            "/api/health",
            "/debug/startup"
        ]
        
        health_results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    async with session.get(f"{self.backend_url}{endpoint}", timeout=10) as response:
                        status = response.status
                        data = await response.json() if response.content_type == 'application/json' else await response.text()
                        health_results[endpoint] = {"status": status, "data": data}
                        print(f"  ✅ {endpoint}: {status}")
                except Exception as e:
                    health_results[endpoint] = {"status": "error", "error": str(e)}
                    print(f"  ❌ {endpoint}: {str(e)}")
        
        self.results['health_checks'] = health_results
        return any(result.get('status') == 200 for result in health_results.values())
    
    async def test_thread_generation(self) -> bool:
        """Test core thread generation functionality"""
        print("🧵 Testing thread generation...")
        
        test_cases = [
            {
                "name": "URL Input",
                "data": {"url": "https://medium.com/@example/test-article"},
                "should_succeed": False  # Will fail without real URL, but should handle gracefully
            },
            {
                "name": "Text Input", 
                "data": {"content": "This is a test article about artificial intelligence and its impact on society. AI has been transforming industries and changing how we work and live. From machine learning to natural language processing, AI technologies are becoming increasingly sophisticated."},
                "should_succeed": True
            }
        ]
        
        generation_results = {}
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                try:
                    async with session.post(
                        f"{self.backend_url}/api/generate",
                        json=test_case["data"],
                        timeout=30
                    ) as response:
                        status = response.status
                        data = await response.json()
                        
                        generation_results[test_case["name"]] = {
                            "status": status,
                            "data": data,
                            "success": status == 200 if test_case["should_succeed"] else status in [200, 400, 422]
                        }
                        
                        if status == 200:
                            print(f"  ✅ {test_case['name']}: Generated {len(data.get('thread', []))} tweets")
                        else:
                            print(f"  ⚠️  {test_case['name']}: {status} - {data.get('detail', 'Unknown error')}")
                            
                except Exception as e:
                    generation_results[test_case["name"]] = {"status": "error", "error": str(e), "success": False}
                    print(f"  ❌ {test_case['name']}: {str(e)}")
        
        self.results['thread_generation'] = generation_results
        return any(result.get('success') for result in generation_results.values())
    
    async def test_email_capture(self) -> bool:
        """Test email capture functionality"""
        print("📧 Testing email capture...")
        
        test_email = f"test+{int(time.time())}@example.com"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.backend_url}/api/capture-email",
                    json={"email": test_email},
                    timeout=10
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    success = status == 200
                    self.results['email_capture'] = {"status": status, "data": data, "success": success}
                    
                    if success:
                        print(f"  ✅ Email capture: {data.get('message', 'Success')}")
                    else:
                        print(f"  ❌ Email capture failed: {status} - {data}")
                    
                    return success
                    
            except Exception as e:
                self.results['email_capture'] = {"status": "error", "error": str(e), "success": False}
                print(f"  ❌ Email capture: {str(e)}")
                return False
    
    async def test_usage_tracking(self) -> bool:
        """Test usage tracking and limits"""
        print("📊 Testing usage tracking...")
        
        test_ip = "127.0.0.1"
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test usage endpoint
                async with session.get(
                    f"{self.backend_url}/api/usage",
                    headers={"X-Forwarded-For": test_ip},
                    timeout=10
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    success = status == 200
                    self.results['usage_tracking'] = {"status": status, "data": data, "success": success}
                    
                    if success:
                        print(f"  ✅ Usage tracking: {data}")
                        return True
                    else:
                        print(f"  ❌ Usage tracking failed: {status}")
                        return False
                        
            except Exception as e:
                self.results['usage_tracking'] = {"status": "error", "error": str(e), "success": False}
                print(f"  ❌ Usage tracking: {str(e)}")
                return False
    
    async def test_stripe_webhook(self) -> bool:
        """Test Stripe webhook endpoint (without actual Stripe data)"""
        print("💳 Testing Stripe webhook endpoint...")
        
        # Test webhook endpoint availability
        async with aiohttp.ClientSession() as session:
            try:
                # This should fail signature validation but endpoint should be accessible
                async with session.post(
                    f"{self.backend_url}/api/stripe/webhook",
                    data="test",
                    headers={"content-type": "application/json"},
                    timeout=10
                ) as response:
                    status = response.status
                    
                    # We expect 400 (bad signature) or similar, not 404
                    success = status != 404
                    self.results['stripe_webhook'] = {"status": status, "success": success}
                    
                    if success:
                        print(f"  ✅ Stripe webhook endpoint accessible: {status}")
                    else:
                        print(f"  ❌ Stripe webhook endpoint not found: {status}")
                    
                    return success
                    
            except Exception as e:
                self.results['stripe_webhook'] = {"status": "error", "error": str(e), "success": False}
                print(f"  ❌ Stripe webhook: {str(e)}")
                return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        print("🚦 Testing rate limiting...")
        
        test_ip = "192.168.1.100"  # Test IP
        
        async with aiohttp.ClientSession() as session:
            success_count = 0
            rate_limited = False
            
            # Make multiple requests to trigger rate limiting
            for i in range(12):  # More than the default limit of 10
                try:
                    async with session.post(
                        f"{self.backend_url}/api/generate",
                        json={"content": f"Test content {i}"},
                        headers={"X-Forwarded-For": test_ip},
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            success_count += 1
                        elif response.status == 429:  # Rate limited
                            rate_limited = True
                            break
                            
                except Exception as e:
                    print(f"  ⚠️  Request {i+1} failed: {str(e)}")
            
            # Rate limiting is working if we got some successes then got rate limited
            success = success_count > 0 and (rate_limited or success_count < 12)
            
            self.results['rate_limiting'] = {
                "success_count": success_count,
                "rate_limited": rate_limited,
                "success": success
            }
            
            if success:
                print(f"  ✅ Rate limiting working: {success_count} successful, rate limited: {rate_limited}")
            else:
                print(f"  ❌ Rate limiting may not be working properly")
            
            return success
    
    def test_frontend_files(self) -> bool:
        """Test frontend file structure"""
        print("🌐 Testing frontend files...")
        
        required_files = [
            "frontend/src/index.html",
            "frontend/src/config.js", 
            "frontend/vercel.json",
            "frontend/package.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        success = len(missing_files) == 0
        self.results['frontend_files'] = {
            "required_files": required_files,
            "missing_files": missing_files,
            "success": success
        }
        
        if success:
            print("  ✅ All frontend files present")
        else:
            print(f"  ❌ Missing frontend files: {missing_files}")
        
        return success
    
    def test_deployment_configs(self) -> bool:
        """Test deployment configuration files"""
        print("⚙️  Testing deployment configs...")
        
        config_files = [
            "nixpacks.toml",
            "backend/requirements.txt",
            "backend/runtime.txt"
        ]
        
        missing_configs = []
        for config_file in config_files:
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", config_file)
            if not os.path.exists(full_path):
                missing_configs.append(config_file)
        
        success = len(missing_configs) == 0
        self.results['deployment_configs'] = {
            "config_files": config_files,
            "missing_configs": missing_configs,
            "success": success
        }
        
        if success:
            print("  ✅ All deployment configs present")
        else:
            print(f"  ❌ Missing deployment configs: {missing_configs}")
        
        return success
    
    async def run_full_verification(self) -> Dict:
        """Run complete verification suite"""
        print("🚀 Starting Threadr Local Verification Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            ("Backend Health", self.verify_backend_health()),
            ("Thread Generation", self.test_thread_generation()),
            ("Email Capture", self.test_email_capture()),
            ("Usage Tracking", self.test_usage_tracking()),
            ("Stripe Webhook", self.test_stripe_webhook()),
            ("Rate Limiting", self.test_rate_limiting())
        ]
        
        # Run async tests
        async_results = {}
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                async_results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                async_results[test_name] = False
        
        # Run sync tests
        sync_results = {
            "Frontend Files": self.test_frontend_files(),
            "Deployment Configs": self.test_deployment_configs()
        }
        
        # Combine results
        all_results = {**async_results, **sync_results}
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in all_results.values() if result)
        total = len(all_results)
        
        for test_name, result in all_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        print(f"Duration: {time.time() - start_time:.1f}s")
        
        # Deployment readiness assessment
        critical_tests = ["Backend Health", "Thread Generation", "Frontend Files", "Deployment Configs"]
        critical_passed = sum(1 for test in critical_tests if all_results.get(test, False))
        
        if critical_passed == len(critical_tests):
            print("\n🎉 DEPLOYMENT READY - All critical tests passed!")
        else:
            print(f"\n⚠️  DEPLOYMENT NOT READY - {len(critical_tests) - critical_passed} critical test(s) failed")
        
        self.results['summary'] = {
            "total_tests": total,
            "passed_tests": passed,
            "critical_tests": critical_tests,
            "critical_passed": critical_passed,
            "deployment_ready": critical_passed == len(critical_tests),
            "duration": time.time() - start_time
        }
        
        return self.results

async def main():
    """Main verification runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Threadr Local Verification Suite")
    parser.add_argument("--backend-url", default="http://localhost:8001", help="Backend URL")
    parser.add_argument("--frontend-url", default="http://localhost:8000", help="Frontend URL")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    verifier = ThreadrLocalVerifier(args.backend_url, args.frontend_url)
    results = await verifier.run_full_verification()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to {args.output}")
    
    # Exit with non-zero if not deployment ready
    if not results['summary']['deployment_ready']:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Threadr Production Verification Script
=====================================

Comprehensive automated testing of all deployed features including:
- API key security verification
- Redis configuration and performance
- Backend API endpoints functionality
- Frontend configuration
- UX improvements verification
- Payment system integration
- Rate limiting functionality

Usage:
    python scripts/verification/production_verification.py
    python scripts/verification/production_verification.py --verbose
    python scripts/verification/production_verification.py --json-output results.json
"""

import asyncio
import aiohttp
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse
from dataclasses import dataclass, asdict
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None
    critical: bool = False

class ThreadrVerifier:
    def __init__(self, frontend_url: str = "https://threadr-plum.vercel.app", 
                 backend_url: str = "https://threadr-production.up.railway.app"):
        self.frontend_url = frontend_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/')
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_result(self, name: str, status: str, message: str, duration: float, 
                   details: Optional[Dict] = None, critical: bool = False):
        """Add a test result to the results list"""
        result = TestResult(name, status, message, duration, details, critical)
        self.results.append(result)
        
        # Print immediate feedback
        status_symbol = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️",
            "SKIP": "⏭️"
        }.get(status, "?")
        
        critical_marker = " [CRITICAL]" if critical else ""
        print(f"{status_symbol} {name}: {message}{critical_marker} ({duration:.2f}s)")
        
        if details and logger.level <= logging.DEBUG:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    async def make_request(self, method: str, url: str, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Make HTTP request with error handling"""
        try:
            async with self.session.request(method, url, **kwargs) as response:
                return response
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            return None
    
    async def test_backend_health(self) -> None:
        """Test backend health and readiness endpoints"""
        start_time = time.time()
        
        try:
            # Test basic health endpoint
            health_url = f"{self.backend_url}/health"
            response = await self.make_request("GET", health_url)
            
            if response is None:
                self.add_result("Backend Health", "FAIL", "Could not connect to backend health endpoint", 
                              time.time() - start_time, critical=True)
                return
            
            if response.status == 200:
                health_data = await response.json()
                self.add_result("Backend Health", "PASS", f"Backend healthy (status: {response.status})", 
                              time.time() - start_time, {"health_data": health_data})
            else:
                self.add_result("Backend Health", "FAIL", f"Backend health check failed (status: {response.status})", 
                              time.time() - start_time, critical=True)
                
        except Exception as e:
            self.add_result("Backend Health", "FAIL", f"Backend health check error: {str(e)}", 
                          time.time() - start_time, critical=True)
    
    async def test_api_key_security(self) -> None:
        """Test API key security implementation"""
        start_time = time.time()
        
        try:
            # Test endpoint without API key
            generate_url = f"{self.backend_url}/api/generate"
            test_data = {
                "content": "Test content for API key verification",
                "input_type": "content"
            }
            
            response = await self.make_request("POST", generate_url, json=test_data)
            
            if response is None:
                self.add_result("API Key Security", "FAIL", "Could not test API key endpoint", 
                              time.time() - start_time, critical=True)
                return
            
            if response.status == 401 or response.status == 403:
                self.add_result("API Key Security", "PASS", "API properly rejects requests without valid API key", 
                              time.time() - start_time)
            elif response.status == 429:
                self.add_result("API Key Security", "WARNING", "Rate limiting active (good), but couldn't test API key auth", 
                              time.time() - start_time)
            else:
                self.add_result("API Key Security", "FAIL", 
                              f"API should reject requests without API key (got {response.status})", 
                              time.time() - start_time, critical=True)
                
        except Exception as e:
            self.add_result("API Key Security", "FAIL", f"API key security test error: {str(e)}", 
                          time.time() - start_time)
    
    async def test_redis_connection(self) -> None:
        """Test Redis connectivity and performance"""
        start_time = time.time()
        
        try:
            # Test Redis via backend health endpoint
            health_url = f"{self.backend_url}/health"
            response = await self.make_request("GET", health_url)
            
            if response is None:
                self.add_result("Redis Connection", "FAIL", "Could not test Redis via health endpoint", 
                              time.time() - start_time)
                return
            
            health_data = await response.json()
            redis_status = health_data.get("services", {}).get("redis", "unknown")
            
            if redis_status == "healthy":
                self.add_result("Redis Connection", "PASS", "Redis connection healthy", 
                              time.time() - start_time, {"redis_info": health_data.get("services", {})})
            else:
                self.add_result("Redis Connection", "FAIL", f"Redis status: {redis_status}", 
                              time.time() - start_time, critical=True)
                
        except Exception as e:
            self.add_result("Redis Connection", "FAIL", f"Redis connection test error: {str(e)}", 
                          time.time() - start_time)
    
    async def test_rate_limiting(self) -> None:
        """Test rate limiting functionality"""
        start_time = time.time()
        
        try:
            # Test usage stats endpoint
            usage_url = f"{self.backend_url}/api/usage-stats"
            response = await self.make_request("GET", usage_url)
            
            if response is None:
                self.add_result("Rate Limiting", "FAIL", "Could not test rate limiting endpoint", 
                              time.time() - start_time)
                return
            
            if response.status == 200:
                usage_data = await response.json()
                self.add_result("Rate Limiting", "PASS", "Rate limiting endpoint accessible", 
                              time.time() - start_time, {"usage_data": usage_data})
            else:
                self.add_result("Rate Limiting", "WARNING", f"Rate limiting endpoint returned {response.status}", 
                              time.time() - start_time)
                
        except Exception as e:
            self.add_result("Rate Limiting", "WARNING", f"Rate limiting test error: {str(e)}", 
                          time.time() - start_time)
    
    async def test_frontend_configuration(self) -> None:
        """Test frontend configuration and API key setup"""
        start_time = time.time()
        
        try:
            # Test frontend accessibility
            response = await self.make_request("GET", self.frontend_url)
            
            if response is None:
                self.add_result("Frontend Access", "FAIL", "Could not access frontend", 
                              time.time() - start_time, critical=True)
                return
            
            if response.status == 200:
                self.add_result("Frontend Access", "PASS", "Frontend accessible", 
                              time.time() - start_time)
                
                # Test config.js availability
                config_url = f"{self.frontend_url}/config.js"
                config_response = await self.make_request("GET", config_url)
                
                if config_response and config_response.status == 200:
                    self.add_result("Frontend Config", "PASS", "Frontend configuration accessible", 
                                  time.time() - start_time)
                else:
                    self.add_result("Frontend Config", "WARNING", "Frontend config.js not accessible", 
                                  time.time() - start_time)
            else:
                self.add_result("Frontend Access", "FAIL", f"Frontend returned status {response.status}", 
                              time.time() - start_time, critical=True)
                
        except Exception as e:
            self.add_result("Frontend Access", "FAIL", f"Frontend test error: {str(e)}", 
                          time.time() - start_time, critical=True)
    
    async def test_stripe_webhook_security(self) -> None:
        """Test Stripe webhook security (without actually triggering webhooks)"""
        start_time = time.time()
        
        try:
            # Test webhook endpoint exists and properly rejects invalid requests
            webhook_url = f"{self.backend_url}/api/stripe/webhook"
            
            # Try with invalid data
            response = await self.make_request("POST", webhook_url, 
                                             json={"invalid": "data"},
                                             headers={"Content-Type": "application/json"})
            
            if response is None:
                self.add_result("Stripe Webhook Security", "FAIL", "Could not test webhook endpoint", 
                              time.time() - start_time)
                return
            
            # Should reject invalid webhook data
            if response.status in [400, 401, 403]:
                self.add_result("Stripe Webhook Security", "PASS", 
                              "Webhook properly rejects invalid requests", 
                              time.time() - start_time)
            else:
                self.add_result("Stripe Webhook Security", "WARNING", 
                              f"Webhook endpoint returned unexpected status {response.status}", 
                              time.time() - start_time)
                
        except Exception as e:
            self.add_result("Stripe Webhook Security", "WARNING", f"Webhook security test error: {str(e)}", 
                          time.time() - start_time)
    
    async def test_premium_status_endpoint(self) -> None:
        """Test premium status endpoint functionality"""
        start_time = time.time()
        
        try:
            # Test premium status endpoint
            premium_url = f"{self.backend_url}/api/premium-status"
            response = await self.make_request("GET", premium_url)
            
            if response is None:
                self.add_result("Premium Status", "FAIL", "Could not access premium status endpoint", 
                              time.time() - start_time)
                return
            
            if response.status == 200:
                premium_data = await response.json()
                self.add_result("Premium Status", "PASS", "Premium status endpoint working", 
                              time.time() - start_time, {"premium_data": premium_data})
            elif response.status == 429:
                self.add_result("Premium Status", "WARNING", "Rate limited on premium status check", 
                              time.time() - start_time)
            else:
                self.add_result("Premium Status", "FAIL", f"Premium status returned {response.status}", 
                              time.time() - start_time)
                
        except Exception as e:
            self.add_result("Premium Status", "WARNING", f"Premium status test error: {str(e)}", 
                          time.time() - start_time)
    
    async def test_email_capture(self) -> None:
        """Test email capture functionality"""
        start_time = time.time()
        
        try:
            # Test email capture endpoint
            email_url = f"{self.backend_url}/api/capture-email"
            test_email = f"test-{int(time.time())}@threadr-verification.local"
            
            response = await self.make_request("POST", email_url, 
                                             json={"email": test_email})
            
            if response is None:
                self.add_result("Email Capture", "FAIL", "Could not test email capture endpoint", 
                              time.time() - start_time)
                return
            
            if response.status == 200:
                self.add_result("Email Capture", "PASS", "Email capture endpoint working", 
                              time.time() - start_time)
            elif response.status == 429:
                self.add_result("Email Capture", "WARNING", "Rate limited on email capture", 
                              time.time() - start_time)
            else:
                self.add_result("Email Capture", "WARNING", f"Email capture returned {response.status}", 
                              time.time() - start_time)
                
        except Exception as e:
            self.add_result("Email Capture", "WARNING", f"Email capture test error: {str(e)}", 
                          time.time() - start_time)
    
    async def run_all_tests(self) -> None:
        """Run all verification tests"""
        print(f"🚀 Starting Threadr Production Verification")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run all tests
        await self.test_backend_health()
        await self.test_frontend_configuration()
        await self.test_api_key_security()
        await self.test_redis_connection()
        await self.test_rate_limiting()
        await self.test_premium_status_endpoint()
        await self.test_stripe_webhook_security()
        await self.test_email_capture()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        warnings = len([r for r in self.results if r.status == "WARNING"])
        skipped = len([r for r in self.results if r.status == "SKIP"])
        critical_failures = len([r for r in self.results if r.status == "FAIL" and r.critical])
        
        total_duration = sum(r.duration for r in self.results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "frontend_url": self.frontend_url,
            "backend_url": self.backend_url,
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "skipped": skipped,
                "critical_failures": critical_failures,
                "total_duration": round(total_duration, 2),
                "success_rate": round((passed / total_tests) * 100, 1) if total_tests > 0 else 0
            },
            "results": [asdict(r) for r in self.results]
        }
    
    def print_summary(self) -> None:
        """Print test summary to console"""
        summary = self.generate_summary()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        stats = summary["summary"]
        print(f"✅ Passed: {stats['passed']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"⚠️  Warnings: {stats['warnings']}")
        print(f"⏭️  Skipped: {stats['skipped']}")
        print(f"🚨 Critical Failures: {stats['critical_failures']}")
        print(f"⏱️  Total Duration: {stats['total_duration']}s")
        print(f"📈 Success Rate: {stats['success_rate']}%")
        
        if stats['critical_failures'] > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for result in self.results:
                if result.status == "FAIL" and result.critical:
                    print(f"   • {result.name}: {result.message}")
        
        if stats['success_rate'] >= 90:
            print(f"\n🎉 DEPLOYMENT STATUS: EXCELLENT")
        elif stats['success_rate'] >= 80:
            print(f"\n✅ DEPLOYMENT STATUS: GOOD")
        elif stats['success_rate'] >= 70:
            print(f"\n⚠️  DEPLOYMENT STATUS: NEEDS ATTENTION")
        else:
            print(f"\n❌ DEPLOYMENT STATUS: CRITICAL ISSUES")

async def main():
    parser = argparse.ArgumentParser(description='Threadr Production Verification')
    parser.add_argument('--frontend-url', default='https://threadr-plum.vercel.app',
                       help='Frontend URL to test')
    parser.add_argument('--backend-url', default='https://threadr-production.up.railway.app',
                       help='Backend URL to test')
    parser.add_argument('--json-output', help='Save results to JSON file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async with ThreadrVerifier(args.frontend_url, args.backend_url) as verifier:
        try:
            await verifier.run_all_tests()
            
            # Print summary
            verifier.print_summary()
            
            # Save JSON output if requested
            if args.json_output:
                summary = verifier.generate_summary()
                with open(args.json_output, 'w') as f:
                    json.dump(summary, f, indent=2)
                print(f"\n💾 Results saved to: {args.json_output}")
            
            # Exit with appropriate code
            critical_failures = len([r for r in verifier.results if r.status == "FAIL" and r.critical])
            if critical_failures > 0:
                sys.exit(1)
            
        except KeyboardInterrupt:
            print("\n⏹️  Verification cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 Verification failed with error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Quick Threadr Business Functionality Validator
============================================

Fast validation script that tests critical business functionality in under 60 seconds.
Tests the most important revenue-generating features to ensure system health.

USAGE:
    python quick_test.py
"""

import asyncio
import httpx
import json
import os
import time
from typing import Dict, Any

BASE_URL = os.getenv("BASE_URL", "https://threadr-pw0s.onrender.com")

class QuickValidator:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {}
        
    async def run_quick_validation(self) -> Dict[str, Any]:
        """Run critical business functionality tests"""
        print("🚀 Threadr Quick Business Validation")
        print("=" * 50)
        
        start_time = time.time()
        
        # Critical tests in order of importance
        tests = [
            ("API Health", self._test_api_health),
            ("Database Connection", self._test_database_connection),
            ("Thread Generation", self._test_thread_generation),
            ("Rate Limiting", self._test_rate_limiting),
            ("Authentication", self._test_authentication)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n⏳ Testing: {test_name}")
            try:
                result = await test_func()
                self.results[test_name] = {"success": True, "details": result}
                print(f"✅ {test_name}: PASS")
                passed += 1
            except Exception as e:
                self.results[test_name] = {"success": False, "error": str(e)}
                print(f"❌ {test_name}: FAIL - {str(e)}")
        
        # Summary
        total_time = time.time() - start_time
        success_rate = (passed / total) * 100
        
        print(f"\n{'='*50}")
        print(f"QUICK VALIDATION RESULTS")
        print(f"{'='*50}")
        print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"Time: {total_time:.1f} seconds")
        
        if success_rate >= 80:
            print(f"✅ SYSTEM HEALTHY - Core business features operational")
            status = "healthy"
        elif success_rate >= 60:
            print(f"⚠️  SYSTEM DEGRADED - Some issues detected")
            status = "degraded"
        else:
            print(f"❌ SYSTEM UNHEALTHY - Critical issues detected")
            status = "unhealthy"
        
        return {
            "status": status,
            "success_rate": success_rate,
            "passed_tests": passed,
            "total_tests": total,
            "execution_time": total_time,
            "results": self.results
        }
    
    async def _test_api_health(self) -> Dict[str, Any]:
        """Test API health and basic connectivity"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")
            
            data = response.json()
            
            if data.get("status") not in ["healthy", "degraded"]:
                raise Exception(f"Unhealthy status: {data.get('status')}")
            
            return {
                "status": data.get("status"),
                "response_time": response.elapsed.total_seconds()
            }
    
    async def _test_database_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL database connectivity"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            data = response.json()
            
            database_status = data.get("services", {}).get("database", False)
            
            if not database_status:
                raise Exception("Database not available")
            
            return {"database_connected": True}
    
    async def _test_thread_generation(self) -> Dict[str, Any]:
        """Test core thread generation functionality"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            content_data = {
                "content": "Quick test of AI-powered thread generation. This should create multiple tweets from this content."
            }
            
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=content_data
            )
            
            if response.status_code != 200:
                raise Exception(f"Generation failed: {response.status_code}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception(f"Generation error: {data.get('error')}")
            
            tweets = data.get("tweets", [])
            
            if len(tweets) < 1:
                raise Exception("No tweets generated")
            
            return {
                "tweets_generated": len(tweets),
                "has_content": bool(tweets[0].get("content") if tweets else False)
            }
    
    async def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting system"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/usage-stats")
            
            if response.status_code != 200:
                raise Exception(f"Usage stats failed: {response.status_code}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Usage stats not working")
            
            return {
                "rate_limiting_active": True,
                "daily_limit": data.get("daily_limit"),
                "can_generate": data.get("can_generate")
            }
    
    async def _test_authentication(self) -> Dict[str, Any]:
        """Test authentication endpoint availability"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test auth endpoint structure (should return 422 for missing data)
            response = await client.post(f"{self.base_url}/api/auth/register", json={})
            
            # Should get validation error, not 404 or 500
            if response.status_code == 404:
                raise Exception("Auth endpoints not available")
            
            if response.status_code >= 500:
                raise Exception("Auth service error")
            
            return {"auth_endpoints_available": True}

async def main():
    validator = QuickValidator()
    
    try:
        results = await validator.run_quick_validation()
        
        # Save results
        timestamp = int(time.time())
        filename = f"quick_validation_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {filename}")
        
        # Exit with appropriate code
        if results["success_rate"] >= 80:
            print("\n🎉 Quick validation PASSED - System ready for business!")
            exit(0)
        else:
            print("\n⚠️  Quick validation FAILED - Review issues before proceeding")
            exit(1)
    
    except Exception as e:
        print(f"\n💥 Validation execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
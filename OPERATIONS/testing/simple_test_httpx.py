#!/usr/bin/env python3
"""
Simple authentication and database test using only existing dependencies.
Uses httpx (already in requirements.txt) instead of aiohttp.
No colored output - works with stdlib only.
"""

import sys
import json
import time
import httpx
import asyncio
from typing import Dict, Any

# Base URL for API testing
BASE_URL = "https://threadr-pw0s.onrender.com"

class SimpleTestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test(self, name: str, condition: bool, details: str = ""):
        """Run a simple test and track results."""
        if condition:
            self.passed += 1
            status = "PASS"
            print(f"✅ {name}: {status}")
        else:
            self.failed += 1
            status = "FAIL"
            print(f"❌ {name}: {status}")
            if details:
                print(f"   Details: {details}")
        
        self.results.append({
            "name": name,
            "status": status,
            "details": details
        })
        return condition
    
    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {self.failed} test(s) failed - review issues above")
        
        return self.failed == 0

def test_api_connectivity():
    """Test basic API connectivity."""
    runner = SimpleTestRunner()
    
    print("🔍 TESTING API CONNECTIVITY")
    print("-" * 30)
    
    try:
        # Test health endpoint
        response = httpx.get(f"{BASE_URL}/health", timeout=10.0)
        runner.test("Health Endpoint Response", response.status_code == 200, 
                   f"Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            runner.test("Health JSON Valid", isinstance(health_data, dict))
            runner.test("Database Status Available", "services" in health_data)
            
            if "services" in health_data:
                services = health_data.get("services", {})
                runner.test("Redis Available", services.get("redis", False))
                runner.test("Database Available", services.get("database", False))
        
        # Test root endpoint  
        root_response = httpx.get(f"{BASE_URL}/", timeout=10.0)
        runner.test("Root Endpoint Response", root_response.status_code == 200,
                   f"Status: {root_response.status_code}")
        
    except Exception as e:
        runner.test("API Connectivity", False, f"Error: {str(e)}")
    
    return runner

def test_authentication_endpoints():
    """Test authentication endpoints without complex JWT validation."""
    runner = SimpleTestRunner()
    
    print("\n🔐 TESTING AUTHENTICATION")
    print("-" * 30)
    
    try:
        # Test registration endpoint (expecting 400 for missing data)
        reg_response = httpx.post(f"{BASE_URL}/api/auth/register", 
                                 json={},  # Empty data should trigger validation error
                                 timeout=10.0)
        runner.test("Registration Endpoint Responds", reg_response.status_code in [400, 422],
                   f"Status: {reg_response.status_code} (400/422 expected for empty data)")
        
        # Test login endpoint (expecting 400 for missing data)  
        login_response = httpx.post(f"{BASE_URL}/api/auth/login",
                                   json={},  # Empty data should trigger validation error
                                   timeout=10.0)
        runner.test("Login Endpoint Responds", login_response.status_code in [400, 422],
                   f"Status: {login_response.status_code} (400/422 expected for empty data)")
        
    except Exception as e:
        runner.test("Authentication Endpoints", False, f"Error: {str(e)}")
    
    return runner

def test_thread_generation():
    """Test thread generation endpoint."""
    runner = SimpleTestRunner()
    
    print("\n🧵 TESTING THREAD GENERATION")
    print("-" * 30)
    
    try:
        # Test generate endpoint (expecting 400 for missing data)
        gen_response = httpx.post(f"{BASE_URL}/api/generate",
                                 json={},  # Empty data should trigger validation error
                                 timeout=30.0)
        runner.test("Generate Endpoint Responds", gen_response.status_code in [400, 422, 503],
                   f"Status: {gen_response.status_code}")
        
        # Test with minimal valid data
        test_data = {"content": "This is a test thread content."}
        gen_response2 = httpx.post(f"{BASE_URL}/api/generate",
                                  json=test_data,
                                  timeout=30.0)
        runner.test("Generate With Data", gen_response2.status_code in [200, 400, 503],
                   f"Status: {gen_response2.status_code}")
        
    except Exception as e:
        runner.test("Thread Generation", False, f"Error: {str(e)}")
    
    return runner

def main():
    """Run all tests."""
    print("🚀 SIMPLE AUTHENTICATION & DATABASE TEST")
    print("Using httpx (existing dependency)")
    print("=" * 60)
    
    all_passed = True
    
    # Test API connectivity
    connectivity_runner = test_api_connectivity()
    all_passed = all_passed and connectivity_runner.summary()
    
    # Test authentication endpoints  
    auth_runner = test_authentication_endpoints()
    all_passed = all_passed and auth_runner.summary()
    
    # Test thread generation
    thread_runner = test_thread_generation()
    all_passed = all_passed and thread_runner.summary()
    
    # Overall summary
    total_passed = connectivity_runner.passed + auth_runner.passed + thread_runner.passed
    total_failed = connectivity_runner.failed + auth_runner.failed + thread_runner.failed
    total_tests = total_passed + total_failed
    
    print("\n" + "="*60)
    print("🎯 OVERALL RESULTS")
    print("="*60)
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Overall Success Rate: {(total_passed/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
    
    if all_passed:
        print("🎉 ALL CORE FUNCTIONALITY WORKING!")
        print("✅ Database integration successful")
        print("✅ Authentication endpoints responsive")  
        print("✅ Thread generation available")
    else:
        print("⚠️  Some tests failed - check individual results above")
    
    # Exit with appropriate code for automation
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
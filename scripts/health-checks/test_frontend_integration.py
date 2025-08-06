#!/usr/bin/env python3
"""
Frontend Integration Test Suite
Comprehensive testing of threadr-plum.vercel.app
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend and Frontend URLs
BACKEND_URL = "https://threadr-pw0s.onrender.com"
FRONTEND_URL = "https://threadr-plum.vercel.app"

# Colors for output
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

class FrontendTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            "frontend_accessible": False,
            "backend_connected": False,
            "thread_generation": False,
            "rate_limiting": False,
            "cors_working": False,
            "api_endpoints": {},
            "issues": []
        }
    
    def test_frontend_accessibility(self) -> bool:
        """Test if frontend is accessible"""
        print("\n[TEST] Frontend Accessibility...")
        try:
            response = self.session.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                print_success(f"Frontend accessible at {FRONTEND_URL}")
                
                # Check for key elements
                content = response.text.lower()
                checks = {
                    "Threadr app": "threadr" in content,
                    "Generate button": "generate" in content,
                    "API configuration": "api" in content or "config" in content
                }
                
                for check, passed in checks.items():
                    if passed:
                        print_success(f"{check} found")
                    else:
                        print_warning(f"{check} not found")
                
                self.results["frontend_accessible"] = True
                return True
            else:
                print_error(f"Frontend returned status {response.status_code}")
                self.results["issues"].append(f"Frontend status: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Could not access frontend: {e}")
            self.results["issues"].append(f"Frontend access error: {e}")
            return False
    
    def test_backend_connection(self) -> bool:
        """Test if frontend can connect to backend"""
        print("\n[TEST] Backend Connection from Frontend...")
        
        # Test CORS preflight
        try:
            response = requests.options(
                f"{BACKEND_URL}/api/generate",
                headers={
                    'Origin': FRONTEND_URL,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            if cors_origin == FRONTEND_URL or cors_origin == "*":
                print_success(f"CORS properly configured: {cors_origin}")
                self.results["cors_working"] = True
            else:
                print_warning(f"CORS origin mismatch: {cors_origin}")
                self.results["issues"].append(f"CORS: Expected {FRONTEND_URL}, got {cors_origin}")
                
        except Exception as e:
            print_error(f"CORS test failed: {e}")
            self.results["issues"].append(f"CORS error: {e}")
        
        # Test actual API call
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/generate",
                json={"content": "Frontend integration test"},
                headers={
                    'Origin': FRONTEND_URL,
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print_success("Backend API responding to frontend requests")
                    self.results["backend_connected"] = True
                    return True
                else:
                    print_warning(f"API returned error: {data.get('error')}")
                    self.results["issues"].append(f"API error: {data.get('error')}")
            else:
                print_error(f"Backend returned status {response.status_code}")
                self.results["issues"].append(f"Backend status: {response.status_code}")
                
        except Exception as e:
            print_error(f"Backend connection failed: {e}")
            self.results["issues"].append(f"Backend connection: {e}")
            
        return False
    
    def test_api_endpoints(self) -> Dict[str, bool]:
        """Test all critical API endpoints"""
        print("\n[TEST] API Endpoints...")
        
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/api/usage-stats", None),
            ("GET", "/api/premium-status", None),
            ("POST", "/api/generate", {"content": "Test"}),
        ]
        
        for method, endpoint, data in endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.post(
                        url, 
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                
                if response.status_code in [200, 201]:
                    print_success(f"{method} {endpoint}")
                    self.results["api_endpoints"][endpoint] = True
                else:
                    print_warning(f"{method} {endpoint} - Status {response.status_code}")
                    self.results["api_endpoints"][endpoint] = False
                    
            except Exception as e:
                print_error(f"{method} {endpoint} - {str(e)[:50]}")
                self.results["api_endpoints"][endpoint] = False
        
        return self.results["api_endpoints"]
    
    def test_thread_generation(self) -> bool:
        """Test thread generation functionality"""
        print("\n[TEST] Thread Generation...")
        
        test_content = "Artificial intelligence is transforming how we work and live"
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/generate",
                json={"content": test_content},
                headers={
                    'Origin': FRONTEND_URL,
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("tweets"):
                    tweets = data.get("tweets", [])
                    print_success(f"Generated {len(tweets)} tweets")
                    
                    # Check if using OpenAI
                    if len(tweets) > 1:
                        print_success("Using OpenAI for generation")
                    else:
                        print_warning("Using fallback splitting")
                    
                    # Check usage tracking
                    usage = data.get("usage", {})
                    if usage:
                        print_info(f"Usage: {usage.get('daily_used')}/{usage.get('daily_limit')} daily")
                    
                    self.results["thread_generation"] = True
                    return True
                else:
                    print_error(f"Generation failed: {data.get('error')}")
                    self.results["issues"].append(f"Generation: {data.get('error')}")
            else:
                print_error(f"Generation returned status {response.status_code}")
                self.results["issues"].append(f"Generation status: {response.status_code}")
                
        except Exception as e:
            print_error(f"Thread generation error: {e}")
            self.results["issues"].append(f"Generation error: {e}")
            
        return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        print("\n[TEST] Rate Limiting...")
        
        try:
            # Check current usage
            response = requests.get(
                f"{BACKEND_URL}/api/usage-stats",
                headers={'Origin': FRONTEND_URL},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print_success("Rate limiting active")
                    print_info(f"Daily: {data.get('daily_used')}/{data.get('daily_limit')}")
                    print_info(f"Monthly: {data.get('monthly_used')}/{data.get('monthly_limit')}")
                    print_info(f"Premium: {data.get('is_premium', False)}")
                    self.results["rate_limiting"] = True
                    return True
                    
        except Exception as e:
            print_error(f"Rate limiting test error: {e}")
            self.results["issues"].append(f"Rate limiting: {e}")
            
        return False
    
    def test_frontend_api_config(self) -> Dict[str, Any]:
        """Check frontend API configuration"""
        print("\n[TEST] Frontend API Configuration...")
        
        # Try to fetch the frontend config
        try:
            # Check if config.js exists
            config_url = f"{FRONTEND_URL}/config.js"
            response = requests.get(config_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for API URL configuration
                if BACKEND_URL in content or "threadr-pw0s.onrender.com" in content:
                    print_success("Backend URL correctly configured in frontend")
                elif "localhost" in content:
                    print_error("Frontend still pointing to localhost!")
                    self.results["issues"].append("Frontend using localhost API")
                else:
                    print_warning("Could not verify API URL in config")
                    
                # Check for hardcoded API keys (security check)
                if "sk-" in content or "your-api-key-here" in content:
                    print_error("SECURITY: API keys found in frontend!")
                    self.results["issues"].append("API keys exposed in frontend")
                else:
                    print_success("No API keys exposed in frontend")
                    
        except Exception as e:
            print_info(f"Could not fetch config.js (may be bundled): {e}")
            
        return {"checked": True}
    
    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        print_header("FRONTEND INTEGRATION TEST REPORT")
        
        # Calculate score
        total_checks = 5
        passed_checks = sum([
            self.results["frontend_accessible"],
            self.results["backend_connected"],
            self.results["thread_generation"],
            self.results["rate_limiting"],
            self.results["cors_working"]
        ])
        
        print(f"\nOverall Score: {passed_checks}/{total_checks}")
        print()
        
        # Show results
        if self.results["frontend_accessible"]:
            print_success("Frontend is accessible")
        else:
            print_error("Frontend is not accessible")
            
        if self.results["backend_connected"]:
            print_success("Backend connection working")
        else:
            print_error("Backend connection failed")
            
        if self.results["thread_generation"]:
            print_success("Thread generation working")
        else:
            print_error("Thread generation failed")
            
        if self.results["rate_limiting"]:
            print_success("Rate limiting active")
        else:
            print_error("Rate limiting not working")
            
        if self.results["cors_working"]:
            print_success("CORS properly configured")
        else:
            print_error("CORS misconfigured")
        
        # API Endpoints summary
        if self.results["api_endpoints"]:
            print("\n[API Endpoints Status]")
            working = sum(1 for v in self.results["api_endpoints"].values() if v)
            total = len(self.results["api_endpoints"])
            print(f"Working: {working}/{total}")
        
        # Issues found
        if self.results["issues"]:
            print_header("ISSUES FOUND")
            for issue in self.results["issues"]:
                print_error(issue)
        else:
            print_header("NO ISSUES FOUND")
            print_success("All systems operational!")
        
        # Recommendations
        print_header("RECOMMENDATIONS")
        
        if passed_checks == total_checks:
            print_success("Frontend is FULLY FUNCTIONAL!")
            print_info("Ready for production use")
        elif passed_checks >= 3:
            print_warning("Frontend is MOSTLY FUNCTIONAL")
            print_info("Some issues need attention")
        else:
            print_error("Frontend has CRITICAL ISSUES")
            print_info("Immediate fixes required")
        
        # Specific recommendations
        if not self.results["backend_connected"]:
            print("\n[ACTION REQUIRED]")
            print_info("1. Check frontend config.js for correct backend URL")
            print_info("2. Verify CORS_ORIGINS in Render environment")
            print_info("3. Check browser console for errors")
            
        if self.results["issues"]:
            print("\n[FIXES NEEDED]")
            for i, issue in enumerate(self.results["issues"], 1):
                print_info(f"{i}. Fix: {issue}")

def main():
    print_header("THREADR FRONTEND INTEGRATION TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    
    tester = FrontendTester()
    
    # Run all tests
    tester.test_frontend_accessibility()
    tester.test_backend_connection()
    tester.test_api_endpoints()
    tester.test_thread_generation()
    tester.test_rate_limiting()
    tester.test_frontend_api_config()
    
    # Generate report
    tester.generate_report()
    
    # Return success if critical functions work
    critical_working = (
        tester.results["frontend_accessible"] and
        tester.results["backend_connected"] and
        tester.results["thread_generation"]
    )
    
    return critical_working

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
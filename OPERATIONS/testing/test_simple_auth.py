#!/usr/bin/env python3
"""
Simple Authentication Test Suite for Threadr (Windows Compatible)
Quick validation of core authentication functionality

Usage:
    python test_simple_auth.py
"""

import asyncio
import aiohttp
import json
import time
import secrets
from colorama import init, Fore

init(autoreset=True)

class SimpleAuthTest:
    """Simple authentication test suite"""
    
    def __init__(self, base_url: str = "https://threadr-pw0s.onrender.com"):
        self.base_url = base_url
        self.session = None
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def print_result(self, test_name: str, success: bool, details: str = "") -> None:
        """Print test result"""
        status = f"{Fore.GREEN}+ PASS" if success else f"{Fore.RED}x FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"      {Fore.CYAN}{details}")
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {details}")
    
    def generate_test_user(self) -> dict:
        """Generate test user data"""
        random_id = secrets.token_hex(4)
        timestamp = int(time.time())
        
        return {
            "email": f"test-{timestamp}-{random_id}@example.com",
            "password": f"TestPass123!{random_id}",
            "confirm_password": f"TestPass123!{random_id}"
        }
    
    async def test_health_check(self) -> None:
        """Test system health"""
        print(f"\n{Fore.YELLOW}>> Testing System Health")
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    db_connected = health_data.get('services', {}).get('database') is True
                    redis_connected = health_data.get('services', {}).get('redis') is True
                    
                    self.print_result("Backend Health Check", 
                                   response.status == 200 and db_connected and redis_connected,
                                   f"Status: {health_data.get('status')}, DB: {db_connected}, Redis: {redis_connected}")
                else:
                    self.print_result("Backend Health Check", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Backend Health Check", False, f"Error: {str(e)}")
    
    async def test_user_registration(self) -> dict:
        """Test user registration"""
        print(f"\n{Fore.YELLOW}>> Testing User Registration")
        
        test_user = self.generate_test_user()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 201:
                    token_data = await response.json()
                    
                    # Validate response structure
                    has_token = "access_token" in token_data
                    has_user = "user" in token_data
                    has_user_id = has_user and "user_id" in token_data["user"]
                    
                    success = has_token and has_user and has_user_id
                    
                    if success:
                        test_user.update({
                            "user_id": token_data["user"]["user_id"],
                            "access_token": token_data["access_token"]
                        })
                    
                    self.print_result("User Registration", success,
                                   f"Token: {has_token}, User: {has_user}, ID: {has_user_id}")
                    
                    return test_user if success else None
                    
                else:
                    error_data = await response.json() if response.status != 500 else {}
                    self.print_result("User Registration", False, 
                                   f"Status: {response.status}, Error: {error_data.get('detail', 'Unknown')}")
                    
        except Exception as e:
            self.print_result("User Registration", False, f"Error: {str(e)}")
        
        return None
    
    async def test_user_login(self, test_user: dict) -> dict:
        """Test user login"""
        print(f"\n{Fore.YELLOW}>> Testing User Login")
        
        if not test_user:
            self.print_result("User Login", False, "No test user available")
            return None
        
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "remember_me": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    token_data = await response.json()
                    
                    has_token = "access_token" in token_data
                    has_user = "user" in token_data
                    email_match = has_user and token_data["user"].get("email") == test_user["email"]
                    
                    success = has_token and has_user and email_match
                    
                    if success:
                        test_user["access_token"] = token_data["access_token"]
                    
                    self.print_result("User Login", success,
                                   f"Token: {has_token}, User: {has_user}, Email match: {email_match}")
                    
                    return test_user if success else None
                    
                else:
                    self.print_result("User Login", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("User Login", False, f"Error: {str(e)}")
        
        return None
    
    async def test_user_profile(self, test_user: dict) -> None:
        """Test user profile access"""
        print(f"\n{Fore.YELLOW}>> Testing User Profile")
        
        if not test_user or not test_user.get("access_token"):
            self.print_result("User Profile", False, "No authenticated user available")
            return
        
        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {test_user['access_token']}"
        }
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=auth_headers
            ) as response:
                
                if response.status == 200:
                    profile_data = await response.json()
                    
                    has_email = "email" in profile_data
                    has_user_id = "user_id" in profile_data
                    has_role = "role" in profile_data
                    email_match = profile_data.get("email") == test_user["email"]
                    
                    success = has_email and has_user_id and has_role and email_match
                    
                    self.print_result("User Profile Access", success,
                                   f"Fields present, Email match: {email_match}")
                    
                else:
                    self.print_result("User Profile Access", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("User Profile Access", False, f"Error: {str(e)}")
    
    async def test_invalid_credentials(self) -> None:
        """Test invalid credential handling"""
        print(f"\n{Fore.YELLOW}>> Testing Security Measures")
        
        # Test invalid login
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=invalid_login,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                success = response.status == 401  # Should be unauthorized
                self.print_result("Invalid Credentials Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Invalid Credentials Rejection", False, f"Error: {str(e)}")
        
        # Test weak password registration
        weak_user = {
            "email": f"weak-{int(time.time())}@example.com",
            "password": "weak",
            "confirm_password": "weak"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=weak_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                success = response.status in [400, 422]  # Should be validation error
                self.print_result("Weak Password Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Weak Password Rejection", False, f"Error: {str(e)}")
    
    async def test_jwt_token_validation(self, test_user: dict) -> None:
        """Test JWT token validation"""
        print(f"\n{Fore.YELLOW}>> Testing JWT Token Security")
        
        if not test_user or not test_user.get("access_token"):
            self.print_result("JWT Token Tests", False, "No token available")
            return
        
        # Test invalid token
        invalid_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid.token.here"
        }
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=invalid_headers
            ) as response:
                
                success = response.status == 401  # Should be unauthorized
                self.print_result("Invalid Token Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Invalid Token Rejection", False, f"Error: {str(e)}")
        
        # Test token structure (basic validation)
        token = test_user["access_token"]
        token_parts = token.split(".")
        has_three_parts = len(token_parts) == 3
        
        self.print_result("JWT Token Structure", has_three_parts,
                       f"Token has {len(token_parts)} parts (expected 3)")
    
    async def run_all_tests(self) -> dict:
        """Run all authentication tests"""
        print(f"{Fore.CYAN}>> THREADR AUTHENTICATION SYSTEM TESTS")
        print(f"{Fore.WHITE}Testing PostgreSQL-backed authentication system")
        print(f"{Fore.WHITE}Backend URL: {self.base_url}")
        
        start_time = time.time()
        
        # Run core test flow
        await self.test_health_check()
        test_user = await self.test_user_registration()
        test_user = await self.test_user_login(test_user)
        await self.test_user_profile(test_user)
        await self.test_invalid_credentials()
        await self.test_jwt_token_validation(test_user)
        
        # Calculate results
        duration = time.time() - start_time
        total_tests = self.passed + self.failed
        pass_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        # Print results
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  TEST RESULTS SUMMARY")
        print(f"{Fore.CYAN}{'='*60}")
        
        status_color = Fore.GREEN if pass_rate >= 90 else Fore.YELLOW if pass_rate >= 80 else Fore.RED
        status_text = "EXCELLENT" if pass_rate >= 90 else "GOOD" if pass_rate >= 80 else "NEEDS ATTENTION"
        
        print(f"\n{status_color}>> OVERALL STATUS: {status_text}")
        print(f"{Fore.WHITE}Total Tests: {total_tests}")
        print(f"{Fore.GREEN}+ Passed: {self.passed}")
        print(f"{Fore.RED}x Failed: {self.failed}")
        print(f"{Fore.CYAN}Pass Rate: {pass_rate:.1f}%")
        print(f"{Fore.WHITE}Duration: {duration:.2f} seconds")
        
        if self.failed > 0:
            print(f"\n{Fore.RED}>> FAILED TESTS:")
            for error in self.errors:
                print(f"   x {error}")
        
        # Production readiness
        print(f"\n{Fore.CYAN}>> PRODUCTION READINESS:")
        if pass_rate >= 90:
            print(f"{Fore.GREEN}+ Authentication system is ready for production")
            print(f"{Fore.GREEN}+ PostgreSQL integration working correctly")
        elif pass_rate >= 80:
            print(f"{Fore.YELLOW}! System mostly ready with minor issues")
        else:
            print(f"{Fore.RED}x Critical issues need resolution before production")
        
        print(f"\n{Fore.WHITE}{'='*60}")
        
        return {
            "total_tests": total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": pass_rate,
            "duration": duration,
            "status": status_text.lower()
        }


async def main():
    """Main execution function"""
    async with SimpleAuthTest() as test_suite:
        results = await test_suite.run_all_tests()
        return 0 if results["pass_rate"] >= 80 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}! Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}x Fatal error: {str(e)}")
        exit(1)
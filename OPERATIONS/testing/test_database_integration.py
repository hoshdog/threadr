#!/usr/bin/env python3
"""
Database Integration Test Suite for Threadr Authentication System
Focuses specifically on PostgreSQL data persistence and consistency

This suite validates:
1. User data is properly stored in PostgreSQL
2. Data persistence across sessions
3. Database schema integrity
4. CRUD operations work correctly
5. Data consistency under load

Usage:
    python test_database_integration.py
"""

import asyncio
import aiohttp
import json
import time
import secrets
from typing import Dict, Any, List
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class DatabaseIntegrationTestSuite:
    """Test suite focused on database integration"""
    
    def __init__(self, base_url: str = "https://threadr-pw0s.onrender.com"):
        self.base_url = base_url
        self.session = None
        self.test_results = {"passed": 0, "failed": 0, "errors": []}
        self.test_users = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def print_result(self, test_name: str, success: bool, details: str = "") -> None:
        """Print test result"""
        status = f"{Fore.GREEN}✓ PASS" if success else f"{Fore.RED}✗ FAIL"
        print(f"{status} {Fore.WHITE}{test_name}")
        if details:
            print(f"      {Fore.CYAN}{details}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
    
    def generate_test_user(self) -> Dict[str, str]:
        """Generate test user data"""
        random_id = secrets.token_hex(4)
        timestamp = int(time.time())
        
        return {
            "email": f"dbtest-{timestamp}-{random_id}@threadr-test.local",
            "password": f"TestPass123!{random_id}",
            "confirm_password": f"TestPass123!{random_id}"
        }
    
    async def test_user_crud_operations(self) -> None:
        """Test Create, Read, Update, Delete operations"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}  DATABASE CRUD OPERATIONS TESTS")
        print(f"{Fore.YELLOW}{'='*60}")
        
        # CREATE - Register new user
        test_user = self.generate_test_user()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 201:
                    user_data = await response.json()
                    test_user.update({
                        "user_id": user_data["user"]["user_id"],
                        "access_token": user_data["access_token"]
                    })
                    self.test_users.append(test_user)
                    self.print_result("CREATE - User Registration", True, f"User ID: {test_user['user_id']}")
                else:
                    self.print_result("CREATE - User Registration", False, f"Status: {response.status}")
                    return
                    
        except Exception as e:
            self.print_result("CREATE - User Registration", False, f"Error: {str(e)}")
            return
        
        # READ - Get user profile
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
                    email_match = profile_data.get("email") == test_user["email"]
                    user_id_match = profile_data.get("user_id") == test_user["user_id"]
                    
                    self.print_result("READ - User Profile", email_match and user_id_match, 
                                   f"Email match: {email_match}, ID match: {user_id_match}")
                else:
                    self.print_result("READ - User Profile", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("READ - User Profile", False, f"Error: {str(e)}")
        
        # UPDATE - Change password
        new_password = f"NewTestPass123!{secrets.token_hex(4)}"
        password_data = {
            "current_password": test_user["password"],
            "new_password": new_password,
            "confirm_new_password": new_password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/change-password",
                json=password_data,
                headers=auth_headers
            ) as response:
                
                change_success = response.status == 200
                self.print_result("UPDATE - Password Change", change_success, f"Status: {response.status}")
                
                if change_success:
                    # Verify new password works
                    login_data = {
                        "email": test_user["email"],
                        "password": new_password,
                        "remember_me": False
                    }
                    
                    async with self.session.post(
                        f"{self.base_url}/api/auth/login",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    ) as login_response:
                        
                        login_success = login_response.status == 200
                        self.print_result("UPDATE - New Password Verification", login_success, 
                                       f"New password login status: {login_response.status}")
                        
                        if login_success:
                            new_token_data = await login_response.json()
                            test_user["access_token"] = new_token_data["access_token"]
                            test_user["password"] = new_password
                    
        except Exception as e:
            self.print_result("UPDATE - Password Change", False, f"Error: {str(e)}")
    
    async def test_data_persistence_across_sessions(self) -> None:
        """Test data persistence across multiple login sessions"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}  DATA PERSISTENCE ACROSS SESSIONS")
        print(f"{Fore.YELLOW}{'='*60}")
        
        if not self.test_users:
            self.print_result("Data Persistence Tests", False, "No test users available")
            return
        
        test_user = self.test_users[0]
        
        # Login multiple times and verify data consistency
        login_attempts = 5
        successful_logins = 0
        consistent_data = 0
        
        for i in range(login_attempts):
            try:
                login_data = {
                    "email": test_user["email"],
                    "password": test_user["password"],
                    "remember_me": False
                }
                
                async with self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        successful_logins += 1
                        token_data = await response.json()
                        
                        # Verify user data consistency
                        user_data = token_data.get("user", {})
                        if (user_data.get("email") == test_user["email"] and 
                            user_data.get("user_id") == test_user["user_id"]):
                            consistent_data += 1
                
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            except Exception as e:
                pass  # Continue with other attempts
        
        all_successful = successful_logins == login_attempts
        all_consistent = consistent_data == successful_logins
        
        self.print_result("Multiple Session Logins", all_successful, 
                       f"{successful_logins}/{login_attempts} successful logins")
        self.print_result("Data Consistency Across Sessions", all_consistent, 
                       f"{consistent_data}/{successful_logins} consistent data responses")
    
    async def test_concurrent_operations(self) -> None:
        """Test concurrent database operations"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}  CONCURRENT DATABASE OPERATIONS")
        print(f"{Fore.YELLOW}{'='*60}")
        
        # Create multiple test users concurrently
        concurrent_users = []
        for i in range(3):  # Create 3 users concurrently
            user_data = self.generate_test_user()
            concurrent_users.append(user_data)
        
        # Register users concurrently
        registration_tasks = []
        for user_data in concurrent_users:
            task = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            registration_tasks.append(task)
        
        successful_registrations = 0
        try:
            responses = await asyncio.gather(*registration_tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    continue
                    
                async with response:
                    if response.status == 201:
                        successful_registrations += 1
                        user_data = await response.json()
                        concurrent_users[i].update({
                            "user_id": user_data["user"]["user_id"],
                            "access_token": user_data["access_token"]
                        })
                        self.test_users.append(concurrent_users[i])
            
            all_successful = successful_registrations == len(concurrent_users)
            self.print_result("Concurrent User Registration", all_successful, 
                           f"{successful_registrations}/{len(concurrent_users)} users registered successfully")
            
        except Exception as e:
            self.print_result("Concurrent User Registration", False, f"Error: {str(e)}")
        
        # Test concurrent logins
        if successful_registrations > 0:
            login_tasks = []
            for user_data in concurrent_users[:successful_registrations]:
                login_request = {
                    "email": user_data["email"],
                    "password": user_data["password"],
                    "remember_me": False
                }
                task = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_request,
                    headers={"Content-Type": "application/json"}
                )
                login_tasks.append(task)
            
            successful_logins = 0
            try:
                login_responses = await asyncio.gather(*login_tasks, return_exceptions=True)
                
                for response in login_responses:
                    if isinstance(response, Exception):
                        continue
                        
                    async with response:
                        if response.status == 200:
                            successful_logins += 1
                
                all_logins_successful = successful_logins == successful_registrations
                self.print_result("Concurrent User Login", all_logins_successful, 
                               f"{successful_logins}/{successful_registrations} concurrent logins successful")
                
            except Exception as e:
                self.print_result("Concurrent User Login", False, f"Error: {str(e)}")
    
    async def test_data_integrity_under_load(self) -> None:
        """Test data integrity under simulated load"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}  DATA INTEGRITY UNDER LOAD")
        print(f"{Fore.YELLOW}{'='*60}")
        
        if not self.test_users:
            self.print_result("Load Test", False, "No test users available")
            return
        
        test_user = self.test_users[0]
        
        # Perform many rapid profile queries
        profile_tasks = []
        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {test_user['access_token']}"
        }
        
        num_requests = 10  # Rapid profile requests
        for _ in range(num_requests):
            task = self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=auth_headers
            )
            profile_tasks.append(task)
        
        try:
            start_time = time.time()
            responses = await asyncio.gather(*profile_tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_requests = 0
            consistent_responses = 0
            
            for response in responses:
                if isinstance(response, Exception):
                    continue
                    
                async with response:
                    if response.status == 200:
                        successful_requests += 1
                        profile_data = await response.json()
                        
                        # Check data consistency
                        if (profile_data.get("email") == test_user["email"] and 
                            profile_data.get("user_id") == test_user["user_id"]):
                            consistent_responses += 1
            
            duration = end_time - start_time
            requests_per_second = num_requests / duration if duration > 0 else 0
            
            all_successful = successful_requests == num_requests
            all_consistent = consistent_responses == successful_requests
            
            self.print_result("Load Test - Request Success", all_successful, 
                           f"{successful_requests}/{num_requests} requests successful ({requests_per_second:.1f} req/s)")
            self.print_result("Load Test - Data Consistency", all_consistent, 
                           f"{consistent_responses}/{successful_requests} responses consistent")
            
        except Exception as e:
            self.print_result("Load Test", False, f"Error: {str(e)}")
    
    async def test_database_schema_validation(self) -> None:
        """Test database schema through API responses"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}  DATABASE SCHEMA VALIDATION")
        print(f"{Fore.YELLOW}{'='*60}")
        
        if not self.test_users:
            self.print_result("Schema Validation", False, "No test users available")
            return
        
        test_user = self.test_users[0]
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
                    user_data = await response.json()
                    
                    # Expected schema fields
                    required_fields = {
                        "user_id": str,
                        "email": str,
                        "role": str,
                        "status": str,
                        "created_at": str,
                        "is_premium": bool
                    }
                    
                    schema_valid = True
                    missing_fields = []
                    wrong_types = []
                    
                    for field, expected_type in required_fields.items():
                        if field not in user_data:
                            missing_fields.append(field)
                            schema_valid = False
                        elif not isinstance(user_data[field], expected_type):
                            wrong_types.append(f"{field}: expected {expected_type.__name__}, got {type(user_data[field]).__name__}")
                            schema_valid = False
                    
                    details = f"Missing: {missing_fields}, Wrong types: {wrong_types}" if not schema_valid else "All fields present with correct types"
                    self.print_result("User Schema Validation", schema_valid, details)
                    
                    # Test enum values
                    valid_roles = ["user", "premium", "admin"]
                    valid_statuses = ["active", "inactive", "suspended"]
                    
                    role_valid = user_data.get("role") in valid_roles
                    status_valid = user_data.get("status") in valid_statuses
                    
                    self.print_result("Enum Values Validation", role_valid and status_valid, 
                                   f"Role: {user_data.get('role')} ({'valid' if role_valid else 'invalid'}), "
                                   f"Status: {user_data.get('status')} ({'valid' if status_valid else 'invalid'})")
                    
                else:
                    self.print_result("Schema Validation", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Schema Validation", False, f"Error: {str(e)}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all database integration tests"""
        print(f"{Fore.CYAN}🗄️  THREADR DATABASE INTEGRATION TEST SUITE")
        print(f"{Fore.WHITE}Testing PostgreSQL integration and data persistence")
        print(f"{Fore.WHITE}Backend URL: {self.base_url}")
        
        start_time = time.time()
        
        # Run all test suites
        await self.test_user_crud_operations()
        await self.test_data_persistence_across_sessions()
        await self.test_concurrent_operations()
        await self.test_data_integrity_under_load()
        await self.test_database_schema_validation()
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        pass_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        # Print results
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  DATABASE INTEGRATION TEST RESULTS")
        print(f"{Fore.CYAN}{'='*60}")
        
        status_color = Fore.GREEN if pass_rate >= 90 else Fore.YELLOW if pass_rate >= 80 else Fore.RED
        status_text = "EXCELLENT" if pass_rate >= 90 else "GOOD" if pass_rate >= 80 else "NEEDS ATTENTION"
        
        print(f"\n{status_color}📊 OVERALL STATUS: {status_text}")
        print(f"{Fore.WHITE}🧪 Total Tests: {total_tests}")
        print(f"{Fore.GREEN}✓ Passed: {self.test_results['passed']}")
        print(f"{Fore.RED}✗ Failed: {self.test_results['failed']}")
        print(f"{Fore.CYAN}📈 Pass Rate: {pass_rate:.1f}%")
        print(f"{Fore.WHITE}⏱️  Duration: {duration:.2f} seconds")
        print(f"{Fore.WHITE}👥 Test Users Created: {len(self.test_users)}")
        
        if self.test_results["failed"] > 0:
            print(f"\n{Fore.RED}❌ FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"   {Fore.RED}• {error}")
        
        print(f"\n{Fore.WHITE}{'='*60}")
        
        return {
            "total_tests": total_tests,
            "passed": self.test_results["passed"],
            "failed": self.test_results["failed"],
            "pass_rate": pass_rate,
            "duration": duration,
            "users_created": len(self.test_users)
        }


async def main():
    """Main execution function"""
    async with DatabaseIntegrationTestSuite() as test_suite:
        results = await test_suite.run_all_tests()
        return 0 if results["pass_rate"] >= 80 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}💥 Fatal error: {str(e)}")
        exit(1)
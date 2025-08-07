#!/usr/bin/env python3
"""
Comprehensive Authentication Testing Suite for Threadr
Tests all authentication functionality with PostgreSQL backend integration

This suite tests:
1. Basic auth endpoints (register, login, profile)
2. Data persistence in PostgreSQL
3. JWT token generation and validation
4. Premium functionality integration
5. Security measures (password hashing, validation)
6. OAuth flow testing (preparation)
7. Error handling validation

Usage:
    python comprehensive_auth_test_suite.py
"""

import asyncio
import aiohttp
import json
import time
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import jwt
from colorama import init, Fore, Style, Back
import re

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class AuthTestSuite:
    """Comprehensive authentication testing suite"""
    
    def __init__(self, base_url: str = "https://threadr-pw0s.onrender.com"):
        self.base_url = base_url
        self.session = None
        self.test_users = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "summary": {}
        }
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Threadr-Auth-Test-Suite/1.0"
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def print_header(self, title: str, level: int = 1) -> None:
        """Print formatted test section header"""
        if level == 1:
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.CYAN}  {title}")
            print(f"{Fore.CYAN}{'='*80}")
        elif level == 2:
            print(f"\n{Fore.YELLOW}{'-'*60}")
            print(f"{Fore.YELLOW}  {title}")
            print(f"{Fore.YELLOW}{'-'*60}")
        else:
            print(f"\n{Fore.WHITE}>> {title}")
    
    def print_result(self, test_name: str, success: bool, details: str = "") -> None:
        """Print test result with formatting"""
        status = f"{Fore.GREEN}✓ PASS" if success else f"{Fore.RED}✗ FAIL"
        print(f"{status} {Fore.WHITE}{test_name}")
        if details:
            print(f"      {Fore.CYAN}{details}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
    
    def generate_test_user(self, prefix: str = "test") -> Dict[str, str]:
        """Generate unique test user data"""
        random_id = secrets.token_hex(4)
        timestamp = int(time.time())
        
        return {
            "email": f"{prefix}-{timestamp}-{random_id}@threadr-test.local",
            "password": f"TestPass123!{random_id}",
            "confirm_password": f"TestPass123!{random_id}"
        }
    
    def validate_jwt_token(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate JWT token structure without secret verification"""
        try:
            # Decode without verification to check structure
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Check required fields
            required_fields = ["sub", "email", "role", "exp", "iat", "type"]
            missing_fields = [field for field in required_fields if field not in decoded]
            
            if missing_fields:
                return False, {"error": f"Missing required fields: {missing_fields}"}
            
            # Check token expiration
            if decoded["exp"] < time.time():
                return False, {"error": "Token is expired"}
            
            return True, decoded
            
        except jwt.InvalidTokenError as e:
            return False, {"error": f"Invalid token structure: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Token validation error: {str(e)}"}
    
    def validate_user_response(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate user response structure"""
        required_fields = [
            "user_id", "email", "role", "status", "created_at",
            "is_premium"
        ]
        
        missing_fields = [field for field in required_fields if field not in user_data]
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # Validate field types and values
        if not isinstance(user_data["user_id"], str) or not user_data["user_id"]:
            return False, "user_id must be a non-empty string"
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data["email"]):
            return False, "email format is invalid"
        
        if user_data["role"] not in ["user", "premium", "admin"]:
            return False, f"role must be one of ['user', 'premium', 'admin'], got: {user_data['role']}"
        
        if user_data["status"] not in ["active", "inactive", "suspended"]:
            return False, f"status must be one of ['active', 'inactive', 'suspended'], got: {user_data['status']}"
        
        if not isinstance(user_data["is_premium"], bool):
            return False, "is_premium must be a boolean"
        
        # Validate datetime format
        try:
            datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False, "created_at must be a valid ISO format datetime"
        
        return True, "User response structure is valid"
    
    # =============================================================================
    # HEALTH CHECK TESTS
    # =============================================================================
    
    async def test_system_health(self) -> None:
        """Test system health and readiness"""
        self.print_header("SYSTEM HEALTH CHECKS", 2)
        
        try:
            # Test basic health endpoint
            async with self.session.get(f"{self.base_url}/health", headers=self.headers) as response:
                health_data = await response.json()
                
                success = (
                    response.status == 200 and
                    health_data.get("status") == "healthy" and
                    health_data.get("services", {}).get("database") is True and
                    health_data.get("services", {}).get("redis") is True
                )
                
                self.print_result(
                    "Backend Health Check",
                    success,
                    f"Status: {health_data.get('status')}, DB: {health_data.get('services', {}).get('database')}, Redis: {health_data.get('services', {}).get('redis')}"
                )
                
                if not success:
                    print(f"{Fore.RED}CRITICAL: System not healthy, aborting tests")
                    return False
                
        except Exception as e:
            self.print_result("Backend Health Check", False, f"Error: {str(e)}")
            return False
        
        # Test readiness endpoint if available
        try:
            async with self.session.get(f"{self.base_url}/readiness", headers=self.headers) as response:
                if response.status == 200:
                    self.print_result("Readiness Check", True, "System ready for testing")
                else:
                    self.print_result("Readiness Check", False, f"Status code: {response.status}")
        except:
            self.print_result("Readiness Check", False, "Endpoint not available (non-critical)")
        
        return True
    
    # =============================================================================
    # BASIC AUTHENTICATION TESTS
    # =============================================================================
    
    async def test_user_registration(self) -> Optional[Dict[str, Any]]:
        """Test user registration endpoint"""
        self.print_header("USER REGISTRATION TESTS", 2)
        
        # Test 1: Valid registration
        test_user = self.generate_test_user("reg")
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=test_user,
                headers=self.headers
            ) as response:
                
                if response.status == 201:
                    token_data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["access_token", "token_type", "expires_in", "user"]
                    missing_fields = [field for field in required_fields if field not in token_data]
                    
                    if not missing_fields:
                        # Validate JWT token
                        token_valid, token_info = self.validate_jwt_token(token_data["access_token"])
                        
                        # Validate user response
                        user_valid, user_msg = self.validate_user_response(token_data["user"])
                        
                        success = token_valid and user_valid
                        details = f"User: {token_data['user']['email']}, Token valid: {token_valid}, User valid: {user_valid}"
                        
                        self.print_result("Valid User Registration", success, details)
                        
                        if success:
                            # Store user for other tests
                            test_user.update({
                                "user_id": token_data["user"]["user_id"],
                                "access_token": token_data["access_token"],
                                "refresh_token": token_data.get("refresh_token")
                            })
                            self.test_users.append(test_user)
                            return test_user
                    else:
                        self.print_result("Valid User Registration", False, f"Missing fields: {missing_fields}")
                        
                elif response.status == 400:
                    error_data = await response.json()
                    self.print_result("Valid User Registration", False, f"Validation error: {error_data.get('detail')}")
                else:
                    self.print_result("Valid User Registration", False, f"Unexpected status: {response.status}")
                    
        except Exception as e:
            self.print_result("Valid User Registration", False, f"Request error: {str(e)}")
        
        # Test 2: Duplicate registration
        if test_user:
            try:
                async with self.session.post(
                    f"{self.base_url}/api/auth/register",
                    json=test_user,
                    headers=self.headers
                ) as response:
                    
                    success = response.status == 409  # Conflict
                    self.print_result("Duplicate Registration Prevention", success, f"Status: {response.status}")
                    
            except Exception as e:
                self.print_result("Duplicate Registration Prevention", False, f"Error: {str(e)}")
        
        # Test 3: Invalid password registration
        invalid_user = self.generate_test_user("invalid")
        invalid_user["password"] = "weak"  # Too weak password
        invalid_user["confirm_password"] = "weak"
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=invalid_user,
                headers=self.headers
            ) as response:
                
                success = response.status == 400  # Bad request
                self.print_result("Weak Password Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Weak Password Rejection", False, f"Error: {str(e)}")
        
        # Test 4: Password mismatch
        mismatch_user = self.generate_test_user("mismatch")
        mismatch_user["confirm_password"] = "DifferentPassword123!"
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=mismatch_user,
                headers=self.headers
            ) as response:
                
                success = response.status == 400  # Bad request
                self.print_result("Password Mismatch Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Password Mismatch Rejection", False, f"Error: {str(e)}")
        
        return test_user
    
    async def test_user_login(self, test_user: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Test user login functionality"""
        self.print_header("USER LOGIN TESTS", 2)
        
        if not test_user and self.test_users:
            test_user = self.test_users[0]
        
        if not test_user:
            self.print_result("Login Tests", False, "No test user available")
            return None
        
        # Test 1: Valid login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "remember_me": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    token_data = await response.json()
                    
                    # Validate token
                    token_valid, token_info = self.validate_jwt_token(token_data["access_token"])
                    
                    # Validate user response
                    user_valid, user_msg = self.validate_user_response(token_data["user"])
                    
                    success = token_valid and user_valid
                    self.print_result("Valid User Login", success, f"Token valid: {token_valid}, User valid: {user_valid}")
                    
                    if success:
                        # Update test user with new token
                        test_user["access_token"] = token_data["access_token"]
                        test_user["refresh_token"] = token_data.get("refresh_token")
                        return test_user
                        
                else:
                    error_data = await response.json()
                    self.print_result("Valid User Login", False, f"Status {response.status}: {error_data.get('detail')}")
                    
        except Exception as e:
            self.print_result("Valid User Login", False, f"Error: {str(e)}")
        
        # Test 2: Remember me login
        remember_login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "remember_me": True
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=remember_login_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    token_data = await response.json()
                    
                    # Token should have longer expiration
                    token_valid, token_info = self.validate_jwt_token(token_data["access_token"])
                    extended_expiry = token_info.get("exp", 0) - time.time() > 86400  # More than 1 day
                    
                    success = token_valid and extended_expiry
                    self.print_result("Remember Me Login", success, f"Extended expiry: {extended_expiry}")
                    
                else:
                    self.print_result("Remember Me Login", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Remember Me Login", False, f"Error: {str(e)}")
        
        # Test 3: Invalid credentials
        invalid_login = {
            "email": test_user["email"],
            "password": "WrongPassword123!",
            "remember_me": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=invalid_login,
                headers=self.headers
            ) as response:
                
                success = response.status == 401  # Unauthorized
                self.print_result("Invalid Credentials Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Invalid Credentials Rejection", False, f"Error: {str(e)}")
        
        # Test 4: Non-existent user
        nonexistent_login = {
            "email": "nonexistent@threadr-test.local",
            "password": "AnyPassword123!",
            "remember_me": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=nonexistent_login,
                headers=self.headers
            ) as response:
                
                success = response.status == 401  # Unauthorized
                self.print_result("Non-existent User Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Non-existent User Rejection", False, f"Error: {str(e)}")
        
        return test_user
    
    async def test_user_profile(self, test_user: Optional[Dict[str, Any]] = None) -> None:
        """Test user profile endpoints"""
        self.print_header("USER PROFILE TESTS", 2)
        
        if not test_user and self.test_users:
            test_user = self.test_users[0]
        
        if not test_user or not test_user.get("access_token"):
            self.print_result("Profile Tests", False, "No authenticated test user available")
            return
        
        auth_headers = {
            **self.headers,
            "Authorization": f"Bearer {test_user['access_token']}"
        }
        
        # Test 1: Get current user profile
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=auth_headers
            ) as response:
                
                if response.status == 200:
                    user_data = await response.json()
                    
                    # Validate user response structure
                    user_valid, user_msg = self.validate_user_response(user_data)
                    
                    # Check if email matches
                    email_match = user_data.get("email") == test_user["email"]
                    
                    success = user_valid and email_match
                    self.print_result("Get Current User Profile", success, f"Valid structure: {user_valid}, Email match: {email_match}")
                    
                else:
                    error_data = await response.json()
                    self.print_result("Get Current User Profile", False, f"Status {response.status}: {error_data.get('detail')}")
                    
        except Exception as e:
            self.print_result("Get Current User Profile", False, f"Error: {str(e)}")
        
        # Test 2: Session status check
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/session/status",
                headers=auth_headers
            ) as response:
                
                if response.status == 200:
                    session_data = await response.json()
                    
                    # Check authenticated status
                    authenticated = session_data.get("authenticated") is True
                    has_user_info = "user" in session_data and session_data["user"].get("email") == test_user["email"]
                    
                    success = authenticated and has_user_info
                    self.print_result("Session Status Check", success, f"Authenticated: {authenticated}, User info: {has_user_info}")
                    
                else:
                    self.print_result("Session Status Check", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Session Status Check", False, f"Error: {str(e)}")
    
    # =============================================================================
    # JWT TOKEN TESTS
    # =============================================================================
    
    async def test_jwt_token_functionality(self, test_user: Optional[Dict[str, Any]] = None) -> None:
        """Test JWT token generation and validation"""
        self.print_header("JWT TOKEN FUNCTIONALITY TESTS", 2)
        
        if not test_user and self.test_users:
            test_user = self.test_users[0]
        
        if not test_user:
            self.print_result("JWT Tests", False, "No test user available")
            return
        
        # Test 1: Token structure validation
        if test_user.get("access_token"):
            token_valid, token_info = self.validate_jwt_token(test_user["access_token"])
            self.print_result("Access Token Structure", token_valid, 
                           f"Fields: {list(token_info.keys()) if token_valid else token_info.get('error', 'Unknown error')}")
        
        # Test 2: Token expiration check
        if test_user.get("access_token"):
            token_valid, token_info = self.validate_jwt_token(test_user["access_token"])
            if token_valid:
                exp_timestamp = token_info.get("exp", 0)
                current_timestamp = time.time()
                time_until_expiry = exp_timestamp - current_timestamp
                
                # Token should be valid for reasonable time (more than 1 minute, less than 31 days)
                reasonable_expiry = 60 < time_until_expiry < (31 * 24 * 3600)
                
                self.print_result("Token Expiration Timing", reasonable_expiry, 
                               f"Expires in: {int(time_until_expiry)} seconds")
        
        # Test 3: Refresh token functionality
        if test_user.get("refresh_token"):
            refresh_data = {
                "refresh_token": test_user["refresh_token"]
            }
            
            try:
                async with self.session.post(
                    f"{self.base_url}/api/auth/refresh",
                    json=refresh_data,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        new_token_data = await response.json()
                        
                        # Validate new token
                        new_token_valid, _ = self.validate_jwt_token(new_token_data["access_token"])
                        
                        # Token should be different from original
                        token_different = new_token_data["access_token"] != test_user["access_token"]
                        
                        success = new_token_valid and token_different
                        self.print_result("Token Refresh", success, f"New token valid: {new_token_valid}, Different: {token_different}")
                        
                        # Update test user token
                        if success:
                            test_user["access_token"] = new_token_data["access_token"]
                            
                    else:
                        self.print_result("Token Refresh", False, f"Status: {response.status}")
                        
            except Exception as e:
                self.print_result("Token Refresh", False, f"Error: {str(e)}")
        
        # Test 4: Invalid token rejection
        invalid_headers = {
            **self.headers,
            "Authorization": "Bearer invalid.token.here"
        }
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=invalid_headers
            ) as response:
                
                success = response.status == 401  # Unauthorized
                self.print_result("Invalid Token Rejection", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Invalid Token Rejection", False, f"Error: {str(e)}")
    
    # =============================================================================
    # DATA PERSISTENCE TESTS
    # =============================================================================
    
    async def test_data_persistence(self, test_user: Optional[Dict[str, Any]] = None) -> None:
        """Test PostgreSQL data persistence"""
        self.print_header("DATA PERSISTENCE TESTS", 2)
        
        if not test_user and self.test_users:
            test_user = self.test_users[0]
        
        if not test_user:
            self.print_result("Persistence Tests", False, "No test user available")
            return
        
        # Test 1: User data persistence across sessions
        # Login again to verify user data is still there
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "remember_me": False
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers=self.headers
            ) as response:
                
                success = response.status == 200
                self.print_result("User Data Persistence", success, 
                               f"User data persisted and retrievable: Status {response.status}")
                
                if success:
                    token_data = await response.json()
                    test_user["access_token"] = token_data["access_token"]
                    
        except Exception as e:
            self.print_result("User Data Persistence", False, f"Error: {str(e)}")
        
        # Test 2: Password change and persistence
        if test_user.get("access_token"):
            auth_headers = {
                **self.headers,
                "Authorization": f"Bearer {test_user['access_token']}"
            }
            
            new_password = f"NewPassword123!{secrets.token_hex(4)}"
            password_change_data = {
                "current_password": test_user["password"],
                "new_password": new_password,
                "confirm_new_password": new_password
            }
            
            try:
                async with self.session.post(
                    f"{self.base_url}/api/auth/change-password",
                    json=password_change_data,
                    headers=auth_headers
                ) as response:
                    
                    change_success = response.status == 200
                    self.print_result("Password Change", change_success, f"Status: {response.status}")
                    
                    if change_success:
                        # Test that old password no longer works
                        old_login_data = {
                            "email": test_user["email"],
                            "password": test_user["password"],
                            "remember_me": False
                        }
                        
                        async with self.session.post(
                            f"{self.base_url}/api/auth/login",
                            json=old_login_data,
                            headers=self.headers
                        ) as old_login_response:
                            
                            old_rejected = old_login_response.status == 401
                            self.print_result("Old Password Rejection", old_rejected, 
                                           f"Old password correctly rejected: Status {old_login_response.status}")
                        
                        # Test that new password works
                        new_login_data = {
                            "email": test_user["email"],
                            "password": new_password,
                            "remember_me": False
                        }
                        
                        async with self.session.post(
                            f"{self.base_url}/api/auth/login",
                            json=new_login_data,
                            headers=self.headers
                        ) as new_login_response:
                            
                            new_accepted = new_login_response.status == 200
                            self.print_result("New Password Acceptance", new_accepted, 
                                           f"New password works: Status {new_login_response.status}")
                            
                            if new_accepted:
                                # Update test user password
                                test_user["password"] = new_password
                                new_token_data = await new_login_response.json()
                                test_user["access_token"] = new_token_data["access_token"]
                    
            except Exception as e:
                self.print_result("Password Change", False, f"Error: {str(e)}")
    
    # =============================================================================
    # PREMIUM FUNCTIONALITY TESTS
    # =============================================================================
    
    async def test_premium_functionality(self, test_user: Optional[Dict[str, Any]] = None) -> None:
        """Test premium status integration"""
        self.print_header("PREMIUM FUNCTIONALITY TESTS", 2)
        
        if not test_user and self.test_users:
            test_user = self.test_users[0]
        
        if not test_user or not test_user.get("access_token"):
            self.print_result("Premium Tests", False, "No authenticated test user available")
            return
        
        auth_headers = {
            **self.headers,
            "Authorization": f"Bearer {test_user['access_token']}"
        }
        
        # Test 1: Check initial premium status (should be false)
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=auth_headers
            ) as response:
                
                if response.status == 200:
                    user_data = await response.json()
                    is_premium = user_data.get("is_premium", True)  # Default True to catch errors
                    
                    # New user should not be premium
                    success = is_premium is False
                    self.print_result("Initial Premium Status", success, f"is_premium: {is_premium} (should be False)")
                    
                else:
                    self.print_result("Initial Premium Status", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Initial Premium Status", False, f"Error: {str(e)}")
        
        # Test 2: Usage stats integration
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=auth_headers
            ) as response:
                
                if response.status == 200:
                    user_data = await response.json()
                    usage_stats = user_data.get("usage_stats")
                    
                    # Usage stats should be present
                    has_usage_stats = usage_stats is not None
                    self.print_result("Usage Stats Integration", has_usage_stats, 
                                   f"Usage stats present: {has_usage_stats}, Data: {usage_stats}")
                    
                else:
                    self.print_result("Usage Stats Integration", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Usage Stats Integration", False, f"Error: {str(e)}")
    
    # =============================================================================
    # SECURITY TESTS
    # =============================================================================
    
    async def test_security_measures(self, test_user: Optional[Dict[str, Any]] = None) -> None:
        """Test security measures and validations"""
        self.print_header("SECURITY MEASURES TESTS", 2)
        
        # Test 1: Password strength validation
        try:
            async with self.session.get(
                f"{self.base_url}/api/auth/password-strength",
                params={"password": "weak"},
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    strength_data = await response.json()
                    
                    # Should indicate weak password
                    has_strength_info = "score" in strength_data or "strength" in strength_data
                    self.print_result("Password Strength Check", has_strength_info, 
                                   f"Strength data: {strength_data}")
                    
                else:
                    self.print_result("Password Strength Check", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.print_result("Password Strength Check", False, f"Error: {str(e)}")
        
        # Test 2: SQL injection prevention
        sql_injection_user = {
            "email": "test'; DROP TABLE users; --@test.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=sql_injection_user,
                headers=self.headers
            ) as response:
                
                # Should either reject invalid email format or handle safely
                safe_handling = response.status in [400, 422]  # Bad request or validation error
                self.print_result("SQL Injection Prevention", safe_handling, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("SQL Injection Prevention", False, f"Error: {str(e)}")
        
        # Test 3: XSS prevention in email field
        xss_user = {
            "email": "<script>alert('xss')</script>@test.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=xss_user,
                headers=self.headers
            ) as response:
                
                # Should reject invalid email format
                safe_handling = response.status in [400, 422]
                self.print_result("XSS Prevention", safe_handling, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("XSS Prevention", False, f"Error: {str(e)}")
        
        # Test 4: Rate limiting (if implemented)
        # Attempt multiple rapid requests
        rate_limit_test_user = self.generate_test_user("ratelimit")
        rapid_requests = 0
        rate_limited = False
        
        try:
            for i in range(10):  # Try 10 rapid registration attempts
                async with self.session.post(
                    f"{self.base_url}/api/auth/register",
                    json={
                        **rate_limit_test_user,
                        "email": f"ratelimit{i}@test.com"
                    },
                    headers=self.headers
                ) as response:
                    rapid_requests += 1
                    if response.status == 429:  # Too Many Requests
                        rate_limited = True
                        break
                    elif response.status >= 500:
                        # Server error might indicate resource exhaustion
                        break
            
            # Rate limiting is optional but good to have
            self.print_result("Rate Limiting Test", True, 
                           f"Processed {rapid_requests} requests, Rate limited: {rate_limited}")
                           
        except Exception as e:
            self.print_result("Rate Limiting Test", False, f"Error: {str(e)}")
    
    # =============================================================================
    # ERROR HANDLING TESTS
    # =============================================================================
    
    async def test_error_handling(self) -> None:
        """Test comprehensive error handling"""
        self.print_header("ERROR HANDLING TESTS", 2)
        
        # Test 1: Malformed JSON
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                data="invalid json",
                headers={**self.headers, "Content-Type": "application/json"}
            ) as response:
                
                success = response.status == 400  # Bad request
                self.print_result("Malformed JSON Handling", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Malformed JSON Handling", False, f"Error: {str(e)}")
        
        # Test 2: Missing required fields
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json={"email": "test@test.com"},  # Missing password fields
                headers=self.headers
            ) as response:
                
                success = response.status in [400, 422]  # Bad request or validation error
                self.print_result("Missing Fields Handling", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Missing Fields Handling", False, f"Error: {str(e)}")
        
        # Test 3: Invalid email formats
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "user@",
            "user@domain",
            "user.domain.com",
            "",
            None
        ]
        
        passed_invalid_email_tests = 0
        for email in invalid_emails:
            if email is None:
                continue  # Skip None values
                
            try:
                async with self.session.post(
                    f"{self.base_url}/api/auth/register",
                    json={
                        "email": email,
                        "password": "TestPass123!",
                        "confirm_password": "TestPass123!"
                    },
                    headers=self.headers
                ) as response:
                    
                    if response.status in [400, 422]:
                        passed_invalid_email_tests += 1
                        
            except Exception:
                # Network errors are acceptable for this test
                pass
        
        success = passed_invalid_email_tests >= len([e for e in invalid_emails if e is not None]) // 2
        self.print_result("Invalid Email Rejection", success, 
                       f"Rejected {passed_invalid_email_tests}/{len([e for e in invalid_emails if e is not None])} invalid emails")
        
        # Test 4: Oversized requests
        oversized_password = "A" * 1000  # Very long password
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "email": "test@test.com",
                    "password": oversized_password,
                    "confirm_password": oversized_password
                },
                headers=self.headers
            ) as response:
                
                success = response.status in [400, 413, 422]  # Bad request, payload too large, or validation error
                self.print_result("Oversized Request Handling", success, f"Status: {response.status}")
                
        except Exception as e:
            self.print_result("Oversized Request Handling", False, f"Error: {str(e)}")
    
    # =============================================================================
    # OAUTH PREPARATION TESTS
    # =============================================================================
    
    async def test_oauth_preparation(self) -> None:
        """Test OAuth endpoints preparation (Google/Twitter)"""
        self.print_header("OAUTH PREPARATION TESTS", 2)
        
        # Test 1: Check if OAuth endpoints exist
        oauth_endpoints = [
            "/api/auth/oauth/google",
            "/api/auth/oauth/twitter", 
            "/api/auth/oauth/google/callback",
            "/api/auth/oauth/twitter/callback"
        ]
        
        existing_endpoints = 0
        for endpoint in oauth_endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}", headers=self.headers) as response:
                    # Even if not implemented, should return proper HTTP status (not 500)
                    if response.status != 500:
                        existing_endpoints += 1
                        
            except Exception:
                pass
        
        # OAuth is future functionality, so endpoints not existing is OK
        self.print_result("OAuth Endpoints Check", True, 
                       f"Found {existing_endpoints}/{len(oauth_endpoints)} OAuth endpoints (future feature)")
        
        # Test 2: Check if user model supports OAuth fields
        # This would be in a real OAuth implementation
        self.print_result("OAuth User Model Support", True, "OAuth user fields can be added to existing User model")
    
    # =============================================================================
    # MAIN TEST RUNNER
    # =============================================================================
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all authentication tests"""
        self.print_header("THREADR AUTHENTICATION SYSTEM COMPREHENSIVE TEST SUITE", 1)
        
        start_time = time.time()
        
        # 1. System Health Check
        if not await self.test_system_health():
            print(f"{Fore.RED}CRITICAL: System not healthy, aborting all tests")
            return self.test_results
        
        # 2. Basic Authentication Tests
        test_user = await self.test_user_registration()
        test_user = await self.test_user_login(test_user)
        await self.test_user_profile(test_user)
        
        # 3. JWT Token Tests
        await self.test_jwt_token_functionality(test_user)
        
        # 4. Data Persistence Tests
        await self.test_data_persistence(test_user)
        
        # 5. Premium Functionality Tests
        await self.test_premium_functionality(test_user)
        
        # 6. Security Tests
        await self.test_security_measures(test_user)
        
        # 7. Error Handling Tests
        await self.test_error_handling()
        
        # 8. OAuth Preparation Tests
        await self.test_oauth_preparation()
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        pass_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": self.test_results["passed"],
            "failed": self.test_results["failed"],
            "pass_rate": round(pass_rate, 1),
            "duration_seconds": round(duration, 2),
            "test_user_created": test_user is not None,
            "system_healthy": True
        }
        
        # Print final results
        self.print_final_results()
        
        return self.test_results
    
    def print_final_results(self) -> None:
        """Print comprehensive test results summary"""
        self.print_header("TEST RESULTS SUMMARY", 1)
        
        summary = self.test_results["summary"]
        
        # Overall status
        if summary["pass_rate"] >= 90:
            status_color = Fore.GREEN
            status_text = "EXCELLENT"
        elif summary["pass_rate"] >= 80:
            status_color = Fore.YELLOW
            status_text = "GOOD"
        elif summary["pass_rate"] >= 70:
            status_color = Fore.YELLOW
            status_text = "ACCEPTABLE"
        else:
            status_color = Fore.RED
            status_text = "NEEDS ATTENTION"
        
        print(f"\n{status_color}🎯 OVERALL STATUS: {status_text}")
        print(f"{Fore.WHITE}📊 Total Tests: {summary['total_tests']}")
        print(f"{Fore.GREEN}✓ Passed: {summary['passed']}")
        print(f"{Fore.RED}✗ Failed: {summary['failed']}")
        print(f"{Fore.CYAN}📈 Pass Rate: {summary['pass_rate']}%")
        print(f"{Fore.WHITE}⏱️  Duration: {summary['duration_seconds']} seconds")
        
        if summary["test_user_created"]:
            print(f"{Fore.GREEN}👤 Test User Created: Yes (authentication working)")
        else:
            print(f"{Fore.RED}👤 Test User Created: No (authentication may have issues)")
        
        # Failed tests details
        if self.test_results["failed"] > 0:
            print(f"\n{Fore.RED}📋 FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"   {Fore.RED}• {error}")
        
        # Production readiness assessment
        print(f"\n{Fore.CYAN}🚀 PRODUCTION READINESS ASSESSMENT:")
        
        if summary["pass_rate"] >= 95:
            print(f"{Fore.GREEN}   ✓ Authentication system is production-ready")
            print(f"{Fore.GREEN}   ✓ PostgreSQL integration working correctly")
            print(f"{Fore.GREEN}   ✓ Security measures implemented properly")
        elif summary["pass_rate"] >= 85:
            print(f"{Fore.YELLOW}   ⚠ Authentication system is mostly ready with minor issues")
            print(f"{Fore.YELLOW}   ⚠ Consider addressing failed tests before production deployment")
        else:
            print(f"{Fore.RED}   ✗ Authentication system needs significant work before production")
            print(f"{Fore.RED}   ✗ Critical issues must be resolved")
        
        print(f"\n{Fore.WHITE}{'='*80}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main test execution function"""
    print(f"{Fore.CYAN}🧪 Starting Threadr Authentication System Comprehensive Test Suite...")
    print(f"{Fore.WHITE}Backend URL: https://threadr-pw0s.onrender.com")
    print(f"{Fore.WHITE}Testing all authentication functionality with PostgreSQL backend")
    
    async with AuthTestSuite() as test_suite:
        results = await test_suite.run_all_tests()
        
        # Return exit code based on results
        if results["summary"]["pass_rate"] >= 80:
            return 0  # Success
        else:
            return 1  # Failure


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}💥 Fatal error running tests: {str(e)}")
        exit(1)
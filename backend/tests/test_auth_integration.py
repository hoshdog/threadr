"""
Integration test for Threadr authentication system
Tests the complete authentication flow and integration with existing endpoints
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Test imports
try:
    from auth_models import UserRegistrationRequest, UserLoginRequest, User, UserRole, UserStatus
    from auth_service import AuthService
    from auth_utils import PasswordService, TokenService, SecurityUtils
    from redis_manager import RedisManager
    print("[OK] All authentication modules imported successfully")
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)


class AuthenticationTester:
    """Test class for authentication system"""
    
    def __init__(self):
        self.redis_manager = None
        self.auth_service = None
        self.test_results = []
    
    async def setup(self):
        """Initialize test environment"""
        print("[SETUP] Setting up test environment...")
        
        # Initialize Redis manager
        self.redis_manager = RedisManager()
        if not self.redis_manager.is_available:
            print("[WARN] Redis not available - some tests will be skipped")
            return False
        
        # Initialize auth service
        self.auth_service = AuthService(self.redis_manager)
        print("[OK] Test environment setup complete")
        return True
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "[PASS]" if success else "[FAIL]"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}: {message}")
    
    async def test_password_service(self):
        """Test password hashing and verification"""
        test_password = "TestPassword123"
        
        try:
            # Test password hashing
            password_hash = PasswordService.hash_password(test_password)
            assert password_hash is not None, "Password hash should not be None"
            assert password_hash != test_password, "Password hash should be different from plain password"
            
            # Test password verification
            is_valid = PasswordService.verify_password(test_password, password_hash)
            assert is_valid, "Password verification should succeed"
            
            # Test invalid password
            is_invalid = PasswordService.verify_password("WrongPassword123", password_hash)
            assert not is_invalid, "Wrong password should not verify"
            
            self.log_test("Password Service", True, "Hash and verify operations working")
            
        except Exception as e:
            self.log_test("Password Service", False, f"Error: {e}")
    
    async def test_token_service(self):
        """Test JWT token generation and verification"""
        try:
            # Create test user
            test_user = User(
                user_id="test_user_123",
                email="test@example.com",
                password_hash="dummy_hash",
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Test access token creation
            access_token = TokenService.create_access_token(test_user)
            assert access_token is not None, "Access token should not be None"
            
            # Test token verification
            token_payload = TokenService.verify_token(access_token, "access")
            assert token_payload.sub == test_user.user_id, "Token subject should match user ID"
            assert token_payload.email == test_user.email, "Token email should match user email"
            
            # Test refresh token
            refresh_token = TokenService.create_refresh_token(test_user)
            refresh_payload = TokenService.verify_token(refresh_token, "refresh")
            assert refresh_payload.type == "refresh", "Refresh token type should be correct"
            
            self.log_test("Token Service", True, "Token generation and verification working")
            
        except Exception as e:
            self.log_test("Token Service", False, f"Error: {e}")
    
    async def test_user_registration(self):
        """Test user registration flow"""
        if not self.auth_service:
            self.log_test("User Registration", False, "Auth service not available")
            return
        
        try:
            # Test user registration
            registration_data = UserRegistrationRequest(
                email="testuser@example.com",
                password="TestPassword123",
                confirm_password="TestPassword123"
            )
            
            client_ip = "127.0.0.1"
            user, token_response = await self.auth_service.register_user(registration_data, client_ip)
            
            assert user is not None, "User should be created"
            assert user.email == "testuser@example.com", "User email should match"
            assert token_response.access_token is not None, "Access token should be provided"
            assert token_response.user.email == user.email, "Response user should match created user"
            
            self.log_test("User Registration", True, f"User {user.email} registered successfully")
            
            # Store for subsequent tests
            self.test_user = user
            self.test_token = token_response.access_token
            
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {e}")
    
    async def test_user_login(self):
        """Test user login flow"""
        if not self.auth_service:
            self.log_test("User Login", False, "Auth service not available")
            return
        
        try:
            # Test user login
            login_data = UserLoginRequest(
                email="testuser@example.com",
                password="TestPassword123"
            )
            
            client_ip = "127.0.0.1"
            token_response = await self.auth_service.login_user(login_data, client_ip)
            
            assert token_response.access_token is not None, "Access token should be provided"
            assert token_response.user.email == "testuser@example.com", "User email should match"
            
            self.log_test("User Login", True, "User login successful")
            
        except Exception as e:
            self.log_test("User Login", False, f"Error: {e}")
    
    async def test_token_validation(self):
        """Test token validation and user retrieval"""
        if not self.auth_service or not hasattr(self, 'test_token'):
            self.log_test("Token Validation", False, "Prerequisites not met")
            return
        
        try:
            # Test getting user from token
            user = await self.auth_service.get_current_user_from_token(self.test_token)
            
            assert user is not None, "User should be retrieved from token"
            assert user.email == "testuser@example.com", "User email should match"
            
            self.log_test("Token Validation", True, "Token validation and user retrieval working")
            
        except Exception as e:
            self.log_test("Token Validation", False, f"Error: {e}")
    
    async def test_security_utils(self):
        """Test security utility functions"""
        try:
            # Test email validation
            assert SecurityUtils.is_email_valid("test@example.com"), "Valid email should pass"
            assert not SecurityUtils.is_email_valid("invalid-email"), "Invalid email should fail"
            
            # Test email sanitization
            sanitized = SecurityUtils.sanitize_email("  TEST@EXAMPLE.COM  ")
            assert sanitized == "test@example.com", "Email should be sanitized"
            
            # Test user ID generation
            user_id = SecurityUtils.generate_user_id()
            assert user_id.startswith("user_"), "User ID should have correct prefix"
            
            # Test password strength
            strength = SecurityUtils.get_password_strength_score("TestPassword123")
            assert strength["score"] > 3, "Strong password should have good score"
            
            self.log_test("Security Utils", True, "All security utilities working")
            
        except Exception as e:
            self.log_test("Security Utils", False, f"Error: {e}")
    
    async def test_premium_integration(self):
        """Test integration with premium access system"""
        if not self.redis_manager:
            self.log_test("Premium Integration", False, "Redis not available")
            return
        
        try:
            client_ip = "127.0.0.1"
            email = "testuser@example.com"
            
            # Check initial premium status
            premium_info = await self.redis_manager.check_premium_access(client_ip, email)
            assert "has_premium" in premium_info, "Premium info should contain has_premium field"
            
            # Grant premium access
            success = await self.redis_manager.grant_premium_access(
                client_ip, email, "premium", 30, {"test": "payment"}
            )
            assert success, "Premium access should be granted"
            
            # Verify premium status
            premium_info = await self.redis_manager.check_premium_access(client_ip, email)
            assert premium_info["has_premium"], "User should now have premium access"
            
            self.log_test("Premium Integration", True, "Premium access system integration working")
            
        except Exception as e:
            self.log_test("Premium Integration", False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all authentication tests"""
        print("[START] Starting authentication system integration tests...\n")
        
        # Setup
        setup_success = await self.setup()
        if not setup_success:
            print("[ERROR] Setup failed - skipping most tests")
            await self.test_password_service()
            await self.test_security_utils()
            return
        
        # Run tests
        await self.test_password_service()
        await self.test_token_service()
        await self.test_security_utils()
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_token_validation()
        await self.test_premium_integration()
        
        # Cleanup
        await self.cleanup()
        
        # Print results
        self.print_summary()
    
    async def cleanup(self):
        """Clean up test data"""
        try:
            if self.redis_manager:
                # Clean up test user data
                test_email = "testuser@example.com"
                user_key = f"threadr:user:email:{test_email}"
                
                def _cleanup():
                    with self.redis_manager._redis_operation() as r:
                        if r:
                            # Get user ID and clean up all related data
                            user_id = r.get(user_key)
                            if user_id:
                                r.delete(f"threadr:user:{user_id}")
                                r.delete(user_key)
                                r.delete(f"threadr:session:{user_id}")
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self.redis_manager.executor, _cleanup)
                
                self.redis_manager.close()
                print("[CLEANUP] Test cleanup completed")
                
        except Exception as e:
            print(f"[WARN] Cleanup error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"\n[SUMMARY] Test Summary:")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if passed_tests == total_tests:
            print("[SUCCESS] All tests passed! Authentication system is working correctly.")
        else:
            print("[WARN] Some tests failed. Check the logs above for details.")
            
            # Print failed tests
            failed_tests = [result for result in self.test_results if not result["success"]]
            if failed_tests:
                print("\n[FAILED TESTS]:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['message']}")


async def main():
    """Main test function"""
    tester = AuthenticationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
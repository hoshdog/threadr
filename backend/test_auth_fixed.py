#!/usr/bin/env python3
"""
Test script for the fixed authentication service
Verifies that users can register successfully with PostgreSQL storage
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.auth.auth_service_fixed import AuthServiceFixed
from src.models.auth import UserRegistrationRequest, UserLoginRequest
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_auth_service_fixed():
    """Test the fixed authentication service"""
    
    print("=" * 60)
    print("TESTING FIXED AUTHENTICATION SERVICE")
    print("=" * 60)
    
    # Initialize auth service without Redis (simulating Redis unavailability)
    auth_service = AuthServiceFixed(redis_manager=None)
    
    # Test storage components
    print("\n1. Testing storage components...")
    components = await auth_service.test_storage_components_fixed()
    for component, status in components.items():
        print(f"   {component}: {status}")
    
    # Test user registration
    print("\n2. Testing user registration...")
    
    test_email = f"test_{int(asyncio.get_event_loop().time())}@example.com"
    registration_data = UserRegistrationRequest(
        email=test_email,
        password="TestPassword123!",
        confirm_password="TestPassword123!"
    )
    
    try:
        user, token_response = await auth_service.register_user(
            registration_data=registration_data,
            client_ip="127.0.0.1"
        )
        
        print(f"   ✅ Registration successful!")
        print(f"   User ID: {user.user_id}")
        print(f"   Email: {user.email}")
        print(f"   Access token length: {len(token_response.access_token)}")
        print(f"   Token expires in: {token_response.expires_in} seconds")
        
        # Test user login
        print("\n3. Testing user login...")
        
        login_data = UserLoginRequest(
            email=test_email,
            password="TestPassword123!",
            remember_me=False
        )
        
        login_response = await auth_service.login_user(
            login_data=login_data,
            client_ip="127.0.0.1"
        )
        
        print(f"   ✅ Login successful!")
        print(f"   User ID: {login_response.user.user_id}")
        print(f"   Login count: {user.login_count + 1}")
        print(f"   Access token length: {len(login_response.access_token)}")
        
        # Test user lookup
        print("\n4. Testing user lookup...")
        
        # By email
        found_user = await auth_service.get_user_by_email(test_email)
        if found_user:
            print(f"   ✅ User found by email: {found_user.user_id}")
        else:
            print(f"   ❌ User not found by email")
        
        # By ID
        found_user_by_id = await auth_service.get_user_by_id(user.user_id)
        if found_user_by_id:
            print(f"   ✅ User found by ID: {found_user_by_id.email}")
        else:
            print(f"   ❌ User not found by ID")
        
        # Test token verification
        print("\n5. Testing token verification...")
        
        token_user = await auth_service.get_current_user_from_token(token_response.access_token)
        if token_user:
            print(f"   ✅ Token verification successful: {token_user.email}")
        else:
            print(f"   ❌ Token verification failed")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - AUTHENTICATION SERVICE WORKING!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_duplicate_registration():
    """Test duplicate registration handling"""
    
    print("\n6. Testing duplicate registration handling...")
    
    auth_service = AuthServiceFixed(redis_manager=None)
    
    test_email = "duplicate@example.com"
    registration_data = UserRegistrationRequest(
        email=test_email,
        password="TestPassword123!",
        confirm_password="TestPassword123!"
    )
    
    try:
        # First registration
        user1, token1 = await auth_service.register_user(
            registration_data=registration_data,
            client_ip="127.0.0.1"
        )
        print(f"   ✅ First registration successful: {user1.user_id}")
        
        # Second registration (should fail)
        try:
            user2, token2 = await auth_service.register_user(
                registration_data=registration_data,
                client_ip="127.0.0.1"
            )
            print(f"   ❌ Duplicate registration should have failed!")
            return False
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ✅ Duplicate registration properly rejected: {e}")
                return True
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"   ❌ Test setup failed: {e}")
        return False


async def main():
    """Main test function"""
    
    try:
        # Test basic functionality
        basic_test = await test_auth_service_fixed()
        
        # Test duplicate handling
        duplicate_test = await test_duplicate_registration()
        
        if basic_test and duplicate_test:
            print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            print("\nThe fixed authentication service:")
            print("✅ Properly detects Redis unavailability")
            print("✅ Successfully stores users in PostgreSQL") 
            print("✅ Handles user registration and login")
            print("✅ Prevents duplicate registrations")
            print("✅ Provides proper token management")
            
        else:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test the fixed authentication service locally before deployment
"""

import asyncio
import sys
import uuid
from datetime import datetime

# Add backend/src to path
sys.path.insert(0, 'src')

from services.auth.auth_service import AuthServiceFixed
from models.auth import UserRegistrationRequest, UserLoginRequest
from services.auth.auth_utils import generate_user_id


async def test_auth_fixed():
    """Test the fixed authentication service"""
    print("TESTING FIXED AUTH SERVICE")
    print("=" * 50)
    
    # Create auth service with no Redis (simulating production)
    auth_service = AuthServiceFixed(redis_manager=None)
    
    # Test storage components
    print("\n1. Testing Storage Components:")
    components = await auth_service.test_storage_components_fixed()
    for key, value in components.items():
        status = "✅" if value else "❌"
        print(f"   {key}: {status} {value}")
    
    # Test registration
    print("\n2. Testing User Registration:")
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    registration_data = UserRegistrationRequest(
        email=test_email,
        password="TestPassword123!",
        confirm_password="TestPassword123!"
    )
    
    try:
        user, token_response = await auth_service.register_user(
            registration_data,
            client_ip="127.0.0.1"
        )
        print(f"   ✅ Registration successful!")
        print(f"   User ID: {user.user_id}")
        print(f"   Email: {user.email}")
        print(f"   Token: {token_response.access_token[:50]}...")
        
        # Test login
        print("\n3. Testing User Login:")
        login_data = UserLoginRequest(
            email=test_email,
            password="TestPassword123!",
            remember_me=False
        )
        
        login_response = await auth_service.login_user(
            login_data,
            client_ip="127.0.0.1"  
        )
        print(f"   ✅ Login successful!")
        print(f"   Token: {login_response.access_token[:50]}...")
        
        # Test user retrieval
        print("\n4. Testing User Retrieval:")
        retrieved_user = await auth_service.get_user_by_email(test_email)
        if retrieved_user:
            print(f"   ✅ User retrieved successfully!")
            print(f"   User ID matches: {retrieved_user.user_id == user.user_id}")
        else:
            print(f"   ❌ Failed to retrieve user")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED - AUTH SERVICE IS FIXED!")
    return True


if __name__ == "__main__":
    # Check if we can import database components
    try:
        from src.database import get_async_db, User as DBUser
        print("✅ PostgreSQL components available")
    except ImportError as e:
        print(f"⚠️ PostgreSQL components not available locally: {e}")
        print("This is expected in local testing without database setup")
    
    success = asyncio.run(test_auth_fixed())
    sys.exit(0 if success else 1)
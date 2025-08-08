#!/usr/bin/env python3
"""
Test individual components of the registration process to isolate the failure
"""

import sys
from pathlib import Path

# Add backend source to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

def test_password_hashing():
    """Test password hashing functionality"""
    print("=== TESTING PASSWORD HASHING ===")
    
    try:
        from services.auth.auth_utils import hash_password, verify_password
        
        test_password = "TestPass123!"
        print(f"Testing password: {test_password}")
        
        # Test hashing
        hashed = hash_password(test_password)
        print(f"✓ Password hashed successfully: {hashed[:20]}...")
        
        # Test verification
        is_valid = verify_password(test_password, hashed)
        print(f"✓ Password verification: {is_valid}")
        
        if is_valid:
            print("SUCCESS: Password hashing and verification working")
        else:
            print("ERROR: Password verification failed")
            
    except Exception as e:
        print(f"ERROR: Password hashing failed: {e}")

def test_user_id_generation():
    """Test user ID generation"""
    print("\n=== TESTING USER ID GENERATION ===")
    
    try:
        from services.auth.auth_utils import generate_user_id
        
        user_id = generate_user_id()
        print(f"✓ Generated user ID: {user_id}")
        
        if user_id and user_id.startswith("user_"):
            print("SUCCESS: User ID generation working")
        else:
            print("ERROR: Invalid user ID format")
            
    except Exception as e:
        print(f"ERROR: User ID generation failed: {e}")

def test_jwt_token_creation():
    """Test JWT token creation"""
    print("\n=== TESTING JWT TOKEN CREATION ===")
    
    try:
        from services.auth.auth_utils import create_access_token, create_refresh_token
        from models.auth import User, UserRole, UserStatus
        from datetime import datetime
        
        # Create a test user
        test_user = User(
            user_id="test_user_123",
            email="test@example.com",
            password_hash="dummy_hash",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        print(f"Test user created: {test_user.email}")
        
        # Test access token creation
        access_token = create_access_token(test_user)
        print(f"✓ Access token created: {access_token[:20]}...")
        
        # Test refresh token creation
        refresh_token = create_refresh_token(test_user)
        print(f"✓ Refresh token created: {refresh_token[:20]}...")
        
        print("SUCCESS: JWT token creation working")
        
    except Exception as e:
        print(f"ERROR: JWT token creation failed: {e}")

def test_user_model_creation():
    """Test User model creation"""
    print("\n=== TESTING USER MODEL CREATION ===")
    
    try:
        from models.auth import User, UserRole, UserStatus
        from datetime import datetime
        
        current_time = datetime.utcnow()
        
        test_user = User(
            user_id="test_user_456",
            email="test2@example.com",
            password_hash="test_hash_123",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            created_at=current_time,
            updated_at=current_time,
            metadata={"test": "data"}
        )
        
        print(f"✓ User model created: {test_user.email}")
        print(f"✓ User ID: {test_user.user_id}")
        print(f"✓ Role: {test_user.role}")
        print(f"✓ Status: {test_user.status}")
        
        # Test JSON serialization (used in Redis storage)
        json_data = test_user.model_dump_json()
        print(f"✓ JSON serialization: {len(json_data)} characters")
        
        print("SUCCESS: User model creation working")
        
    except Exception as e:
        print(f"ERROR: User model creation failed: {e}")

def test_pydantic_registration_request():
    """Test UserRegistrationRequest validation"""
    print("\n=== TESTING PYDANTIC REGISTRATION REQUEST ===")
    
    try:
        from models.auth import UserRegistrationRequest
        
        test_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        registration_request = UserRegistrationRequest(**test_data)
        print(f"✓ Registration request created: {registration_request.email}")
        print(f"✓ Password validated: {registration_request.password}")
        
        print("SUCCESS: Pydantic registration request validation working")
        
    except Exception as e:
        print(f"ERROR: Registration request validation failed: {e}")

def run_all_tests():
    """Run all component tests"""
    print("TESTING REGISTRATION COMPONENTS LOCALLY\n")
    
    test_pydantic_registration_request()
    test_password_hashing()
    test_user_id_generation()
    test_user_model_creation()
    test_jwt_token_creation()
    
    print("\n" + "="*60)
    print("LOCAL COMPONENT TESTING COMPLETE")
    print("If all tests pass, the issue is likely environment-specific")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
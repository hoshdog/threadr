#!/usr/bin/env python3
"""
Test JWT token creation locally to verify timestamp format is correct
"""

import sys
from pathlib import Path
import os
from datetime import datetime

# Add backend path
backend_path = Path("C:/Users/HoshitoPowell/Desktop/Threadr/backend/src")
sys.path.insert(0, str(backend_path))

# Set required environment variables
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-debugging"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

try:
    from models.auth import User, UserRole, UserStatus
    from services.auth.auth_utils import create_access_token, create_refresh_token
    print("SUCCESS: Successfully imported JWT utilities")
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    try:
        # Try alternative imports
        from src.models.auth import User, UserRole, UserStatus
        from src.services.auth.auth_utils import create_access_token, create_refresh_token  
        print("SUCCESS: Successfully imported JWT utilities (src path)")
    except ImportError as e2:
        print(f"ERROR: Both import attempts failed: {e2}")
        sys.exit(1)

def test_jwt_creation():
    """Test JWT token creation with timestamp formats"""
    
    print("\n1. Creating test user:")
    current_time = datetime.utcnow()
    
    try:
        test_user = User(
            user_id="test_user_123",
            email="test@example.com",
            password_hash="fake_hash",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            created_at=current_time,
            updated_at=current_time,
            login_count=0,
            failed_login_attempts=0,
            is_email_verified=False,
            metadata={}
        )
        print(f"   SUCCESS: Test user created")
        print(f"   User ID: {test_user.user_id}")
        print(f"   Email: {test_user.email}")
        print(f"   Created at: {test_user.created_at}")
    except Exception as e:
        print(f"   ERROR: Failed to create test user: {e}")
        return
    
    print("\n2. Testing JWT token creation:")
    try:
        access_token = create_access_token(test_user)
        print(f"   SUCCESS: Access token created")
        print(f"   Token length: {len(access_token)}")
        print(f"   Token preview: {access_token[:50]}...")
        
        # Test refresh token
        refresh_token = create_refresh_token(test_user)
        print(f"   SUCCESS: Refresh token created") 
        print(f"   Refresh token length: {len(refresh_token)}")
        
    except Exception as e:
        print(f"   ERROR: JWT creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n3. Testing JWT payload inspection:")
    try:
        from jose import jwt
        
        # Decode without verification to inspect payload
        payload = jwt.get_unverified_claims(access_token)
        print(f"   Token payload: {payload}")
        
        # Check timestamp format
        exp_timestamp = payload.get("exp")
        iat_timestamp = payload.get("iat")
        
        print(f"   Expiry timestamp: {exp_timestamp}")
        print(f"   Issued timestamp: {iat_timestamp}")
        
        # Convert timestamps back to datetime
        if exp_timestamp:
            exp_dt = datetime.fromtimestamp(exp_timestamp)
            print(f"   Expiry datetime: {exp_dt}")
            
        if iat_timestamp:
            iat_dt = datetime.fromtimestamp(iat_timestamp)
            print(f"   Issued datetime: {iat_dt}")
        
    except Exception as e:
        print(f"   ERROR: JWT inspection failed: {e}")
        import traceback
        traceback.print_exc()

def test_datetime_formats():
    """Test different datetime format approaches"""
    
    print("\n4. Testing datetime formats:")
    
    current_time = datetime.utcnow()
    
    print(f"   Current UTC time: {current_time}")
    print(f"   ISO format: {current_time.isoformat()}")
    print(f"   Timestamp: {current_time.timestamp()}")
    print(f"   Integer timestamp: {int(current_time.timestamp())}")

if __name__ == "__main__":
    test_jwt_creation()
    test_datetime_formats()
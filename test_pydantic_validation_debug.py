#!/usr/bin/env python3
"""
Test Pydantic validation locally to identify model_post_init issues
"""

import sys
import os
from pathlib import Path

# Add backend path
backend_path = Path("C:/Users/HoshitoPowell/Desktop/Threadr/backend/src")
sys.path.insert(0, str(backend_path))

try:
    from models.auth import UserRegistrationRequest
    print("SUCCESS: Successfully imported UserRegistrationRequest")
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)

def test_validation_scenarios():
    """Test different validation scenarios"""
    
    print("\n1. Testing Valid Registration Data:")
    try:
        valid_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "confirm_password": "TestPass123"
        }
        user_request = UserRegistrationRequest(**valid_data)
        print("   SUCCESS: Valid data passed validation")
        print(f"   Email: {user_request.email}")
        print(f"   Password length: {len(user_request.password)}")
    except Exception as e:
        print(f"   ERROR: Valid data failed: {e}")
    
    print("\n2. Testing Password Mismatch (HTTP 500 trigger):")
    try:
        mismatch_data = {
            "email": "test@example.com", 
            "password": "TestPass123",
            "confirm_password": "DifferentPass123"
        }
        user_request = UserRegistrationRequest(**mismatch_data)
        print("   ERROR: Password mismatch should have failed but didn't!")
    except ValueError as e:
        print(f"   SUCCESS: Password mismatch correctly rejected: {e}")
    except Exception as e:
        print(f"   ERROR: Unexpected error type: {type(e).__name__}: {e}")
    
    print("\n3. Testing Weak Password:")
    try:
        weak_data = {
            "email": "test@example.com",
            "password": "weak",
            "confirm_password": "weak"
        }
        user_request = UserRegistrationRequest(**weak_data)
        print("   ERROR: Weak password should have failed!")
    except ValueError as e:
        print(f"   SUCCESS: Weak password correctly rejected: {e}")
    except Exception as e:
        print(f"   ERROR: Unexpected error: {e}")
    
    print("\n4. Testing Invalid Email:")
    try:
        invalid_email_data = {
            "email": "invalid-email",
            "password": "TestPass123", 
            "confirm_password": "TestPass123"
        }
        user_request = UserRegistrationRequest(**invalid_email_data)
        print("   ERROR: Invalid email should have failed!")
    except ValueError as e:
        print(f"   SUCCESS: Invalid email correctly rejected: {e}")
    except Exception as e:
        print(f"   ERROR: Unexpected error: {e}")

def test_model_post_init_issue():
    """Test if model_post_init is causing the HTTP 500"""
    
    print("\n5. Testing model_post_init behavior:")
    
    # Test the raw model_post_init method
    try:
        from pydantic import BaseModel, Field, field_validator
        from typing import Any
        
        print("   Testing isolated model_post_init logic...")
        
        # Simulate the problematic data
        class TestModel(BaseModel):
            password: str
            confirm_password: str
            
            def model_post_init(self, __context: Any) -> None:
                """Test version of model_post_init"""
                print(f"     Password: '{self.password}'")
                print(f"     Confirm: '{self.confirm_password}'")
                if self.password != self.confirm_password:
                    raise ValueError('Passwords do not match')
        
        # This should work
        good_model = TestModel(password="test123", confirm_password="test123")
        print("   SUCCESS: Matching passwords work")
        
        # This should fail gracefully
        try:
            bad_model = TestModel(password="test123", confirm_password="different")
        except ValueError as e:
            print(f"   SUCCESS: Password mismatch handled properly: {e}")
        except Exception as e:
            print(f"   ERROR: Unexpected error in model_post_init: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"   ERROR: model_post_init test failed: {e}")

if __name__ == "__main__":
    test_validation_scenarios()
    test_model_post_init_issue()
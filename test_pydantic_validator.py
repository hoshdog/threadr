#!/usr/bin/env python3
"""
Test Pydantic model validation behavior
"""

from pydantic import BaseModel, field_validator, model_validator, ValidationError

class TestRegistration(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validate password confirmation matches password"""
        print(f"Model validator called - password: {getattr(self, 'password', 'MISSING')}, confirm: {getattr(self, 'confirm_password', 'MISSING')}")
        if hasattr(self, 'password') and hasattr(self, 'confirm_password'):
            if self.password != self.confirm_password:
                raise ValueError('Passwords do not match')
        return self

def test_validation():
    print("Testing Pydantic model validation...")
    
    # Test 1: Valid data
    try:
        valid = TestRegistration(password="test123", confirm_password="test123")
        print(f"[OK] Valid data: {valid}")
    except Exception as e:
        print(f"[FAIL] Valid data failed: {e}")
    
    # Test 2: Invalid data (passwords don't match)
    try:
        invalid = TestRegistration(password="test123", confirm_password="different")
        print(f"[FAIL] Invalid data should have failed: {invalid}")
    except ValidationError as e:
        print(f"[OK] ValidationError caught: {e}")
    except ValueError as e:
        print(f"[OK] ValueError caught: {e}")
    except Exception as e:
        print(f"[?] Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_validation()
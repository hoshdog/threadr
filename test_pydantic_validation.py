#!/usr/bin/env python3
"""
Test Pydantic validation directly to identify the exact validation issue
"""

import sys
import os
from pathlib import Path

# Add backend source to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from pydantic import ValidationError

try:
    from models.auth import UserRegistrationRequest
    print("Successfully imported UserRegistrationRequest")
except ImportError as e:
    print(f"Import error: {e}")
    try:
        from src.models.auth import UserRegistrationRequest  
        print("Successfully imported UserRegistrationRequest via src path")
    except ImportError as e2:
        print(f"Second import error: {e2}")
        sys.exit(1)

def test_registration_validation():
    """Test various registration data scenarios"""
    
    test_cases = [
        {
            "name": "Valid Strong Password",
            "data": {
                "email": "test@example.com",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!"
            }
        },
        {
            "name": "Valid Simple Password",
            "data": {
                "email": "test@example.com", 
                "password": "TestPass1",
                "confirm_password": "TestPass1"
            }
        },
        {
            "name": "Password Mismatch",
            "data": {
                "email": "test@example.com",
                "password": "TestPass123",
                "confirm_password": "DifferentPass123"
            }
        },
        {
            "name": "No Uppercase", 
            "data": {
                "email": "test@example.com",
                "password": "testpass123",
                "confirm_password": "testpass123"
            }
        },
        {
            "name": "No Lowercase",
            "data": {
                "email": "test@example.com", 
                "password": "TESTPASS123",
                "confirm_password": "TESTPASS123"
            }
        },
        {
            "name": "No Digit",
            "data": {
                "email": "test@example.com",
                "password": "TestPassword",
                "confirm_password": "TestPassword"  
            }
        },
        {
            "name": "Too Short",
            "data": {
                "email": "test@example.com",
                "password": "Test1",
                "confirm_password": "Test1"
            }
        },
        {
            "name": "Invalid Email",
            "data": {
                "email": "invalid-email",
                "password": "TestPass123",
                "confirm_password": "TestPass123"
            }
        }
    ]
    
    print("=== PYDANTIC VALIDATION TESTS ===\n")
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        
        try:
            # Attempt to create the Pydantic model
            registration_request = UserRegistrationRequest(**test_case['data'])
            print("VALIDATION PASSED")
            print(f"Created model: {registration_request}")
            
        except ValidationError as e:
            print("VALIDATION FAILED (Pydantic)")
            print(f"Validation errors: {e}")
            
        except ValueError as e:
            print("VALIDATION FAILED (ValueError)")
            print(f"ValueError: {e}")
            
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_registration_validation()
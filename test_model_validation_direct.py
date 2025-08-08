#!/usr/bin/env python3
"""
Test the exact model used in the backend
"""

import sys
import os

# Add the backend src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from models.auth import UserRegistrationRequest
    print("[OK] Successfully imported UserRegistrationRequest")
except ImportError as e:
    print(f"[FAIL] Failed to import UserRegistrationRequest: {e}")
    try:
        from src.models.auth import UserRegistrationRequest 
        print("[OK] Successfully imported UserRegistrationRequest (with src prefix)")
    except ImportError as e2:
        print(f"[FAIL] Failed with src prefix too: {e2}")
        sys.exit(1)

def test_our_model():
    print("\nTesting the actual UserRegistrationRequest model...")
    
    # Test 1: Valid data
    try:
        valid = UserRegistrationRequest(
            email="test@example.com", 
            password="ValidPass123", 
            confirm_password="ValidPass123"
        )
        print(f"[OK] Valid data works: {valid.email}")
    except Exception as e:
        print(f"[FAIL] Valid data failed: {e}")
    
    # Test 2: Password mismatch
    try:
        invalid = UserRegistrationRequest(
            email="test@example.com", 
            password="ValidPass123", 
            confirm_password="DifferentPass123"
        )
        print(f"[FAIL] Invalid should have failed: {invalid}")
    except Exception as e:
        print(f"[OK] Password mismatch correctly caught: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_our_model()
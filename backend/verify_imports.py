#!/usr/bin/env python3
"""
Verify that imports work correctly with the new src/ structure
Run this to test import resolution before deploying
"""

import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nTesting imports...")

try:
    # Test absolute import when running from backend directory
    from src.redis_manager import RedisManager
    print("[OK] Successfully imported RedisManager using 'from src.redis_manager'")
except ImportError as e:
    print(f"[FAIL] Failed to import RedisManager: {e}")

try:
    # Test running main as module
    import src.main
    print("[OK] Successfully imported src.main")
except ImportError as e:
    print(f"[FAIL] Failed to import src.main: {e}")

print("\nChecking file structure...")
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, "src")

print(f"Backend directory: {backend_dir}")
print(f"Src directory: {src_dir}")
print(f"Src directory exists: {os.path.exists(src_dir)}")

if os.path.exists(src_dir):
    print("Files in src/:")
    for file in os.listdir(src_dir):
        print(f"  {file}")
#!/usr/bin/env python3
"""
Grant Premium Access Script
==========================

This script grants premium access to a specific test account for development/testing purposes.
It directly interfaces with the Redis manager to add premium status.

Usage:
    python grant_premium_test_account.py

This will grant premium access to hoshito@detron.com.au for testing purposes.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to the path so we can import our modules
backend_src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src_path))

try:
    from core.redis_manager import RedisManager
except ImportError as e:
    print(f"Error importing RedisManager: {e}")
    print("Make sure you're running this from the backend directory and Redis is configured")
    sys.exit(1)


async def grant_test_premium_access():
    """Grant premium access to the test account"""
    
    # Test account details
    TEST_EMAIL = "hoshito@detron.com.au"
    TEST_IP = "127.0.0.1"  # Fallback IP for testing
    DURATION_DAYS = 365  # 1 year for extensive testing
    PLAN = "pro"  # Use "pro" plan for testing advanced features
    
    print(f"Granting premium access to test account...")
    print(f"   Email: {TEST_EMAIL}")
    print(f"   Duration: {DURATION_DAYS} days")
    print(f"   Plan: {PLAN}")
    print()
    
    try:
        # Initialize Redis manager
        redis_manager = RedisManager()
        
        if not redis_manager.is_available:
            print("ERROR: Redis is not available. Please check your Redis configuration.")
            print("   Make sure REDIS_URL is set in your environment variables.")
            return False
        
        # Check current premium status
        print("Checking current premium status...")
        current_status = await redis_manager.check_premium_access(TEST_IP, TEST_EMAIL)
        print(f"   Current status: {current_status}")
        print()
        
        # Grant premium access
        print("Granting premium access...")
        payment_info = {
            "source": "manual_test_grant",
            "granted_by": "development_script",
            "timestamp": datetime.now().isoformat(),
            "test_account": True
        }
        
        success = await redis_manager.grant_premium_access(
            client_ip=TEST_IP,
            email=TEST_EMAIL,
            plan=PLAN,
            duration_days=DURATION_DAYS,
            payment_info=payment_info
        )
        
        if success:
            print("SUCCESS: Premium access granted successfully!")
            
            # Verify the grant worked
            print("\nVerifying premium access...")
            verification = await redis_manager.check_premium_access(TEST_IP, TEST_EMAIL)
            
            if verification.get("has_premium", False):
                print("SUCCESS: Premium access verified!")
                print(f"   Plan: {verification.get('plan', 'unknown')}")
                print(f"   Expires: {verification.get('expires_at', 'unknown')}")
                print(f"   Source: {verification.get('source', 'unknown')}")
                
                # Calculate days remaining
                expires_at = verification.get("expires_at")
                if expires_at:
                    try:
                        expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        days_remaining = (expiry_date - datetime.now()).days
                        print(f"   Days remaining: {days_remaining}")
                    except:
                        print("   Days remaining: Could not calculate")
                
                print()
                print("SUCCESS: Test account is now premium!")
                print(f"   You can now test premium features with email: {TEST_EMAIL}")
                print(f"   Premium access expires: {expires_at}")
                
                return True
                
            else:
                print("ERROR: Premium access verification failed!")
                print(f"   Verification result: {verification}")
                return False
                
        else:
            print("ERROR: Failed to grant premium access!")
            return False
            
    except Exception as e:
        print(f"ERROR: Error granting premium access: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up Redis connection
        try:
            if 'redis_manager' in locals() and hasattr(redis_manager, 'executor'):
                redis_manager.executor.shutdown(wait=False)
        except:
            pass


async def check_premium_status():
    """Check current premium status for the test account"""
    
    TEST_EMAIL = "hoshito@detron.com.au"
    TEST_IP = "127.0.0.1"
    
    print(f"Checking premium status for: {TEST_EMAIL}")
    print()
    
    try:
        redis_manager = RedisManager()
        
        if not redis_manager.is_available:
            print("ERROR: Redis is not available.")
            return
        
        status = await redis_manager.check_premium_access(TEST_IP, TEST_EMAIL)
        
        print("Premium Status Report:")
        print(f"   Has Premium: {status.get('has_premium', False)}")
        print(f"   Source: {status.get('source', 'none')}")
        print(f"   Plan: {status.get('plan', 'N/A')}")
        print(f"   Granted At: {status.get('granted_at', 'N/A')}")
        print(f"   Expires At: {status.get('expires_at', 'N/A')}")
        
        if status.get('expires_at'):
            try:
                expiry_date = datetime.fromisoformat(status['expires_at'].replace('Z', '+00:00'))
                days_remaining = (expiry_date - datetime.now()).days
                print(f"   Days Remaining: {days_remaining}")
            except:
                print(f"   Days Remaining: Could not calculate")
        
        print()
        
        if status.get('has_premium'):
            print("SUCCESS: Account has premium access!")
        else:
            print("INFO: Account does not have premium access.")
            
    except Exception as e:
        print(f"ERROR: Error checking premium status: {e}")
        
    finally:
        try:
            if 'redis_manager' in locals() and hasattr(redis_manager, 'executor'):
                redis_manager.executor.shutdown(wait=False)
        except:
            pass


def main():
    """Main function to handle command line arguments"""
    
    print("Threadr Premium Test Account Manager")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Just check status
        asyncio.run(check_premium_status())
    else:
        # Grant premium access
        success = asyncio.run(grant_test_premium_access())
        
        if success:
            print("\n" + "=" * 50)
            print("Next Steps:")
            print("1. Test premium features in the frontend")
            print("2. Check the /api/premium/check endpoint")
            print("3. Verify unlimited thread generation")
            print("4. Test analytics and advanced features")
            print()
            print("Pro tip: Use 'python grant_premium_test_account.py check' to check status anytime")
        else:
            print("\n" + "=" * 50)
            print("ERROR: Failed to grant premium access. Check the error messages above.")
            print("Make sure Redis is running and REDIS_URL is configured correctly.")


if __name__ == "__main__":
    main()
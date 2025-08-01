#!/usr/bin/env python3
"""
Manual Premium Grant Script
==========================

This script directly grants premium access through the API endpoint instead of
trying to connect to Redis directly. This bypasses Redis connection issues.

Usage:
    python manual_premium_grant.py

This will grant premium access to hoshito@detron.com.au via the API.
"""

import requests
import json
import asyncio
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "https://threadr-production.up.railway.app"  # Production API
TEST_EMAIL = "hoshito@detron.com.au"
DURATION_DAYS = 365  # 1 year for testing
PLAN = "pro"


def grant_premium_via_api():
    """Grant premium access via the API endpoint"""
    
    print("Manual Premium Grant via API")
    print("=" * 40)
    print(f"Email: {TEST_EMAIL}")
    print(f"Duration: {DURATION_DAYS} days")
    print(f"Plan: {PLAN}")
    print()
    
    # Prepare the request data
    grant_data = {
        "email": TEST_EMAIL,
        "duration_days": DURATION_DAYS,
        "plan": PLAN
    }
    
    try:
        print("Sending premium grant request...")
        
        # Make the API call to grant premium access
        response = requests.post(
            f"{API_BASE_URL}/api/premium/grant",
            json=grant_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Premium-Grant-Script/1.0"
            },
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Premium access granted!")
            print(f"Message: {result.get('message', 'No message')}")
            print(f"Plan: {result.get('plan', 'Unknown')}")
            print(f"Duration: {result.get('duration_days', 'Unknown')} days")
            
            # Now verify the premium status
            print("\nVerifying premium status...")
            verify_premium_status()
            
            return True
            
        else:
            print(f"ERROR: Failed to grant premium access")
            print(f"Status Code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False


def verify_premium_status():
    """Verify premium status via the API"""
    
    try:
        print("Checking premium status...")
        
        # Check premium status
        response = requests.get(
            f"{API_BASE_URL}/api/premium/check",
            params={"email": TEST_EMAIL},
            headers={"User-Agent": "Premium-Check-Script/1.0"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Premium Status:")
            print(f"  Has Premium: {result.get('has_premium', False)}")
            print(f"  Expires At: {result.get('premium_expires_at', 'N/A')}")
            print(f"  Message: {result.get('message', 'N/A')}")
            
            if result.get('has_premium'):
                print("SUCCESS: Premium access verified!")
            else:
                print("WARNING: Premium access not found after grant")
                
        else:
            print(f"ERROR: Could not check premium status (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"ERROR: Could not verify premium status: {e}")


def create_manual_redis_entry():
    """Create a manual Redis entry by calling the production API directly"""
    
    print("\nAlternative: Creating manual premium entry...")
    
    # Create the premium data structure
    expires_at = (datetime.now() + timedelta(days=DURATION_DAYS)).isoformat()
    
    premium_data = {
        "granted_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "plan": PLAN,
        "duration_days": DURATION_DAYS,
        "email": TEST_EMAIL,
        "payment_info": {
            "source": "manual_test_grant",
            "granted_by": "development_script",
            "test_account": True
        }
    }
    
    print("Premium data to be stored:")
    print(json.dumps(premium_data, indent=2))
    
    # Redis keys that should be created:
    print(f"\nRedis keys to create:")
    print(f"  threadr:premium:email:{TEST_EMAIL}")
    print(f"  Value: {json.dumps(premium_data)}")
    print(f"  TTL: {DURATION_DAYS * 24 * 3600 + 7 * 24 * 3600} seconds")
    
    return premium_data


def test_api_connection():
    """Test if the API is available"""
    
    print("Testing API connection...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=10
        )
        
        if response.status_code == 200:
            print("SUCCESS: API is available")
            health_data = response.json()
            print(f"Status: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"ERROR: API returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to API: {e}")
        return False


def main():
    """Main function"""
    
    print("Threadr Manual Premium Grant Tool")
    print("=" * 50)
    print()
    
    # Test API connection first
    if not test_api_connection():
        print("\nCannot connect to API. Please check:")
        print("1. Internet connection")
        print("2. API URL is correct")
        print("3. API server is running")
        return
    
    print()
    
    # Try to grant premium access
    success = grant_premium_via_api()
    
    if success:
        print("\n" + "=" * 50)
        print("SUCCESS: Premium access granted!")
        print("\nNext steps:")
        print("1. Test the frontend with your email")
        print("2. Verify unlimited thread generation")
        print("3. Check premium features are accessible")
        print(f"4. Premium expires: {(datetime.now() + timedelta(days=DURATION_DAYS)).strftime('%Y-%m-%d')}")
    else:
        print("\n" + "=" * 50)
        print("ERROR: Could not grant premium access via API")
        print("\nManual alternative:")
        print("You can manually add the Redis key using these details:")
        create_manual_redis_entry()


if __name__ == "__main__":
    main()
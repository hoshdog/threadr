#!/usr/bin/env python3
"""
Direct Redis Premium Grant
==========================

This script directly connects to Redis and adds premium access keys.
Use this when you have direct access to the REDIS_URL.

Usage:
    REDIS_URL="your_redis_url_here" python direct_redis_premium_grant.py
    
    Or set REDIS_URL as an environment variable first:
    export REDIS_URL="your_redis_url_here"
    python direct_redis_premium_grant.py

This will directly add the premium access keys to Redis.
"""

import redis
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Configuration
TEST_EMAIL = "hoshito@detron.com.au"
TEST_IP = "127.0.0.1"  # Fallback IP
DURATION_DAYS = 365  # 1 year for testing
PLAN = "pro"


def connect_to_redis(redis_url):
    """Connect to Redis using the provided URL"""
    
    if not redis_url:
        return None, "No REDIS_URL provided"
    
    try:
        print(f"Connecting to Redis...")
        print(f"URL: {redis_url[:30]}..." if len(redis_url) > 30 else f"URL: {redis_url}")
        
        # Parse the Redis URL to determine connection type
        parsed = urlparse(redis_url)
        
        if redis_url.startswith("rediss://"):
            # SSL connection (Upstash/Heroku Redis)
            client = redis.Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10,
                ssl_cert_reqs=None  # For cloud Redis services
            )
        else:
            # Standard Redis connection
            client = redis.Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10
            )
        
        # Test the connection
        client.ping()
        print("SUCCESS: Connected to Redis!")
        return client, None
        
    except redis.ConnectionError as e:
        return None, f"Connection error: {e}"
    except redis.AuthenticationError as e:
        return None, f"Authentication error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def create_premium_data():
    """Create the premium data structure"""
    
    current_time = datetime.now()
    expires_at = current_time + timedelta(days=DURATION_DAYS)
    
    premium_data = {
        "granted_at": current_time.isoformat(),
        "expires_at": expires_at.isoformat(),
        "plan": PLAN,
        "duration_days": DURATION_DAYS,
        "client_ip": TEST_IP,
        "email": TEST_EMAIL,
        "payment_info": {
            "source": "manual_test_grant",
            "granted_by": "direct_redis_script",
            "timestamp": current_time.isoformat(),
            "test_account": True
        }
    }
    
    return premium_data


def grant_premium_access(redis_client):
    """Grant premium access by directly setting Redis keys"""
    
    premium_data = create_premium_data()
    premium_ttl = DURATION_DAYS * 24 * 3600 + 7 * 24 * 3600  # Extra 7 days buffer
    
    print("\nGranting premium access...")
    print(f"Email: {TEST_EMAIL}")
    print(f"Plan: {PLAN}")
    print(f"Duration: {DURATION_DAYS} days")
    print(f"Expires: {premium_data['expires_at']}")
    
    try:
        # Use Redis pipeline for atomic operations
        pipe = redis_client.pipeline()
        
        # Store premium access by email
        email_premium_key = f"threadr:premium:email:{TEST_EMAIL}"
        pipe.setex(email_premium_key, premium_ttl, json.dumps(premium_data))
        
        # Store premium access by IP as fallback
        ip_premium_key = f"threadr:premium:ip:{TEST_IP}"
        pipe.setex(ip_premium_key, premium_ttl, json.dumps(premium_data))
        
        # Update premium stats
        pipe.hincrby("threadr:usage:stats", "total_premium_grants", 1)
        pipe.hincrby("threadr:usage:stats", f"premium_grants_{datetime.now().strftime('%Y-%m')}", 1)
        
        # Execute all operations
        results = pipe.execute()
        
        print("SUCCESS: Premium access keys created!")
        print(f"  Email key: {email_premium_key}")
        print(f"  IP key: {ip_premium_key}")
        print(f"  TTL: {premium_ttl} seconds ({premium_ttl // (24 * 3600)} days)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create premium access keys: {e}")
        return False


def verify_premium_access(redis_client):
    """Verify that the premium access was created correctly"""
    
    print("\nVerifying premium access...")
    
    try:
        # Check email-based key
        email_key = f"threadr:premium:email:{TEST_EMAIL}"
        email_data = redis_client.get(email_key)
        
        # Check IP-based key
        ip_key = f"threadr:premium:ip:{TEST_IP}"
        ip_data = redis_client.get(ip_key)
        
        if email_data:
            email_premium = json.loads(email_data)
            print("SUCCESS: Email-based premium access found!")
            print(f"  Plan: {email_premium.get('plan', 'unknown')}")
            print(f"  Expires: {email_premium.get('expires_at', 'unknown')}")
            
            # Check TTL
            ttl = redis_client.ttl(email_key)
            print(f"  TTL: {ttl} seconds ({ttl // (24 * 3600)} days remaining)")
            
        else:
            print("ERROR: Email-based premium access not found!")
            
        if ip_data:
            print("SUCCESS: IP-based premium access found!")
        else:
            print("ERROR: IP-based premium access not found!")
            
        return bool(email_data or ip_data)
        
    except Exception as e:
        print(f"ERROR: Failed to verify premium access: {e}")
        return False


def list_all_premium_users(redis_client):
    """List all premium users for debugging"""
    
    print("\nListing all premium users...")
    
    try:
        # Scan for all premium keys
        premium_keys = list(redis_client.scan_iter("threadr:premium:*"))
        
        if not premium_keys:
            print("No premium users found.")
            return
        
        print(f"Found {len(premium_keys)} premium access keys:")
        
        for key in premium_keys[:10]:  # Limit to first 10
            try:
                data = redis_client.get(key)
                if data:
                    premium_info = json.loads(data)
                    email = premium_info.get('email', 'N/A')
                    plan = premium_info.get('plan', 'N/A')
                    expires = premium_info.get('expires_at', 'N/A')
                    print(f"  {key}: {email} ({plan}) expires {expires}")
                else:
                    print(f"  {key}: [no data]")
            except:
                print(f"  {key}: [invalid data]")
        
        if len(premium_keys) > 10:
            print(f"  ... and {len(premium_keys) - 10} more")
            
    except Exception as e:
        print(f"ERROR: Failed to list premium users: {e}")


def main():
    """Main function"""
    
    print("Direct Redis Premium Grant Tool")
    print("=" * 50)
    print()
    
    # Get Redis URL from environment or command line
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url and len(sys.argv) > 1:
        redis_url = sys.argv[1]
    
    if not redis_url:
        print("ERROR: No REDIS_URL provided!")
        print()
        print("Usage:")
        print("  REDIS_URL='your_redis_url' python direct_redis_premium_grant.py")
        print("  OR")
        print("  python direct_redis_premium_grant.py 'your_redis_url'")
        print("  OR")
        print("  export REDIS_URL='your_redis_url'")
        print("  python direct_redis_premium_grant.py")
        print()
        print("Example URLs:")
        print("  Redis: redis://localhost:6379")
        print("  Upstash: rediss://default:password@host:port")
        print("  Heroku: rediss://h:password@host:port")
        return
    
    # Connect to Redis
    redis_client, error = connect_to_redis(redis_url)
    
    if not redis_client:
        print(f"ERROR: Could not connect to Redis: {error}")
        print()
        print("Please check:")
        print("1. Redis URL is correct")
        print("2. Redis server is running")
        print("3. Network connectivity")
        print("4. Authentication credentials")
        return
    
    try:
        # Grant premium access
        success = grant_premium_access(redis_client)
        
        if success:
            # Verify the grant
            verify_success = verify_premium_access(redis_client)
            
            if verify_success:
                print("\n" + "=" * 50)
                print("SUCCESS: Premium access granted and verified!")
                print(f"Account: {TEST_EMAIL}")
                print(f"Plan: {PLAN}")
                print(f"Duration: {DURATION_DAYS} days")
                print()
                print("Next steps:")
                print("1. Test premium features in the frontend")
                print("2. Use the email in API calls")
                print("3. Verify unlimited access")
            else:
                print("\nWARNING: Premium access granted but verification failed")
        else:
            print("\nERROR: Failed to grant premium access")
            
        # Show debug info
        list_all_premium_users(redis_client)
        
    finally:
        # Close Redis connection
        try:
            redis_client.close()
        except:
            pass


if __name__ == "__main__":
    main()
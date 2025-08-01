#!/usr/bin/env python3
"""
Show Redis Commands for Manual Premium Grant
===========================================

This script shows you the exact Redis commands to run manually
to grant premium access to your test account.

Usage:
    python show_redis_commands.py

This will output the Redis CLI commands you need to run.
"""

import json
from datetime import datetime, timedelta

# Configuration
TEST_EMAIL = "hoshito@detron.com.au"
TEST_IP = "127.0.0.1"
DURATION_DAYS = 365  # 1 year for testing
PLAN = "pro"


def generate_premium_data():
    """Generate the premium data structure"""
    
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
            "granted_by": "manual_redis_commands",
            "timestamp": current_time.isoformat(),
            "test_account": True
        }
    }
    
    return premium_data


def show_redis_commands():
    """Show the Redis commands to run manually"""
    
    premium_data = generate_premium_data()
    premium_json = json.dumps(premium_data, separators=(',', ':'))  # Compact JSON
    premium_ttl = DURATION_DAYS * 24 * 3600 + 7 * 24 * 3600  # Extra 7 days buffer
    
    print("Manual Redis Commands for Premium Grant")
    print("=" * 60)
    print()
    print(f"Account: {TEST_EMAIL}")
    print(f"Plan: {PLAN}")
    print(f"Duration: {DURATION_DAYS} days")
    print(f"Expires: {premium_data['expires_at']}")
    print(f"TTL: {premium_ttl} seconds ({premium_ttl // (24 * 3600)} days)")
    print()
    
    print("Option 1: Using Redis CLI")
    print("-" * 30)
    print()
    print("Connect to your Redis instance and run these commands:")
    print()
    
    # Email-based key
    email_key = f"threadr:premium:email:{TEST_EMAIL}"
    print(f'SETEX "{email_key}" {premium_ttl} \'{premium_json}\'')
    print()
    
    # IP-based key (fallback)
    ip_key = f"threadr:premium:ip:{TEST_IP}"
    print(f'SETEX "{ip_key}" {premium_ttl} \'{premium_json}\'')
    print()
    
    # Update stats
    print('HINCRBY "threadr:usage:stats" "total_premium_grants" 1')
    current_month = datetime.now().strftime('%Y-%m')
    print(f'HINCRBY "threadr:usage:stats" "premium_grants_{current_month}" 1')
    print()
    
    print("Option 2: Using Redis Desktop Manager or RedisInsight")
    print("-" * 50)
    print()
    print("Create these keys manually:")
    print()
    print(f"Key 1: {email_key}")
    print(f"Type: String")
    print(f"Value: {premium_json}")
    print(f"TTL: {premium_ttl} seconds")
    print()
    print(f"Key 2: {ip_key}")
    print(f"Type: String")
    print(f"Value: {premium_json}")
    print(f"TTL: {premium_ttl} seconds")
    print()
    
    print("Option 3: Using curl to call the API (requires API key)")
    print("-" * 55)
    print()
    api_payload = {
        "email": TEST_EMAIL,
        "duration_days": DURATION_DAYS,
        "plan": PLAN
    }
    api_json = json.dumps(api_payload, indent=2)
    
    print("curl -X POST https://threadr-production.up.railway.app/api/premium/grant \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -H 'X-API-Key: YOUR_API_KEY_HERE' \\")
    print(f"  -d '{json.dumps(api_payload)}'")
    print()
    
    print("Verification Commands")
    print("-" * 20)
    print()
    print("To verify the premium access was created:")
    print()
    print(f'GET "{email_key}"')
    print(f'TTL "{email_key}"')
    print()
    
    print("To check if it's working via API:")
    print()
    print(f"curl 'https://threadr-production.up.railway.app/api/premium/check?email={TEST_EMAIL}'")
    print()
    
    print("Raw Premium Data")
    print("-" * 16)
    print()
    print("If you need the raw JSON data:")
    print(json.dumps(premium_data, indent=2))
    print()
    
    print("Key Information Summary")
    print("-" * 23)
    print(f"Email Key: {email_key}")
    print(f"IP Key: {ip_key}")
    print(f"TTL: {premium_ttl} seconds")
    print(f"Expires: {premium_data['expires_at']}")
    print(f"Plan: {PLAN}")


def show_connection_examples():
    """Show examples of how to connect to different Redis services"""
    
    print("\nRedis Connection Examples")
    print("=" * 30)
    print()
    
    print("Local Redis:")
    print("  redis-cli")
    print("  redis-cli -h localhost -p 6379")
    print()
    
    print("Upstash Redis:")
    print("  redis-cli --tls -h your-endpoint.upstash.io -p 6380 -a your-password")
    print()
    
    print("Railway Redis:")
    print("  redis-cli -h your-host -p your-port -a your-password")
    print()
    
    print("Heroku Redis:")
    print("  redis-cli -h your-host -p your-port -a your-password --tls")
    print()


def main():
    """Main function"""
    
    show_redis_commands()
    show_connection_examples()
    
    print("\nNext Steps:")
    print("1. Choose one of the options above")
    print("2. Execute the Redis commands")
    print("3. Verify the premium access")
    print("4. Test in the frontend with your email")
    print(f"5. The premium access will expire on: {(datetime.now() + timedelta(days=DURATION_DAYS)).strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
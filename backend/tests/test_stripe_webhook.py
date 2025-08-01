#!/usr/bin/env python3
"""
Test script for Stripe webhook integration
Run this to test the webhook endpoint locally
"""

import json
import hmac
import hashlib
import time
import requests
from datetime import datetime

# Test configuration
WEBHOOK_URL = "http://localhost:8000/api/webhooks/stripe"  # Change to your local server
TEST_WEBHOOK_SECRET = "whsec_test_secret"  # Set this in your .env file for testing

# Sample Stripe checkout.session.completed event
SAMPLE_EVENT = {
    "id": "evt_test_webhook",
    "object": "event",
    "api_version": "2020-08-27",
    "created": int(time.time()),
    "data": {
        "object": {
            "id": "cs_test_session_123",
            "object": "checkout.session",
            "amount_total": 499,  # $4.99 in cents
            "currency": "usd",
            "customer_details": {
                "email": "test@example.com"
            },
            "payment_status": "paid",
            "mode": "payment"
        }
    },
    "livemode": False,
    "pending_webhooks": 1,
    "request": {
        "id": "req_test_123",
        "idempotency_key": None
    },
    "type": "checkout.session.completed"
}

def create_stripe_signature(payload: str, secret: str) -> str:
    """Create a valid Stripe signature for testing"""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload}"
    
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"

def test_webhook():
    """Test the Stripe webhook endpoint"""
    payload = json.dumps(SAMPLE_EVENT)
    signature = create_stripe_signature(payload, TEST_WEBHOOK_SECRET)
    
    headers = {
        'Content-Type': 'application/json',
        'Stripe-Signature': signature,
        'User-Agent': 'Stripe/1.0 (+https://stripe.com/docs/webhooks)'
    }
    
    print(f"Testing webhook at: {WEBHOOK_URL}")
    print(f"Event type: {SAMPLE_EVENT['type']}")
    print(f"Customer email: {SAMPLE_EVENT['data']['object']['customer_details']['email']}")
    print(f"Amount: ${SAMPLE_EVENT['data']['object']['amount_total']/100:.2f}")
    print("-" * 50)
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('processed'):
                print("✅ Webhook processed successfully!")
                print("Premium access should have been granted.")
            else:
                print("⚠️  Webhook received but not processed.")
                print(f"Reason: {result.get('message', 'Unknown')}")
        else:
            print("❌ Webhook failed to process.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to webhook endpoint: {e}")
        print("Make sure your local server is running on port 8000")

def test_invalid_signature():
    """Test webhook with invalid signature (should fail)"""
    payload = json.dumps(SAMPLE_EVENT)
    invalid_signature = "t=123456789,v1=invalid_signature"
    
    headers = {
        'Content-Type': 'application/json',
        'Stripe-Signature': invalid_signature
    }
    
    print("\nTesting invalid signature (should fail):")
    print("-" * 50)
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 401:
            print("✅ Invalid signature correctly rejected!")
        else:
            print("⚠️  Expected 401 status for invalid signature")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Stripe Webhook Test Script")
    print("=" * 30)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test valid webhook
    test_webhook()
    
    # Test invalid signature
    test_invalid_signature()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNext steps:")
    print("1. Check your server logs for webhook processing details")
    print("2. Verify premium access was granted in Redis")
    print("3. Test with real Stripe webhook in Stripe Dashboard")
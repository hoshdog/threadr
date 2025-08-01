# Stripe Payment Link Debug Summary

## Issue
The "Upgrade Now" button in the payment modal wasn't redirecting to Stripe because the payment URL was returning `null` from the backend.

## Root Cause
The `STRIPE_PAYMENT_LINK_URL` environment variable is not configured in Railway, despite other Stripe variables being properly set.

## Evidence
Debug endpoint `/debug/env` shows:
```json
{
  "stripe_vars": {
    "STRIPE_SECRET_KEY": "configured",
    "STRIPE_WEBHOOK_SECRET": "configured", 
    "STRIPE_PRICE_ID": "not_configured",
    "STRIPE_PAYMENT_LINK_URL": "not_configured"
  },
  "payment_vars_raw": {
    "payment_link_type": "<class 'NoneType'>",
    "payment_link_none": true
  }
}
```

## Solution
1. Go to Railway project dashboard
2. Navigate to backend service → Variables tab
3. Add environment variable:
   - **Key**: `STRIPE_PAYMENT_LINK_URL`
   - **Value**: Your Stripe payment link (e.g., `https://buy.stripe.com/xxxxx`)

## Verification Steps
After adding the variable:
1. Wait for Railway auto-redeploy
2. Test: `curl https://threadr-production.up.railway.app/api/payment/config`
3. Verify `payment_url` is no longer `null`
4. Test "Upgrade Now" button functionality

## Code Flow
1. Backend reads `STRIPE_PAYMENT_LINK_URL` from environment
2. `/api/payment/config` endpoint returns it as `payment_url`
3. Frontend fetches config when showing payment modal
4. "Upgrade Now" button uses `paymentConfig?.payment_url`
5. Opens payment link in new tab with `window.open()`

## Files Modified for Debugging
- `backend/src/main.py`: Added debug logging and `/debug/env` endpoint
- These can be removed after the issue is resolved

## Current Status
- ✅ Root cause identified
- ⏳ Waiting for user to add Railway environment variable
- ⏳ Verification pending
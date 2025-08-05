# Stripe Subscription System Verification Guide

**Date**: 2025-08-04  
**Status**: DEPLOYMENT ISSUE IDENTIFIED - Subscription router not loading  
**Backend URL**: https://threadr-production.up.railway.app  
**Frontend URL**: https://threadr-plum.vercel.app

## 🚨 CRITICAL ISSUE FOUND

**Problem**: Subscription API endpoints are not accessible (404 errors)  
**Root Cause**: Subscription router not being included in FastAPI app despite code being present  
**Impact**: Users cannot access pricing plans or create subscriptions  

## ✅ VERIFIED WORKING COMPONENTS

### 1. Railway Deployment Status
```bash
curl -s https://threadr-production.up.railway.app/health
# Response: {"status":"healthy","timestamp":"2025-08-04T22:09:03.172072","environment":"production"}
# Status: ✅ WORKING
```

### 2. Environment Variables Configuration
```bash
curl -s https://threadr-production.up.railway.app/debug/env | head -10
# All Stripe environment variables properly configured:
# - STRIPE_SECRET_KEY: configured
# - STRIPE_WEBHOOK_SECRET: configured  
# - STRIPE_STARTER_MONTHLY_PRICE_ID: present
# - STRIPE_STARTER_ANNUAL_PRICE_ID: present
# - STRIPE_PRO_MONTHLY_PRICE_ID: present
# - STRIPE_PRO_ANNUAL_PRICE_ID: present
# - STRIPE_TEAM_MONTHLY_PRICE_ID: present
# - STRIPE_TEAM_ANNUAL_PRICE_ID: present
# Status: ✅ ALL CONFIGURED
```

### 3. Stripe Webhook Endpoint
```bash
curl -s -w "HTTP Status: %{http_code}\n" https://threadr-production.up.railway.app/api/webhooks/stripe
# Response: {"detail":"Method Not Allowed"}HTTP Status: 405
# Status: ✅ ENDPOINT EXISTS (405 = POST only, which is correct)
```

### 4. Base API Functionality
```bash
curl -s https://threadr-production.up.railway.app/api/test
# Response: {"status":"working","message":"This is a test message..."}
# Status: ✅ WORKING
```

## ❌ FAILING COMPONENTS

### 1. Subscription API Endpoints
```bash
# All subscription endpoints return 404:
curl -s https://threadr-production.up.railway.app/api/subscription/plans
# Response: {"detail":"Not Found"}
# Status: ❌ NOT FOUND

# Expected subscription endpoints (defined in code but not accessible):
# GET /api/subscription/plans - Get subscription plans and pricing
# POST /api/subscription/create-checkout - Create Stripe checkout session
# GET /api/subscription/status - Get user's subscription status
# POST /api/subscription/cancel - Cancel subscription
# POST /api/subscription/reactivate - Reactivate subscription
# POST /api/subscription/change-plan - Change subscription plan
# GET /api/subscription/usage - Get subscription usage stats
```

### 2. API Documentation Missing Subscription Routes
```bash
curl -s https://threadr-production.up.railway.app/openapi.json | grep -o '"/[^"]*"' | grep subscription
# Response: (empty - no subscription routes found)
# Status: ❌ SUBSCRIPTION ROUTES NOT REGISTERED
```

## 🔧 TROUBLESHOOTING STEPS

### Step 1: Verify Subscription Router Import Issue
**Problem**: The subscription router is defined in `backend/src/routes/subscription.py` but not being loaded by FastAPI.

**Check**: Look at Railway deployment logs for import errors:
1. Go to Railway dashboard → Threadr project → Deployments → View logs
2. Look for Python import errors related to subscription module
3. Check for Stripe API key initialization errors

### Step 2: Potential Fix - Redeploy Backend
The issue is likely a deployment-time import error. Try redeploying:

```bash
# From the backend directory:
railway up --detach
```

### Step 3: Check Stripe API Initialization
The subscription router might fail to load if Stripe API key is invalid:

```bash
# Test Stripe connection manually
curl -s https://threadr-production.up.railway.app/debug/env | grep STRIPE_SECRET_KEY
# Should show "configured" not the actual key
```

### Step 4: Verify FastAPI Router Registration
Check if there are conditional statements preventing router inclusion:
- Look at `backend/src/main.py` around lines 325-357
- Verify that both Redis and non-Redis code paths include subscription router
- Check for any exception handling that might be swallowing import errors

## 🧪 COMPLETE TESTING CHECKLIST

### Backend API Tests (Run these after fixing the deployment issue)

1. **Subscription Plans Endpoint**
```bash
curl -s https://threadr-production.up.railway.app/api/subscription/plans
# Expected: {"success": true, "plans": {...}}
```

2. **Create Checkout Session (Requires Auth)**
```bash
# First login to get JWT token
TOKEN=$(curl -s -X POST https://threadr-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Then test checkout creation
curl -s -X POST https://threadr-production.up.railway.app/api/subscription/create-checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price_id":"STRIPE_STARTER_MONTHLY_PRICE_ID"}'
# Expected: {"success": true, "checkout_url": "https://checkout.stripe.com/..."}
```

3. **Subscription Status (Requires Auth)**
```bash
curl -s https://threadr-production.up.railway.app/api/subscription/status \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"subscription_id": null, "status": "inactive", ...}
```

4. **Webhook Endpoint (POST)**
```bash
# Test with dummy webhook data (will fail signature verification, but endpoint should respond)
curl -s -X POST https://threadr-production.up.railway.app/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type":"test"}'
# Expected: 400 error about missing/invalid signature (not 404)
```

### Frontend Integration Tests

1. **Check Frontend Can Load Pricing Data**
```javascript
// Test in browser console on https://threadr-plum.vercel.app
fetch('https://threadr-production.up.railway.app/api/subscription/plans')
  .then(r => r.json())
  .then(console.log)
// Expected: Plans object with pricing information
```

2. **Verify CORS Configuration**
```javascript
// Test CORS from frontend domain
fetch('https://threadr-production.up.railway.app/api/subscription/plans', {
  method: 'GET',
  mode: 'cors',
  credentials: 'omit'
}).then(r => console.log('CORS OK:', r.status))
```

## 📋 IMMEDIATE ACTION ITEMS

### High Priority (Fix Deployment Issue)
1. **Redeploy Backend with Debug Logging**
   - Add temporary logging to verify subscription router loading
   - Check Railway deployment logs for import errors
   - Verify all dependencies are installed correctly

2. **Test Subscription Router Import Locally**
   - Run backend locally with same environment variables
   - Verify subscription endpoints work in local development
   - Compare local vs production behavior

3. **Verify Stripe SDK Version Compatibility**
   - Check if Stripe library version in requirements.txt is compatible
   - Ensure all Stripe imports are working correctly

### Medium Priority (After Backend Fixed)
1. **Frontend Integration Testing**
   - Update frontend to consume subscription API endpoints
   - Test checkout flow end-to-end
   - Verify webhook processing with test events

2. **User Experience Testing**
   - Test complete subscription signup flow
   - Verify payment success/failure handling
   - Test subscription management features

### Low Priority (Monitoring & Analytics)
1. **Set up Subscription Analytics**
   - Track conversion rates
   - Monitor failed payments
   - Set up alerts for webhook failures

## 🎯 SUCCESS CRITERIA

**Deployment Fixed When:**
- ✅ `GET /api/subscription/plans` returns 200 with pricing data
- ✅ Subscription endpoints appear in `/openapi.json`
- ✅ Authenticated users can create checkout sessions
- ✅ Webhook endpoint processes Stripe events correctly

**Integration Complete When:**
- ✅ Frontend pricing page loads subscription data
- ✅ Users can complete checkout flow end-to-end
- ✅ Subscription status updates after payment
- ✅ Premium features are unlocked for paying users

## 🔍 DEBUG COMMANDS REFERENCE

```bash
# Check backend health
curl https://threadr-production.up.railway.app/health

# List all available endpoints
curl -s https://threadr-production.up.railway.app/openapi.json | grep -o '"/[^"]*"' | sort

# Check environment variables
curl https://threadr-production.up.railway.app/debug/env

# Test subscription plans (main failing endpoint)
curl https://threadr-production.up.railway.app/api/subscription/plans

# Test webhook accessibility
curl -X POST https://threadr-production.up.railway.app/api/webhooks/stripe

# Check CORS from frontend
curl -H "Origin: https://threadr-plum.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://threadr-production.up.railway.app/api/subscription/plans
```

## 📞 NEXT STEPS

1. **IMMEDIATE**: Fix subscription router deployment issue
2. **SHORT-TERM**: Complete end-to-end testing once backend is working  
3. **LONG-TERM**: Set up monitoring and analytics for subscription system

**Priority**: HIGH - Subscription system is critical for monetization  
**Timeline**: Should be resolved within 1-2 hours of deployment fix
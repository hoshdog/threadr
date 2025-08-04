# Railway Subscription Deployment Verification Guide

## 🚨 CRITICAL ISSUE IDENTIFIED

**Status**: Railway backend is returning 502 Bad Gateway - Application failed to respond
**URL**: https://threadr-production.up.railway.app/health
**Impact**: Complete service unavailable - all subscription features non-functional

## Root Cause Analysis

### 1. Missing Environment Variables
The Railway deployment is likely missing **OPENAI_API_KEY** which causes startup failure:
- Backend startup function `check_openai_availability()` requires OPENAI_API_KEY
- If missing, the startup process may fail silently
- 502 error indicates the application process is not responding

### 2. Potential Import Issues
The backend has complex import patterns that may fail in Railway environment:
- Multiple try/except import blocks for relative imports
- PYTHONPATH configuration in nixpacks.toml might be insufficient

## IMMEDIATE FIX REQUIRED

### Step 1: Verify Required Environment Variables in Railway
**Critical Variables That Must Be Set:**

```bash
# Core API Keys (REQUIRED)
OPENAI_API_KEY=sk-...                     # OpenAI API key for thread generation
REDIS_URL=redis://...                     # Upstash Redis connection string

# Stripe Configuration (REQUIRED for subscriptions)
STRIPE_SECRET_KEY=sk_live_...             # Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...           # Stripe webhook secret
STRIPE_PRICE_ID_STARTER_MONTHLY=price_... # Starter monthly plan
STRIPE_PRICE_ID_STARTER_ANNUAL=price_...  # Starter annual plan
STRIPE_PRICE_ID_PRO_MONTHLY=price_...     # Pro monthly plan
STRIPE_PRICE_ID_PRO_ANNUAL=price_...      # Pro annual plan
STRIPE_PRICE_ID_TEAM_MONTHLY=price_...    # Team monthly plan
STRIPE_PRICE_ID_TEAM_ANNUAL=price_...     # Team annual plan

# Application Configuration
ENVIRONMENT=production
CORS_ORIGINS=https://threadr-plum.vercel.app
```

### Step 2: Railway Deployment Commands

```bash
# Check current environment variables
railway variables list

# Add missing variables (if not set)
railway variables set OPENAI_API_KEY=sk-your-key-here
railway variables set REDIS_URL=redis://your-redis-url

# Redeploy after setting variables
railway up --detach
```

### Step 3: Verify Deployment Success

```bash
# Wait 2-3 minutes after deployment, then test
curl -X GET "https://threadr-production.up.railway.app/health"

# Expected successful response:
{
  "status": "healthy",
  "timestamp": "2025-08-04T22:17:32.000Z",
  "services": {
    "redis": "connected",
    "openai": "available",
    "stripe": "configured"
  }
}
```

## Complete Verification Checklist

Once the 502 error is fixed, run these tests:

### 1. Basic Health Check
```bash
curl -X GET "https://threadr-production.up.railway.app/health" \
  -H "Accept: application/json"
```
**Expected**: 200 OK with health status

### 2. Subscription Plans Endpoint
```bash
curl -X GET "https://threadr-production.up.railway.app/api/subscription/plans" \
  -H "Accept: application/json"
```
**Expected**: JSON with pricing tiers and Stripe price IDs

### 3. Stripe Webhook Endpoint
```bash
curl -X POST "https://threadr-production.up.railway.app/api/subscription/webhook" \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test" \
  -d '{}'
```
**Expected**: 401 or 400 (endpoint accessible, signature validation working)

### 4. Authentication Test
```bash
# Register test user
curl -X POST "https://threadr-production.up.railway.app/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'

# Login to get token
curl -X POST "https://threadr-production.up.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```
**Expected**: JWT token in response

### 5. Subscription Status (Authenticated)
```bash
# Use token from login response
curl -X GET "https://threadr-production.up.railway.app/api/subscription/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Accept: application/json"
```
**Expected**: User subscription status

### 6. Create Checkout Session
```bash
curl -X POST "https://threadr-production.up.railway.app/api/subscription/create-checkout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "price_id": "price_starter_monthly",
    "success_url": "https://threadr-plum.vercel.app/success",
    "cancel_url": "https://threadr-plum.vercel.app/cancel"
  }'
```
**Expected**: Stripe checkout session URL

## Frontend-Backend Integration Tests

### 1. Test from Browser Console
```javascript
// Open https://threadr-plum.vercel.app and run in console:

// Test health endpoint
fetch('https://threadr-production.up.railway.app/health')
  .then(r => r.json())
  .then(console.log);

// Test subscription plans
fetch('https://threadr-production.up.railway.app/api/subscription/plans')
  .then(r => r.json())
  .then(console.log);

// Test CORS headers
fetch('https://threadr-production.up.railway.app/api/subscription/plans', {
  mode: 'cors',
  credentials: 'omit'
}).then(r => console.log('CORS works:', r.ok));
```

### 2. Network Tab Verification
1. Open browser DevTools > Network tab
2. Navigate to https://threadr-plum.vercel.app
3. Look for API calls to threadr-production.up.railway.app
4. Verify no CORS errors in console
5. Check response status codes (should be 200, not 502)

## Common Issues & Solutions

### 502 Bad Gateway
- **Cause**: Application not starting due to missing environment variables
- **Fix**: Set all required environment variables in Railway dashboard
- **Check**: Verify OPENAI_API_KEY and REDIS_URL are set

### CORS Errors
- **Cause**: Incorrect CORS_ORIGINS configuration
- **Fix**: Ensure CORS_ORIGINS=https://threadr-plum.vercel.app (no trailing slash)
- **Test**: Use fetch with explicit CORS mode in browser console

### Import Errors
- **Cause**: Python import path issues in Railway container
- **Fix**: Check nixpacks.toml PYTHONPATH configuration
- **Debug**: Add logging to startup process

### Stripe Webhook Failures
- **Cause**: Missing STRIPE_WEBHOOK_SECRET or incorrect endpoint URL
- **Fix**: Verify webhook secret matches Stripe dashboard configuration
- **Test**: Use Stripe CLI to test webhook locally first

### Database Connection Issues
- **Cause**: Invalid REDIS_URL or Redis service unavailable
- **Fix**: Check Redis connection string format and service status
- **Fallback**: App should continue with in-memory storage if Redis fails

## Railway Logs Debugging

### View Deployment Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and view logs
railway login
railway logs --tail 100

# Filter for errors
railway logs --tail 100 | grep -i error
railway logs --tail 100 | grep -i startup
```

### Key Log Messages to Look For
- ✅ "Threadr backend startup completed successfully"
- ❌ "CRITICAL STARTUP ERROR"
- ❌ "OpenAI API key not found"
- ❌ "Redis connection failed"
- ❌ Import error messages

## Success Indicators

### Backend Healthy
- Health endpoint returns 200 OK
- All services show as "connected" or "available"
- No 502 Bad Gateway errors
- Railway logs show successful startup

### Subscription System Working
- Plans endpoint returns pricing data with Stripe price IDs
- Authentication endpoints accept login/register
- Checkout session creation works
- Webhook endpoint is accessible (even if it rejects invalid signatures)

### Frontend Integration Working
- No CORS errors in browser console
- API calls from frontend receive responses
- Subscription plans load on frontend
- Payment flow initiates successfully

## Production Monitoring

### Set Up Alerts
- Monitor health endpoint uptime
- Track 502 error rates
- Alert on startup failures
- Monitor Stripe webhook delivery success rates

### Performance Metrics
- Response time for subscription endpoints
- Database connection pool usage
- Memory and CPU utilization
- API rate limiting effectiveness

---

## Next Steps After Fixing 502 Error

1. **Complete this verification checklist**
2. **Test all subscription endpoints systematically**
3. **Verify frontend-backend integration**
4. **Set up monitoring and alerting**
5. **Document any additional configuration needed**
6. **Create subscription flow end-to-end tests**

**Priority**: Fix the 502 error IMMEDIATELY - the entire subscription system is non-functional until the backend starts properly.
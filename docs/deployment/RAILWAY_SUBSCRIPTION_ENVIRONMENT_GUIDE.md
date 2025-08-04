# Railway Environment Variables Configuration Guide for Threadr Subscription System

This guide provides step-by-step instructions for configuring Railway environment variables specifically for the Threadr subscription billing system using Stripe.

## Prerequisites

- Railway account with Threadr project deployed
- Stripe account with subscription products configured
- Access to Railway dashboard
- Stripe API keys and webhook secrets

## Overview

The Threadr subscription system requires 8 specific environment variables to handle different subscription tiers (Starter, Pro, Team) with both monthly and annual pricing options.

## Environment Variables Required

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `STRIPE_SECRET_KEY` | Stripe API secret key | `sk_live_...` or `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook endpoint verification | `whsec_...` |
| `STRIPE_STARTER_MONTHLY_PRICE_ID` | Starter plan monthly price | `price_...` |
| `STRIPE_STARTER_ANNUAL_PRICE_ID` | Starter plan annual price | `price_...` |
| `STRIPE_PRO_MONTHLY_PRICE_ID` | Pro plan monthly price | `price_...` |
| `STRIPE_PRO_ANNUAL_PRICE_ID` | Pro plan annual price | `price_...` |
| `STRIPE_TEAM_MONTHLY_PRICE_ID` | Team plan monthly price | `price_...` |
| `STRIPE_TEAM_ANNUAL_PRICE_ID` | Team plan annual price | `price_...` |

## Step-by-Step Railway Configuration

### Step 1: Access Railway Dashboard

1. **Open Railway Dashboard**
   - Go to [railway.app](https://railway.app)
   - Sign in to your account
   - You should see your projects listed

2. **Select Threadr Project**
   - Click on your "threadr" or "threadr-production" project
   - You should see the project overview with services

3. **Access Backend Service**
   - Click on the backend service (usually named "backend" or shows FastAPI)
   - You should now see the service dashboard

### Step 2: Navigate to Variables Section

1. **Find Variables Tab**
   - Look for tabs at the top: "Deployments", "Variables", "Settings", etc.
   - Click on the "Variables" tab
   - You should see a list of current environment variables

2. **Variables Interface Overview**
   - **Left Panel**: List of existing variables
   - **Right Panel**: Add new variable form
   - **Search Box**: Filter existing variables (if many exist)

### Step 3: Add Stripe Environment Variables

#### 3.1: Add STRIPE_SECRET_KEY

1. **Click "New Variable" Button** (usually in top-right of variables section)
2. **Variable Name Field**: Enter exactly `STRIPE_SECRET_KEY`
3. **Variable Value Field**: 
   - For testing: `sk_test_51...` (your Stripe test key)
   - For production: `sk_live_51...` (your Stripe live key)
4. **Click "Add" or "Save"**
5. **Verify**: The variable should appear in the left panel

⚠️ **Security Warning**: Never share or expose your Stripe secret key. It should start with `sk_test_` or `sk_live_`.

#### 3.2: Add STRIPE_WEBHOOK_SECRET

1. **Click "New Variable" Button**
2. **Variable Name**: `STRIPE_WEBHOOK_SECRET`
3. **Variable Value**: Your webhook secret (starts with `whsec_`)
4. **Click "Add"**

💡 **How to find webhook secret**: 
- Stripe Dashboard → Developers → Webhooks → Your endpoint → "Signing secret"

#### 3.3: Add Price ID Variables

Repeat for each of the 6 price ID variables:

1. **STRIPE_STARTER_MONTHLY_PRICE_ID**
   - Variable Name: `STRIPE_STARTER_MONTHLY_PRICE_ID`
   - Variable Value: `price_...` (from Stripe Dashboard → Products → Starter → Monthly price)

2. **STRIPE_STARTER_ANNUAL_PRICE_ID**
   - Variable Name: `STRIPE_STARTER_ANNUAL_PRICE_ID`
   - Variable Value: `price_...` (from Stripe Dashboard → Products → Starter → Annual price)

3. **STRIPE_PRO_MONTHLY_PRICE_ID**
   - Variable Name: `STRIPE_PRO_MONTHLY_PRICE_ID`
   - Variable Value: `price_...` (from Stripe Dashboard → Products → Pro → Monthly price)

4. **STRIPE_PRO_ANNUAL_PRICE_ID**
   - Variable Name: `STRIPE_PRO_ANNUAL_PRICE_ID`
   - Variable Value: `price_...` (from Stripe Dashboard → Products → Pro → Annual price)

5. **STRIPE_TEAM_MONTHLY_PRICE_ID**
   - Variable Name: `STRIPE_TEAM_MONTHLY_PRICE_ID`
   - Variable Value: `price_...` (from Stripe Dashboard → Products → Team → Monthly price)

6. **STRIPE_TEAM_ANNUAL_PRICE_ID**
   - Variable Name: `STRIPE_TEAM_ANNUAL_PRICE_ID`
   - Variable Value: `price_...` (from Stripe Dashboard → Products → Team → Annual price)

💡 **How to find price IDs**:
- Stripe Dashboard → Products → Click product → Copy price ID (starts with `price_`)

### Step 4: Verify Variables Are Set

After adding all variables, you should see 8 new environment variables in the Variables list:

```
✅ STRIPE_SECRET_KEY = sk_***...
✅ STRIPE_WEBHOOK_SECRET = whsec_***...
✅ STRIPE_STARTER_MONTHLY_PRICE_ID = price_***...
✅ STRIPE_STARTER_ANNUAL_PRICE_ID = price_***...  
✅ STRIPE_PRO_MONTHLY_PRICE_ID = price_***...
✅ STRIPE_PRO_ANNUAL_PRICE_ID = price_***...
✅ STRIPE_TEAM_MONTHLY_PRICE_ID = price_***...
✅ STRIPE_TEAM_ANNUAL_PRICE_ID = price_***...
```

## Step 5: Redeploy Application

### Option A: Automatic Redeploy (Recommended)
Railway automatically redeploys when environment variables change:

1. **Wait for Auto-Deploy**
   - Railway detects the environment variable changes
   - A new deployment should start automatically
   - You'll see "Deploying..." status in the project dashboard

2. **Monitor Deployment**
   - Click on the latest deployment to see logs
   - Look for successful startup messages

### Option B: Manual Redeploy
If automatic deployment doesn't occur:

1. **Go to Deployments Tab**
   - Click "Deployments" tab in your service
   - Click "Deploy" button to trigger manual deployment

2. **Force Git Push** (Alternative)
   ```bash
   git commit --allow-empty -m "Trigger Railway redeploy for subscription variables"
   git push
   ```

## Step 6: Verify Deployment Success

### 6.1: Check Deployment Logs

1. **Access Deployment Logs**
   - Go to "Deployments" tab
   - Click on the latest (most recent) deployment
   - Click "View Logs" or similar option

2. **Look for Success Indicators**
   ```
   ✅ Good logs:
   INFO: Started server process [1]
   INFO: Application startup complete
   INFO: Uvicorn running on http://0.0.0.0:8080
   
   ❌ Error indicators:
   ERROR: Could not start server
   ModuleNotFoundError
   KeyError: 'STRIPE_SECRET_KEY'
   ```

### 6.2: Test Health Endpoint

1. **Get Your Railway URL**
   - In Railway dashboard, look for your app URL
   - Should be something like: `https://threadr-production.up.railway.app`

2. **Test Health Check**
   - Open browser and go to: `https://your-app-url.railway.app/health`
   - Should return JSON response with "status": "healthy"

3. **Test Subscription Endpoint** (Optional)
   ```bash
   curl -X GET https://your-app-url.railway.app/api/subscription/config \
     -H "Content-Type: application/json"
   ```

## Step 7: Test Subscription System

### 7.1: Frontend Integration Test

1. **Visit Frontend Application**
   - Go to your Vercel-deployed frontend (e.g., `https://threadr-plum.vercel.app`)
   - Ensure it can connect to your Railway backend

2. **Test Subscription Flow**
   - Navigate to subscription/pricing page
   - Try creating a checkout session
   - Verify Stripe checkout loads correctly

### 7.2: Webhook Testing

1. **Stripe Dashboard Test**
   - Go to Stripe Dashboard → Webhooks
   - Find your Railway webhook endpoint
   - Click "Send test webhook"
   - Check Railway logs for webhook processing

## Common Issues and Solutions

### Issue 1: Variables Not Taking Effect

**Symptoms**: 
- KeyError messages in logs
- "Environment variable not found" errors
- Subscription endpoints returning 500 errors

**Solutions**:
1. **Verify Variable Names**: Ensure exact spelling (case-sensitive)
2. **Check Variable Values**: Ensure no extra spaces or characters
3. **Force Redeploy**: 
   ```bash
   git commit --allow-empty -m "Force redeploy"
   git push
   ```
4. **Clear Railway Cache**: In Settings → "Reset Build Cache"

### Issue 2: Stripe API Key Invalid

**Symptoms**:
- "Invalid API key" errors in logs
- Stripe-related endpoints failing
- 401 authentication errors from Stripe

**Solutions**:
1. **Check Key Format**: 
   - Test keys start with `sk_test_`
   - Live keys start with `sk_live_`
2. **Verify in Stripe Dashboard**: API Keys section
3. **Regenerate Key**: If necessary, create new key in Stripe
4. **Update Railway Variable**: Replace with new key

### Issue 3: Price IDs Not Found

**Symptoms**:
- "Price not found" errors
- Checkout sessions failing to create
- Invalid price ID errors from Stripe

**Solutions**:
1. **Verify Price IDs in Stripe**:
   - Go to Products → Your Product → Pricing
   - Copy exact price ID (starts with `price_`)
2. **Check Product Status**: Ensure products are active in Stripe
3. **Test vs Live Mode**: Ensure price IDs match your key mode

### Issue 4: Webhook Secret Invalid

**Symptoms**:
- Webhook signature verification failing
- "Invalid signature" errors
- Webhooks not processing

**Solutions**:
1. **Get Correct Secret**: 
   - Stripe Dashboard → Webhooks → Your endpoint → Signing secret
2. **Format Check**: Should start with `whsec_`
3. **Regenerate Secret**: Delete and recreate webhook endpoint if needed

### Issue 5: Deployment Fails After Adding Variables

**Symptoms**:
- Deployment stuck or failing
- Service won't start after variable changes
- Import errors or module not found

**Solutions**:
1. **Check Deployment Logs**: Look for specific error messages
2. **Verify nixpacks.toml**: Ensure configuration is correct
3. **Test Locally**: 
   ```bash
   cd backend
   export STRIPE_SECRET_KEY=sk_test_...
   # Set other variables
   python -m uvicorn src.main:app --reload
   ```
4. **Rollback if Needed**: Remove variables and redeploy, then add back one by one

## Security Best Practices

### 1. Environment Variable Security
- ✅ **Never commit secrets to git**: Use `.env` files locally, Railway variables in production
- ✅ **Use test keys for development**: Switch to live keys only for production
- ✅ **Rotate keys regularly**: Update API keys periodically
- ❌ **Don't share keys**: Never share secret keys via chat, email, or screenshots

### 2. Production vs Test Environment
- **Test Environment**: Use `sk_test_` keys and test price IDs
- **Production Environment**: Use `sk_live_` keys and live price IDs
- **Separate Railway Projects**: Consider separate projects for test/prod

### 3. Webhook Security
- ✅ **Always verify webhook signatures**: Use `STRIPE_WEBHOOK_SECRET`
- ✅ **Use HTTPS endpoints**: Railway provides HTTPS by default
- ✅ **Validate webhook events**: Check event types and data

## Verification Checklist

Before considering setup complete, verify:

- [ ] All 8 environment variables are set in Railway
- [ ] Variable names match exactly (case-sensitive)
- [ ] Variable values are correct (no extra spaces)
- [ ] Deployment completed successfully
- [ ] Health endpoint returns 200 OK
- [ ] No error messages in deployment logs
- [ ] Frontend can connect to backend
- [ ] Subscription endpoints respond correctly
- [ ] Stripe webhook endpoint is configured
- [ ] Test webhook delivery works

## Environment Variables Quick Reference

Copy this template for your Railway variables:

```bash
# Core Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51... # or sk_live_51... for production
STRIPE_WEBHOOK_SECRET=whsec_...

# Subscription Price IDs
STRIPE_STARTER_MONTHLY_PRICE_ID=price_...
STRIPE_STARTER_ANNUAL_PRICE_ID=price_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_ANNUAL_PRICE_ID=price_...
STRIPE_TEAM_MONTHLY_PRICE_ID=price_...
STRIPE_TEAM_ANNUAL_PRICE_ID=price_...
```

## Next Steps

After successful configuration:

1. **Test Complete Subscription Flow**
   - Create test subscription
   - Process webhook events
   - Verify user access changes

2. **Monitor Production Usage**
   - Check Railway logs regularly
   - Monitor Stripe dashboard for events
   - Set up alerting for errors

3. **Document Your Configuration**
   - Keep record of price IDs used
   - Document any custom configuration
   - Update team on new variables

## Support Resources

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Stripe API Documentation**: [stripe.com/docs/api](https://stripe.com/docs/api)
- **Threadr Railway Guide**: `docs/deployment/railway/RAILWAY_DEPLOYMENT_GUIDE.md`
- **Railway Support**: Available through Railway dashboard

## Troubleshooting Commands

```bash
# Check Railway service status
railway status

# View recent logs
railway logs --tail 50

# View environment variables (from Railway CLI)
railway variables

# Test health endpoint
curl https://your-app.railway.app/health

# Test subscription config endpoint
curl https://your-app.railway.app/api/subscription/config
```

---

This guide should enable successful configuration of all subscription system environment variables in Railway. If you encounter issues not covered here, check the main Railway deployment guide or contact support with specific error messages.
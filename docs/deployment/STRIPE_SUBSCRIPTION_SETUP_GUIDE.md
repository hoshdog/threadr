# Stripe Subscription Setup Guide for Threadr

This comprehensive guide walks through setting up Stripe subscription products for Threadr's tiered pricing model. Follow these steps exactly to avoid common configuration issues.

## Overview

**Transformation:** From $4.99 flat rate to tiered subscriptions
**Products to Create:**
- Starter: $9.99/month ($95.90/year - 20% discount)
- Pro: $19.99/month ($191.90/year - 20% discount)  
- Team: $49.99/month ($479.90/year - 20% discount)

## Phase 1: Stripe Account Setup & API Keys

### Step 1: Access Stripe Dashboard
1. Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Log in to your Stripe account
3. **CRITICAL:** Ensure you're in **Test Mode** first (toggle in left sidebar shows "Test Mode")
4. You should see "Test Mode" indicator in the top-left corner

### Step 2: Get Test API Keys
1. In left sidebar, click **"Developers"**
2. Click **"API Keys"**
3. You'll see two sections:
   - **Publishable key** (starts with `pk_test_`)
   - **Secret key** (starts with `sk_test_`)
4. Click **"Reveal test key token"** for the Secret key
5. **Copy and save both keys securely**

**What you should see:**
- Publishable key: `pk_test_51ABC123...` (visible by default)
- Secret key: `sk_test_51ABC123...` (hidden, click to reveal)

### Step 3: Set Test Environment Variables
Add these to your development environment:
```bash
# Test Mode Keys
STRIPE_PUBLISHABLE_KEY=pk_test_51ABC123...
STRIPE_SECRET_KEY=sk_test_51ABC123...
STRIPE_WEBHOOK_SECRET=whsec_test_123... (we'll get this later)
```

## Phase 2: Create Subscription Products

### Method A: Using the Python Script (Recommended)

1. **Set the API key in your environment:**
   ```bash
   export STRIPE_SECRET_KEY=sk_test_51ABC123...
   ```

2. **Run the product creation script:**
   ```bash
   cd backend
   python scripts/create_stripe_products.py
   ```

3. **Verify script output shows:**
   ```
   ✓ Created Starter product (monthly): price_ABC123
   ✓ Created Starter product (annual): price_DEF456
   ✓ Created Pro product (monthly): price_GHI789
   ✓ Created Pro product (annual): price_JKL012
   ✓ Created Team product (monthly): price_MNO345
   ✓ Created Team product (annual): price_PQR678
   ```

4. **Copy the price IDs** - you'll need these for environment variables

### Method B: Manual Creation (If Script Fails)

#### Step 1: Create Products
1. In Stripe Dashboard, go to **"Products"** in left sidebar
2. Click **"+ Add product"**

**For each product (Starter, Pro, Team):**

**Product 1: Starter**
1. Click **"+ Add product"**
2. **Name:** `Threadr Starter`
3. **Description:** `100 threads/month + basic analytics`
4. **Image:** Leave blank or upload Threadr logo
5. Click **"Save product"**

**Product 2: Pro**
1. Click **"+ Add product"**
2. **Name:** `Threadr Pro`
3. **Description:** `Unlimited threads + advanced features`
4. **Image:** Leave blank or upload Threadr logo
5. Click **"Save product"**

**Product 3: Team**
1. Click **"+ Add product"**
2. **Name:** `Threadr Team`
3. **Description:** `Team accounts + collaboration tools`
4. **Image:** Leave blank or upload Threadr logo
5. Click **"Save product"**

#### Step 2: Add Pricing to Each Product

**For Starter Product:**
1. Click on **"Threadr Starter"** product
2. Click **"Add pricing"**

**Monthly Price:**
- **Price:** `9.99`
- **Currency:** `USD`
- **Billing period:** `Monthly`
- **Usage type:** `Licensed` (not metered)
- Click **"Save pricing"**

**Annual Price:**
1. Click **"Add pricing"** again
- **Price:** `95.90` (20% discount: $9.99 × 12 × 0.8)
- **Currency:** `USD`
- **Billing period:** `Yearly`
- **Usage type:** `Licensed`
- Click **"Save pricing"**

**Repeat for Pro Product:**
- Monthly: `$19.99`
- Annual: `$191.90` ($19.99 × 12 × 0.8)

**Repeat for Team Product:**
- Monthly: `$49.99`
- Annual: `$479.90` ($49.99 × 12 × 0.8)

#### Step 3: Copy Price IDs
1. For each product, click on it to view details
2. You'll see pricing entries with IDs like `price_ABC123`
3. **Copy all 6 price IDs** (3 products × 2 billing periods each)

## Phase 3: Webhook Configuration

### Step 1: Create Webhook Endpoint
1. In Stripe Dashboard, go to **"Developers"** → **"Webhooks"**
2. Click **"+ Add endpoint"**
3. **Endpoint URL:** 
   - For testing: `https://your-backend-url.railway.app/api/stripe/webhook`
   - For production: `https://threadr-production.up.railway.app/api/stripe/webhook`

### Step 2: Select Events
**CRITICAL:** Select these exact events (scroll through the list):
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `checkout.session.completed`

### Step 3: Get Webhook Secret
1. After creating the webhook, click on it
2. Click **"Reveal"** next to **"Signing secret"**
3. Copy the secret (starts with `whsec_test_`)
4. Add to your environment variables:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_test_123...
   ```

## Phase 4: Environment Variables Setup

### Complete Test Environment Variables
Add these to your Railway test environment:

```bash
# Stripe Configuration (Test Mode)
STRIPE_PUBLISHABLE_KEY=pk_test_51ABC123...
STRIPE_SECRET_KEY=sk_test_51ABC123...
STRIPE_WEBHOOK_SECRET=whsec_test_123...

# Product Price IDs (Test Mode)
STRIPE_STARTER_MONTHLY_PRICE_ID=price_starter_monthly_test
STRIPE_STARTER_ANNUAL_PRICE_ID=price_starter_annual_test
STRIPE_PRO_MONTHLY_PRICE_ID=price_pro_monthly_test
STRIPE_PRO_ANNUAL_PRICE_ID=price_pro_annual_test
STRIPE_TEAM_MONTHLY_PRICE_ID=price_team_monthly_test
STRIPE_TEAM_ANNUAL_PRICE_ID=price_team_annual_test

# Success/Cancel URLs
STRIPE_SUCCESS_URL=https://threadr-plum.vercel.app/success
STRIPE_CANCEL_URL=https://threadr-plum.vercel.app/cancel
```

### How to Set Environment Variables in Railway
1. Go to your Railway project dashboard
2. Click on your backend service
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add each variable name and value
6. Click **"Deploy"** to restart service with new variables

## Phase 5: Testing Phase

### Step 1: Test Subscription Creation
1. **Start your backend service** with test environment variables
2. **Test the subscription endpoint:**
   ```bash
   curl -X POST https://your-backend-url.railway.app/api/create-subscription \
     -H "Content-Type: application/json" \
     -d '{
       "price_id": "price_starter_monthly_test",
       "customer_email": "test@example.com"
     }'
   ```

3. **Expected response:**
   ```json
   {
     "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
     "session_id": "cs_test_..."
   }
   ```

### Step 2: Test Checkout Flow
1. **Visit the checkout URL** from the response
2. **Use Stripe test card numbers:**
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - Expiry: Any future date (e.g., `12/25`)
   - CVV: Any 3 digits (e.g., `123`)

### Step 3: Verify Webhook Reception
1. **Complete a test payment**
2. **Check Railway logs** for webhook events:
   ```bash
   railway logs
   ```
3. **Look for log entries:**
   ```
   Webhook received: checkout.session.completed
   Customer subscription created: sub_test_...
   ```

### Step 4: Test Each Subscription Tier
**Test all 6 combinations:**
1. Starter Monthly
2. Starter Annual
3. Pro Monthly
4. Pro Annual
5. Team Monthly
6. Team Annual

**For each test:**
- Create checkout session
- Complete payment with test card
- Verify webhook received
- Check subscription created in Stripe Dashboard

## Phase 6: Production Setup

### Step 1: Switch to Live Mode
1. In Stripe Dashboard, toggle to **"Live Mode"** (top-left)
2. **WARNING:** You're now working with real money

### Step 2: Get Production API Keys
1. Go to **"Developers"** → **"API Keys"**
2. Copy **Live** keys (start with `pk_live_` and `sk_live_`)
3. **Keep these extremely secure**

### Step 3: Recreate Products in Live Mode
**Option A: Run script with live keys**
```bash
export STRIPE_SECRET_KEY=sk_live_...
python scripts/create_stripe_products.py
```

**Option B: Manually recreate products**
- Follow Method B steps above in Live Mode
- Use exact same names and prices

### Step 4: Create Production Webhook
1. In Live Mode, go to **"Developers"** → **"Webhooks"**
2. Create webhook with production URL:
   ```
   https://threadr-production.up.railway.app/api/stripe/webhook
   ```
3. Select same events as test mode
4. Copy production webhook secret (`whsec_live_...`)

### Step 5: Update Production Environment Variables
In Railway production environment:
```bash
# Stripe Configuration (Live Mode)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...

# Production Price IDs
STRIPE_STARTER_MONTHLY_PRICE_ID=price_live_starter_monthly
STRIPE_STARTER_ANNUAL_PRICE_ID=price_live_starter_annual
STRIPE_PRO_MONTHLY_PRICE_ID=price_live_pro_monthly
STRIPE_PRO_ANNUAL_PRICE_ID=price_live_pro_annual
STRIPE_TEAM_MONTHLY_PRICE_ID=price_live_team_monthly
STRIPE_TEAM_ANNUAL_PRICE_ID=price_live_team_annual
```

## Phase 7: Final Testing Checklist

### Pre-Launch Verification
- [ ] All 6 price IDs are correct in production environment
- [ ] Webhook endpoint responds to test events
- [ ] Success/cancel URLs redirect properly
- [ ] Customer emails are captured correctly
- [ ] Subscriptions appear in Stripe Dashboard
- [ ] Database records are created for new subscriptions
- [ ] Premium access is granted immediately after payment

### Test Scenarios
- [ ] **Happy Path:** Complete payment flow for each tier
- [ ] **Declined Card:** Test with `4000 0000 0000 0002`
- [ ] **Webhook Failure:** Verify retry logic works
- [ ] **Duplicate Subscription:** Test existing customer flow
- [ ] **Cancellation:** Test subscription cancellation
- [ ] **Refund:** Test refund processing

## Common Pitfalls & Solutions

### Problem: "No such price" error
**Cause:** Using test price IDs in live mode or vice versa
**Solution:** Verify you're using correct price IDs for current mode

### Problem: Webhook signature verification fails
**Cause:** Wrong webhook secret or endpoint URL mismatch
**Solution:** 
- Verify `STRIPE_WEBHOOK_SECRET` matches dashboard
- Ensure webhook URL exactly matches your endpoint

### Problem: CORS errors during checkout
**Cause:** Domain mismatch in Stripe settings
**Solution:** Verify success/cancel URLs match your domain exactly

### Problem: Duplicate customers created
**Cause:** Not checking for existing customers by email
**Solution:** Use `customer.list(email=email)` before creating new customer

### Problem: Subscription not activated after payment
**Cause:** Webhook event not processed correctly
**Solution:** Check Railway logs for webhook processing errors

## Security Checklist

- [ ] **Never commit API keys to git**
- [ ] **Use environment variables for all secrets**
- [ ] **Verify webhook signatures in production**
- [ ] **Use test mode for all development**
- [ ] **Restrict API key permissions if possible**
- [ ] **Monitor failed webhook attempts**
- [ ] **Log all payment events for audit trail**

## Support Resources

### Stripe Documentation
- [Subscriptions Guide](https://stripe.com/docs/billing/subscriptions/overview)
- [Webhook Events](https://stripe.com/docs/api/events/types)
- [Test Cards](https://stripe.com/docs/testing#cards)

### Threadr Backend Integration
- Webhook handler: `backend/src/routes/stripe.py`
- Subscription models: `backend/src/models/subscription.py`
- Environment config: `backend/src/core/config.py`

### Emergency Contacts
- If payments fail: Check Railway logs first
- If webhooks fail: Verify endpoint URL and secret key
- If customers complain: Check Stripe Dashboard for payment status

---

**Next Steps After Setup:**
1. Update frontend with new subscription options
2. Test upgrade/downgrade flows
3. Implement subscription management dashboard
4. Add billing history features
5. Configure subscription analytics

This completes the Stripe subscription setup. All products should now be configured and ready for customer subscriptions.
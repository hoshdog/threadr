# Stripe Payment Link Setup Guide for Threadr Premium

## Overview
This guide walks you through setting up Stripe Payment Links for Threadr Premium ($4.99 one-time payment) with complete webhook integration.

## Prerequisites
- Stripe account (create at [stripe.com](https://stripe.com))
- Railway deployment access
- Vercel deployment access

## Step 1: Create Stripe Payment Link

### 1.1 Access Stripe Dashboard
1. Go to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Ensure you're in **Test mode** (toggle in top-left corner)
3. You'll switch to Live mode after testing is complete

### 1.2 Create Product
1. Navigate to **Products** in the left sidebar
2. Click **+ Add product**
3. Fill in product details:
   ```
   Name: Threadr Premium
   Description: Unlimited Twitter thread generation with premium features including priority processing, advanced customization, and email support
   ```
4. Add product image (optional but recommended)

### 1.3 Set Pricing
1. Under **Pricing Information**:
   - **Pricing model**: One time
   - **Price**: $4.99
   - **Currency**: USD
   - **Tax behavior**: Exclusive (recommended)
2. Click **Save product**

### 1.4 Create Payment Link
1. Navigate to **Payment Links** in the left sidebar
2. Click **+ Create payment link**
3. Select your **Threadr Premium** product
4. Configure Payment Link settings:

   **Customer Information:**
   - ✅ Collect email address (required)
   - ✅ Collect phone number (optional)
   - ✅ Collect billing address (optional)

   **After Payment:**
   - Redirect to your website: ✅
   - Success URL: `https://threadr-plum.vercel.app/?payment=success&session_id={CHECKOUT_SESSION_ID}`
   - Cancel URL: `https://threadr-plum.vercel.app/?payment=cancelled`

   **Additional Options:**
   - ✅ Allow promotion codes (for future discounts)
   - ✅ Collect additional information (for analytics)

5. Click **Create link**
6. **IMPORTANT**: Copy the full Payment Link URL - you'll need this for environment variables

## Step 2: Configure Railway Environment Variables

### 2.1 Get Required Values from Stripe

**API Keys:**
1. Go to **Developers** > **API keys**
2. Copy the **Secret key** (starts with `sk_test_` for test mode)

**Webhook Secret:** (Complete Step 3 first, then return here)

**Payment Link Details:**
1. From your Payment Link URL, extract the price ID
2. URL format: `https://buy.stripe.com/test_[random_string]`
3. The price ID is visible in your Products page (format: `price_[random_string]`)

### 2.2 Set Environment Variables in Railway
1. Go to your Railway project dashboard
2. Select your **backend service**
3. Click **Variables** tab
4. Add these variables:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_... # Your secret key from Step 2.1
STRIPE_WEBHOOK_SECRET=whsec_... # From Step 3 (webhook setup)
STRIPE_PRICE_ID=price_... # From your product page
STRIPE_PAYMENT_LINK_URL=https://buy.stripe.com/test_... # Full Payment Link URL

# Pricing Configuration
PREMIUM_PRICE_USD=4.99

# Free Tier Settings
FREE_TIER_DAILY_LIMIT=5
FREE_TIER_MONTHLY_LIMIT=20
FREE_TIER_ENABLED=true
```

## Step 3: Set up Webhook Integration

### 3.1 Create Webhook Endpoint
1. In Stripe Dashboard, go to **Developers** > **Webhooks**
2. Click **+ Add endpoint**
3. **Endpoint URL**: `https://threadr-production.up.railway.app/api/webhooks/stripe`
4. **Description**: `Threadr Premium Payment Processing`

### 3.2 Select Events
Add these events to listen for:
- ✅ `checkout.session.completed` (REQUIRED - grants premium access)
- ✅ `customer.subscription.created` (for future subscription support)
- ✅ `invoice.payment_succeeded` (for future subscription support)
- ✅ `invoice.payment_failed` (for error handling)

### 3.3 Get Webhook Secret
1. After creating the webhook, click on it to view details
2. In the **Signing secret** section, click **Reveal**
3. Copy the webhook secret (starts with `whsec_...`)
4. Add this as `STRIPE_WEBHOOK_SECRET` in Railway (Step 2.2)

## Step 4: Deploy and Test

### 4.1 Deploy Backend Changes
1. Commit and push your changes to trigger Railway deployment
2. Wait for deployment to complete
3. Check Railway logs for successful startup

### 4.2 Test Payment Configuration Endpoint
Test that the payment config is working:
```bash
curl https://threadr-production.up.railway.app/api/payment/config
```

Expected response:
```json
{
  "stripe_configured": true,
  "webhook_configured": true,
  "premium_price": 4.99,
  "display_price": "$4.99",
  "currency": "USD",
  "price_id": "price_...",
  "payment_url": "https://buy.stripe.com/test_...",
  "payment_methods": ["stripe_payment_links"],
  "pricing_type": "one_time"
}
```

### 4.3 Test Complete User Journey

**Step A: Trigger Payment Flow**
1. Visit https://threadr-plum.vercel.app
2. Generate 5 threads to hit the daily limit
3. Try to generate a 6th thread
4. Verify the "Upgrade to Premium" modal appears
5. Click "Upgrade Now" - should redirect to Stripe Payment Link

**Step B: Complete Test Payment**
1. Use Stripe test card numbers:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
2. Use any future expiry date and any CVC
3. Complete the payment process

**Step C: Verify Premium Access**
1. After successful payment, you should be redirected back to Threadr
2. Refresh the page and check that:
   - Usage counter shows "Premium" instead of "Free Plan"
   - You can generate unlimited threads
   - No more payment prompts appear

### 4.4 Test Webhook Processing
1. In Stripe Dashboard, go to **Developers** > **Webhooks**
2. Click on your webhook endpoint
3. Check the **Attempts** section for successful deliveries
4. Each completed payment should show a successful webhook delivery

## Step 5: Switch to Production Mode

### 5.1 Activate Live Mode in Stripe
1. Switch to **Live mode** in Stripe Dashboard (toggle in top-left)
2. Repeat Steps 1-3 with live keys and webhook secrets
3. Update Railway environment variables with live keys

### 5.2 Production Environment Variables
Replace test keys with live keys:
```env
STRIPE_SECRET_KEY=sk_live_... # Live secret key
STRIPE_WEBHOOK_SECRET=whsec_... # Live webhook secret
STRIPE_PAYMENT_LINK_URL=https://buy.stripe.com/live_... # Live payment link
```

### 5.3 Update Success/Cancel URLs
Update your Payment Link redirect URLs to:
- Success: `https://threadr-plum.vercel.app/?payment=success&session_id={CHECKOUT_SESSION_ID}`
- Cancel: `https://threadr-plum.vercel.app/?payment=cancelled`

## Troubleshooting

### Common Issues

**Payment Modal Not Showing:**
- Check browser console for API errors
- Verify `STRIPE_PAYMENT_LINK_URL` is set in Railway
- Test the `/api/payment/config` endpoint

**Webhook Not Processing:**
- Check Railway logs for webhook delivery attempts
- Verify webhook URL is accessible: `https://threadr-production.up.railway.app/api/webhooks/stripe`
- Ensure webhook secret matches environment variable

**Premium Access Not Granted:**
- Check webhook event in Stripe Dashboard for delivery status
- Verify `checkout.session.completed` event is being sent
- Check Railway logs for processing errors

**Payment Link Redirect Issues:**
- Ensure success/cancel URLs are correctly formatted
- Check that URLs are accessible and don't have trailing slashes

### Testing Commands

**Test webhook endpoint:**
```bash
curl -X POST https://threadr-production.up.railway.app/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**Check premium status:**
```bash
curl https://threadr-production.up.railway.app/api/premium/check
```

**Test payment config:**
```bash
curl https://threadr-production.up.railway.app/api/payment/config
```

## Security Notes

- Never commit Stripe keys to version control
- Use test mode for all development and testing
- Webhook signatures are automatically verified
- All sensitive data is handled server-side only
- Payment processing uses Stripe's secure hosted checkout

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Review Stripe Dashboard for webhook delivery status
3. Test API endpoints directly with curl
4. Verify all environment variables are correctly set

The integration includes comprehensive error handling and logging for troubleshooting.
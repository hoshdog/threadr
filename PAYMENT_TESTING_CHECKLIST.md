# Threadr Premium Payment Testing Checklist

## Pre-Testing Setup Verification

### ✅ Stripe Configuration
- [ ] Payment Link created in Stripe Dashboard (Test mode)
- [ ] Product: "Threadr Premium" - $4.99 one-time payment
- [ ] Webhook endpoint created: `https://threadr-production.up.railway.app/api/webhooks/stripe`
- [ ] Webhook events: `checkout.session.completed` enabled
- [ ] Success URL: `https://threadr-plum.vercel.app/?payment=success&session_id={CHECKOUT_SESSION_ID}`
- [ ] Cancel URL: `https://threadr-plum.vercel.app/?payment=cancelled`

### ✅ Railway Environment Variables
- [ ] `STRIPE_SECRET_KEY=sk_test_...` (test key for now)
- [ ] `STRIPE_WEBHOOK_SECRET=whsec_...`
- [ ] `STRIPE_PRICE_ID=price_...`
- [ ] `STRIPE_PAYMENT_LINK_URL=https://buy.stripe.com/test_...`
- [ ] `PREMIUM_PRICE_USD=4.99`
- [ ] `FREE_TIER_DAILY_LIMIT=5`
- [ ] `FREE_TIER_ENABLED=true`

### ✅ Deployment Status
- [ ] Backend deployed to Railway with new environment variables
- [ ] Frontend deployed to Vercel with updated payment handling
- [ ] Both services are accessible and healthy

## Test Sequence

### 1. API Endpoint Testing

**Test payment configuration endpoint:**
```bash
curl https://threadr-production.up.railway.app/api/payment/config
```

**Expected Response:**
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

**Test usage status endpoint:**
```bash
curl https://threadr-production.up.railway.app/api/usage/status
```

### 2. Frontend Payment Flow Testing

#### 2.1 Trigger Payment Modal
- [ ] Visit https://threadr-plum.vercel.app
- [ ] Generate threads until you hit the daily limit (5 threads)
- [ ] On the 6th attempt, verify:
  - [ ] "Upgrade to Generate More" button appears
  - [ ] Clicking it opens payment modal
  - [ ] Modal shows "$4.99 one-time payment"
  - [ ] "Upgrade Now" button is enabled

#### 2.2 Payment Modal Content Verification
- [ ] Header shows "Upgrade to Premium"
- [ ] Features list displays correctly:
  - [ ] Unlimited thread generation
  - [ ] Priority processing
  - [ ] Advanced customization options
  - [ ] Email support
- [ ] Price shows "$4.99" (not "$9.99")
- [ ] Shows "one-time payment" (not "per month")
- [ ] "Upgrade Now" button is functional

#### 2.3 Payment Link Redirect
- [ ] Click "Upgrade Now"
- [ ] Redirects to Stripe Payment Link page
- [ ] Payment page shows:
  - [ ] "Threadr Premium" product name
  - [ ] $4.99 price
  - [ ] Correct description
  - [ ] Email field (required)

### 3. Payment Processing Testing

#### 3.1 Test Successful Payment
Use Stripe test card: `4242 4242 4242 4242`
- [ ] Enter test card details
- [ ] Complete payment form
- [ ] Payment processes successfully
- [ ] Redirects to: `https://threadr-plum.vercel.app/?payment=success&session_id=...`

#### 3.2 Test Payment Cancellation
- [ ] Start payment process
- [ ] Click "Back" or cancel
- [ ] Redirects to: `https://threadr-plum.vercel.app/?payment=cancelled`

#### 3.3 Test Failed Payment
Use Stripe decline card: `4000 0000 0000 0002`
- [ ] Enter declined card details
- [ ] Verify payment fails gracefully
- [ ] User can retry with different card

### 4. Post-Payment Verification

#### 4.1 Webhook Processing
Check in Stripe Dashboard → Developers → Webhooks:
- [ ] Webhook attempt logged for completed payment
- [ ] Status shows "200 OK" response
- [ ] No failed delivery attempts

Check Railway logs:
- [ ] Webhook received log entry
- [ ] Premium access granted log entry
- [ ] No error messages in webhook processing

#### 4.2 Premium Access Verification
After successful payment:
- [ ] Return to https://threadr-plum.vercel.app
- [ ] Green success banner appears: "Payment successful! You now have premium access."
- [ ] Usage counter shows "Premium" instead of "Free Plan"
- [ ] Usage counter shows "Unlimited" instead of "X/5 today"
- [ ] Can generate unlimited threads without restrictions
- [ ] No payment modal appears on subsequent generations

#### 4.3 Session Persistence
- [ ] Refresh the page - premium status persists
- [ ] Open new browser tab - premium status persists
- [ ] Clear browser cache - premium status persists (server-side tracking)

### 5. Edge Case Testing

#### 5.1 Double Payment Prevention
- [ ] Complete one successful payment
- [ ] Try to access payment link again
- [ ] Verify premium users don't see payment prompts

#### 5.2 Network Error Handling
- [ ] Temporarily disconnect internet during payment
- [ ] Verify graceful error handling
- [ ] Verify payment can be retried

#### 5.3 Webhook Failure Recovery
- [ ] Check webhook retry mechanism in Stripe Dashboard
- [ ] Verify failed webhooks are retried automatically

### 6. Production Readiness Check

#### 6.1 Security Verification
- [ ] Webhook signature verification enabled
- [ ] No sensitive data logged in frontend console
- [ ] Payment processing handled entirely by Stripe
- [ ] No payment data stored in Threadr backend

#### 6.2 Error Handling
- [ ] Payment modal shows appropriate error messages
- [ ] Network failures handled gracefully
- [ ] Stripe service unavailable scenarios handled
- [ ] Invalid payment configurations detected

#### 6.3 User Experience
- [ ] Payment flow is intuitive and smooth
- [ ] Success/failure feedback is clear
- [ ] Loading states provide appropriate feedback
- [ ] Mobile-responsive payment modal

## Production Migration Checklist

When ready to go live:

### ✅ Switch to Stripe Live Mode
- [ ] Create live version of Payment Link
- [ ] Update webhook endpoint to use live keys
- [ ] Update Railway environment variables:
  - [ ] `STRIPE_SECRET_KEY=sk_live_...`
  - [ ] `STRIPE_WEBHOOK_SECRET=whsec_...` (live webhook secret)
  - [ ] `STRIPE_PAYMENT_LINK_URL=https://buy.stripe.com/live_...`

### ✅ Final Production Tests
- [ ] Test with real (small) payment amount
- [ ] Verify webhook processing in live mode
- [ ] Confirm premium access granted correctly
- [ ] Test customer email notifications from Stripe

## Troubleshooting Common Issues

### Payment Modal Not Appearing
1. Check browser console for JavaScript errors
2. Verify `/api/payment/config` returns valid configuration
3. Ensure daily limit is actually reached

### Webhook Not Processing
1. Check Railway logs for webhook delivery attempts
2. Verify webhook URL is publicly accessible
3. Confirm webhook secret matches environment variable
4. Check Stripe Dashboard for webhook delivery status

### Premium Access Not Granted
1. Verify webhook delivered successfully to backend
2. Check that `checkout.session.completed` event is configured
3. Ensure webhook processing completed without errors
4. Verify Redis/storage system is working correctly

### Payment Link Issues
1. Confirm Payment Link URL is correct and accessible
2. Verify success/cancel URLs are properly formatted
3. Check that Payment Link hasn't been deactivated in Stripe

---

## Test Results Log

Document your test results here:

**Date:** ___________
**Tester:** ___________

| Test Case | Status | Notes |
|-----------|--------|-------|
| Payment Config API | ✅/❌ | |
| Payment Modal Display | ✅/❌ | |
| Stripe Redirect | ✅/❌ | |
| Successful Payment | ✅/❌ | |
| Webhook Processing | ✅/❌ | |
| Premium Access Grant | ✅/❌ | |
| Session Persistence | ✅/❌ | |

**Overall Status:** ✅ Ready for Production / ❌ Needs Fixes

**Notes:**
_Document any issues found and their resolutions_
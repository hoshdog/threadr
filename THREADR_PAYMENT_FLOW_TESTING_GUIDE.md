# Threadr Payment Flow - Visual Testing Guide

## Overview
This guide provides step-by-step instructions for manually testing the complete payment flow in Threadr, from free tier usage through premium upgrade and webhook processing.

## Prerequisites

### Environment Setup
- **Frontend URL**: https://threadr-plum.vercel.app
- **Backend URL**: https://threadr-production.up.railway.app
- **Test User**: Use incognito browser for clean testing
- **Payment Method**: Use Stripe test card numbers

### Required Access
- Stripe Dashboard access for webhook monitoring
- Railway logs access for backend monitoring
- Browser Developer Tools for network inspection

## Testing Checklist

### Phase 1: Free Tier Experience (5 threads)

#### Step 1.1: First User Visit
**What to do:**
1. Open https://threadr-plum.vercel.app in incognito browser
2. Observe the header usage counter

**Expected Results:**
- [ ] Usage counter shows "Free Plan" with "0/5 today"
- [ ] Counter has gray styling (not premium purple/blue gradient)
- [ ] No premium indicators visible

**Visual Screenshots to Capture:**
- Header showing "Free Plan 0/5 today"
- Clean interface with no upgrade prompts

#### Step 1.2: Generate First Thread
**What to do:**
1. Input a URL (e.g., `https://medium.com/@example/article`)
2. Click "Generate Thread"
3. Wait for completion

**Expected Results:**
- [ ] Thread generates successfully
- [ ] Usage counter updates to "1/5 today"
- [ ] No payment prompts appear
- [ ] Email capture modal appears after generation

**Backend Verification:**
```bash
# Check Railway logs for:
- "Thread generated successfully" 
- Usage tracking incremented
- No payment-related logs
```

#### Step 1.3: Continue Using Free Tier (Threads 2-4)
**What to do:**
1. Generate 3 more threads using different content
2. Observe usage counter progression

**Expected Results:**
- [ ] Counter shows: "2/5", "3/5", "4/5" progression
- [ ] No upgrade warnings until thread 4
- [ ] At 4/5: Amber warning appears: "You're running low on free threads!"

**Visual Screenshots to Capture:**
- Usage counter at 3/5 and 4/5
- Warning banner appearance at 4/5

### Phase 2: Hitting Daily Limit (Thread 5)

#### Step 2.1: Fifth Thread Generation
**What to do:**
1. Generate 5th thread
2. Observe usage counter and warnings

**Expected Results:**
- [ ] Thread generates successfully
- [ ] Counter shows "5/5 today"
- [ ] Warning banner shows "Daily limit reached"
- [ ] "Upgrade" button appears in warning banner

**Visual Screenshots to Capture:**
- Usage counter at "5/5 today"
- Amber warning banner with "Daily limit reached"

#### Step 2.2: Attempt Sixth Thread
**What to do:**
1. Try to generate a 6th thread
2. Observe button behavior and modal triggering

**Expected Results:**
- [ ] Generate button text changes to "Upgrade to Generate More"
- [ ] Button styling changes to purple/blue gradient
- [ ] Clicking button opens payment modal (no thread generation)

**Network Monitoring:**
```javascript
// In browser console, monitor:
fetch('/api/generate', {...}).then(r => console.log('Status:', r.status))
// Should show 402 Payment Required response
```

### Phase 3: Payment Upgrade Modal

#### Step 3.1: Modal Appearance
**What to do:**
1. Click "Upgrade to Generate More" or warning "Upgrade" button
2. Examine modal content and styling

**Expected Results:**
- [ ] Modal opens with purple/blue gradient header
- [ ] Shows lightning bolt icon in gradient circle
- [ ] Title: "Upgrade to Premium"
- [ ] Description: "Unlock unlimited thread generation and premium features"

**Visual Screenshots to Capture:**
- Full payment modal overlay
- Modal content with pricing

#### Step 3.2: Pricing Display
**What to do:**
1. Verify pricing information in modal

**Expected Results:**
- [ ] Price shows "$4.99" (from config)
- [ ] Text shows "one-time payment"
- [ ] Gradient pricing box styling

#### Step 3.3: Feature List
**What to do:**
1. Check feature benefits listed

**Expected Results:**
- [ ] "Unlimited thread generation" with checkmark
- [ ] "Priority processing" with checkmark  
- [ ] "Advanced customization options" with checkmark
- [ ] "Email support" with checkmark

### Phase 4: Stripe Payment Link Integration

#### Step 4.1: Payment Button Functionality
**What to do:**
1. Click "Upgrade Now" button
2. Monitor network requests and tab behavior

**Expected Results:**
- [ ] Button shows loading state with spinner
- [ ] New tab opens to Stripe Payment Link
- [ ] Payment modal closes after 1 second
- [ ] No JavaScript errors in console

**Backend API Verification:**
```bash
# Check Railway logs for:
GET /api/payment/config - 200 OK
GET /api/premium/check - 200 OK
```

#### Step 4.2: Stripe Payment Page
**What to do:**
1. In new Stripe tab, verify payment form
2. Use test card: `4242 4242 4242 4242`

**Expected Results:**
- [ ] Stripe Checkout page loads correctly
- [ ] Shows "$4.99" amount
- [ ] Product name matches configuration
- [ ] Test card acceptance works

**Stripe Dashboard Verification:**
1. Login to Stripe Dashboard
2. Navigate to Payments > Payment Links
3. Verify activity shows initiated session

#### Step 4.3: Complete Test Payment
**What to do:**
1. Complete payment with test card details:
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - Name: Any name
   - Email: Use test email

**Expected Results:**
- [ ] Payment processes successfully
- [ ] Redirects to success page
- [ ] Shows payment confirmation

### Phase 5: Webhook Processing

#### Step 5.1: Webhook Delivery Monitoring
**What to do:**
1. Monitor Stripe Dashboard for webhook delivery
2. Check Railway logs for webhook processing

**Stripe Dashboard Verification:**
1. Go to Developers > Webhooks
2. Find recent `checkout.session.completed` event
3. Verify status shows successful delivery (200 response)

**Backend Logs Verification:**
```bash
# In Railway logs, look for:
"Received Stripe webhook (snapshot): checkout.session.completed"
"Processing Stripe checkout completion: Session=cs_..."
"Premium access granted successfully via Stripe webhook"
```

#### Step 5.2: Premium Access Grant
**What to do:**
1. Wait 10-30 seconds for webhook processing
2. Return to Threadr application tab
3. Refresh the page

**Expected Results:**
- [ ] Usage counter changes to "Premium" with unlimited indicator
- [ ] Counter styling changes to purple/blue gradient
- [ ] Dot indicator appears next to "Premium"
- [ ] Counter shows "Unlimited" instead of usage numbers

**Redis Verification (via backend logs):**
```bash
# Look for successful Redis operations:
"Premium access granted: Email=test@email.com, IP=..., Plan=premium, Duration=30 days"
```

### Phase 6: Premium Access Verification

#### Step 6.1: Premium UI Indicators
**What to do:**
1. Verify all premium UI elements are active

**Expected Results:**
- [ ] Header shows "Premium" with gradient styling
- [ ] Usage shows "Unlimited" 
- [ ] Purple/blue gradient dot indicator
- [ ] No upgrade warnings or prompts

**Visual Screenshots to Capture:**
- Premium header styling
- Full premium interface

#### Step 6.2: Unlimited Thread Generation
**What to do:**
1. Generate multiple threads (6, 7, 8+)
2. Verify no limitations

**Expected Results:**
- [ ] All threads generate successfully
- [ ] No rate limiting or upgrade prompts
- [ ] Premium status maintained throughout

#### Step 6.3: Premium API Responses
**What to do:**
1. Monitor network requests during generation

**Expected API Responses:**
```javascript
// GET /api/premium/check should return:
{
  "has_premium": true,
  "usage_status": {
    "has_premium": true,
    // ...
  },
  "needs_payment": false,
  "message": "Premium access active."
}
```

### Phase 7: Error Scenarios & Edge Cases

#### Step 7.1: Payment Cancellation
**What to do:**
1. Start new payment flow (use different browser/IP)
2. Reach Stripe page but click "Back" or close tab

**Expected Results:**
- [ ] User returns to Threadr without premium access
- [ ] Free tier limits still apply
- [ ] Can retry payment process

#### Step 7.2: Webhook Failure Simulation
**What to do:**
1. Check Stripe Dashboard for any failed webhook deliveries
2. Verify retry mechanisms

**Expected Behavior:**
- [ ] Stripe retries failed webhooks automatically
- [ ] Railway logs show retry attempts
- [ ] User eventually gets premium access

#### Step 7.3: Multiple Payment Attempts
**What to do:**
1. Complete payment for same user/email multiple times

**Expected Results:**
- [ ] Each payment extends premium duration
- [ ] No duplicate premium grants cause errors
- [ ] Backend handles gracefully

## Monitoring & Logging

### Key Railway Log Patterns
```bash
# Successful Payment Flow:
1. "Received Stripe webhook (snapshot): checkout.session.completed"
2. "Processing Stripe checkout completion: Session=cs_..."
3. "Premium access granted successfully via Stripe webhook: Email=..."

# Premium Access Verification:
1. "Premium access check: has_premium=true"
2. "Thread generated for premium user"

# Error Patterns to Watch:
1. "Stripe webhook signature verification failed"
2. "Failed to grant premium access"
3. "Redis not available - cannot grant premium access"
```

### Stripe Dashboard Checks
1. **Payments**: Verify test payments appear with correct amounts
2. **Webhooks**: Confirm successful delivery (200 responses)
3. **Events**: Check `checkout.session.completed` events
4. **Logs**: Review any failed webhook attempts

### Frontend Console Monitoring
```javascript
// Monitor for errors:
console.log('Payment errors:', window.paymentErrors);

// Check API responses:
fetch('/api/premium/check').then(r => r.json()).then(console.log);
```

## Common Issues & Solutions

### Issue: Payment Modal Won't Open
**Symptoms**: Button clicks don't show modal
**Check**: 
- [ ] Browser console for JavaScript errors
- [ ] API response from `/api/payment/config`
- [ ] Network connectivity

### Issue: Stripe Page Won't Load
**Symptoms**: Payment button opens blank tab
**Check**:
- [ ] `STRIPE_PAYMENT_LINK_URL` configuration
- [ ] Stripe Payment Link is active
- [ ] No ad blockers interfering

### Issue: Webhook Not Processing
**Symptoms**: Payment completes but no premium access
**Check**:
- [ ] Railway logs for webhook errors
- [ ] Stripe Dashboard webhook delivery status
- [ ] `STRIPE_WEBHOOK_SECRET` configuration
- [ ] Redis connectivity

### Issue: Premium Status Not Persisting
**Symptoms**: Premium access disappears on refresh
**Check**:
- [ ] Redis storage successful
- [ ] Premium expiration date
- [ ] IP/email matching logic

## Success Criteria

### Complete Success Checklist
- [ ] Free tier works (5 threads max)
- [ ] Limit enforcement triggers payment modal
- [ ] Payment modal displays correctly with pricing 
- [ ] Stripe Payment Link opens and processes payment
- [ ] Webhook delivers and processes successfully
- [ ] Premium access grants immediately after payment
- [ ] Premium UI indicators activate correctly
- [ ] Unlimited thread generation works
- [ ] Premium status persists across sessions
- [ ] Error scenarios handle gracefully

### Performance Benchmarks
- **Payment Modal Load**: < 1 second
- **Stripe Page Redirect**: < 2 seconds  
- **Webhook Processing**: < 30 seconds
- **Premium Activation**: < 1 minute total
- **Thread Generation (Premium)**: No rate limits

## Test Data Cleanup

### After Testing
1. **Stripe Dashboard**: Archive test payment data
2. **Railway Logs**: Review and save relevant error patterns
3. **Redis Data**: Premium test data will expire automatically
4. **Browser**: Clear incognito session data

This comprehensive testing guide ensures the complete payment flow works correctly from user experience through backend processing and premium access activation.
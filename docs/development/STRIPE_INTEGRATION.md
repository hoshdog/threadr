# Stripe Payment Integration Guide

This document outlines the Stripe Payment Links integration for Threadr's premium access system.

## Overview

Threadr uses Stripe Payment Links for simple, secure payment processing. When users exceed their free tier limits, they can purchase premium access for unlimited thread generation.

## Implementation Details

### Architecture
- **Payment Method**: Stripe Payment Links (no complex checkout integration needed)
- **Webhook Processing**: Secure webhook endpoint handles `checkout.session.completed` events
- **Premium Access**: Automatically granted when payment succeeds
- **Duration**: 30 days of premium access per payment

### Security Features
- Webhook signature verification using HMAC-SHA256
- Environment-based configuration
- Comprehensive error handling and logging
- API key protection for webhook endpoint

## Setup Instructions

### 1. Stripe Dashboard Configuration

1. **Create a Stripe Account**: Sign up at [stripe.com](https://stripe.com)

2. **Get API Keys**:
   - Go to Developers > API keys
   - Copy your Secret key (starts with `sk_test_` for test mode)
   - Set as `STRIPE_SECRET_KEY` environment variable

3. **Create a Product and Price**:
   - Go to Products > Add product
   - Name: "Threadr Premium Access"
   - Price: $4.99 monthly (or your preferred amount)
   - Copy the Price ID (starts with `price_`)
   - Set as `STRIPE_PRICE_ID` environment variable

4. **Create a Payment Link**:
   - Go to Payment Links > Create link
   - Select your premium product
   - Configure success/cancel URLs if desired
   - Share this link with users for payments

5. **Set up Webhook**:
   - Go to Developers > Webhooks > Add endpoint
   - Endpoint URL: `https://your-railway-domain.up.railway.app/api/webhooks/stripe`
   - Events to send: Select `checkout.session.completed`
   - Copy the Signing secret (starts with `whsec_`)
   - Set as `STRIPE_WEBHOOK_SECRET` environment variable

### 2. Environment Variables

Add these to your Railway environment variables:

```bash
# Required
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Optional
STRIPE_PRICE_ID=price_your_price_id_here

# Existing Threadr config
PREMIUM_PRICE_USD=4.99
API_KEYS=your_api_key_here
```

### 3. Frontend Integration

The backend provides a configuration endpoint for the frontend:

```javascript
// Get payment configuration
const response = await fetch('/api/payment/config');
const config = await response.json();

if (config.stripe_configured) {
    // Show payment option to users
    // Redirect to Stripe Payment Link when user wants to upgrade
}
```

## API Endpoints

### Webhook Endpoint
- **URL**: `POST /api/webhooks/stripe`
- **Purpose**: Receives Stripe webhook events
- **Security**: Signature verification required
- **Events Handled**: `checkout.session.completed`

### Payment Configuration
- **URL**: `GET /api/payment/config`
- **Purpose**: Get payment system status for frontend
- **Response**:
  ```json
  {
    "stripe_configured": true,
    "webhook_configured": true,
    "premium_price": 4.99,
    "currency": "USD",
    "price_id": "price_...",
    "payment_methods": ["stripe_payment_links"]
  }
  ```

### Premium Status Check
- **URL**: `GET /api/premium/check`
- **Purpose**: Check user's premium status and usage limits
- **Response**: Premium status, usage limits, and payment requirement

## Webhook Flow

1. **User Completes Payment**: Customer pays via Stripe Payment Link
2. **Stripe Sends Webhook**: `checkout.session.completed` event sent to `/api/webhooks/stripe`
3. **Signature Verification**: Webhook signature verified for security
4. **Payment Validation**: Payment status and amount verified
5. **Premium Access Granted**: 30 days of premium access granted to customer email
6. **Response Sent**: Success/failure response sent back to Stripe

## Error Handling

### Webhook Failures
- Invalid signatures are rejected with 401 status
- Malformed payloads return 400 status
- Processing errors are logged with unique error IDs
- Failed premium grants are retried automatically

### Payment Validation
- Only `paid` status payments are processed
- Amount verification (warns if unexpected but doesn't fail)
- Duplicate payment handling via idempotent operations

### Logging
All webhook events are logged with:
- Event type and ID
- Customer email
- Payment amount and currency
- Processing success/failure
- Error details for debugging

## Testing

### Test Mode
1. Use Stripe test keys (starting with `sk_test_`)
2. Use test Payment Links
3. Use test webhook endpoints
4. Test webhook signature verification

### Test Scenarios
1. **Successful Payment**: Complete payment flow and verify premium access
2. **Invalid Signature**: Test webhook security
3. **Failed Payment**: Verify failed payments don't grant access
4. **Duplicate Events**: Test idempotent processing

## Production Deployment

### Railway Configuration
1. Set all environment variables in Railway dashboard
2. Deploy the updated backend with Stripe integration
3. Test webhook endpoint accessibility
4. Verify webhook signature validation

### Stripe Production Setup
1. Switch to live API keys
2. Create production Payment Links
3. Update webhook URLs to production domain
4. Test with small real payment

## Monitoring and Maintenance

### Key Metrics to Monitor
- Webhook success/failure rates
- Payment completion rates  
- Premium access grants
- Error rates and types

### Logs to Check
- Stripe webhook processing logs
- Premium access grant logs
- Payment validation logs
- Error logs with unique IDs

### Security Checklist
- [ ] Webhook signature verification enabled
- [ ] Environment variables secured
- [ ] API keys rotated regularly
- [ ] Error logging doesn't expose sensitive data
- [ ] HTTPS enforced for webhook endpoint

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Events**
   - Check webhook URL is accessible
   - Verify Railway deployment is running
   - Check Stripe webhook logs for delivery failures

2. **Signature Verification Failing**
   - Verify `STRIPE_WEBHOOK_SECRET` is correct
   - Check webhook secret hasn't been regenerated
   - Ensure raw payload is used for verification

3. **Premium Access Not Granted**
   - Check Redis connection is available
   - Verify customer email in webhook payload
   - Check premium access grant logs

4. **Payment Amount Mismatch**
   - Verify `PREMIUM_PRICE_USD` matches Stripe price
   - Check for currency conversion issues
   - Review Stripe price configuration

### Debug Steps
1. Check Railway logs for webhook processing
2. Verify Stripe webhook delivery in Stripe dashboard
3. Test webhook signature locally
4. Validate Redis connectivity
5. Check premium access queries in Redis

## Frontend Integration Instructions

### Payment Flow
1. **Check Premium Status**: Call `/api/premium/check` to determine if payment needed
2. **Show Payment Option**: Display upgrade button when limits exceeded
3. **Redirect to Payment**: Direct users to Stripe Payment Link
4. **Handle Return**: After payment, redirect users back to app
5. **Verify Access**: Check premium status to confirm upgrade

### Example Frontend Code
```javascript
// Check if user needs premium
async function checkPremiumStatus() {
    const response = await fetch('/api/premium/check');
    const status = await response.json();
    
    if (status.needs_payment) {
        showUpgradeOption(status.premium_price);
    }
}

// Show upgrade option
function showUpgradeOption(price) {
    const upgradeButton = document.getElementById('upgrade-btn');
    upgradeButton.textContent = `Upgrade to Premium ($${price}/month)`;
    upgradeButton.onclick = () => {
        // Redirect to Stripe Payment Link
        window.location.href = 'https://buy.stripe.com/your-payment-link';
    };
    upgradeButton.style.display = 'block';
}
```

This integration provides a secure, reliable payment system that automatically grants premium access upon successful payment completion.
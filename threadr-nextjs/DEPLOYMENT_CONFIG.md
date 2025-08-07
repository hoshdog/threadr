# Next.js Deployment Configuration

## Environment Variables for Vercel Dashboard

Add these in Vercel Dashboard → Settings → Environment Variables:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://threadr-pw0s.onrender.com/api
NEXT_PUBLIC_APP_URL=https://threadr-nextjs.vercel.app
NEXT_PUBLIC_FRONTEND_URL=https://threadr-nextjs.vercel.app

# Stripe (Optional - for payments)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
```

## Environment Variables for Render Dashboard

Ensure these are set in Render → Environment:

```bash
# CORS Configuration (add Next.js URL)
CORS_ORIGINS=https://threadr-plum.vercel.app,https://threadr-nextjs.vercel.app,https://threadr.vercel.app

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_THREADR_STARTER_MONTHLY_PRICE_ID=price_...
STRIPE_THREADR_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_THREADR_TEAM_MONTHLY_PRICE_ID=price_...
```

## 3-Tier Pricing Structure

- **Free**: $0 - 5 daily/20 monthly threads
- **Threadr Starter**: $9.99/month - 100 threads
- **Threadr Pro**: $19.99/month - Unlimited threads (Most Popular)
- **Threadr Team**: $49.99/month - Team features + API

## Auto-Deployment

This project is configured for auto-deployment:
- **Frontend**: Vercel auto-deploys from main branch
- **Backend**: Render auto-deploys from main branch

Pushing to GitHub will trigger both deployments.
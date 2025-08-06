# Render.com Environment Variables Configuration
*Required for Full Backend Functionality*

## ✅ Core Variables (REQUIRED)
```env
ENVIRONMENT=production
PYTHON_VERSION=3.11.9
PYTHONUNBUFFERED=1
```

## ✅ OpenAI Configuration (REQUIRED)
```env
OPENAI_API_KEY=sk-...  # Your OpenAI API key
```

## ✅ Redis Configuration (REQUIRED)
```env
REDIS_URL=redis://...  # Your Render Redis internal URL
```

## ✅ Stripe Configuration (REQUIRED for payments)
```env
STRIPE_SECRET_KEY=sk_...  # Your Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...  # Your Stripe webhook secret
STRIPE_PRICE_ID=price_...  # Your Stripe price ID
```

## ✅ CORS Configuration (REQUIRED)
```env
CORS_ORIGINS=https://threadr-plum.vercel.app
```

## 📋 Optional but Recommended
```env
# Rate Limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW_HOURS=1

# Content Settings
MAX_TWEET_LENGTH=280
MAX_CONTENT_LENGTH=10000

# Free Tier Limits
FREE_TIER_DAILY_LIMIT=5
FREE_TIER_MONTHLY_LIMIT=20

# Cache Settings
CACHE_TTL_HOURS=24

# Security
ALLOWED_DOMAINS=medium.com,*.medium.com,dev.to,*.dev.to,substack.com,*.substack.com

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://...  # Optional - for user accounts
BYPASS_DATABASE=true  # Set to true if no database yet
```

## 🔧 Verification Checklist
- [ ] OPENAI_API_KEY is set and valid
- [ ] REDIS_URL points to your Render Redis instance
- [ ] STRIPE_SECRET_KEY is from Stripe dashboard
- [ ] CORS_ORIGINS includes your frontend URL
- [ ] ENVIRONMENT is set to "production"

## 📝 Notes
- Redis URL should be the internal connection string from Render
- OpenAI key should have GPT-3.5-turbo access
- Stripe keys should be from live mode for production
- CORS must include exact frontend URL (no trailing slash)
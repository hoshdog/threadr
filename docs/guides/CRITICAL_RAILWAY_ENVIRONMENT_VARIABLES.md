# 🚨 CRITICAL: RAILWAY DEPLOYMENT FIX REQUIRED

## **YOUR BACKEND IS DOWN - 502 Bad Gateway**

The Railway backend is failing to start because **CRITICAL environment variables are missing**. Here's exactly what you need to add:

---

## 🔴 **IMMEDIATE ACTION REQUIRED**

### **Step 1: Add ALL These Variables to Railway**

Go to your Railway dashboard → Your project → Backend service → Variables tab

**CORE REQUIRED VARIABLES** (Without these, the app won't start):

```bash
# 1. OpenAI API Key (REQUIRED FOR STARTUP)
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE

# 2. Redis URL (REQUIRED FOR STARTUP) 
# Option A: Use Upstash Redis (free tier)
REDIS_URL=redis://default:YOUR_REDIS_PASSWORD@YOUR_REDIS_HOST:PORT

# Option B: Use Railway Redis (if you have it)
# Railway will auto-populate this if you add Redis service

# 3. Environment Setting
ENVIRONMENT=production

# 4. CORS Configuration (Replace with your frontend URL)
CORS_ORIGINS=https://threadr-plum.vercel.app
```

**STRIPE SUBSCRIPTION VARIABLES** (You said you already added these):

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_live_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# Stripe Price IDs (from your product setup)
STRIPE_STARTER_MONTHLY_PRICE_ID=price_xxx
STRIPE_STARTER_ANNUAL_PRICE_ID=price_xxx
STRIPE_PRO_MONTHLY_PRICE_ID=price_xxx
STRIPE_PRO_ANNUAL_PRICE_ID=price_xxx
STRIPE_TEAM_MONTHLY_PRICE_ID=price_xxx
STRIPE_TEAM_ANNUAL_PRICE_ID=price_xxx
```

**ADDITIONAL CONFIGURATION VARIABLES**:

```bash
# Rate Limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW_HOURS=1

# Content Limits
MAX_TWEET_LENGTH=280
MAX_CONTENT_LENGTH=50000

# Free Tier Settings
FREE_TIER_DAILY_LIMIT=5
FREE_TIER_MONTHLY_LIMIT=20
FREE_TIER_ENABLED=true

# Premium Settings
PREMIUM_PRICE_USD=19.99

# Allowed Domains for URL Scraping
ALLOWED_DOMAINS=medium.com,*.medium.com,dev.to,*.dev.to,substack.com,*.substack.com,hashnode.com,*.hashnode.com,ghost.io,*.ghost.io,wordpress.com,*.wordpress.com,blogger.com,*.blogger.com
```

---

## 🔧 **Step 2: Setting up Redis (CRITICAL)**

### **Option 1: Use Upstash Redis (Recommended - Free)**

1. Go to https://upstash.com
2. Create free account
3. Create new Redis database
4. Copy the Redis URL (starts with `redis://`)
5. Add to Railway as `REDIS_URL`

### **Option 2: Add Railway Redis**

1. In Railway dashboard → New → Database → Redis
2. Railway will automatically add `REDIS_URL` variable
3. No additional configuration needed

---

## ✅ **Step 3: Verify Deployment**

After adding variables, Railway will automatically redeploy. Watch for:

1. **Deployment Logs**: Should show "Application startup complete"
2. **No Error Messages**: Look for any red error text
3. **Green Status**: Deployment should show green checkmark

---

## 🧪 **Step 4: Test Your Backend**

Once deployed, run these tests:

```bash
# 1. Health Check (Should return 200 OK)
curl https://threadr-production.up.railway.app/health

# 2. Subscription Plans (Should show your pricing)
curl https://threadr-production.up.railway.app/api/subscription/plans

# 3. Test from Browser Console
fetch('https://threadr-production.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 🚨 **Common Issues & Solutions**

### **Still Getting 502 Error?**

1. **Check Logs**: Railway → Deployments → View Logs
2. **Missing Variables**: Look for "KeyError" or "not found" errors
3. **Redis Connection**: If Redis errors, double-check REDIS_URL format

### **CORS Errors?**

Make sure `CORS_ORIGINS` matches your Vercel frontend URL exactly (no trailing slash)

### **Stripe Errors?**

Verify all 8 Stripe variables are set (2 keys + 6 price IDs)

---

## 📋 **Complete Variable Checklist**

Before your backend will work, ensure ALL these are set:

- [ ] OPENAI_API_KEY
- [ ] REDIS_URL
- [ ] ENVIRONMENT=production
- [ ] CORS_ORIGINS
- [ ] STRIPE_SECRET_KEY
- [ ] STRIPE_WEBHOOK_SECRET
- [ ] All 6 Stripe Price IDs
- [ ] Rate limiting variables
- [ ] Free tier configuration

---

## 🎯 **Expected Result**

When properly configured:

1. **Health endpoint** returns: 
   ```json
   {
     "status": "healthy",
     "environment": "production",
     "services": {
       "openai": "available",
       "redis": "connected",
       "stripe": "configured"
     }
   }
   ```

2. **Subscription plans** returns your pricing tiers

3. **No 502 errors** - Backend responds to all requests

---

**⚡ PRIORITY: Add OPENAI_API_KEY and REDIS_URL immediately - these are blocking your entire backend from starting!**
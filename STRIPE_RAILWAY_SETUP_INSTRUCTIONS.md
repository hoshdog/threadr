# 🚀 COMPLETE STRIPE & RAILWAY SETUP INSTRUCTIONS

## **YOUR ACTION PLAN: Step-by-Step Subscription Setup**

I've created comprehensive guides and fixed the setup script. Here's exactly what you need to do:

---

## 📋 **PHASE 1: STRIPE SETUP (15-20 minutes)**

### **Step 1: Get Your Stripe API Keys**

1. **Log into Stripe Dashboard**: https://dashboard.stripe.com
2. **Navigate to**: Developers → API keys
3. **Copy these keys**:
   - **Secret Key**: Starts with `sk_test_` (for testing) or `sk_live_` (for production)
   - **Publishable Key**: Starts with `pk_test_` or `pk_live_`

### **Step 2: Set Up Local Environment (Required for Script)**

1. **Edit the backend .env file**:
   ```bash
   cd backend
   # Open .env file and add:
   STRIPE_SECRET_KEY=sk_test_YOUR_TEST_SECRET_KEY_HERE
   ```

2. **Install Python dependencies** (if not already done):
   ```bash
   pip install stripe python-dotenv
   ```

### **Step 3: Run the Subscription Setup Script**

1. **Execute the script** (I've fixed the Unicode issues):
   ```bash
   cd backend
   python stripe_subscription_setup.py
   ```

2. **What the script will create**:
   - **Starter Plan**: $9.99/month, $95.90/year (100 threads/month)
   - **Pro Plan**: $19.99/month, $191.90/year (unlimited threads)
   - **Team Plan**: $49.99/month, $479.90/year (team features)

3. **IMPORTANT**: Copy ALL the Price IDs that the script outputs. You'll need these for Railway.

### **Step 4: Manual Backup Method (If Script Fails)**

If the script doesn't work, here's how to create products manually in Stripe:

1. **Go to**: Products → Add product
2. **Create each product**:
   
   **Product 1 - Starter**:
   - Name: `Threadr Starter`
   - Description: `100 threads per month with basic analytics`
   - Pricing:
     - Monthly: $9.99, recurring monthly
     - Annual: $95.90, recurring yearly

   **Product 2 - Pro**:
   - Name: `Threadr Pro`
   - Description: `Unlimited threads with advanced analytics and premium templates`
   - Pricing:
     - Monthly: $19.99, recurring monthly
     - Annual: $191.90, recurring yearly

   **Product 3 - Team**:
   - Name: `Threadr Team`
   - Description: `Everything in Pro plus team collaboration and admin features`
   - Pricing:
     - Monthly: $49.99, recurring monthly
     - Annual: $479.90, recurring yearly

3. **Copy each Price ID** (shown after creating each price)

### **Step 5: Configure Stripe Webhook**

1. **Navigate to**: Developers → Webhooks → Add endpoint
2. **Endpoint URL**: `https://threadr-production.up.railway.app/api/webhooks/stripe`
3. **Select events**:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
4. **Copy the Signing Secret** (starts with `whsec_`)

---

## 🚂 **PHASE 2: RAILWAY CONFIGURATION (10 minutes)**

### **Step 1: Access Railway Dashboard**

1. **Go to**: https://railway.app/dashboard
2. **Select**: Your Threadr project
3. **Click on**: Your backend service (usually named `threadr` or `backend`)

### **Step 2: Add Environment Variables**

1. **Click on**: Variables tab
2. **Add each variable** (click "New Variable" for each):

   **Essential Stripe Variables**:
   ```
   STRIPE_SECRET_KEY = sk_test_YOUR_SECRET_KEY_HERE
   STRIPE_WEBHOOK_SECRET = whsec_YOUR_WEBHOOK_SECRET_HERE
   ```

   **Price IDs from Script** (use exact IDs the script gave you):
   ```
   STRIPE_STARTER_MONTHLY_PRICE_ID = price_xxxxxxxxxxxxx
   STRIPE_STARTER_ANNUAL_PRICE_ID = price_xxxxxxxxxxxxx
   STRIPE_PRO_MONTHLY_PRICE_ID = price_xxxxxxxxxxxxx
   STRIPE_PRO_ANNUAL_PRICE_ID = price_xxxxxxxxxxxxx
   STRIPE_TEAM_MONTHLY_PRICE_ID = price_xxxxxxxxxxxxx
   STRIPE_TEAM_ANNUAL_PRICE_ID = price_xxxxxxxxxxxxx
   ```

   **Additional Variables**:
   ```
   STRIPE_SUCCESS_URL = https://threadr-plum.vercel.app/dashboard?session_id={CHECKOUT_SESSION_ID}
   STRIPE_CANCEL_URL = https://threadr-plum.vercel.app/pricing
   ```

### **Step 3: Deploy Changes**

1. **Railway will automatically redeploy** when you add variables
2. **Monitor deployment**: Watch the deployment logs for any errors
3. **Check status**: Green checkmark = successful deployment

### **Step 4: Verify Deployment**

1. **Test health endpoint**:
   ```bash
   curl https://threadr-production.up.railway.app/health
   ```

2. **Test subscription endpoints**:
   ```bash
   # Get available plans
   curl https://threadr-production.up.railway.app/api/subscription/plans
   ```

---

## ✅ **PHASE 3: VERIFICATION CHECKLIST**

### **Stripe Dashboard Checks**:
- [ ] Products created (Starter, Pro, Team)
- [ ] Each product has monthly AND annual pricing
- [ ] Webhook endpoint configured
- [ ] Webhook events selected (6 subscription events)
- [ ] Copied all Price IDs
- [ ] Copied webhook signing secret

### **Railway Dashboard Checks**:
- [ ] All 8 Stripe environment variables added
- [ ] Deployment successful (green status)
- [ ] No errors in deployment logs
- [ ] Health endpoint returns 200 OK

### **Integration Testing**:
- [ ] `/api/subscription/plans` returns your products
- [ ] Pricing page displays correctly on frontend
- [ ] Can navigate to Stripe checkout
- [ ] Webhook endpoint accessible

---

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: Script fails with "Invalid API Key"**
- **Solution**: Make sure you're using the correct test/live key
- **Check**: Key should start with `sk_test_` for testing

### **Issue 2: Webhook signature verification fails**
- **Solution**: Copy the EXACT webhook signing secret from Stripe
- **Check**: Should start with `whsec_`

### **Issue 3: Railway deployment fails**
- **Solution**: Check for typos in environment variable names
- **Check**: Variable names must match EXACTLY (case-sensitive)

### **Issue 4: Products not showing on frontend**
- **Solution**: Ensure all Price IDs are set in Railway
- **Check**: Each product needs BOTH monthly and annual Price IDs

---

## 📚 **DETAILED GUIDES CREATED FOR YOU**

I've created two comprehensive guides with even more details:

1. **Stripe Setup Guide**: `docs/deployment/STRIPE_SUBSCRIPTION_SETUP_GUIDE.md`
   - Detailed Stripe Dashboard navigation
   - Testing procedures with test cards
   - Production deployment checklist

2. **Railway Environment Guide**: `docs/deployment/RAILWAY_SUBSCRIPTION_ENVIRONMENT_GUIDE.md`
   - Step-by-step Railway UI instructions
   - Troubleshooting deployment issues
   - Security best practices

---

## 🎯 **QUICK REFERENCE: ALL ENVIRONMENT VARIABLES**

Copy this template and fill in your values:

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# Stripe Price IDs (from script output)
STRIPE_STARTER_MONTHLY_PRICE_ID=price_xxx
STRIPE_STARTER_ANNUAL_PRICE_ID=price_xxx
STRIPE_PRO_MONTHLY_PRICE_ID=price_xxx
STRIPE_PRO_ANNUAL_PRICE_ID=price_xxx
STRIPE_TEAM_MONTHLY_PRICE_ID=price_xxx
STRIPE_TEAM_ANNUAL_PRICE_ID=price_xxx

# URLs
STRIPE_SUCCESS_URL=https://threadr-plum.vercel.app/dashboard?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=https://threadr-plum.vercel.app/pricing
```

---

## 🚀 **FINAL DEPLOYMENT STEPS**

Once you've completed Stripe and Railway setup:

1. **Commit and push** (if you haven't already):
   ```bash
   git add .
   git commit -m "Add Stripe subscription configuration"
   git push origin main
   ```

2. **Monitor deployment** in Railway dashboard

3. **Test the full flow**:
   - Visit your app
   - Click "Pricing" in navigation
   - Select a plan
   - Complete test purchase
   - Verify subscription status

---

## 💡 **PRO TIPS**

1. **Start with Test Mode**: Use Stripe test keys first, switch to live when ready
2. **Test Card Numbers**: Use `4242 4242 4242 4242` for successful payments
3. **Monitor Logs**: Check Railway logs during first webhook events
4. **Gradual Rollout**: Test with yourself before announcing to users

---

**You're now ready to launch your subscription model! The script is fixed, guides are comprehensive, and everything is documented. Let me know if you encounter any issues during setup.** 🎉
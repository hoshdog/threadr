# VERCEL DEPLOYMENT ACTION PLAN - AUGUST 7, 2025

## ✅ BUILD FIXES DEPLOYED

The TypeScript build errors have been fixed and pushed. Vercel should now be deploying automatically.

## 🎯 IMMEDIATE ACTIONS REQUIRED

### 1. Configure Vercel Environment Variables (5 minutes)

Go to Vercel Dashboard → Your Project → Settings → Environment Variables and add:

```bash
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=https://threadr-pw0s.onrender.com/api

# App URLs (will be auto-filled after first deployment)
NEXT_PUBLIC_APP_URL=https://threadr-nextjs.vercel.app
NEXT_PUBLIC_FRONTEND_URL=https://threadr-nextjs.vercel.app

# Optional: Stripe Public Key (if you want payments in frontend)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
```

### 2. Update CORS in Render Dashboard (2 minutes)

Go to Render Dashboard → Your Service → Environment and update:

```bash
CORS_ORIGINS=https://threadr-plum.vercel.app,https://threadr-nextjs.vercel.app,https://threadr.vercel.app,http://localhost:3000
```

Add all possible URLs your Next.js app might use.

### 3. Monitor Deployment (5-10 minutes)

Check deployment status:
1. Go to https://vercel.com/dashboard
2. Look for your threadr project
3. Check the deployment logs
4. Once deployed, visit the URL (usually https://threadr-nextjs.vercel.app)

### 4. Test Core Features

Once deployed, test these critical paths:

#### Thread Generation
1. Visit the deployed URL
2. Go to Generate page
3. Try generating a thread from text
4. Verify it connects to backend

#### Authentication
1. Click Sign Up
2. Create a test account
3. Verify login works
4. Check if JWT tokens are stored

#### Pricing Display
1. Check homepage shows 3-tier pricing
2. Verify prices: Starter $9.99, Pro $19.99, Team $49.99
3. Click upgrade buttons
4. Ensure modals display correctly

## 🔍 DEPLOYMENT VERIFICATION

Run the monitoring script:
```bash
python scripts/health-checks/monitor_nextjs_deployment.py
```

Expected output:
- Next.js Frontend: ✓ DEPLOYED
- Backend API: ✓ RUNNING
- API Connection: ✓ WORKING

## 🚨 TROUBLESHOOTING

### If Build Still Fails on Vercel:
1. Check build logs in Vercel dashboard
2. Look for any missing environment variables
3. Verify all dependencies are in package.json

### If API Connection Fails:
1. Check CORS configuration in Render
2. Verify backend is running at https://threadr-pw0s.onrender.com
3. Check browser console for CORS errors
4. Ensure environment variables are set in Vercel

### If Authentication Doesn't Work:
1. Check if auth endpoints are initialized in backend
2. Verify JWT_SECRET_KEY is set in Render
3. Check browser DevTools for API errors

## 📊 SUCCESS METRICS

When everything is working, you should see:

- [ ] Next.js app loads at Vercel URL
- [ ] 3-tier pricing displays correctly
- [ ] Thread generation works
- [ ] Authentication system functional
- [ ] API calls succeed without CORS errors

## 🎬 NEXT STEPS AFTER DEPLOYMENT

1. **Marketing Launch**
   - Share the new URL with users
   - Update social media links
   - Send announcement email

2. **Revenue Activation**
   - Configure Stripe webhooks to new backend
   - Test payment flow end-to-end
   - Monitor first conversions

3. **Performance Monitoring**
   - Set up analytics (Google Analytics, Mixpanel)
   - Monitor Core Web Vitals
   - Track user engagement

4. **Gradual Migration**
   - Keep old Alpine.js app running temporarily
   - Redirect traffic gradually
   - Monitor for issues

## 📝 DEPLOYMENT URLS

- **Next.js Frontend**: https://threadr-nextjs.vercel.app (or custom domain)
- **Backend API**: https://threadr-pw0s.onrender.com
- **Old Alpine.js**: https://threadr-plum.vercel.app (deprecate soon)

## ✅ CURRENT STATUS

- Build errors: FIXED ✅
- TypeScript issues: RESOLVED ✅
- Deployment: IN PROGRESS ⏳
- Environment vars: PENDING CONFIGURATION ⚠️
- CORS: NEEDS UPDATE ⚠️

---

**Time to Production**: ~15 minutes once environment variables are configured

**Critical Path**: Environment Variables → CORS → Test → Launch
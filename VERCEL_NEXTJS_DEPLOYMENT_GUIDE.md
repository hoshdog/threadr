# 🚀 Vercel Next.js Deployment Guide

## ✅ Build Status: READY FOR DEPLOYMENT
The Next.js app builds successfully with no errors. All TypeScript checks pass!

## 📋 Pre-Deployment Checklist

### 1. Backend Status (Current Blocker)
⚠️ **Railway Backend**: Currently returning 503 (degraded services)

**Action Required in Railway Dashboard**:
1. Check deployment logs for errors
2. Verify these environment variables are set:
   ```
   OPENAI_API_KEY=sk-proj-[NEW-KEY-AFTER-ROTATION]
   API_KEYS=key1,key2
   REDIS_URL=redis://your-redis-url
   CORS_ORIGINS=https://threadr-plum.vercel.app,https://threadr-nextjs.vercel.app
   BYPASS_DATABASE=true
   ```
3. Confirm the Railway URL (should be `https://threadr-production.up.railway.app`)

### 2. Environment Variables Needed
Update these placeholders with real values:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://threadr-production.up.railway.app/api
NEXT_PUBLIC_API_KEY=[Use one of the API_KEYS from Railway]

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_[Get from Stripe Dashboard]

# App URL
NEXT_PUBLIC_APP_URL=https://threadr-nextjs.vercel.app
```

## 🚀 Deployment Steps

### Option 1: Vercel CLI (Recommended)
```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Navigate to Next.js directory
cd threadr-nextjs

# Deploy to Vercel
vercel

# Follow prompts:
# - Link to existing project? No
# - What's your project name? threadr-nextjs
# - In which directory is your code located? ./
# - Want to override settings? No

# Set environment variables
vercel env add NEXT_PUBLIC_API_BASE_URL
vercel env add NEXT_PUBLIC_API_KEY
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
vercel env add NEXT_PUBLIC_APP_URL

# Deploy to production
vercel --prod
```

### Option 2: GitHub Integration
1. Push code to GitHub
2. Visit https://vercel.com/new
3. Import GitHub repository
4. Select `threadr-nextjs` as root directory
5. Add environment variables in Vercel dashboard
6. Deploy

## 🔧 Environment Variables in Vercel

### Required Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://threadr-production.up.railway.app/api` | Railway backend URL |
| `NEXT_PUBLIC_API_KEY` | `[Your API Key]` | One of the API_KEYS from Railway |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `pk_live_xxx` | From Stripe Dashboard |
| `NEXT_PUBLIC_APP_URL` | `https://threadr-nextjs.vercel.app` | Your Vercel app URL |

### Setting Variables in Vercel Dashboard
1. Go to Project Settings → Environment Variables
2. Add each variable for Production, Preview, and Development
3. Save changes
4. Redeploy to apply

## 📊 Post-Deployment Testing

### 1. Basic Functionality
- [ ] Landing page loads
- [ ] Navigation works
- [ ] No console errors

### 2. Authentication Flow
- [ ] Register new account
- [ ] Login with credentials
- [ ] JWT token stored correctly
- [ ] Protected routes redirect properly

### 3. Core Features
- [ ] Thread generation (requires backend)
- [ ] Templates display correctly
- [ ] Premium modal appears for Pro templates
- [ ] Analytics dashboard loads

### 4. Payment Integration
- [ ] Stripe checkout loads
- [ ] Payment flow completes
- [ ] Premium access granted

## 🎯 Feature Status

### ✅ Ready Now
- Landing page with marketing content
- Authentication UI (login/register)
- Templates showcase
- UI/UX for all features
- Responsive design

### ⚠️ Requires Backend Fix
- Actual thread generation
- User authentication (JWT)
- Thread history
- Analytics data
- Payment processing

## 🔍 Debugging Tips

### If Build Fails
```bash
# Check for errors locally
npm run build
npm run type-check
```

### If API Calls Fail
1. Check browser DevTools Network tab
2. Verify API_KEY is being sent in headers
3. Check CORS errors
4. Verify backend health: `https://threadr-production.up.railway.app/health`

### Common Issues
- **504 Gateway Timeout**: Backend is down or URL is wrong
- **401 Unauthorized**: API_KEY is missing or incorrect
- **CORS Error**: Add Vercel URL to Railway CORS_ORIGINS

## 🚨 Critical Notes

1. **API Keys**: Use NEW keys after rotation (old ones were exposed)
2. **Backend First**: Fix Railway backend health before full testing
3. **Staging First**: Deploy to preview URL before production
4. **Monitor Logs**: Check Vercel Functions logs for errors

## 📈 Success Metrics

### Technical Success
- [ ] Build completes without errors
- [ ] Deployment successful on Vercel
- [ ] No TypeScript errors
- [ ] API connectivity established

### Business Success
- [ ] Users can view landing page
- [ ] Marketing content displays correctly
- [ ] Templates showcase works
- [ ] Premium upgrade flow visible

## 🎉 Next Steps After Deployment

1. **Fix Backend**: Get Railway health endpoint working
2. **Full Testing**: Test all user flows end-to-end
3. **Performance**: Check Core Web Vitals
4. **Analytics**: Set up monitoring
5. **Go Live**: Update DNS and launch!

---

**Current Status**: Next.js app is READY. Just need to fix backend and add real environment variables!
# 🚀 Next.js Deployment Guide for Threadr

## Current Status
- ✅ TypeScript errors fixed
- ✅ Build successful  
- ✅ Deployment configuration created
- 🔄 Authentication integration needed
- 📋 Vercel deployment ready

## Quick Deploy Instructions

### 1. Set Environment Variables in Vercel

Go to your Vercel project settings and add these environment variables:

```
NEXT_PUBLIC_API_BASE_URL = https://threadr-production.up.railway.app/api
NEXT_PUBLIC_API_KEY = [Generate new API key from backend]
NEXT_PUBLIC_APP_URL = https://threadr-plum.vercel.app
```

### 2. Deploy Next.js Version

```bash
cd threadr-nextjs
npx vercel --prod
```

When prompted:
- Link to existing project? **No** (create new project)
- Project name: `threadr-nextjs` 
- Which directory? `.` (current directory)

### 3. Update DNS/Routing

Once deployed, you'll get a new URL like `threadr-nextjs.vercel.app`.

To replace the Alpine.js version:
1. Go to Vercel dashboard
2. Navigate to project settings → Domains
3. Add your custom domain or update the existing one

## Authentication Integration Status

### What's Already Built (Next.js Side):
- ✅ Login/Register pages with forms
- ✅ Auth context and hooks (`useAuth`)
- ✅ JWT token management
- ✅ Protected route middleware
- ✅ User state management

### What Needs Connection:
- 🔄 Connect login form to `/api/auth/login` endpoint
- 🔄 Connect register form to `/api/auth/register` endpoint
- 🔄 Implement token refresh logic
- 🔄 Wire up logout functionality

### Backend API Endpoints (Already Working):
```
POST /api/auth/register - User registration
POST /api/auth/login - User login  
POST /api/auth/logout - User logout
GET /api/auth/me - Get current user
PUT /api/auth/profile - Update profile
```

## Feature Comparison

| Feature | Alpine.js (Current) | Next.js (New) | Status |
|---------|-------------------|---------------|--------|
| Thread Generation | ✅ Working | ✅ Built | Ready |
| Templates | ✅ Working | ✅ Built | Ready |
| Subscription/Pricing | ✅ Working | ✅ Built | Ready |
| User Authentication | ❌ Not integrated | 🔄 Partial | Needs connection |
| Thread History | ❌ Not built | ✅ Built | Ready |
| Analytics Dashboard | ❌ Not built | ✅ Built | Ready |
| Performance | 324KB bundle | ~80KB bundle | 75% improvement |

## Migration Strategy

### Option A: Blue-Green Deployment (Recommended)
1. Deploy Next.js to new subdomain (e.g., `beta.threadr.app`)
2. Test all features thoroughly
3. Gradually redirect traffic from Alpine.js to Next.js
4. Monitor for issues
5. Complete cutover when stable

### Option B: Direct Replacement
1. Deploy Next.js to staging
2. Complete auth integration
3. Test all features
4. Replace Alpine.js version directly
5. Keep Alpine.js as emergency rollback

## Next Steps Priority

1. **Complete Auth Integration** (2-3 hours)
   - Wire up login/register forms to API
   - Test JWT token flow
   - Verify protected routes work

2. **Deploy to Staging** (30 minutes)
   - Set up staging environment
   - Configure environment variables
   - Test full functionality

3. **Production Deployment** (1 hour)
   - Deploy to production
   - Update DNS if needed
   - Monitor for issues

4. **Sunset Alpine.js** (After 1 week stable)
   - Archive Alpine.js code
   - Remove old deployment
   - Update documentation

## Common Issues & Solutions

### CORS Errors
- Backend already configured for CORS
- Ensure frontend uses correct API URL
- Check `mode: 'cors'` in fetch requests

### Authentication Failures
- Verify JWT_SECRET_KEY is set in Railway
- Check token expiration settings
- Ensure cookies are configured correctly

### Build Failures
- Run `npm install` to update dependencies
- Check for TypeScript errors with `npm run type-check`
- Verify all environment variables are set

## Monitoring Post-Deployment

1. **Check Application Health**
   - Visit site and test core functionality
   - Monitor browser console for errors
   - Check network tab for failed requests

2. **Backend Integration**
   - Verify API calls succeed
   - Check authentication flow
   - Test subscription features

3. **Performance Metrics**
   - Page load time (<2 seconds target)
   - Time to interactive
   - Bundle size verification

## Rollback Plan

If issues arise:
1. Revert DNS to Alpine.js version
2. Fix issues in Next.js version
3. Re-deploy when ready
4. Alpine.js remains at `https://threadr-plum.vercel.app` as backup
# Vercel Deployment Instructions - Next.js Threadr App

## Prerequisites Completed ✅
- Next.js application built successfully (confirmed)
- Vercel CLI installed (v44.6.4)
- Project structure validated
- Environment variables configured

## Step 1: Manual Vercel Login
Since interactive login isn't available in the current environment, you'll need to:

1. Open a new Command Prompt/PowerShell window
2. Navigate to the project directory:
   ```cmd
   cd "C:\Users\HoshitoPowell\Desktop\Threadr\threadr-nextjs"
   ```

3. Login to Vercel (this will open your browser):
   ```cmd
   vercel login
   ```
   - Choose your preferred login method (GitHub recommended)
   - Complete authentication in browser

## Step 2: Deploy to Vercel Staging

After successful login, deploy the application:

```cmd
vercel --prod=false
```

During deployment, Vercel will ask:
- **Set up and deploy**: `Yes`
- **Which scope**: Choose your personal account or team
- **Link to existing project**: `No` (creating new staging deployment)
- **Project name**: `threadr-nextjs-staging` (or similar)
- **Directory**: Accept default (`./`)
- **Override settings**: `No` (use vercel.json)

## Step 3: Configure Environment Variables

After deployment, go to Vercel Dashboard:

1. Open https://vercel.com/dashboard
2. Find your new project: `threadr-nextjs-staging`
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

### Required Environment Variables:
```
NEXT_PUBLIC_API_BASE_URL = https://threadr-production.up.railway.app/api
NEXT_PUBLIC_APP_URL = [YOUR_VERCEL_URL]
NEXT_PUBLIC_FRONTEND_URL = [YOUR_VERCEL_URL]
NODE_ENV = production
```

**Note**: No API key required! The backend uses IP-based authentication and rate limiting.

### Optional (if Stripe payment features are needed):
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY = pk_test_your_stripe_key_here
```

**Important**: Replace `[YOUR_VERCEL_URL]` with your actual Vercel deployment URL (provided after deployment)

## Step 4: Redeploy with Environment Variables

After adding environment variables:

```cmd
vercel --prod=false
```

This redeploys with the new environment variables.

## Step 5: Verify Deployment

### Check Deployment Status:
1. **URL Access**: Visit your Vercel URL
2. **API Connectivity**: Check if the app can reach the Railway backend
3. **Authentication**: Test login/register functionality
4. **Thread Generation**: Test core functionality

### Quick Health Check:
- Homepage loads correctly
- Navigation works between pages
- API calls to Railway backend succeed
- Console shows no critical errors

## Expected Deployment URL Format:
Your staging deployment will be available at:
`https://threadr-nextjs-staging-[hash].vercel.app`

## Troubleshooting

### Common Issues:

**1. Build Fails:**
- Check for TypeScript errors
- Verify all dependencies are installed
- Review build logs in Vercel dashboard

**2. Runtime Errors:**
- Verify environment variables are set correctly
- Check CORS settings on Railway backend
- Review browser console for specific errors

**3. API Connection Issues:**
- Confirm Railway backend is running: https://threadr-production.up.railway.app/health
- Verify API_BASE_URL is correct
- Check network tab for failed requests

### Debug Commands:
```cmd
# Check current deployment status
vercel ls

# View deployment logs
vercel logs [deployment-url]

# Check environment variables
vercel env ls
```

## Security Notes
- Never commit `.env.local` files
- API keys should only be set in Vercel dashboard
- Use different API keys for staging vs production

## Next Steps After Deployment
1. Update DNS/domain settings if needed
2. Configure custom domain in Vercel (optional)
3. Set up monitoring and analytics
4. Plan production deployment strategy

## File Changes Made:
- Created `.env.production` with template values
- Updated `vercel.json` with API proxy configuration
- Built application successfully (confirmed working)

## Support
If you encounter issues:
1. Check Vercel deployment logs
2. Verify Railway backend health
3. Review browser console errors
4. Test API endpoints directly
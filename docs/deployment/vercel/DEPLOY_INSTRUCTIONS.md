# Threadr Frontend Deployment Instructions

## Current Problem
The frontend at `https://threadr-plum.vercel.app` is returning a 404 error, which means it's not properly deployed.

## Solution: Step-by-Step Deployment

### Step 1: Authentication
Open PowerShell in the frontend directory and run:
```powershell
cd "C:\Users\HoshitoPowell\Desktop\Threadr\frontend"
vercel login
```
- This will open a browser window
- Sign in with your Vercel account (GitHub, Google, etc.)
- Return to the terminal when complete

### Step 2: Deploy to Production
After authentication, run:
```powershell
vercel --prod --yes
```

This will:
- Create a new Vercel project (if needed)
- Deploy the static files
- Provide you with the production URL

### Step 3: Verify Deployment
1. Visit the provided URL (should be something like `https://threadr-abc123.vercel.app`)
2. Test the application:
   - Enter a URL or paste text
   - Click "Generate Thread"
   - Verify it connects to the Railway backend at `https://threadr-production.up.railway.app`

## Alternative: Using the Deployment Scripts

We've created two deployment scripts for you:

### PowerShell (Windows)
```powershell
.\deploy-now.ps1
```

### Bash (Cross-platform)
```bash
./deploy.sh --production
```

## Expected Result
After successful deployment:
- The 404 error will be resolved
- Your frontend will be accessible at the new Vercel URL
- The app will work with your Railway backend
- You can test thread generation end-to-end

## Files Ready for Deployment
✅ `index.html` - Complete Alpine.js application  
✅ `config.js` - Configured for Railway backend  
✅ `vercel.json` - Optimized Vercel configuration  
✅ Deployment scripts created and ready  

## Troubleshooting
If deployment fails:
1. Check that Vercel CLI is installed: `vercel --version`
2. Ensure you're authenticated: `vercel whoami`
3. Try with debug output: `vercel --prod --debug`
4. Check Vercel dashboard for error details

## Next Steps After Deployment
1. Test the application thoroughly
2. Configure custom domain (optional)
3. Monitor the deployment in Vercel dashboard
4. Update DNS if using custom domain
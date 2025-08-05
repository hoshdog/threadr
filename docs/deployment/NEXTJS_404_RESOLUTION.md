# Next.js 404 Error Resolution Guide

## Problem Summary
The Next.js deployment showed a 404 error despite multiple configuration attempts.

## Root Cause
The large Alpine.js `index.html` file (316KB) in the root directory was causing Vercel to detect the project as a static HTML site instead of recognizing the Next.js application in the `threadr-nextjs` subdirectory.

## Solution Applied

### 1. Renamed Conflicting File
```bash
# Changed:
index.html → index-alpine-legacy.html
```

This prevents Vercel from detecting the project as static HTML.

### 2. Simplified Root vercel.json
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://threadr-production.up.railway.app/api/:path*"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "$NEXT_PUBLIC_API_BASE_URL",
    "NEXT_PUBLIC_API_KEY": "$NEXT_PUBLIC_API_KEY", 
    "NEXT_PUBLIC_APP_URL": "$NEXT_PUBLIC_APP_URL"
  }
}
```

Removed conflicting build commands that interfered with the root directory setting.

## Vercel Project Settings
Ensure these settings in your Vercel dashboard:
- **Root Directory**: `threadr-nextjs`
- **Framework Preset**: Next.js (should auto-detect)
- **Build Command**: (use default)
- **Output Directory**: (use default)

## Verification Steps

1. **Check Deployment Logs**
   - Should see "Detected Next.js" instead of "Static HTML"
   - Should list all 17 routes being built

2. **Test Live Site**
   - Homepage should load without 404
   - Navigation should work
   - API calls should proxy to Railway backend

## If Still Having Issues

1. **Clear Build Cache**
   - Go to Vercel project settings
   - Find "Build Cache" section
   - Click "Clear Cache"
   - Redeploy

2. **Check Environment Variables**
   ```
   NEXT_PUBLIC_API_BASE_URL=https://threadr-production.up.railway.app/api
   NEXT_PUBLIC_API_KEY=[your-api-key]
   NEXT_PUBLIC_APP_URL=[your-vercel-url]
   ```

3. **Manual Redeploy**
   - Go to Deployments tab
   - Click "..." on latest deployment
   - Select "Redeploy"

## Common Pitfalls
- Don't have `index.html` in root when deploying Next.js from subdirectory
- Don't mix static site config with Next.js config
- Ensure root directory setting matches your project structure

## Status
- **Fix Applied**: ✅ 
- **Committed**: ✅ (commit: 6abd376)
- **Documentation**: This file
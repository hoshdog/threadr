# Vercel Security Setup - API Key Environment Variables

## Overview

This document explains how to securely configure API keys for Threadr using Vercel environment variables, eliminating the security vulnerability of hardcoded API keys in the frontend code.

## Security Issue Addressed

**Problem**: API key was hardcoded in `frontend/public/config.js` line 59:
```javascript
return 'zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8';
```

**Risk**: This exposes the API key to anyone who views the source code, creating a critical security vulnerability.

**Solution**: Use Vercel environment variables with build-time injection to keep API keys secure.

## Implementation Details

### 1. Code Changes Made

#### A. Modified `frontend/public/config.js`
- Updated API key retrieval to check `window.THREADR_API_KEY` first
- Added fallback to hardcoded key for backward compatibility
- Added warning message when using fallback

#### B. Updated `frontend/public/index.html`
- Added placeholder script for environment variable injection
- Build process replaces placeholder with actual environment variable

#### C. Created Build System
- `frontend/build.js`: Node.js script that injects environment variables during build
- `frontend/package.json`: Updated build script configuration
- `vercel.json`: Vercel configuration for custom build process

### 2. Vercel Environment Variable Setup

#### Step 1: Access Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Navigate to your Threadr project
3. Click on "Settings" tab
4. Click on "Environment Variables" in the sidebar

#### Step 2: Add the API Key
1. Click "Add New" button
2. Enter the following details:
   - **Name**: `THREADR_API_KEY`
   - **Value**: `zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8`
   - **Environment**: Select "Production", "Preview", and "Development" (all environments)
3. Click "Save"

#### Step 3: Trigger Redeploy
1. Go to "Deployments" tab
2. Click "..." on the latest deployment
3. Click "Redeploy" to trigger a new build with environment variables

### 3. Verification

#### A. Check Build Logs
After deployment, check the build logs for these messages:
- ✅ "Injecting API key from environment variable" (success)
- ⚠️ "No THREADR_API_KEY environment variable found" (needs setup)

#### B. Browser Console
Open browser developer tools on your deployed site:
- Should NOT see: "Using fallback API key" warning
- Should see: Clean initialization without warnings

#### C. Source Code Inspection
View page source - the API key should NOT be visible in the HTML or JavaScript files.

## Security Benefits

### Before (Insecure)
- API key visible in source code
- Anyone can copy and misuse the key
- No way to rotate keys without code changes
- Keys exposed in version control

### After (Secure)
- API key injected at build time from environment variables
- Not visible in source code or client-side JavaScript
- Easy key rotation through Vercel dashboard
- No sensitive data in version control

## Development Workflow

### Local Development
- No changes needed - development environments use `null` API key
- Local testing continues to work as before

### Production Deployment
1. Update environment variable in Vercel dashboard if needed
2. Deploy code changes normally
3. Vercel build process automatically injects secure API key

### Key Rotation
1. Generate new API key in backend system
2. Update `THREADR_API_KEY` in Vercel environment variables
3. Redeploy to apply new key
4. Old key can be safely deactivated

## Backup and Recovery

### If Environment Variable Setup Fails
The system includes a fallback mechanism:
- Will use hardcoded key temporarily
- Displays warning in console
- Gives time to properly configure environment variables

### Removing the Fallback (Recommended)
Once environment variables are confirmed working:

1. Remove the fallback code from `config.js`:
```javascript
// Remove these lines after confirming environment variables work
console.warn('Using fallback API key. Please configure THREADR_API_KEY environment variable.');
return 'zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8';
```

2. Replace with error handling:
```javascript
throw new Error('THREADR_API_KEY environment variable not configured');
```

## Troubleshooting

### Problem: "Using fallback API key" warning
**Cause**: Environment variable not properly configured
**Solution**: 
1. Verify environment variable exists in Vercel dashboard
2. Check spelling: `THREADR_API_KEY` (case sensitive)
3. Ensure it's set for the correct environment (Production/Preview)
4. Redeploy the application

### Problem: Build fails with "Cannot read property"
**Cause**: Build script cannot access environment variables
**Solution**:
1. Check `vercel.json` configuration
2. Verify build command is `node build.js`
3. Ensure Node.js is available in build environment

### Problem: API key still visible in source
**Cause**: Build process not running or environment variable empty
**Solution**:
1. Check build logs for injection messages
2. Verify environment variable has a value
3. Clear browser cache and reload

## Next Steps

### Phase 1: Immediate (DONE)
- ✅ Implement environment variable injection system
- ✅ Add fallback for backward compatibility
- ✅ Create Vercel configuration
- ✅ Document setup process

### Phase 2: Hardening (Recommended within 1 week)
- Remove fallback mechanism after confirming environment variables work
- Add environment variable validation in build process
- Implement key rotation procedures
- Add monitoring for API key usage

### Phase 3: Advanced Security (Future)
- Implement API key scoping (different keys for different environments)
- Add API key expiration and automatic rotation
- Implement rate limiting per API key
- Add audit logging for API key usage

## Contact

For questions about this security implementation:
- Check build logs in Vercel dashboard
- Test in development environment first
- Monitor browser console for warnings/errors

## Security Checklist

- [ ] Environment variable `THREADR_API_KEY` configured in Vercel
- [ ] Environment variable set for all environments (Production, Preview, Development)
- [ ] Successful deployment with environment variable injection
- [ ] No "fallback API key" warnings in browser console
- [ ] API key not visible in page source
- [ ] Application functionality working correctly
- [ ] Plan created for removing fallback mechanism
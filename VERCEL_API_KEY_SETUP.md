# Vercel API Key Security Setup Guide

## 🚨 Critical Security Fix: API Key Configuration

This guide will help you secure your Threadr API key by moving it from hardcoded source code to Vercel environment variables.

## Current Status

✅ **Code is ready**: All files have been updated to support environment variable injection
⚠️ **Action required**: You need to configure the environment variable in Vercel

## Step-by-Step Configuration

### 1. Access Vercel Dashboard
1. Go to [https://vercel.com](https://vercel.com)
2. Log in to your account
3. Navigate to your **threadr** project

### 2. Configure Environment Variable
1. Click on **Settings** tab
2. Select **Environment Variables** from the left sidebar
3. Click **Add Variable**
4. Configure as follows:
   - **Key**: `threadr-api-key`
   - **Value**: `zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8`
   - **Environment**: Select all (Production, Preview, Development)
   - **Sensitive**: ✅ Check this box

### 3. Deploy Changes
1. Trigger a new deployment:
   ```bash
   git add .
   git commit -m "Security: Move API key to environment variable"
   git push
   ```
2. Vercel will automatically deploy with the secure API key

### 4. Verify Security
1. Visit your production site: https://threadr-plum.vercel.app
2. Open browser DevTools (F12)
3. Go to Sources tab
4. Check `config.js` - API key should NOT be visible
5. Check Console - you should see: "API key not found in environment variable" until the env var is set

## How It Works

1. **Build Time**: Vercel runs `build.js` which reads `THREADR_API_KEY` from environment
2. **Injection**: The build script injects the API key into `index.html`
3. **Runtime**: `config.js` reads from `window.THREADR_API_KEY`
4. **Fallback**: Temporarily uses hardcoded key if env var not set (remove after verification)

## Security Benefits

- ✅ API key no longer visible in source code
- ✅ Key rotation possible without code changes
- ✅ Different keys for different environments
- ✅ Audit trail of who accessed the key
- ✅ Automatic encryption at rest

## Testing Locally

For local development, the API key is not required (returns null for localhost).

If you need to test with API key locally:
```bash
# Windows
set THREADR_API_KEY=your-test-key
npm run build

# Mac/Linux
THREADR_API_KEY=your-test-key npm run build
```

## Important Notes

1. **Fallback Removal**: After confirming the environment variable works, remove the fallback in `config.js` (line 66)
2. **Key Rotation**: Consider generating a new API key after this security fix
3. **Access Control**: Limit who has access to Vercel environment variables
4. **Monitoring**: Set up alerts for unusual API usage

## Troubleshooting

### API Key Not Working
1. Check Vercel build logs for "Injecting API key from environment variable"
2. Verify the environment variable name is exactly `threadr-api-key`
3. Ensure you've redeployed after adding the variable
4. Check browser console for any errors

### Still Seeing Hardcoded Key
1. Clear browser cache
2. Check you're on the latest deployment
3. Verify build.js ran successfully in Vercel logs
4. Ensure you're not looking at cached files

## Next Steps

1. ✅ Configure environment variable in Vercel (TODAY!)
2. ✅ Deploy and verify security
3. 📅 Remove fallback after 1 week
4. 📅 Rotate API key after migration complete
5. 📅 Implement user-specific API keys (Phase 2)

## Support

If you encounter any issues:
1. Check Vercel deployment logs
2. Review browser console errors
3. Verify environment variable configuration
4. Contact support with deployment URL and error messages

---

**Security First**: This fix eliminates a critical vulnerability. Complete it immediately to protect your application and users.
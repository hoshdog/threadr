# ✅ CORRECTED VERCEL SETUP - ENVIRONMENT VARIABLE FIX

## 🚨 CRITICAL: Use Underscores, Not Hyphens!

### ❌ WRONG (causes error):
```
threadr-api-key    ← Vercel rejects this!
```

### ✅ CORRECT:
```
THREADR_API_KEY    ← Use this!
```

## Step-by-Step Instructions

### 1. Open Vercel Dashboard
- Go to: https://vercel.com/dashboard
- Click on your **threadr** project

### 2. Navigate to Environment Variables
- Click **Settings** tab (top navigation)
- Click **Environment Variables** (left sidebar)

### 3. Add New Environment Variable
- Click **Add Variable** button
- Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `THREADR_API_KEY` |
| **Value** | `zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8` |
| **Environment** | ☑ Production ☑ Preview ☑ Development |
| **Sensitive** | ☑ Yes |

### 4. Save and Deploy
- Click **Save** button
- Vercel will show: "Updated environment variables"
- Click **Redeploy** when prompted

## Why This Error Happened

Vercel environment variable names follow strict rules:
- ✅ Can use: Letters (A-Z, a-z)
- ✅ Can use: Numbers (0-9)
- ✅ Can use: Underscores (_)
- ❌ Cannot use: Hyphens (-)
- ❌ Cannot use: Spaces or special characters
- ❌ Cannot: Start with a number

## Verification Steps

After deployment completes (2-3 minutes):

1. **Visit your site**: https://threadr-plum.vercel.app
2. **Open DevTools** (F12)
3. **Go to Console** tab
4. **Look for**:
   - ✅ No warning about "Using fallback API key"
   - ✅ No API key visible in Sources → config.js
   - ✅ API calls working (generate a thread)

## Common Issues

### Still seeing "Using fallback API key"?
- Clear browser cache (Ctrl+Shift+R)
- Verify deployment completed
- Check environment variable name is exactly `THREADR_API_KEY`

### Deployment failed?
- Check Vercel build logs
- Ensure no typos in environment variable name
- Verify the value doesn't have extra spaces

### API calls failing?
- The API key value should be exactly: `zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8`
- No quotes around the value in Vercel
- All environments should be checked

## Technical Details

The system works like this:
1. Vercel reads `THREADR_API_KEY` environment variable
2. Build script (`build.js`) injects it into the HTML
3. Frontend code reads from `window.THREADR_API_KEY`
4. Config.js uses it for API authentication

## Success Checklist

After completing setup:
- [ ] Environment variable added with correct name
- [ ] Deployment triggered and completed
- [ ] No API key visible in browser source
- [ ] No console warnings about fallback
- [ ] Thread generation working
- [ ] Trust signals visible
- [ ] Character counter working

## Next Steps

Once this is working:
1. Set up Redis (see RAILWAY_REDIS_SETUP_GUIDE.md)
2. Run verification suite: `run_verification_suite.bat`
3. Remove API key fallback after 1 week

---

**Remember**: The environment variable name must be `THREADR_API_KEY` with underscores, not hyphens!
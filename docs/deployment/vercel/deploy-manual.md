# Manual Vercel Deployment Guide

## Prerequisites
- Vercel CLI is installed ✅
- Frontend files are ready ✅
- Backend API is working ✅

## Step-by-Step Deployment

### 1. Authenticate with Vercel
```bash
cd frontend
vercel login
```
Choose your preferred authentication method (GitHub recommended).

### 2. Deploy to Production
```bash
vercel --prod --yes
```

### 3. Expected Output
You should see output similar to:
```
🔍  Inspect: https://vercel.com/...
✅  Production: https://threadr-plum.vercel.app [copied to clipboard] [2s]
```

### 4. Test the Deployment
1. Visit the production URL: https://threadr-plum.vercel.app
2. Test URL input: Try pasting a blog article URL
3. Test text input: Try pasting some article content
4. Verify the API connection works with the Railway backend

### 5. Verification Checklist
- [ ] Frontend loads without errors
- [ ] API calls reach the Railway backend successfully
- [ ] CORS headers allow cross-origin requests
- [ ] Email capture modal appears after first use
- [ ] Generated threads can be copied individually and as a whole
- [ ] Error handling works for invalid inputs

## Configuration Details

### Current API Configuration
- **Production API**: https://threadr-production.up.railway.app
- **Frontend URL**: https://threadr-plum.vercel.app (after deployment)
- **Auto-detection**: The frontend automatically detects the environment

### Environment Variables (Already Set)
- `THREADR_API_URL`: https://threadr-production.up.railway.app

### Security Features
- CORS properly configured
- Security headers set in vercel.json
- Rate limiting handled by backend
- No sensitive data in frontend

## Troubleshooting

### If CORS errors occur:
1. Check that the backend at Railway has CORS enabled for the Vercel domain
2. Verify the API URL in config.js matches the Railway deployment

### If the deployment fails:
1. Ensure you're in the frontend directory
2. Check that vercel.json is valid JSON
3. Verify all required files are present

### If the API connection fails:
1. Test the backend health: `curl https://threadr-production.up.railway.app/health`
2. Check browser developer tools for detailed error messages
3. Verify the API URL configuration

## Next Steps After Deployment
1. Test the full user flow
2. Monitor for any errors in production
3. Update project documentation with the live URL
4. Set up analytics if needed
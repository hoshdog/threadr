# Threadr Deployment Guide (Consolidated)

This guide consolidates all deployment information for the Threadr project.

## Current Deployment Architecture

### Frontend: Next.js on Vercel
- **URL**: https://threadr-nextjs.vercel.app
- **Directory**: threadr-nextjs/
- **Deployment**: 
px vercel --prod

### Backend: FastAPI on Render.com
- **URL**: https://threadr-backend.onrender.com
- **Directory**: backend/
- **Configuration**: backend/render.yaml
- **Main File**: src/main_minimal.py

## Quick Deployment Steps

### 1. Backend (Render.com)
1. Sign up at render.com with GitHub
2. New+ â†’ Web Service â†’ Connect "threadr" repo
3. Render auto-detects render.yaml
4. Deploy (takes ~5 minutes)

### 2. Frontend (Vercel)
`ash
cd threadr-nextjs
echo NEXT_PUBLIC_API_BASE_URL=https://threadr-backend.onrender.com > .env.production.local
npx vercel --prod
`

### 3. Environment Variables
Set in Vercel Dashboard:
- NEXT_PUBLIC_API_BASE_URL = https://threadr-backend.onrender.com
- NEXT_PUBLIC_APP_URL = [your-vercel-url]

## Previous Deployment Methods (Archived)

### Railway (Deprecated due to caching issues)
- See archive/railway-deployment/ for historical reference

### Alpine.js Frontend (Deprecated)
- Legacy frontend at frontend/public/
- Being migrated to Next.js

## Troubleshooting

### Common Issues
1. **CORS Errors**: Backend configured with allow_origins=["*"]
2. **404 Errors**: Check API base URL has no trailing slash
3. **Slow First Request**: Render free tier has cold starts

### Health Checks
- Backend: https://threadr-backend.onrender.com/health
- Frontend: Check browser console for API calls

## Related Documentation
- [API Reference](../api/API_DOCUMENTATION.md)
- [Development Guide](../development/README.md)
- [Security Guide](../security/SECURITY.md)

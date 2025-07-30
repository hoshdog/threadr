# Threadr Frontend Deployment Guide

## Vercel Deployment

### 1. Prerequisites
- Vercel CLI installed: `npm i -g vercel`
- Vercel account connected

### 2. Environment Variables
Set these in your Vercel dashboard or via CLI:

```bash
# Set production API URL
vercel env add THREADR_API_URL production https://threadr-production.up.railway.app

# Optional: Set for preview deployments
vercel env add THREADR_API_URL preview https://threadr-production.up.railway.app
```

### 3. Deploy Commands

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

### 4. Custom Domain
1. Go to Vercel dashboard
2. Select your project
3. Go to Settings > Domains
4. Add your custom domain

## Local Testing with Production Backend

```bash
# Start a local server
npx serve . -p 3000

# Or use Python
python -m http.server 3000

# Or use Node.js serve
npm install -g serve
serve -s . -p 3000
```

The frontend will automatically detect localhost and use the production backend URL.

## Configuration

The app automatically detects the environment:
- `localhost` → Development mode with localhost:8000 backend
- `*.vercel.app` → Preview/Production mode with Railway backend
- Custom domain → Production mode with Railway backend

## CORS Considerations

The frontend handles CORS by:
1. Using appropriate request headers
2. Handling CORS errors gracefully
3. Providing fallback functionality when needed

## Troubleshooting

### Backend Connection Issues
1. Check network connectivity
2. Verify Railway backend is running
3. Check browser console for CORS errors
4. Enable fallback mode in localStorage: `localStorage.setItem('threadr_allow_fallback', 'true')`

### Environment Variable Issues
1. Check Vercel dashboard environment variables
2. Verify environment variable names match config.js
3. Redeploy after changing environment variables
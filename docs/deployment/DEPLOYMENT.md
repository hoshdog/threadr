# Threadr Deployment Guide

This guide will help you deploy Threadr with the backend on Railway and frontend on Vercel.

## Prerequisites

1. **Accounts Required:**
   - [Railway Account](https://railway.app)
   - [Vercel Account](https://vercel.com)
   - [OpenAI API Key](https://platform.openai.com/api-keys)

2. **CLI Tools:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Install Vercel CLI
   npm install -g vercel
   ```

## Backend Deployment (Railway)

### Option 1: Deploy via GitHub (Recommended)

1. Push your code to GitHub
2. Go to [Railway Dashboard](https://railway.app/dashboard)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository and the `backend` directory
5. Railway will auto-detect the Python app

### Option 2: Deploy via CLI

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Create a new project:
   ```bash
   railway init
   ```

4. Deploy:
   ```bash
   railway up
   ```

### Configure Environment Variables

1. Go to your Railway project dashboard
2. Click on your service → "Variables"
3. Add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

4. Optional variables:
   ```
   RATE_LIMIT_REQUESTS=10
   RATE_LIMIT_WINDOW_HOURS=1
   MAX_TWEET_LENGTH=280
   MAX_CONTENT_LENGTH=10000
   ```

### Get Your Backend URL

After deployment, Railway will provide a URL like:
`https://threadr-backend.up.railway.app`

## Frontend Deployment (Vercel)

### Step 1: Update Configuration

1. Edit `frontend/config.js`:
   ```javascript
   const config = {
       API_URL: window.location.hostname === 'localhost' 
           ? 'http://localhost:8000' 
           : 'https://threadr-backend.up.railway.app', // Your Railway URL
       // ... rest of config
   };
   ```

### Step 2: Deploy to Vercel

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Deploy with Vercel CLI:
   ```bash
   vercel
   ```

3. Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? **Select your account**
   - Link to existing project? **N**
   - Project name? **threadr-frontend** (or your choice)
   - Directory? **./** (current directory)
   - Override settings? **N**

4. For production deployment:
   ```bash
   vercel --prod
   ```

### Step 3: Update Backend CORS

1. Go back to Railway dashboard
2. Update the `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://threadr-frontend.vercel.app
   ```
   Or for multiple origins:
   ```
   CORS_ORIGINS=https://threadr-frontend.vercel.app,https://threadr.com
   ```

## Security Checklist

- [ ] OPENAI_API_KEY is set in Railway (not in code)
- [ ] CORS_ORIGINS is restricted to your frontend domain
- [ ] Rate limiting is enabled
- [ ] HTTPS is used for all connections
- [ ] No sensitive data in frontend code

## Monitoring & Maintenance

### Railway
- Monitor logs: `railway logs`
- Check metrics in Railway dashboard
- Set up health check alerts

### Vercel
- Monitor analytics in Vercel dashboard
- Set up error tracking
- Configure custom domain if needed

## Troubleshooting

### Backend Issues
1. **500 errors**: Check Railway logs for Python errors
2. **CORS errors**: Verify CORS_ORIGINS includes your frontend URL
3. **Rate limit issues**: Check rate limiter configuration

### Frontend Issues
1. **API connection failed**: Verify API_URL in config.js
2. **404 errors**: Check vercel.json routing configuration

### Common Commands

```bash
# Railway
railway logs          # View backend logs
railway status       # Check deployment status
railway variables    # List environment variables

# Vercel
vercel logs          # View frontend logs
vercel env pull      # Pull environment variables
vercel domains       # Manage custom domains
```

## Cost Estimation

- **Railway**: Free tier includes 500 hours/month, $5 credit
- **Vercel**: Free tier includes 100GB bandwidth/month
- **OpenAI**: Pay per API usage (~$0.002 per request)

## Next Steps

1. Set up custom domains
2. Configure monitoring/alerts
3. Set up CI/CD pipeline
4. Add error tracking (Sentry)
5. Implement analytics
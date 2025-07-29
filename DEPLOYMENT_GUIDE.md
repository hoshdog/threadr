# Threadr Deployment Guide

## Overview

This guide will walk you through deploying your Threadr application to production with:
- **Backend**: Railway (Python FastAPI)
- **Frontend**: Vercel (Static HTML)
- **DDoS Protection**: Cloudflare
- **Estimated Cost**: $0-$5/month for MVP

## Prerequisites

### 1. Required Accounts (All Free Tier)

1. **Railway Account**
   - Sign up at: https://railway.app
   - Free tier: $5 credit/month (sufficient for MVP)
   - No credit card required initially

2. **Vercel Account**
   - Sign up at: https://vercel.com
   - Free tier: Unlimited static sites
   - No credit card required

3. **Cloudflare Account**
   - Sign up at: https://cloudflare.com
   - Free tier includes DDoS protection
   - Domain required (can buy through Cloudflare ~$10/year)

4. **GitHub Account** (Recommended)
   - Sign up at: https://github.com
   - For version control and automated deployments

## Step 1: Prepare Your Codebase

### 1.1 Environment Variables
Your backend needs the OpenAI API key. We'll set this up securely in Railway.

### 1.2 Update Backend for Production
The backend code needs some adjustments for production deployment.

### 1.3 Update Frontend API Endpoint
The frontend needs to point to your production backend URL.

## Step 2: Deploy Backend to Railway

### 2.1 Push Code to GitHub (Recommended)

1. Create a new repository on GitHub
2. Initialize git in your project:
   ```bash
   cd C:\Users\HoshitoPowell\Desktop\Threadr
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/threadr.git
   git push -u origin main
   ```

### 2.2 Deploy to Railway

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select the threadr repository
5. Railway will auto-detect Python and start deployment

### 2.3 Configure Railway

1. In Railway dashboard, click on your project
2. Go to "Variables" tab
3. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: [Your OpenAI API key]
4. Go to "Settings" tab
5. Under "Service", set:
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `/`

### 2.4 Get Your Backend URL

1. In Railway dashboard, go to "Settings"
2. Under "Domains", click "Generate Domain"
3. Copy your backend URL (e.g., `threadr-backend.up.railway.app`)

## Step 3: Deploy Frontend to Vercel

### 3.1 Update Frontend Configuration

Before deploying, update the API endpoint in your frontend to use the Railway backend URL.

### 3.2 Deploy to Vercel

#### Option A: Deploy via GitHub (Recommended)
1. Go to https://vercel.com and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Other
   - Root Directory: `frontend`
   - Build Command: (leave empty)
   - Output Directory: `.`
5. Click "Deploy"

#### Option B: Deploy via CLI
1. Install Vercel CLI: `npm i -g vercel`
2. In your frontend directory:
   ```bash
   cd frontend
   vercel
   ```
3. Follow the prompts

### 3.3 Get Your Frontend URL

Vercel will provide you with a URL like `threadr.vercel.app`

## Step 4: Set Up Cloudflare (Optional but Recommended)

### 4.1 Add Your Domain

1. Buy a domain through Cloudflare or transfer existing domain
2. In Cloudflare dashboard, add your site
3. Update nameservers at your registrar to Cloudflare's

### 4.2 Configure DNS

1. Add CNAME record:
   - Name: `@` or `www`
   - Target: Your Vercel URL
2. Add CNAME record for API (optional):
   - Name: `api`
   - Target: Your Railway URL

### 4.3 Enable Security Features

1. Go to "Security" → "Settings"
2. Set Security Level to "Medium"
3. Enable "Bot Fight Mode"
4. Go to "SSL/TLS" → Set to "Full"

## Step 5: Production Configuration

### 5.1 CORS Configuration

Update your backend CORS settings to only allow your frontend domain.

### 5.2 Rate Limiting

Your backend already has rate limiting implemented (10 requests per hour per IP).

### 5.3 Environment Variables Summary

**Railway (Backend)**:
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: (Automatically set by Railway)

**Vercel (Frontend)**:
- No environment variables needed

## Cost Breakdown

### Monthly Costs (MVP Stage)

1. **Railway**: 
   - Free tier: $5 credit/month
   - Estimated usage: ~$2-3/month for light traffic
   - **Cost: $0** (within free tier)

2. **Vercel**:
   - Static hosting: Free unlimited
   - **Cost: $0**

3. **Cloudflare**:
   - Free tier includes DDoS protection
   - **Cost: $0**

4. **OpenAI API**:
   - GPT-3.5-turbo: ~$0.001 per 1K tokens
   - Estimated: 100 threads/day = ~$3-5/month
   - **Cost: $3-5/month**

5. **Domain** (if purchasing):
   - **Cost: ~$10-15/year**

**Total Monthly Cost: $3-5 + domain cost**

## Monitoring and Maintenance

### 1. Railway Monitoring
- View logs: Railway dashboard → Deployments → View Logs
- Monitor usage: Railway dashboard → Usage tab

### 2. Vercel Analytics
- Enable Web Analytics in Vercel dashboard (free tier available)

### 3. Error Tracking (Optional)
- Consider adding Sentry (free tier available) for error tracking

## Security Checklist

- [x] API key stored as environment variable
- [x] CORS configured for production
- [x] Rate limiting implemented
- [x] HTTPS enabled on all endpoints
- [x] Input validation on backend
- [x] DDoS protection via Cloudflare

## Deployment Checklist

- [ ] Create Railway account
- [ ] Create Vercel account
- [ ] Create Cloudflare account (optional)
- [ ] Push code to GitHub
- [ ] Deploy backend to Railway
- [ ] Set OPENAI_API_KEY in Railway
- [ ] Update frontend API URL
- [ ] Deploy frontend to Vercel
- [ ] Configure custom domain (optional)
- [ ] Test the full application flow
- [ ] Monitor for 24 hours

## Troubleshooting

### Backend Issues
1. **500 errors**: Check Railway logs for Python errors
2. **API key issues**: Verify OPENAI_API_KEY is set correctly
3. **CORS errors**: Check allowed origins match your frontend URL

### Frontend Issues
1. **API connection failed**: Verify backend URL is correct
2. **CORS errors**: Backend CORS configuration needs updating

### Performance Issues
1. **Slow responses**: Check OpenAI API response times
2. **Rate limiting**: Monitor usage patterns

## Next Steps

1. **Add Custom Domain**: Professional appearance
2. **Implement Caching**: Reduce API costs
3. **Add Authentication**: For premium features
4. **Analytics**: Track usage patterns
5. **A/B Testing**: Optimize conversion

## Support Resources

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Cloudflare Docs: https://developers.cloudflare.com
- FastAPI Docs: https://fastapi.tiangolo.com

---

This deployment will give you a production-ready MVP with:
- Scalable infrastructure
- DDoS protection
- Minimal costs
- Easy maintenance
- Room to grow
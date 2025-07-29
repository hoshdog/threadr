# Threadr Deployment Checklist

Follow these steps in order to deploy your application successfully.

## Pre-Deployment Setup

- [ ] Create accounts:
  - [ ] Railway account (https://railway.app)
  - [ ] Vercel account (https://vercel.com)
  - [ ] GitHub account (https://github.com)
  - [ ] Cloudflare account - optional (https://cloudflare.com)

- [ ] Get your OpenAI API key ready from https://platform.openai.com/api-keys

## Step 1: Prepare Your Code

- [ ] Copy `backend/main_production.py` to `backend/main.py`:
  ```bash
  cp backend/main_production.py backend/main.py
  ```

- [ ] Remove sensitive files:
  ```bash
  rm openaiKey.key
  rm backend/.openai_key  # if it exists
  ```

## Step 2: Push to GitHub

- [ ] Initialize git repository:
  ```bash
  git init
  git add .
  git commit -m "Initial commit - Threadr MVP"
  ```

- [ ] Create repository on GitHub and push:
  ```bash
  git branch -M main
  git remote add origin https://github.com/YOUR_USERNAME/threadr.git
  git push -u origin main
  ```

## Step 3: Deploy Backend to Railway

- [ ] Go to https://railway.app/new
- [ ] Click "Deploy from GitHub repo"
- [ ] Select your `threadr` repository
- [ ] Wait for initial deployment to complete

- [ ] Configure environment variables:
  - [ ] Go to your project dashboard
  - [ ] Click on the service
  - [ ] Go to "Variables" tab
  - [ ] Add: `OPENAI_API_KEY` = `your-api-key-here`

- [ ] Generate public URL:
  - [ ] Go to "Settings" tab
  - [ ] Under "Networking", click "Generate Domain"
  - [ ] Copy your backend URL (e.g., `threadr-production.up.railway.app`)

- [ ] Verify deployment:
  - [ ] Visit `https://your-backend-url.railway.app/health`
  - [ ] Should return: `{"status": "healthy", "timestamp": "..."}`

## Step 4: Update Frontend Configuration

- [ ] Edit `frontend/config.js`:
  ```javascript
  API_URL: window.location.hostname === 'localhost' 
      ? 'http://localhost:8000' 
      : 'https://YOUR-BACKEND-URL.up.railway.app',  // <- Update this
  ```

- [ ] Commit and push changes:
  ```bash
  git add frontend/config.js
  git commit -m "Update API URL for production"
  git push
  ```

## Step 5: Deploy Frontend to Vercel

- [ ] Go to https://vercel.com/new
- [ ] Import your GitHub repository
- [ ] Configure deployment:
  - [ ] Framework Preset: `Other`
  - [ ] Root Directory: `frontend`
  - [ ] Build Command: (leave empty)
  - [ ] Output Directory: `.`

- [ ] Click "Deploy"
- [ ] Copy your frontend URL (e.g., `threadr.vercel.app`)

## Step 6: Update CORS Settings

- [ ] Edit `backend/main_production.py` to add your Vercel URL:
  ```python
  PRODUCTION_ORIGINS = [
      "https://threadr.vercel.app",  # <- Your actual Vercel URL
      "https://www.threadr.com",     # <- Your custom domain (if any)
      "https://threadr.com",
  ]
  ```

- [ ] Commit and push:
  ```bash
  git add backend/main_production.py
  git commit -m "Update CORS for production frontend"
  git push
  ```

- [ ] Railway will auto-deploy the changes

## Step 7: Test Your Application

- [ ] Visit your Vercel URL
- [ ] Test with a URL:
  - [ ] Enter a news article URL
  - [ ] Click "Generate Thread"
  - [ ] Verify thread is generated

- [ ] Test with text:
  - [ ] Switch to "Paste Text" tab
  - [ ] Enter some text
  - [ ] Generate thread

- [ ] Check rate limiting:
  - [ ] Try generating more than 10 threads
  - [ ] Verify rate limit message appears

## Step 8: Set Up Cloudflare (Optional)

If you have a custom domain:

- [ ] Add site to Cloudflare
- [ ] Update DNS records:
  - [ ] CNAME `@` -> `cname.vercel-dns.com`
  - [ ] CNAME `www` -> `cname.vercel-dns.com`

- [ ] Configure Vercel custom domain:
  - [ ] Go to Vercel project settings
  - [ ] Add your custom domain

- [ ] Enable Cloudflare protections:
  - [ ] Bot Fight Mode: ON
  - [ ] Security Level: Medium
  - [ ] SSL/TLS: Full

## Post-Deployment

- [ ] Monitor Railway usage (Dashboard -> Usage)
- [ ] Set up Vercel Analytics (optional)
- [ ] Test from different devices/browsers
- [ ] Share with a few users for feedback

## Troubleshooting Commands

Check Railway logs:
```bash
railway logs
```

Check deployment status:
```bash
railway status
```

Test API locally with production settings:
```bash
OPENAI_API_KEY=your-key-here uvicorn backend.main:app --reload
```

## Important URLs to Save

- Railway Backend: `https://_____________________.up.railway.app`
- Vercel Frontend: `https://_____________________.vercel.app`
- GitHub Repo: `https://github.com/________________/threadr`
- Railway Dashboard: `https://railway.app/project/_____________`
- Vercel Dashboard: `https://vercel.com/________________/threadr`

## Success Criteria

- [ ] Frontend loads without errors
- [ ] Can generate threads from URLs
- [ ] Can generate threads from text
- [ ] Rate limiting works (10 requests/hour)
- [ ] No CORS errors in browser console
- [ ] API health check returns healthy

Congratulations! Your Threadr app is now live! 🎉
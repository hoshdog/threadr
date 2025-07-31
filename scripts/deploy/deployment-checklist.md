# Threadr Deployment Checklist
*Complete verification and deployment guide for monetization features*

## Pre-Deployment Verification

### ✅ Local Testing
- [ ] **Backend Health Check**
  ```bash
  cd backend
  uvicorn src.main:app --reload --port 8001
  # Test: http://localhost:8001/health
  ```

- [ ] **Frontend Local Testing**
  ```bash
  cd frontend/src
  python -m http.server 8000
  # Test: http://localhost:8000
  ```

- [ ] **Run Verification Suite**
  ```bash
  python scripts/deploy/local-verification.py
  # Should show "DEPLOYMENT READY"
  ```

### ✅ Code Verification
- [ ] **Backend Files Present**
  - [ ] `backend/src/main.py` (with Stripe integration)
  - [ ] `backend/src/redis_manager.py`
  - [ ] `backend/requirements.txt` (includes stripe)
  - [ ] `backend/runtime.txt` (Python 3.11)

- [ ] **Frontend Files Present**
  - [ ] `frontend/src/index.html` (with monetization UI)
  - [ ] `frontend/src/config.js` (production URLs)
  - [ ] `frontend/vercel.json`
  - [ ] `frontend/package.json`

- [ ] **Deployment Config**
  - [ ] `nixpacks.toml` (Railway config)
  - [ ] Environment variables documented

### ✅ Feature Testing
- [ ] **Core Features**
  - [ ] Thread generation from URL
  - [ ] Thread generation from text
  - [ ] Tweet editing functionality
  - [ ] Copy individual tweets
  - [ ] Copy entire thread

- [ ] **Monetization Features**
  - [ ] Email capture modal appears after first use
  - [ ] Usage tracking (daily/monthly limits)
  - [ ] Free tier limits enforced
  - [ ] Premium features locked for free users
  - [ ] Stripe webhook endpoint responds

## Deployment Options

### Option 1: Automated Deployment (When Network Available)
```bash
# Backend to Railway
python scripts/deploy/manual-railway-deploy.py --method cli

# Frontend to Vercel  
python scripts/deploy/manual-vercel-deploy.py --method cli
```

### Option 2: Manual CLI Deployment
```bash
# Railway CLI
railway login
railway up --detach

# Vercel CLI  
vercel --prod --yes
```

### Option 3: Manual Upload Deployment
```bash
# Create deployment packages
python scripts/deploy/manual-railway-deploy.py --method zip
python scripts/deploy/manual-vercel-deploy.py --method zip

# Upload via web dashboards
```

## Post-Deployment Verification

### ✅ Backend Verification (Railway)
- [ ] **Health Endpoints**
  ```bash
  curl https://threadr-production.up.railway.app/health
  curl https://threadr-production.up.railway.app/readiness
  ```

- [ ] **API Endpoints**
  ```bash
  # Test thread generation
  curl -X POST https://threadr-production.up.railway.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"content": "Test article content"}'
  
  # Test email capture
  curl -X POST https://threadr-production.up.railway.app/api/capture-email \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com"}'
  
  # Test usage tracking
  curl https://threadr-production.up.railway.app/api/usage
  ```

- [ ] **Stripe Integration**
  ```bash
  # Test webhook endpoint exists (should return 400, not 404)
  curl -X POST https://threadr-production.up.railway.app/api/stripe/webhook
  ```

### ✅ Frontend Verification (Vercel)
- [ ] **Page Loads**
  - [ ] Visit Vercel URL (e.g., https://threadr-plum.vercel.app)
  - [ ] No console errors
  - [ ] UI displays correctly
  - [ ] Mobile responsive

- [ ] **API Communication**
  - [ ] Frontend can reach Railway backend
  - [ ] CORS properly configured
  - [ ] Network requests visible in DevTools

- [ ] **Feature Testing**
  - [ ] Generate thread from URL
  - [ ] Generate thread from text
  - [ ] Edit tweets inline
  - [ ] Copy functionality works
  - [ ] Email capture modal appears
  - [ ] Usage counter updates

### ✅ Integration Testing
- [ ] **End-to-End Flow**
  1. [ ] Visit frontend URL
  2. [ ] Paste article URL or content
  3. [ ] Generate thread successfully
  4. [ ] Edit a tweet
  5. [ ] Copy individual tweet
  6. [ ] Copy entire thread
  7. [ ] Email capture modal appears
  8. [ ] Enter email successfully
  9. [ ] Usage counter increments

- [ ] **Rate Limiting**
  - [ ] Test from different IPs
  - [ ] Verify limits enforced
  - [ ] Error messages appropriate

- [ ] **Premium Features**
  - [ ] Free tier limits respected
  - [ ] Premium features locked
  - [ ] Upgrade prompts shown

## Environment Variables Checklist

### Railway Backend Variables
- [ ] `ENVIRONMENT=production`
- [ ] `OPENAI_API_KEY` (if available)
- [ ] `STRIPE_SECRET_KEY`
- [ ] `STRIPE_WEBHOOK_SECRET`
- [ ] `REDIS_URL` (if using external Redis)
- [ ] `RATE_LIMIT_REQUESTS=10`
- [ ] `FREE_TIER_DAILY_LIMIT=5`
- [ ] `FREE_TIER_MONTHLY_LIMIT=20`

### Vercel Frontend Variables
- [ ] `NODE_ENV=production`
- [ ] Config.js points to Railway backend URL

## Rollback Plan

### If Backend Deployment Fails
1. [ ] Check Railway logs: `railway logs`
2. [ ] Revert to previous deployment
3. [ ] Use ZIP upload method as fallback
4. [ ] Verify health endpoints restore

### If Frontend Deployment Fails  
1. [ ] Check Vercel deployment logs
2. [ ] Revert to previous deployment via dashboard
3. [ ] Use drag-and-drop deployment as fallback
4. [ ] Restore config.js backup

### Emergency Rollback
```bash
# Railway: Redeploy previous version
railway redeploy [previous-deployment-id]

# Vercel: Rollback via dashboard
# Go to Deployments -> Select previous -> Promote to Production
```

## Success Criteria
- [ ] ✅ Backend health checks pass
- [ ] ✅ Frontend loads without errors  
- [ ] ✅ Thread generation works end-to-end
- [ ] ✅ Email capture functional
- [ ] ✅ Usage tracking operational
- [ ] ✅ Rate limiting enforced
- [ ] ✅ Premium features properly locked
- [ ] ✅ No console errors
- [ ] ✅ Mobile responsive
- [ ] ✅ CORS configured correctly

## Monitoring Setup
- [ ] **Railway Monitoring**
  - [ ] CPU/Memory usage within limits
  - [ ] Response times < 2s
  - [ ] Error rate < 1%

- [ ] **Vercel Monitoring**  
  - [ ] Function execution within limits
  - [ ] CDN cache hit rate > 90%
  - [ ] Core Web Vitals green

## Documentation Updates
- [ ] Update CLAUDE.md with deployment URLs
- [ ] Update README.md with new features
- [ ] Document any configuration changes
- [ ] Update API documentation if needed

## Communication Plan
- [ ] **Stakeholder Notification**
  - [ ] New features deployed
  - [ ] URLs updated (if changed)
  - [ ] Known issues (if any)

- [ ] **User Notification**
  - [ ] Email capture feature live
  - [ ] Free tier limits active
  - [ ] Premium features available

## Cleanup Tasks
- [ ] Remove temporary deployment files
- [ ] Clear local caches
- [ ] Update local development config
- [ ] Archive old deployment artifacts

---

## Quick Commands Reference

```bash
# Full local verification
python scripts/deploy/local-verification.py

# Manual Railway deployment
python scripts/deploy/manual-railway-deploy.py

# Manual Vercel deployment  
python scripts/deploy/manual-vercel-deploy.py

# Test production endpoints
curl https://threadr-production.up.railway.app/health
curl https://threadr-plum.vercel.app

# Railway CLI commands
railway login
railway up
railway logs
railway status

# Vercel CLI commands
vercel login
vercel --prod
vercel logs
vercel list
```

---

**Last Updated:** $(date)  
**Next Review:** After successful deployment
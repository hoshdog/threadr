# 🔧 Railway Deployment Troubleshooting Guide

## Your Specific Issue
**Problem**: Railway is deploying `main.py` instead of `main_minimal.py`
**Root Cause**: Build cache or configuration override

## Quick Diagnosis Script
```bash
curl https://threadr-production.up.railway.app/
```

### If you see:
- `"app": "Threadr Minimal"` → ✅ Fixed! New deployment active
- `"message": "Threadr API", "version": "2.0.0"` → ❌ Still old deployment

## Method Priority Order

### 1. Dashboard Cache Clear (5 min) ⭐ TRY FIRST
1. Railway.app → Your Project → Service → Settings
2. Scroll to "Danger Zone" → "Clear Build Cache"
3. Go to Deployments → Click ⋮ → "Redeploy"
4. Watch logs for "main_minimal.py"

### 2. Environment Variable Force (2 min) ⭐ IF #1 FAILS
```
Variables Tab → New Variable
Key: FORCE_REBUILD_NOW
Value: delete-after-deploy
```
This tricks Railway into rebuilding.

### 3. Git Force Push (3 min) ⭐ IF #2 FAILS
```bash
cd C:\Users\HoshitoPowell\Desktop\Threadr
python scripts/force_railway_rebuild.py
```
Choose option 1 or 4.

### 4. Railway CLI (5 min) ⭐ POWER USER
```bash
npm install -g @railway/cli
railway login
railway link
railway up --force
```

### 5. Nuclear Option (10 min) ⭐ LAST RESORT
1. Copy all environment variables
2. Delete service completely
3. Create new service from GitHub

## Common Railway Problems & Solutions

### Problem: "Build cache not clearing"
**Symptoms**: Old code still running after cache clear
**Solutions**:
1. Add dummy environment variable
2. Modify nixpacks.toml slightly
3. Force push with timestamp

### Problem: "nixpacks.toml ignored"
**Symptoms**: Using default Python buildpack
**Check**: Settings → Build → Start Command
**Fix**: Remove any override, ensure nixpacks.toml is used

### Problem: "Import errors in logs"
**Symptoms**: `ModuleNotFoundError` or import failures
**Our Case**: Routes trying to import non-existent files
**Fix**: That's why we created main_minimal.py!

### Problem: "Service stuck in deploying"
**Symptoms**: Deployment never completes
**Solutions**:
1. Cancel deployment
2. Clear cache
3. Redeploy

### Problem: "GitHub webhook not firing"
**Symptoms**: Pushes don't trigger deploys
**Fix**: 
1. GitHub → Settings → Webhooks
2. Find Railway webhook
3. Click "Redeliver" on recent delivery

## Railway Dashboard Navigation

### Finding Build Logs
```
Project → Service → Deployments → Click deployment → View Logs
```

### Finding Environment Variables
```
Project → Service → Variables
```

### Finding Build Settings
```
Project → Service → Settings → Build
```

### Finding Deploy Webhooks
```
Project → Service → Settings → Deploy
```

## What to Look for in Logs

### ✅ GOOD Signs:
```
Using main_minimal.py for deployment
exec uvicorn src.main_minimal:app
Installing dependencies...
Deployment is live
```

### ❌ BAD Signs:
```
exec uvicorn src.main:app
Routes import failed
ModuleNotFoundError
Service degraded
```

## Alternative Platforms (If Railway Won't Cooperate)

### Render.com (5 min) ⭐ EASIEST
1. Sign up at render.com
2. New → Web Service → Connect GitHub
3. Auto-detects our `render.yaml`
4. Deploy!

### Fly.io (10 min) ⭐ FASTEST
```bash
cd backend
fly launch --config fly.toml
fly deploy
```

### Heroku (15 min) ⭐ RELIABLE
```bash
cd backend
echo "web: uvicorn src.main_minimal:app --host 0.0.0.0 --port \$PORT" > Procfile
heroku create threadr-backend
git push heroku main
```

## Emergency Checklist

If nothing works:
- [ ] Check Railway status page: https://status.railway.app
- [ ] Try incognito browser (cache issues)
- [ ] Check GitHub Actions/Webhooks
- [ ] Verify nixpacks.toml is in root (not in backend/)
- [ ] Check for typos in start command
- [ ] Ensure main_minimal.py exists and is committed
- [ ] Try different browser
- [ ] Contact Railway Discord

## Success Verification

After any method, verify with:
```bash
# Quick check
curl https://threadr-production.up.railway.app/health

# Full verification
python scripts/verify_railway_cache_clear.py
```

## Time-Saving Pro Tips

1. **Always check logs first** - They tell you exactly what's wrong
2. **Environment variable trick** - Fastest way to force rebuild
3. **Git timestamp method** - Works when UI fails
4. **Have Render.com ready** - Quick fallback option
5. **Document what works** - Railway can be finicky

## Contact & Support

### Railway Help
- Discord: https://discord.gg/railway (very responsive)
- Docs: https://docs.railway.app
- Status: https://status.railway.app

### Our Alternatives
- Render: Already configured with `render.yaml`
- Fly.io: Dockerfile ready in `backend/`
- Vercel: Next.js ready to deploy

---

**Remember**: If Railway takes more than 15 minutes to fix, switch to Render.com. Time is money! 💰
# 🚀 Railway Cache Clear - Quick Summary

## Your Issue
Railway is stuck deploying old `main.py` instead of new `main_minimal.py`

## Fastest Solution (2 minutes)

### Step 1: Login to Railway
https://railway.app → Login → Select "threadr" project

### Step 2: Clear Cache
1. Click your service box
2. Click **Settings** tab
3. Scroll to **Danger Zone** (red section)
4. Click **Clear Build Cache**
5. Confirm by clicking **Clear Cache** in popup

### Step 3: Redeploy
1. Click **Deployments** tab
2. Find latest deployment
3. Click **⋮** (three dots) → **Redeploy**

### Step 4: Verify in Logs
Look for this line in build logs:
```
exec uvicorn src.main_minimal:app
```

NOT this:
```
exec uvicorn src.main:app
```

## Quick Test (After Deploy)
```bash
curl https://threadr-production.up.railway.app/
```

Should return:
```json
{
  "app": "Threadr Minimal",
  "version": "1.0.0"
}
```

## If Cache Clear Fails

### Option 1: Force with Variable (1 min)
1. Go to **Variables** tab
2. Add: `FORCE_DEPLOY = timestamp`
3. Delete after deploy starts

### Option 2: Git Force (2 min)
```bash
cd C:\Users\HoshitoPowell\Desktop\Threadr
python scripts/force_railway_rebuild.py
```

### Option 3: Deploy to Render (5 min)
1. Go to render.com
2. Connect GitHub
3. It auto-deploys!

## Verification Script
```bash
python scripts/verify_railway_cache_clear.py
```

## Time: 2-5 minutes total

---
**Need help?** All methods documented in:
- `RAILWAY_CACHE_CLEAR_GUIDE.md` (detailed steps)
- `RAILWAY_VISUAL_CHECKLIST.md` (visual guide)
- `RAILWAY_TROUBLESHOOTING.md` (if things go wrong)
# ⚠️ MANUAL ACTION REQUIRED ON RENDER DASHBOARD

## Critical Issue Found
**render.yaml was in .gitignore**, preventing Render from seeing our configuration file. This has been fixed in commit `a05f5d1`.

## Why Manual Action May Be Required
Render.com has a known issue where **manual dashboard configurations override render.yaml Blueprint configurations**. Since the service was initially created without a Blueprint, the dashboard settings are likely taking precedence.

## 🔴 IMMEDIATE ACTION STEPS

### Step 1: Go to Render Dashboard
1. Open https://dashboard.render.com
2. Navigate to your `threadr-backend` service

### Step 2: Force Blueprint Sync
Look for one of these options:
- **"Blueprint"** section in the service settings
- **"Infrastructure as Code"** tab
- **"Sync Blueprint"** button
- **"Redeploy with Blueprint"** button

Click it to force Render to use the render.yaml configuration.

### Step 3: If No Blueprint Option Available
Manually update the service configuration:

1. Go to **Settings** → **Environment**
2. Update the **Start Command** to:
   ```
   uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info
   ```
3. Verify these environment variables are set:
   - `PYTHON_VERSION`: 3.11.9
   - `PYTHONUNBUFFERED`: 1
   - `ENVIRONMENT`: production
   - `PYTHONPATH`: /opt/render/project/src/backend
   - `OPENAI_API_KEY`: (your key)
   - `REDIS_URL`: (your Redis URL)
   - `STRIPE_SECRET_KEY`: (your Stripe key)

4. Click **Save Changes**
5. Click **Manual Deploy** → **Deploy latest commit**

## 🎯 How to Verify Success

After deployment completes, run this test:
```bash
curl https://threadr-pw0s.onrender.com/health
```

### ❌ If you see this (WRONG):
```json
{"status":"healthy","app":"minimal","timestamp":"..."}
```

### ✅ You should see this (CORRECT):
```json
{
  "status": "healthy",
  "timestamp": "...",
  "environment": "production",
  "services": {
    "redis": true,
    "database": false,
    "routes": true
  }
}
```

## 📝 What Changed in Our Fix

1. **render.yaml moved to repository root** ✅
2. **render.yaml removed from .gitignore** ✅
3. **Correct startCommand pointing to main.py** ✅
4. **Fixed PYTHONPATH for imports** ✅
5. **All required environment variables specified** ✅

## 🚨 If Still Having Issues

1. **Clear Build Cache**:
   - Settings → Build & Deploy → Clear build cache
   - Trigger a new deployment

2. **Check Build Logs**:
   - Look for "Using render.yaml" in the build logs
   - Verify it's running `uvicorn src.main:app`
   - NOT `uvicorn src.main_minimal:app`

3. **Verify Git Sync**:
   - Make sure latest commit `a05f5d1` is deployed
   - Check "Events" tab for deployment status

## 📞 Next Steps After Manual Sync

Once the correct backend is running:
1. Run full test suite: `python scripts/health-checks/test_full_backend.py`
2. Test OpenAI integration
3. Test Redis rate limiting
4. Test Stripe webhooks
5. Verify frontend can connect

## Time Estimate
- Manual sync: 1 minute
- Deployment: 3-5 minutes
- Verification: 2 minutes

**Total: ~8 minutes to full functionality**
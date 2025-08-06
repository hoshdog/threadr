# Render.com Deployment Fix - Action Plan

## Issue Summary
Render.com is still running the minimal app (`main_minimal.py`) despite having the correct `render.yaml` configuration pointing to the full app (`src.main:app`). Health check returns `{"app": "minimal"}` instead of the full Threadr API.

## Root Cause
**Dashboard Configuration Override**: Render.com has a known issue where manual dashboard configurations take precedence over `render.yaml` Blueprint configurations. This is why the service continues using the old start command even after updating the YAML file.

## Changes Applied ✅

### 1. Fixed .gitignore
- **Issue**: `render.yaml` was in `.gitignore` so Render couldn't detect it
- **Fix**: Removed `render.yaml` from `.gitignore` and committed to git
- **Result**: Render Blueprint can now read the configuration file

### 2. Updated render.yaml Configuration
- **File**: `render.yaml` (now in repository root)
- **Key Changes**:
  ```yaml
  startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info
  PYTHONPATH: /opt/render/project/src/backend:/opt/render/project/src/backend/src
  ```
- **Result**: Points to full app (`main.py`) instead of minimal (`main_minimal.py`)

### 3. Committed and Pushed Changes
- **Commit**: `a05f5d1` - "CRITICAL: Fix Render.com deployment to use full app instead of minimal"
- **Status**: Pushed to `main` branch, should trigger auto-deployment

## Required Manual Actions in Render Dashboard

### Step 1: Force Blueprint Sync
1. Go to your Render Dashboard: https://dashboard.render.com/
2. Navigate to your "threadr-backend" service
3. Look for "Blueprint" or "Infrastructure as Code" section
4. Click **"Sync Blueprint"** or **"Redeploy with Blueprint"**
5. This forces Render to use the `render.yaml` configuration instead of cached dashboard settings

### Step 2: Verify Configuration Override (If Step 1 Fails)
If Blueprint sync doesn't work, manually override in dashboard:

1. **Go to Service Settings**:
   - Navigate to your service → Settings → Environment
   
2. **Check Start Command**:
   - Look for "Start Command" setting
   - If it shows `uvicorn src.main_minimal:app` or similar
   - Change it to: `uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info`

3. **Verify Environment Variables**:
   - Ensure `ENVIRONMENT=production`
   - Ensure `PYTHONUNBUFFERED=1`
   - Add `PYTHONPATH=/opt/render/project/src/backend:/opt/render/project/src/backend/src`

4. **Trigger Manual Deploy**:
   - Click "Deploy Latest Commit" or "Manual Deploy"

### Step 3: Alternative - Recreate Service from Blueprint
If dashboard overrides persist:

1. **Create New Blueprint Service**:
   - Dashboard → "New" → "Blueprint"
   - Connect to your GitHub repository
   - Select `main` branch
   - Render will read `render.yaml` from repository root

2. **Delete Old Service** (after new one works):
   - This ensures no dashboard configuration conflicts

## Verification Steps

### 1. Check Deployment Logs
- Monitor Render build logs for:
  ```
  Starting command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
  ```
- Should NOT show `main_minimal.py` anywhere

### 2. Test Health Endpoint
After deployment completes:
```bash
curl https://your-render-app-url.onrender.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "app": "Threadr API",  // NOT "minimal"
  "version": "1.0.0",
  "environment": "production"
}
```

### 3. Test API Endpoints
Verify full API functionality:
```bash
# Test thread generation
curl -X POST https://your-render-app-url.onrender.com/api/generate \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content for thread generation"}'
```

## Common Issues & Solutions

### Issue 1: "Blueprint Not Found"
- **Cause**: `render.yaml` not in repository root or not committed
- **Solution**: Ensure file is committed to `main` branch ✅ (Done)

### Issue 2: "Configuration Not Applied"
- **Cause**: Dashboard overrides Blueprint
- **Solution**: Manual Blueprint sync or dashboard configuration update

### Issue 3: "Python Module Not Found"
- **Cause**: Incorrect `PYTHONPATH` configuration
- **Solution**: Verify `PYTHONPATH` includes both backend directories ✅ (Fixed)

### Issue 4: "Service Still Running Minimal App"
- **Cause**: Render caching old configuration
- **Solution**: Force redeploy or recreate service from Blueprint

## Render.yaml Configuration Explained

```yaml
services:
  - type: web
    name: threadr-backend           # Service name in Render
    runtime: python                 # Python runtime
    plan: free                     # Free tier
    rootDir: backend               # Run from /backend directory
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info
    # ↑ This points to main.py (full app) NOT main_minimal.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: PYTHONUNBUFFERED      # Ensure Python output is unbuffered
        value: "1"
      - key: ENVIRONMENT           # Set production environment
        value: production
      - key: PYTHONPATH            # Enable imports from src/ directory
        value: /opt/render/project/src/backend:/opt/render/project/src/backend/src
    autoDeploy: true               # Auto-deploy on git push
```

## Next Steps

1. **Monitor Auto-Deploy**: Check if the git push triggered a deployment
2. **Force Blueprint Sync**: If auto-deploy doesn't fix it, manually sync Blueprint
3. **Verify Health Check**: Confirm API returns full app response, not minimal
4. **Test Full Functionality**: Ensure thread generation and all endpoints work

## Success Criteria ✅

- [ ] Health endpoint returns `"app": "Threadr API"` not `"minimal"`
- [ ] All API endpoints functional (`/api/generate`, `/api/capture-email`, etc.)
- [ ] Deployment logs show `uvicorn src.main:app` not `main_minimal`
- [ ] Production environment variables loaded correctly
- [ ] No import errors in application startup

---

**Status**: Configuration fixes applied and pushed. Awaiting Render deployment update.
**ETA**: 5-10 minutes for auto-deployment, or immediate with manual Blueprint sync.
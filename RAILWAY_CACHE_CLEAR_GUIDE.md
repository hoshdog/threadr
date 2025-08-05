# 🚨 Railway Cache Clear Guide - COMPLETE INSTRUCTIONS

## Your Current Issue
Railway is deploying the OLD `main.py` instead of NEW `main_minimal.py` specified in nixpacks.toml

## Method 1: Dashboard Cache Clear (RECOMMENDED)

### Step 1: Login to Railway
1. Go to https://railway.app
2. Click "Login" (top right)
3. Login with GitHub/Email

### Step 2: Navigate to Your Project
1. Click on "threadr" project (or your project name)
2. You should see your services listed

### Step 3: Access Project Settings
1. Click on your backend service (likely named "threadr-production" or similar)
2. Look for tabs at the top: **Deployments | Settings | Metrics | Logs**
3. Click **"Settings"** tab

### Step 4: Clear Build Cache
1. Scroll down to find **"Danger Zone"** section (red bordered area)
2. Look for **"Clear Build Cache"** button
3. Click **"Clear Build Cache"**
4. A modal will appear saying "Are you sure?"
5. Click **"Clear Cache"** to confirm

### Step 5: Trigger New Deployment
1. Go back to **"Deployments"** tab
2. Find the latest deployment (should show as failed or old)
3. Click the **three dots (...)** menu on the right
4. Select **"Redeploy"**
5. Confirm redeployment

### Step 6: Monitor Build Logs
1. Click on the new deployment that starts
2. Click **"View Logs"**
3. **CRITICAL**: Look for these lines:
   ```
   Using main_minimal.py for deployment
   cmd = "exec uvicorn src.main_minimal:app
   ```
   
If you see `main.py` instead, the cache clear didn't work - try Method 2.

## Method 2: Force Rebuild via Environment Variable

### Step 1: Add Dummy Environment Variable
1. In Railway dashboard → Your Service → **Variables** tab
2. Click **"+ New Variable"**
3. Add:
   - Key: `FORCE_REBUILD`
   - Value: `2025-08-06-rebuild`
4. Click **"Add"**

This forces Railway to rebuild because environment changed.

### Step 2: Remove and Re-add
1. After deployment starts, delete the `FORCE_REBUILD` variable
2. This keeps your environment clean

## Method 3: Railway CLI Method

### Install Railway CLI (if not installed)
```bash
npm install -g @railway/cli
```

### Clear Cache via CLI
```bash
# Login to Railway
railway login

# Link to your project
railway link

# Get project ID
railway status

# Clear cache and redeploy
railway up --force
```

## Method 4: Nuclear Option - Delete and Recreate Service

### If all else fails:
1. **Export your environment variables first!**
   - Go to Variables tab
   - Copy all your env vars to a text file

2. **Delete the service**
   - Settings → Danger Zone → Delete Service
   - Type service name to confirm

3. **Create new service**
   - Click "New Service"
   - Choose "Deploy from GitHub Repo"
   - Select your repo and branch
   - Re-add all environment variables

## Verification Checklist ✅

After redeployment, verify with these commands:

### 1. Check Health Endpoint
```bash
curl https://threadr-production.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "app": "minimal",
  "timestamp": "2025-08-06T..."
}
```

### 2. Check Root Endpoint
```bash
curl https://threadr-production.up.railway.app/
```

Should return:
```json
{
  "app": "Threadr Minimal",
  "version": "1.0.0",
  "deployment": "main_minimal.py"
}
```

### 3. Test Generate Endpoint
```bash
curl -X POST https://threadr-production.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"content": "Test thread generation"}'
```

Should return generated tweets, not an error.

## Common Issues & Solutions

### Issue 1: Still seeing old deployment
**Solution**: Railway might be caching at service level
- Try changing the start command slightly in nixpacks.toml:
  ```toml
  cmd = "exec uvicorn src.main_minimal:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info --reload"
  ```
  (Added --reload flag temporarily)

### Issue 2: Build succeeds but wrong file
**Solution**: Check if Railway is overriding nixpacks.toml
- Go to Settings → Check for "Start Command" override
- Remove any custom start command
- Ensure "Use nixpacks.toml" is selected

### Issue 3: GitHub sync issues
**Solution**: Force GitHub webhook
1. Go to GitHub → Your repo → Settings → Webhooks
2. Find Railway webhook
3. Click "Recent Deliveries"
4. Click "Redeliver" on latest

### Issue 4: nixpacks.toml not being read
**Solution**: Ensure it's in root directory
```bash
# Your file structure should be:
/
├── nixpacks.toml          # ← Must be here
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── main_minimal.py
│   │   └── ...
│   └── requirements.txt
└── ...
```

## Quick Verification Script

Save this as `verify_railway.sh`:
```bash
#!/bin/bash
echo "Checking Railway Deployment..."
echo "=============================="

URL="https://threadr-production.up.railway.app"

echo -n "1. Health Check: "
curl -s "$URL/health" | grep -q "minimal" && echo "✅ PASS" || echo "❌ FAIL"

echo -n "2. Root Check: "
curl -s "$URL/" | grep -q "Threadr Minimal" && echo "✅ PASS" || echo "❌ FAIL"

echo -n "3. Generate Test: "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"content": "test"}')
[ "$STATUS" = "200" ] && echo "✅ PASS" || echo "❌ FAIL (Status: $STATUS)"

echo "=============================="
echo "If all PASS, deployment successful!"
```

## Emergency Contacts

### Railway Support
- Discord: https://discord.gg/railway
- Status Page: https://status.railway.app
- Docs: https://docs.railway.app

### Alternative Actions
If Railway continues to fail after all methods:
1. Deploy to Render.com (5 minutes)
2. Deploy to Fly.io (10 minutes)
3. Contact Railway support with deployment ID

## Success Indicators 🎯

You'll know it worked when:
1. Build logs show: `Using main_minimal.py`
2. Health endpoint returns: `"app": "minimal"`
3. No more 503 errors
4. Thread generation works

---

**IMPORTANT**: After clearing cache, always check build logs immediately. If you don't see "main_minimal.py" mentioned, the cache clear didn't take effect.
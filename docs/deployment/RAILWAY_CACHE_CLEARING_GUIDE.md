# Railway Cache Clearing Guide - COMPREHENSIVE

**CRITICAL SITUATION**: Railway is deploying old version (main.py) instead of new version (main_minimal.py) specified in nixpacks.toml

## Current Deployment Issue

**Problem**: Railway deployment cache is stuck, ignoring nixpacks.toml changes
- **Expected**: `src.main_minimal:app` (ultra-minimal FastAPI app)
- **Actual**: Old main.py deployment with complex dependencies
- **Evidence**: Build logs still reference old file structure
- **Impact**: Deployment failures due to cached configuration

## Method 1: Railway Dashboard Cache Clear (PRIMARY METHOD)

### Step 1: Access Project Settings
1. **Navigate to Railway Dashboard**:
   - Go to https://railway.app/dashboard
   - Click on your "Threadr" project (or exact project name)
   - You should see the service overview page

2. **Access Service Settings**:
   - Look for your backend service (usually named "backend" or similar)
   - Click on the service name/card to enter service view
   - In the top navigation bar, look for "Settings" tab
   - Click "Settings" (should be rightmost tab after Deploy, Metrics, etc.)

### Step 2: Clear Build Cache
1. **Locate Cache Section**:
   - Scroll down in Settings until you find "Danger Zone" section
   - Look for "Clear Build Cache" or "Reset Build Cache" button
   - **Button Text**: Usually says "Clear Build Cache" with red background

2. **Execute Cache Clear**:
   - Click the "Clear Build Cache" button
   - **Confirmation Dialog**: A modal will appear asking "Are you sure?"
   - Click "Clear Cache" or "Confirm" to proceed
   - **Expected Result**: You should see "Build cache cleared" notification

### Step 3: Force Fresh Deployment
1. **Trigger New Deployment**:
   - Go back to "Deploy" tab
   - Look for "Deploy Latest" or "Redeploy" button (usually blue)
   - Click to trigger fresh deployment
   - **Alternative**: Make a dummy commit and push to trigger auto-deploy

2. **Monitor Build Logs**:
   - Click on the new deployment in the deployment list
   - Watch build logs in real-time
   - **Look for**: `"Using main_simple.py for deployment"` message
   - **Look for**: `exec uvicorn src.main_minimal:app` in start command

## Method 2: CLI Cache Clear (SECONDARY METHOD)

### Prerequisites
1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   # OR
   brew install railway
   ```

2. **Login and Connect**:
   ```bash
   railway login
   railway link  # Select your Threadr project
   ```

### Cache Clear Commands
```bash
# Method 2A: Environment reset
railway environment reset

# Method 2B: Service redeploy with fresh build
railway redeploy --detach

# Method 2C: Force rebuild from scratch
railway up --detach --force
```

### Verify CLI Success
```bash
# Check deployment status
railway status

# View recent deployments
railway logs
```

## Method 3: Project-Level Reset (NUCLEAR OPTION)

### When to Use
- Dashboard cache clear failed
- CLI methods failed
- Multiple failed deployments in a row
- Build environment seems corrupted

### Steps
1. **Access Project Settings**:
   - Go to Railway Dashboard → Your Project
   - Click "Settings" at project level (not service level)
   - Look for "Advanced" or "Danger Zone" section

2. **Environment Reset**:
   - Find "Reset Environment" button
   - **WARNING**: This will reset ALL services in the project
   - Click and confirm when prompted
   - **Confirmation Text**: Usually requires typing project name

3. **Complete Redeployment**:
   - After reset, redeploy all services
   - Environment variables will need to be re-added
   - Custom domains will need to be reconfigured

## Method 4: Git-Based Force Deploy

### Technique 1: Dummy Commit
```bash
# Make a small change to force new build
echo "# Force rebuild $(date)" >> .railway-rebuild
git add .railway-rebuild
git commit -m "Force Railway rebuild with main_minimal.py"
git push origin main
```

### Technique 2: Re-push Same Commit
```bash
# Force push the same commit
git push --force-with-lease origin main

# OR delete and recreate the commit
git reset --soft HEAD~1
git commit -m "Deploy ultra-minimal backend (main_minimal.py) - CACHE CLEARED"
git push --force-with-lease origin main
```

## Verification Checklist

### Step 1: Check Build Logs
**Look for these EXACT strings in build logs**:
- ✅ `"Starting Python setup... (Updated 2025-08-05)"`
- ✅ `"Using main_simple.py for deployment"`
- ✅ `exec uvicorn src.main_minimal:app --host 0.0.0.0 --port $PORT`

**RED FLAGS in build logs**:
- ❌ References to old main.py
- ❌ Loading complex dependencies not in main_minimal.py
- ❌ WSGI server startup (should be uvicorn only)
- ❌ Missing the updated echo messages

### Step 2: Test Deployment Endpoint
```bash
# Test the root endpoint
curl https://your-railway-app.up.railway.app/

# Expected response for main_minimal.py:
{
  "app": "Threadr Minimal",
  "version": "1.0.0",
  "deployment": "main_minimal.py",
  "timestamp": "2025-08-05T..."
}
```

### Step 3: Verify Configuration
**Check these deployment details**:
- ✅ Start command: `exec uvicorn src.main_minimal:app`
- ✅ Working directory: `backend`
- ✅ Python version: 3.11
- ✅ Build time: Should be under 2 minutes for minimal app

## Common Pitfalls and Solutions

### Pitfall 1: Multiple nixpacks.toml Files
**Problem**: Railway might be reading wrong nixpacks.toml
**Solution**:
```bash
# Check for multiple config files
find . -name "nixpacks.toml" -type f
find . -name "Procfile*" -type f
find . -name "railway.json" -type f

# Remove any duplicate configs
rm backend/nixpacks.toml  # If exists
rm backend/Procfile       # If exists
```

### Pitfall 2: Environment Variables Override
**Problem**: Railway environment variables might override nixpacks.toml
**Check**: Railway Dashboard → Service → Variables
**Solution**: Remove any variables that specify different start commands:
- Remove `CMD` or `COMMAND` variables
- Remove `PYTHONPATH` overrides
- Remove `WEB_CONCURRENCY` if not needed

### Pitfall 3: Cached Dependencies
**Problem**: Old requirements.txt cached, preventing fresh install
**Solution**: Update requirements.txt with comment:
```python
# Updated 2025-08-05 - Force cache refresh
fastapi==0.104.1
uvicorn==0.24.0
# ... other deps
```

### Pitfall 4: Service Detection Override
**Problem**: Railway auto-detects Python and ignores nixpacks.toml
**Solution**: Ensure these variables are set in Railway Dashboard:
```
NIXPACKS_PYTHON_WSGI_MODULE=""
DISABLE_COLLECTSTATIC=1
```

## Advanced Troubleshooting

### Debug Method 1: Build Cache Inspection
1. **Enable Build Debug**:
   - Railway Dashboard → Service → Settings
   - Find "Build Settings" or "Advanced"
   - Enable "Verbose Build Logs" if available

2. **Analyze Cache Behavior**:
   - Look for "Cache restored from" in logs
   - Check if old file paths are cached
   - Verify nixpacks.toml is being read

### Debug Method 2: Manual Build Verification
```bash
# Clone your repo to fresh directory
cd /tmp
git clone https://github.com/your-username/threadr.git fresh-threadr
cd fresh-threadr

# Test nixpacks locally (if installed)
nixpacks build . --name threadr-test

# Verify it uses main_minimal.py
docker run -p 8000:8000 threadr-test
curl localhost:8000  # Should show main_minimal response
```

### Debug Method 3: Railway API Direct Call
```bash
# Get auth token from Railway CLI
railway whoami

# Direct API call to trigger deployment
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  "https://backboard.railway.app/graphql/v2" \
  -d '{"query": "mutation { serviceRedeploy(serviceId: \"YOUR_SERVICE_ID\") { id } }"}'
```

## Alternative Deployment Strategies

### Strategy 1: Docker Override
**If nixpacks continues to fail, force Docker build**:

1. **Create Dockerfile in root**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
WORKDIR /app
CMD ["uvicorn", "src.main_minimal:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

2. **Railway Dashboard Settings**:
   - Go to Service → Settings
   - Find "Build Method" or "Source"
   - Change from "Nixpacks" to "Dockerfile"
   - Specify dockerfile path if needed

### Strategy 2: New Service Creation
**Last resort: Create entirely new Railway service**:

1. **Create New Service**:
   - Railway Dashboard → Project → "New Service"
   - Connect same GitHub repo
   - Different name (e.g., "threadr-minimal")

2. **Configure Fresh**:
   - Set environment variables
   - Configure custom domain
   - Update frontend API_BASE_URL
   - Delete old service after verification

## Success Indicators

### ✅ Cache Clear Successful
- Build logs show updated timestamp messages
- Start command references main_minimal.py
- Build time significantly reduced (under 2 minutes)
- No references to old dependencies in logs

### ✅ Deployment Working
- API responds with minimal app JSON
- Health endpoint returns minimal response
- Generate endpoint works with simple logic
- No 500 errors in application logs

### ✅ Configuration Applied
- Railway dashboard shows correct start command
- Environment variables properly set
- Build method shows "Nixpacks" (not auto-detected)
- Service URL responds correctly

## Emergency Rollback Plan

**If cache clearing breaks production**:

1. **Immediate Rollback**:
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Restore Previous Version**:
   - Railway Dashboard → Deployments
   - Find last working deployment
   - Click "Redeploy" on that version

3. **Restore nixpacks.toml**:
   ```bash
   git checkout HEAD~5 -- nixpacks.toml
   git commit -m "Restore working nixpacks.toml"
   git push origin main
   ```

## Contact Support

**If all methods fail**:
1. **Railway Discord**: https://discord.gg/railway
2. **Railway Support**: support@railway.app
3. **Include Information**:
   - Project ID
   - Service ID
   - Build logs from failed attempts
   - nixpacks.toml contents
   - Steps attempted

## Final Verification Script

```bash
#!/bin/bash
# Run this script to verify successful cache clear and deployment

echo "=== Railway Cache Clear Verification ==="
echo "1. Testing deployment endpoint..."

RESPONSE=$(curl -s https://your-railway-url.up.railway.app/)
echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "main_minimal.py"; then
    echo "✅ SUCCESS: Deployment using main_minimal.py"
else
    echo "❌ FAILURE: Still using old deployment"
fi

echo "2. Testing health endpoint..."
HEALTH=$(curl -s https://your-railway-url.up.railway.app/health)
echo "Health: $HEALTH"

echo "3. Testing generate endpoint..."
GENERATE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":"Test content for thread generation"}' \
  https://your-railway-url.up.railway.app/api/generate)
echo "Generate: $GENERATE"

echo "=== Verification Complete ==="
```

## Conclusion

This guide provides multiple redundant methods to clear Railway's deployment cache. Start with Method 1 (Dashboard), escalate to Method 2 (CLI), and use Method 3 (Nuclear Reset) only if necessary. Always verify the deployment is working before considering the cache clear successful.

**Remember**: The goal is to get Railway to deploy the main_minimal.py file as specified in nixpacks.toml, not the old main.py file that's causing issues.
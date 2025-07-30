# Railway Uvicorn Deployment Guide - BULLETPROOF Configuration

This guide ensures Railway deploys your FastAPI app with uvicorn, not gunicorn.

## The Problem
Railway's Python buildpack auto-detects web frameworks and often defaults to gunicorn, even when nixpacks.toml specifies uvicorn. This guide provides a bulletproof solution.

## Solution Overview
1. **Bulletproof nixpacks.toml** - Forces Railway to use uvicorn
2. **Clean configuration** - Removes conflicting files
3. **Explicit exclusions** - Prevents gunicorn detection
4. **Environment variables** - Overrides Railway defaults

## Files Modified

### 1. nixpacks.toml (Root Directory)
```toml
# BULLETPROOF Railway Nixpacks Configuration
# This configuration FORCES Railway to use uvicorn, not gunicorn
# DO NOT MODIFY - Any changes may cause Railway to revert to gunicorn

# Force Python provider and disable auto-detection
[providers]
python = "3.11"

# Set working directory to backend subdirectory
# This eliminates the need for 'cd backend' commands
[phases.build]
workDir = "backend"

# Setup phase - install dependencies
[phases.setup]
workDir = "backend"
cmds = [
  "echo 'Installing Python dependencies...'",
  "pip install --upgrade pip",
  "pip install --no-cache-dir -r requirements.txt",
  "echo 'Dependencies installed successfully'"
]

# Start command - EXPLICIT uvicorn with full path
# Using exec to ensure proper signal handling
[start]
workDir = "backend"
cmd = "exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2 --log-level info --access-log"

# Environment variables to prevent gunicorn detection
[variables]
PYTHONUNBUFFERED = "1"
ENVIRONMENT = "production"
# Force nixpacks to use uvicorn
NIXPACKS_PYTHON_WSGI_MODULE = ""
# Disable gunicorn auto-detection
DISABLE_COLLECTSTATIC = "1"
# Force uvicorn as the server
WEB_CONCURRENCY = "2"
```

### 2. backend/requirements.txt
```txt
# Production requirements.txt for Railway FastAPI deployment
# IMPORTANT: Do not add gunicorn - this app uses uvicorn only

# Core FastAPI requirements
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Basic request handling
httpx==0.26.0
pydantic==2.5.3

# Request handling
python-multipart==0.0.6

# Essential for our app
openai>=1.10.0
beautifulsoup4>=4.12.3
python-dotenv>=1.0.0

# EXPLICITLY EXCLUDE gunicorn to prevent Railway auto-detection
# gunicorn  # DO NOT UNCOMMENT - Railway will use this if present
```

## Deployment Steps

### Step 1: Clear Railway Cache
1. Go to your Railway project dashboard
2. Click on Settings → Danger Zone
3. Click "Reset Build Cache"
4. Confirm the reset

### Step 2: Force New Deployment
1. Make a small commit to trigger deployment:
   ```bash
   git add .
   git commit -m "Force uvicorn deployment - updated nixpacks config"
   git push
   ```

### Step 3: Monitor Deployment
1. Watch the build logs in Railway dashboard
2. Look for these success indicators:
   - `Installing Python dependencies...`
   - `Dependencies installed successfully`
   - `exec uvicorn main:app --host 0.0.0.0 --port $PORT`
   - NO mention of gunicorn

### Step 4: Verify Health Endpoints
After deployment, test these endpoints:
- `https://your-app.railway.app/health`
- `https://your-app.railway.app/readiness`
- `https://your-app.railway.app/debug/startup`

## Key Configuration Explained

### Why This Works
1. **workDir = "backend"** - Sets context properly, eliminates `cd backend` conflicts
2. **exec uvicorn** - Ensures proper process management and signal handling
3. **NIXPACKS_PYTHON_WSGI_MODULE = ""** - Disables WSGI auto-detection
4. **Explicit providers** - Forces Python 3.11, prevents auto-detection
5. **No Procfile** - Eliminates conflicting deployment instructions

### Environment Variables Explained
- `PYTHONUNBUFFERED = "1"` - Ensures real-time logging
- `ENVIRONMENT = "production"` - Sets production mode
- `NIXPACKS_PYTHON_WSGI_MODULE = ""` - Disables WSGI detection
- `DISABLE_COLLECTSTATIC = "1"` - Prevents Django-style static collection
- `WEB_CONCURRENCY = "2"` - Controls worker count

## Troubleshooting

### If Railway Still Uses Gunicorn

1. **Check for hidden files:**
   ```bash
   find . -name "*Procfile*" -o -name "*railway*" -o -name "*gunicorn*"
   ```

2. **Verify no other config files exist:**
   - Remove any `Procfile` in backend/
   - Remove any `railway.json` files
   - Remove any `start.sh` scripts that mention gunicorn

3. **Force cache clear:**
   - Delete and recreate the Railway service
   - Or use Railway CLI: `railway service delete` and redeploy

### Common Issues

**Issue:** "ModuleNotFoundError: No module named 'main'"
**Solution:** Ensure workDir is set correctly in nixpacks.toml

**Issue:** "Port already in use"
**Solution:** Make sure only one process is running, using exec in start command

**Issue:** "Health check fails"
**Solution:** Verify your app starts on `0.0.0.0:$PORT`, not localhost

## Success Indicators

Your deployment is successful when you see:
1. Build logs show `exec uvicorn main:app`
2. No mention of gunicorn in any logs
3. Health endpoint returns 200 OK
4. App responds correctly to requests

## Emergency Fallback

If all else fails, you can deploy using a Dockerfile instead:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE $PORT

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT", "--workers", "2"]
```

Then set Railway to use Docker builds in project settings.

## Support

If you continue having issues:
1. Check Railway build logs for exact error messages
2. Verify nixpacks.toml syntax with online TOML validators
3. Test locally with: `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Contact Railway support with this configuration as reference

## Final Notes

- Never add gunicorn to requirements.txt
- Always use `exec` in start commands for proper signal handling
- Keep nixpacks.toml minimal and explicit
- Monitor first deployment carefully to ensure uvicorn is used
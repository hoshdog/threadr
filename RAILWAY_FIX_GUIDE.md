# Railway Gunicorn to Uvicorn Fix Guide

## Problem Summary
Railway was deploying with gunicorn despite nixpacks.toml specifying uvicorn, causing "/bin/sh: 1: gunicorn: not found" errors.

## Root Causes Identified and Fixed

### 1. ✅ Multiple Configuration Files
**Issue**: Railway found gunicorn references in multiple files and auto-detected it as the preferred server.
**Fixed**: 
- Removed `gunicorn==21.2.0` from `backend/pyproject.toml`
- Removed `gunicorn==21.2.0` from `requirements_minimal.txt`
- Disabled backup nixpacks files: `nixpacks_backup.toml.disabled`, `nixpacks_simplified.toml.disabled`, `nixpacks_minimal.toml.disabled`

### 2. ✅ Dockerfile Gunicorn References
**Issue**: Dockerfile contained gunicorn CMD, providing fallback option Railway might use.
**Fixed**: Updated Dockerfile to use uvicorn consistently with nixpacks.toml

### 3. ✅ Configuration Comments
**Issue**: Comments containing "gunicorn" might confuse Railway's auto-detection.
**Fixed**: Cleaned up all comments to avoid mentioning alternative servers.

### 4. ✅ Environment Variables
**Added**: Railway-specific environment variables to force uvicorn:
```toml
RAILWAY_NO_GUNICORN = "true"
NIXPACKS_PYTHON_WSGI_MODULE = ""
```

## Current Configuration

### Active Files:
- **nixpacks.toml**: ✅ Uses uvicorn only
- **backend/requirements.txt**: ✅ Contains uvicorn, no gunicorn
- **backend/pyproject.toml**: ✅ Contains uvicorn, no gunicorn
- **Dockerfile**: ✅ Uses uvicorn for Docker fallback

### Disabled Files:
- `nixpacks_backup.toml.disabled`
- `nixpacks_simplified.toml.disabled`
- `nixpacks_minimal.toml.disabled`

## Railway Deployment Steps

### 1. Clear Railway Build Cache
Railway may still be using cached configuration with gunicorn references.

**Options:**
- **Option A**: Trigger a fresh deployment
  ```bash
  # Make a small change to force rebuild
  git commit --allow-empty -m "Force Railway cache clear - use uvicorn only"
  git push
  ```

- **Option B**: In Railway dashboard:
  1. Go to your project settings
  2. Click "Variables" tab
  3. Add temporary variable: `FORCE_REBUILD=1`
  4. Deploy
  5. Remove the variable after successful deployment

### 2. Verify Railway Logs
After deployment, check Railway logs for these indicators:

**✅ Success Indicators:**
```
INFO: Started server process
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:[PORT]
```

**❌ Failure Indicators:**
```
/bin/sh: 1: gunicorn: not found
ModuleNotFoundError: No module named 'gunicorn'
```

### 3. Environment Variables Check
Verify these environment variables are set in Railway:
- `PYTHONUNBUFFERED=1`
- `ENVIRONMENT=production`
- `RAILWAY_NO_GUNICORN=true` (automatically set by nixpacks.toml)

### 4. Build Process Verification
Railway should show these steps in build logs:
1. ✅ Detecting Python app
2. ✅ Using nixpacks.toml configuration
3. ✅ Installing dependencies from backend/requirements.txt
4. ✅ Starting with: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Troubleshooting Commands

### If Deployment Still Fails:

1. **Check for remaining gunicorn references:**
   ```bash
   python verify_railway_config.py
   ```

2. **Force Railway to use nixpacks:**
   Add to Railway environment variables:
   ```
   NIXPACKS_NO_GUNICORN=true
   ```

3. **Verify local uvicorn works:**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Check Railway build method:**
   In Railway dashboard, ensure build method is set to "nixpacks" (not Docker).

## Expected Results

After applying these fixes:
- ✅ Railway uses nixpacks.toml configuration
- ✅ Deployment starts with uvicorn, not gunicorn
- ✅ No "gunicorn: not found" errors
- ✅ FastAPI app starts successfully
- ✅ Health checks pass

## Monitoring

After successful deployment, monitor for:
- Application startup time (should be faster with uvicorn)
- Memory usage (should be lower without gunicorn overhead)
- Response times (should be consistent)

## Files Modified
- `C:\Users\HoshitoPowell\Desktop\Threadr\backend\pyproject.toml`
- `C:\Users\HoshitoPowell\Desktop\Threadr\requirements_minimal.txt`
- `C:\Users\HoshitoPowell\Desktop\Threadr\nixpacks.toml`
- `C:\Users\HoshitoPowell\Desktop\Threadr\Dockerfile`
- `C:\Users\HoshitoPowell\Desktop\Threadr\backend\requirements.txt`

## Next Steps
1. Deploy to Railway and monitor logs
2. Verify health endpoint responds correctly
3. Test API endpoints functionality
4. Remove temporary debugging variables if added
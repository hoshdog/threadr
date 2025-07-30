# Railway 502 Error Fix Guide

## Problem
Your Railway deployment at https://threadr-production.up.railway.app is returning 502 "Application failed to respond" errors.

## Root Cause Analysis
Based on the code analysis, the most likely causes are:
1. **Working directory resolution** (80% likely) - Railway not finding main.py in the backend directory
2. **Port binding issues** (15% likely) - PORT environment variable not being passed correctly
3. **Import/startup errors** (5% likely) - Missing dependencies or OpenAI configuration

## Immediate Fix Steps

### Step 1: Apply Updated Configuration ✅ COMPLETED
The nixpacks.toml has been updated with:
- Explicit Python module invocation: `python -m uvicorn`
- Proper port variable expansion: `${PORT:-8000}`
- Single worker for stability: `--workers 1`
- Debug logging: `--log-level debug`
- Extended timeout: `--timeout-keep-alive 30`

### Step 2: Debug Current Deployment
Run these commands to identify the exact issue:

```bash
# Check Railway logs for startup errors
railway logs --tail 100

# View environment variables
railway variables

# Test in Railway shell environment
railway shell
cd backend
python -c "import main; print('Import successful')"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

### Step 3: Deploy Fixed Configuration

```bash
# Deploy with updated nixpacks.toml
railway up

# Monitor deployment logs
railway logs --follow
```

### Step 4: Test Health Endpoints
Once deployed, test these endpoints:
- https://threadr-production.up.railway.app/health
- https://threadr-production.up.railway.app/readiness
- https://threadr-production.up.railway.app/debug/startup

## Fallback Configuration

If the main fix doesn't work, use the fallback configuration:

```bash
# Use the fallback nixpacks configuration
cp nixpacks_fallback.toml nixpacks.toml
railway up
```

## Key Changes Made

### 1. nixpacks.toml Updates
- Changed from `uvicorn main:app` to `python -m uvicorn main:app`
- Fixed port variable: `$PORT` → `${PORT:-8000}`
- Reduced workers: `--workers 2` → `--workers 1`
- Added debug logging and extended timeouts
- Set PYTHONPATH environment variable

### 2. main.py Enhancements
- Enhanced startup logging for better debugging
- Single worker configuration for production
- Better error handling in lifespan events

### 3. Debug Tools Created
- `railway_debug_502.py` - Local testing script
- `nixpacks_fallback.toml` - Alternative configuration
- `RAILWAY_502_FIX_GUIDE.md` - This guide

## Environment Variables Required

Ensure these are set in Railway:
- `PORT` (automatically set by Railway)
- `ENVIRONMENT=production` (set in nixpacks.toml)
- `OPENAI_API_KEY` (optional - app works without it)

## Testing Commands

### Local Testing
```bash
# Run the debug script
python railway_debug_502.py

# Manual test
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

### Railway Testing
```bash
# Test health endpoint
curl https://threadr-production.up.railway.app/health

# Test basic API
curl https://threadr-production.up.railway.app/api/test
```

## Expected Success Indicators

After successful deployment, you should see:
1. **200 OK** response from health endpoints
2. **Startup logs** showing "Threadr backend startup completed successfully"
3. **API endpoints** responding correctly
4. **No 502 errors** when accessing the application

## Troubleshooting

If the fixes don't work:

1. **Check Railway logs** for specific error messages
2. **Verify working directory** - ensure Railway is in the correct directory
3. **Test imports** - verify all dependencies are installed correctly
4. **Check port binding** - ensure Railway's PORT variable is being used
5. **Try minimal config** - use nixpacks_fallback.toml for simplest setup

## Next Steps

1. Deploy the updated configuration
2. Monitor logs during startup
3. Test all health endpoints
4. Verify API functionality
5. Update any client applications to use the working endpoints

The updated configuration should resolve the 502 errors. The key fix is using `python -m uvicorn` with proper working directory handling and reduced worker count for Railway's environment.
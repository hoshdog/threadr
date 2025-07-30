# Railway Health Check Fixes

## Issues Identified and Fixed

### 1. OpenAI API Key Startup Dependency
**Problem**: App was crashing at startup if OpenAI API key wasn't configured
**Fix**: Made OpenAI optional - app starts but disables AI features if not configured

### 2. Gunicorn Configuration Issues
**Problem**: Incorrect gunicorn configuration causing port binding failures
**Fix**: Updated gunicorn command with proper parameters:
- Single worker (Railway limitation)
- Proper timeout settings (120s)
- Correct logging configuration

### 3. Health Check Timeout
**Problem**: Default 30s timeout too short for cold starts
**Fix**: Increased to 60s and enhanced health endpoint with diagnostics

### 4. Enhanced Health Check Endpoint
**Fix**: Added detailed health information including:
- Environment status
- Port configuration
- OpenAI availability
- Timestamp and version info

## Quick Deployment Steps

### Step 1: Verify Environment Variables
In Railway dashboard, ensure these are set:
```
ENVIRONMENT=production
OPENAI_API_KEY=your_key_here (optional but recommended)
```

### Step 2: Deploy with Fixed Configuration
1. Push all changes to your repo
2. Railway will auto-deploy using the updated nixpacks.toml
3. Check logs for detailed startup information

### Step 3: Test Health Endpoint
Once deployed, test:
```bash
curl https://your-railway-url/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T10:01:10.764980",
  "version": "1.0.0",
  "environment": "production",
  "port": "8000",
  "services": {
    "api": "healthy",
    "openai": "configured"
  }
}
```

### Step 4: Monitor Deployment Logs
Watch Railway logs during deployment:
```bash
railway logs --tail
```

Look for these success indicators:
- `Starting Threadr backend in production mode...`
- `OpenAI client initialized successfully` (if API key provided)
- `Production startup checks passed`
- `Health check passed: {...}`

## Debugging Commands

### Run Local Debug Script
```bash
cd backend
python debug_start.py
```

### Test Locally
```bash
cd backend
export PORT=8000
export ENVIRONMENT=production
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Check Railway Logs
```bash
railway logs
```

## Common Issues and Solutions

### Issue: "service unavailable"
- **Cause**: App not binding to correct port
- **Solution**: Ensure $PORT environment variable is used

### Issue: "1/1 replicas never became healthy"
- **Cause**: Health check failing or timing out
- **Solution**: Check /health endpoint returns 200 OK

### Issue: OpenAI errors in logs
- **Cause**: Missing OPENAI_API_KEY
- **Solution**: Set environment variable or app will use fallback

### Issue: Import errors
- **Cause**: Missing dependencies
- **Solution**: Check requirements.txt and Railway build logs

## Files Modified

1. `backend/main.py` - Fixed OpenAI dependency and enhanced health check
2. `nixpacks.toml` - Updated gunicorn configuration
3. `railway.toml` - Increased health check timeout
4. `backend/debug_start.py` - NEW: Debug script
5. `backend/start.sh` - NEW: Emergency start script
6. `backend/requirements.txt` - Added testing dependency

## Next Steps

1. Deploy and monitor Railway logs
2. Test health endpoint after deployment
3. If still failing, run debug script locally first
4. Check Railway dashboard for specific error messages

## Emergency Fallback

If gunicorn still fails, Railway can fallback to:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Add this as startCommand in railway.toml if needed.
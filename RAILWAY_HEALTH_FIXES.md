# Railway Health Check Fixes

## Issues Fixed

### 1. **Startup Failures Due to OpenAI Initialization**
- **Problem**: App was failing to start if OpenAI API key was missing or invalid
- **Fix**: Added graceful degradation with `openai_available` flag
- **Result**: App starts successfully even without OpenAI, using fallback methods

### 2. **Health Check Reliability**
- **Problem**: Health checks might fail due to OpenAI dependency
- **Fix**: Health endpoint always returns 200 OK if app is responding
- **Result**: Railway correctly identifies healthy replicas

### 3. **Startup Timing and Logging**
- **Problem**: Limited visibility into startup issues
- **Fix**: Added comprehensive startup logging and debug endpoints
- **Result**: Easy debugging of deployment issues

### 4. **Configuration Optimization**
- **Problem**: Health check timeout too aggressive, suboptimal gunicorn settings
- **Fix**: Updated Railway and nixpacks configuration
- **Result**: More reliable health checks and better resource usage

## Key Changes Made

### FastAPI Application (`backend/main.py`)

1. **Graceful OpenAI Initialization**
```python
# New approach - doesn't fail on startup
openai_available = False

def initialize_openai_client():
    global openai_client, openai_available
    try:
        api_key = load_openai_key()
        openai_client = OpenAI(api_key=api_key)
        openai_available = True
        return True
    except Exception as e:
        logger.warning(f"OpenAI initialization failed: {e}")
        openai_available = False
        return False
```

2. **Robust Health Endpoints**
```python
@app.get("/health")
async def health_check():
    # Always returns 200 OK if app can respond
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "openai": "available" if openai_available else "unavailable"
        }
    }

@app.get("/readiness")
async def readiness_check():
    # Tests basic functionality
    test_tweets = split_into_tweets("test content")
    return {"status": "ready" if test_tweets else "not_ready"}
```

3. **Enhanced Startup Logging**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Threadr backend in {ENVIRONMENT} mode...")
    logger.info(f"Port from ENV: {os.getenv('PORT', 'not set')}")
    logger.info(f"OpenAI available: {openai_available}")
    # ... more diagnostic info
```

4. **Debug Endpoint**
```python
@app.get("/debug/startup")
async def debug_startup():
    # Complete startup configuration info
    return {
        "environment": ENVIRONMENT,
        "openai_available": openai_available,
        "port": os.getenv("PORT"),
        # ... all config details
    }
```

### Railway Configuration (`railway.toml`)

```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 60  # Increased from 30
startCommand = "gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Nixpacks Configuration (`nixpacks.toml`)

```toml
[start]
cmd = "gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --log-level info --access-logfile - --error-logfile -"

[variables]
PYTHONUNBUFFERED = "1"
ENVIRONMENT = "production"
```

## Testing Before Deployment

Use the provided test script:

```bash
# Start the app locally
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# In another terminal, run tests
python test_health_checks.py
```

## Deployment Checklist

1. **Environment Variables in Railway**
   - `OPENAI_API_KEY` (optional - app works without it)
   - `ENVIRONMENT=production`
   - `CORS_ORIGINS` (set to your frontend domains)

2. **Verify Health Endpoints**
   - `GET /health` - Should always return 200 OK
   - `GET /readiness` - Should return ready status
   - `GET /debug/startup` - Shows all configuration

3. **Monitor Startup Logs**
   - Look for "Threadr backend startup completed successfully"
   - Check OpenAI availability status
   - Verify port binding and environment

## Expected Behavior

### With OpenAI API Key
- Full functionality including AI-generated threads
- Health check shows `openai: "available"`
- Fallback methods available if OpenAI fails

### Without OpenAI API Key
- Basic functionality using text splitting
- Health check shows `openai: "unavailable"`
- App still starts and serves requests normally

## Troubleshooting

### If Health Checks Still Fail

1. Check Railway logs for startup errors
2. Visit `/debug/startup` endpoint to verify configuration
3. Test `/readiness` endpoint for basic functionality
4. Ensure port binding is correct (`0.0.0.0:$PORT`)

### If App Won't Start

1. Check Python version compatibility (3.11)
2. Verify all dependencies in requirements.txt
3. Check for import errors in startup logs
4. Test locally with same configuration

## Key Benefits

1. **Reliability**: App starts even if external services fail
2. **Observability**: Comprehensive logging and debug endpoints
3. **Resilience**: Graceful degradation when OpenAI unavailable
4. **Performance**: Optimized gunicorn configuration
5. **Debugging**: Easy to diagnose deployment issues
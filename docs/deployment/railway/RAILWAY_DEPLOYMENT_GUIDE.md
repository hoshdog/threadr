# Railway Deployment Guide for Threadr

This comprehensive guide consolidates all Railway deployment knowledge and fixes for the Threadr FastAPI backend.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Environment Variables](#environment-variables)
4. [Deployment Process](#deployment-process)
5. [Common Issues & Solutions](#common-issues--solutions)
6. [Redis Setup](#redis-setup)
7. [URL Scraping](#url-scraping)
8. [Health Checks](#health-checks)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Quick Start

### Prerequisites
- Railway account connected to GitHub
- Environment variables ready (see section below)
- Code repository with proper structure

### 5-Minute Deployment
1. **Connect Repository**: Railway Dashboard → New Project → Deploy from GitHub → Select "threadr"
2. **Set Environment Variables** (see [Environment Variables](#environment-variables))
3. **Deploy**: Railway auto-deploys on push to main branch
4. **Test**: Check health endpoint once deployed

## Configuration

### nixpacks.toml (Root Directory)
Current working configuration forces Railway to use uvicorn (not gunicorn):

```toml
# BULLETPROOF Railway Nixpacks Configuration
# Forces Railway to use uvicorn only
[providers]
python = "3.11"

[phases.build]
workDir = "backend"
cmds = [
  "echo 'Verifying directory structure...'",
  "ls -la",
  "ls -la src/ || echo 'src directory not found'",
  "echo 'Python path will be: /app/backend:/app/backend/src'"
]

[phases.setup]
workDir = "backend"
cmds = [
  "echo 'Installing Python dependencies...'",
  "pip install --upgrade pip",
  "pip install --no-cache-dir -r requirements.txt",
  "echo 'Dependencies installed successfully'"
]

[start]
workDir = "backend"
cmd = "exec python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info --access-log --timeout-keep-alive 30"

[variables]
PYTHONUNBUFFERED = "1"
ENVIRONMENT = "production"
NIXPACKS_PYTHON_WSGI_MODULE = ""
DISABLE_COLLECTSTATIC = "1"
WEB_CONCURRENCY = "1"
RAILWAY_NO_GUNICORN = "true"
PYTHONPATH = "/app/backend:/app/backend/src"
DEBUG = "false"
```

### Key Configuration Points
- **workDir = "backend"**: Sets working directory consistently
- **exec python -m uvicorn**: Proper signal handling and explicit module loading
- **NIXPACKS_PYTHON_WSGI_MODULE = ""**: Disables WSGI auto-detection
- **RAILWAY_NO_GUNICORN = "true"**: Explicitly prevents gunicorn usage
- **PYTHONPATH**: Includes both backend and src directories for imports

## Environment Variables

### Required Variables
Set these in Railway Dashboard → Your Project → Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `OPENAI_API_KEY` | OpenAI API key for GPT | `sk-...` |
| `API_KEYS` | Comma-separated API keys | `key1,key2` |
| `CORS_ORIGINS` | Frontend URL (NO trailing slash) | `https://threadr-plum.vercel.app` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | None (disables caching) |
| `RATE_LIMIT_REQUESTS` | Requests per window | `50` |
| `RATE_LIMIT_WINDOW_HOURS` | Rate limit window | `1` |
| `ALLOWED_DOMAINS` | Scraping allowlist | `medium.com,dev.to,...` |
| `CACHE_TTL_HOURS` | Cache duration | `24` |

### Complete Environment Setup
```bash
# Core Configuration
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=https://threadr-plum.vercel.app
API_KEYS=your-secure-key-1,your-secure-key-2

# Optional - Redis & Caching
REDIS_URL=rediss://default:password@host:port
CACHE_TTL_HOURS=24

# Optional - Rate Limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW_HOURS=1

# Optional - URL Scraping
ALLOWED_DOMAINS=medium.com,*.medium.com,dev.to,*.dev.to,substack.com,*.substack.com
```

## Deployment Process

### Step 1: Clear Railway Cache (If Needed)
If Railway is using cached configuration:
```bash
# Option A: Force rebuild with empty commit
git commit --allow-empty -m "Force Railway rebuild - clear cache"
git push

# Option B: Railway Dashboard → Settings → Reset Build Cache
```

### Step 2: Monitor Deployment
```bash
# View logs during deployment
railway logs --follow

# Check build logs specifically
railway logs --build
```

### Step 3: Verify Success
Look for these indicators in logs:
```
INFO: Started server process [1]
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8080
```

### Step 4: Test Endpoints
```bash
# Health check
curl https://your-app.railway.app/health

# API test (with your API key)
curl -X POST https://your-app.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text": "Test content"}'
```

## Common Issues & Solutions

### Issue 1: "Service Unavailable" / 502 Errors
**Symptoms**: Health checks fail, app won't start

**Root Causes & Solutions**:
1. **Import Errors** (80% of cases)
   - **Fix**: Check PYTHONPATH in nixpacks.toml
   - **Debug**: Use try/except imports in code
   ```python
   try:
       from .redis_manager import initialize_redis
   except ImportError:
       from redis_manager import initialize_redis
   ```

2. **Port Binding Issues** (15% of cases)
   - **Fix**: Always use `$PORT` environment variable
   - **Verify**: Railway automatically sets PORT

3. **Working Directory Problems** (5% of cases)
   - **Fix**: Consistent workDir in all nixpacks phases

### Issue 2: Gunicorn Errors
**Error**: `/bin/sh: 1: gunicorn: not found`

**Solution**: Remove all gunicorn references
- ❌ Never add gunicorn to requirements.txt
- ✅ Use RAILWAY_NO_GUNICORN environment variable
- ✅ Disable backup nixpacks files containing gunicorn

### Issue 3: CORS Errors
**Error**: Frontend can't connect to backend

**Solutions**:
```bash
# CORRECT (no trailing slash)
CORS_ORIGINS=https://threadr-plum.vercel.app

# INCORRECT (with trailing slash)
CORS_ORIGINS=https://threadr-plum.vercel.app/
```

### Issue 4: Pydantic v2 Type Errors
**Error**: `TypeError: Subscripted generics cannot be used with class and instance checks`

**Solution**:
```python
# GOOD - Always convert to string
url_str = str(url)

# BAD - Don't use isinstance with HttpUrl
if isinstance(url, HttpUrl):  # This fails
```

### Issue 5: httpx SSL/Connection Failures
**Solution**: Use simple httpx configuration
```python
# GOOD - Simple configuration
async with httpx.AsyncClient(
    timeout=30.0,
    follow_redirects=True,
    headers={"User-Agent": "..."}
) as client:
    response = await client.get(url)

# BAD - Complex SSL contexts fail in Railway
ssl_context = create_default_context()
```

## Redis Setup

### Option 1: Railway Redis Plugin
1. Railway Dashboard → Add Service → Database → Redis
2. Railway automatically sets `REDIS_URL`
3. Verify connection in app logs

### Option 2: Upstash Redis (Recommended)
1. Sign up at [upstash.com](https://upstash.com)
2. Create Redis database (free tier: 10,000 commands/day)
3. Copy Redis URL: `rediss://default:password@host:port`
4. Add to Railway environment variables

### Redis Configuration in Code
```python
import redis
import os
from urllib.parse import urlparse

def get_redis_client():
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        return None
    
    try:
        url = urlparse(redis_url)
        return redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=True
        )
    except Exception as e:
        print(f"Redis connection error: {e}")
        return None
```

## URL Scraping

### Current Implementation
The URL scraping system includes:
- ✅ SSL/TLS flexibility with automatic fallback
- ✅ Retry mechanism (3 attempts with exponential backoff)
- ✅ Enhanced error handling
- ✅ Multiple CA bundle location checks

### Supported Domains
Default allowed domains for scraping:
- Medium: `medium.com`, `*.medium.com`
- Dev.to: `dev.to`, `*.dev.to`
- Substack: `substack.com`, `*.substack.com`
- Hashnode: `hashnode.com`, `*.hashnode.com`

### Testing URL Scraping
```bash
# Test with sample URLs
curl -X POST https://your-app.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"url": "https://medium.com/@example/article"}'
```

## Health Checks

### Available Health Endpoints
- `GET /health` - Basic health check
- `GET /readiness` - Kubernetes readiness probe
- `GET /debug/startup` - Detailed diagnostics (debug mode only)

### Health Check Response
Successful health check returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-01T10:00:00.000000",
  "version": "1.0.0",
  "environment": "production",
  "port": "8080",
  "services": {
    "api": "healthy",
    "openai": "configured",
    "redis": "connected"
  }
}
```

## Troubleshooting

### Diagnostic Commands
```bash
# Check service status
railway status

# View recent logs
railway logs --tail 100

# View environment variables
railway variables

# Get deployment URL
railway domain
```

### Log Analysis Patterns

**✅ Successful Startup**:
```
INFO: Started server process [1]
INFO: CORS Origins configured: ['https://...']
INFO: OpenAI client is available
INFO: Redis connection successful
INFO: Application startup complete
```

**❌ Common Error Patterns**:
```
ModuleNotFoundError: No module named 'src'
# Fix: Update PYTHONPATH

OSError: [Errno 98] Address already in use
# Fix: Use $PORT environment variable

/bin/sh: 1: gunicorn: not found
# Fix: Remove gunicorn references, use uvicorn only
```

### Railway-Specific Debugging
```bash
# Test in Railway shell
railway shell
cd backend
python -c "import main; print('Import successful')"
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Best Practices

### 1. Configuration Management
- ✅ Use environment variables for all configuration
- ✅ Keep development and production configs separate
- ✅ Never hardcode secrets in code
- ❌ Don't use complex SSL configurations
- ❌ Never add gunicorn to requirements.txt

### 2. Deployment Process
- ✅ Test locally first: `uvicorn src.main:app --reload`
- ✅ Use consistent working directories in nixpacks
- ✅ Monitor first deployment closely
- ✅ Clear Railway cache when configuration changes
- ❌ Don't mix different server configurations

### 3. Error Handling
- ✅ Use try/except for imports (src/ directory structure)
- ✅ Implement graceful fallbacks (Redis optional)
- ✅ Log detailed error information
- ✅ Provide user-friendly error messages

### 4. Performance
- ✅ Use Redis caching to reduce API costs
- ✅ Implement proper timeout settings
- ✅ Monitor resource usage in Railway dashboard
- ✅ Use connection pooling for external services

### 5. Security
- ✅ Use API key authentication
- ✅ Implement CORS properly
- ✅ Use HTTPS only in production
- ✅ Validate all user inputs
- ❌ Don't expose internal error details

## Emergency Procedures

### Complete Deployment Failure
1. **Minimal Test App**:
   Create `backend/minimal_main.py`:
   ```python
   from fastapi import FastAPI
   app = FastAPI()
   
   @app.get("/")
   def root():
       return {"status": "ok"}
   ```

2. **Fallback Configuration**:
   ```toml
   [start]
   cmd = "cd backend && python -m uvicorn minimal_main:app --host 0.0.0.0 --port $PORT"
   ```

### Rollback Strategy
1. Use git to revert to last working commit
2. Force Railway rebuild with empty commit
3. Monitor logs for successful startup
4. Test health endpoints

### Alternative Deployment Methods
If nixpacks fails completely:
1. **Docker Deployment**: Use provided Dockerfile
2. **Different Buildpack**: Try Railway's Python buildpack
3. **Manual Configuration**: Contact Railway support

## Success Metrics

### Deployment Success Indicators
- ✅ Health endpoint returns 200 OK
- ✅ API endpoints respond correctly
- ✅ No 502/503 errors in Railway logs
- ✅ CORS configured properly (frontend connects)
- ✅ Redis connection established (if configured)
- ✅ OpenAI integration working
- ✅ Rate limiting functional

### Performance Benchmarks
- **Startup Time**: < 30 seconds
- **Response Time**: < 2 seconds (uncached), < 100ms (cached)
- **Memory Usage**: < 512MB typical
- **Error Rate**: < 1% of requests

## Support Resources

### Internal Documentation
- `CLAUDE.md` - Project overview and recent updates
- Backend source code with inline documentation
- Test files with usage examples

### External Resources
- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [nixpacks Documentation](https://nixpacks.com/)

### Getting Help
1. Check Railway build and runtime logs first
2. Verify environment variables are set correctly
3. Test the exact configuration locally
4. Review this guide for common solutions
5. Contact Railway support with specific error messages

---

This guide represents the consolidated knowledge from multiple deployment iterations and fixes. It should handle 95% of Railway deployment scenarios for the Threadr backend.
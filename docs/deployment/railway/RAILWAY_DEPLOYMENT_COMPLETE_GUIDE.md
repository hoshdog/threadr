# Railway Deployment Complete Guide for Threadr

This guide consolidates all Railway deployment learnings and fixes from July 2025.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Common Issues & Solutions](#common-issues--solutions)
3. [Configuration Files](#configuration-files)
4. [Environment Variables](#environment-variables)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Quick Start

### Prerequisites
- Railway account
- GitHub repository connected
- Environment variables ready

### Deployment Steps

1. **Connect GitHub Repository**
   ```
   Railway Dashboard → New Project → Deploy from GitHub → Select "threadr"
   ```

2. **Set Environment Variables**
   ```env
   ENVIRONMENT=production
   OPENAI_API_KEY=your-key-here
   API_KEYS=generated-key-1,generated-key-2
   CORS_ORIGINS=https://threadr-plum.vercel.app
   REDIS_URL=redis://default:password@redis.railway.internal:6379
   ```

3. **Deploy**
   - Railway will auto-deploy on push to main branch
   - Monitor build logs for any errors
   - Check health endpoint once deployed

## Common Issues & Solutions

### 1. 502 Bad Gateway / Service Unavailable

**Symptoms:**
- Health check returns 502
- "Application failed to respond"

**Solutions:**
```toml
# nixpacks.toml - Use proper PYTHONPATH
[variables]
PYTHONPATH = "/app/backend:/app/backend/src"
```

### 2. Import Errors with src/ Directory

**Problem:** Moving files to `src/` breaks imports

**Solution 1:** Update imports to handle both cases
```python
try:
    from .redis_manager import initialize_redis
except ImportError:
    from redis_manager import initialize_redis
```

**Solution 2:** Set PYTHONPATH correctly in nixpacks.toml

### 3. Pydantic v2 HttpUrl Type Error

**Error:** `TypeError: Subscripted generics cannot be used with class and instance checks`

**Solution:**
```python
# Don't use isinstance with HttpUrl
# BAD:
url_str = str(url) if isinstance(url, HttpUrl) else url

# GOOD:
url_str = str(url)  # Works for both str and HttpUrl
```

### 4. httpx Configuration Failures

**Problem:** Complex SSL contexts fail in Railway containers

**Solution:** Use simple httpx configuration
```python
# GOOD - Simple configuration that works
async with httpx.AsyncClient(
    timeout=30.0,
    follow_redirects=True,
    headers={...}
) as client:
    response = await client.get(url)

# BAD - Complex configuration that fails
ssl_context = create_default_context()
transport = httpx.AsyncHTTPTransport(ssl_context=ssl_context)
```

### 5. CORS Errors

**Problem:** Frontend can't connect to backend

**Solution:** Remove trailing slashes
```env
# GOOD
CORS_ORIGINS=https://threadr-plum.vercel.app

# BAD
CORS_ORIGINS=https://threadr-plum.vercel.app/
```

## Configuration Files

### nixpacks.toml (Working Configuration)
```toml
[providers]
python = "3.11"

[phases.build]
workDir = "backend"

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

### Key Points:
- Always use `exec` for proper signal handling
- Set `PYTHONPATH` to include both backend and src
- Disable gunicorn with `NIXPACKS_PYTHON_WSGI_MODULE = ""`
- Use uvicorn explicitly in start command

## Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `OPENAI_API_KEY` | OpenAI API key for GPT | `sk-...` |
| `API_KEYS` | Comma-separated API keys | `key1,key2` |
| `CORS_ORIGINS` | Allowed frontend URL | `https://threadr-plum.vercel.app` |
| `REDIS_URL` | Redis connection URL | `redis://...` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_REQUESTS` | Requests per window | `50` |
| `RATE_LIMIT_WINDOW_HOURS` | Rate limit window | `1` |
| `ALLOWED_DOMAINS` | Scraping allowlist | `medium.com,dev.to,...` |

## Troubleshooting

### Check Deployment Status
```bash
# Health check
curl https://your-app.railway.app/health

# Test API
curl https://your-app.railway.app/api/test
```

### View Logs
1. Railway Dashboard → Your Project → Deployments
2. Click on deployment → View Logs
3. Look for startup errors or crashes

### Common Log Patterns

**Successful Start:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Import Error:**
```
ModuleNotFoundError: No module named 'src'
# Fix: Update PYTHONPATH
```

**Port Binding Error:**
```
ERROR:    [Errno 98] Address already in use
# Fix: Use $PORT environment variable
```

## Best Practices

### 1. Always Test Locally First
```bash
cd backend
uvicorn src.main:app --reload --port 8001
```

### 2. Monitor Resource Usage
- Railway has memory limits
- Watch for memory leaks in long-running processes
- Use connection pooling for external services

### 3. Use Environment Variables
- Never hardcode secrets
- Use `.env.production` as template
- Keep development and production configs separate

### 4. Deployment Checklist
- [ ] Test endpoints locally
- [ ] Verify environment variables
- [ ] Check CORS configuration
- [ ] Test with frontend
- [ ] Monitor logs after deployment

### 5. Keep It Simple
- Avoid complex SSL configurations
- Use default httpx settings
- Let Railway handle port binding
- Don't overthink containerization

## Migration from Old Structure

If migrating from flat structure to src/ directory:

1. **Update imports** in all files
2. **Update PYTHONPATH** in deployment config
3. **Update run commands** to use `src.main:app`
4. **Test thoroughly** before deploying

## Summary

The key to successful Railway deployment is:
1. Simple configurations work better than complex ones
2. Always set PYTHONPATH for custom directory structures
3. Use environment variables for all configuration
4. Monitor logs closely during first deployment
5. Test locally with the same Python version

For additional help, check Railway's documentation or the other guides in this folder.
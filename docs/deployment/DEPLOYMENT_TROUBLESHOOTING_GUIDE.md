# Deployment Troubleshooting Guide

This guide helps you troubleshoot common deployment issues for both Railway (backend) and Vercel (frontend).

## Quick Diagnosis Flowchart

```
Is the issue with Backend or Frontend?
├── Backend (Railway) → See Section 1
│   ├── 502 Error → Check health endpoint
│   ├── Import Error → Check PYTHONPATH
│   └── Scraping Error → Check httpx config
└── Frontend (Vercel) → See Section 2
    ├── 404 Error → Check outputDirectory
    ├── CORS Error → Check backend URL
    └── API Error → Check API keys
```

## Section 1: Railway Backend Issues

### 1.1 502 Bad Gateway / Service Unavailable

**Symptoms:**
```json
{
  "status": "error",
  "code": 502,
  "message": "Application failed to respond"
}
```

**Diagnosis Steps:**
1. Check Railway logs for startup errors
2. Verify health endpoint locally
3. Check import statements

**Solutions:**

**A. Python Import Errors**
```python
# If you see: ModuleNotFoundError: No module named 'src'
# Fix in nixpacks.toml:
[variables]
PYTHONPATH = "/app/backend:/app/backend/src"
```

**B. Port Binding Issues**
```toml
# Always use $PORT variable
cmd = "exec uvicorn src.main:app --host 0.0.0.0 --port $PORT"
```

### 1.2 URL Scraping Returns 500

**Error Example:**
```json
{
  "detail": "Internal server error. Error ID: 2025-07-31T03:08:53.091091"
}
```

**Common Causes:**

**A. Pydantic v2 Type Error**
```python
# Error: TypeError: Subscripted generics cannot be used
# BAD:
if isinstance(url, HttpUrl):

# GOOD:
url_str = str(url)  # Just convert to string
```

**B. httpx Configuration**
```python
# BAD - Complex config fails on Railway:
ssl_context = create_default_context()
transport = httpx.AsyncHTTPTransport(
    ssl_context=ssl_context,
    local_address="0.0.0.0"
)

# GOOD - Simple config works:
async with httpx.AsyncClient(
    timeout=30.0,
    follow_redirects=True,
    headers={...}
) as client:
```

### 1.3 CORS Errors

**Browser Console Error:**
```
Access to fetch at 'https://backend.railway.app' from origin 
'https://frontend.vercel.app' has been blocked by CORS policy
```

**Fix:**
```env
# In Railway environment variables
# Remove trailing slash!
CORS_ORIGINS=https://threadr-plum.vercel.app
```

### 1.4 Health Check Timeouts

**Railway Dashboard Shows:** "Health check failed"

**Solutions:**
1. Increase timeout in Railway settings (30s → 60s)
2. Ensure health endpoint is lightweight
3. Check startup time in logs

## Section 2: Vercel Frontend Issues

### 2.1 404 Page Not Found

**After Moving Files to src/**

**Fix in vercel.json:**
```json
{
  "outputDirectory": "src",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 2.2 API Connection Failures

**Console Error:** "Failed to fetch"

**Checklist:**
1. Verify backend URL in config.js
2. Check API key is set
3. Ensure CORS is configured

**config.js Debug:**
```javascript
console.log('API URL:', CONFIG.apiUrl);
console.log('API Key present:', !!CONFIG.apiKey);
```

### 2.3 Environment Variable Issues

**Vercel Dashboard Settings:**
- Project Settings → Environment Variables
- Add `THREADR_API_URL` if needed
- Redeploy after changes

## Section 3: Integration Issues

### 3.1 Frontend Can't Reach Backend

**Test Connectivity:**
```bash
# From your local machine
curl https://threadr-production.up.railway.app/health

# Should return:
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0",
  "environment": "production"
}
```

### 3.2 API Key Authentication Failures

**Error:** "API key required"

**Debug Steps:**
1. Check API_KEYS in Railway environment
2. Verify X-API-Key header in frontend
3. Test with curl:

```bash
curl -X POST https://backend.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{"text": "test"}'
```

## Section 4: Debugging Tools

### 4.1 Railway Logs

```bash
# Via Railway CLI
railway logs

# Or in dashboard:
Project → Deployments → View Logs
```

### 4.2 Vercel Logs

```bash
# Via Vercel CLI
vercel logs

# Or in dashboard:
Project → Functions → View Logs
```

### 4.3 Browser DevTools

1. **Network Tab**: Check API requests
2. **Console**: Look for JavaScript errors
3. **Application Tab**: Verify localStorage/cookies

## Section 5: Common Patterns

### Pattern 1: "Works Locally, Fails in Production"

**Usually caused by:**
- Environment variable differences
- Port configuration
- SSL/TLS handling
- File path differences

**Debug approach:**
1. Compare local vs production configs
2. Check environment variables
3. Review deployment logs

### Pattern 2: "Worked Yesterday, Broken Today"

**Check for:**
- Recent commits
- Dependency updates
- Service outages (Railway/Vercel status)
- API key expiration

### Pattern 3: "Intermittent Failures"

**Possible causes:**
- Rate limiting
- Memory limits
- Timeout issues
- External service failures

## Quick Fixes Reference

| Issue | Quick Fix |
|-------|-----------|
| 502 Error | Check PYTHONPATH in nixpacks.toml |
| Import Error | Update to `src.main:app` |
| CORS Error | Remove trailing slash from URL |
| Type Error | Use `str(url)` instead of isinstance |
| SSL Error | Simplify httpx configuration |
| 404 Frontend | Update outputDirectory in vercel.json |
| API Key Error | Check X-API-Key header |

## Emergency Procedures

### Backend Down Completely

1. **Rollback:**
   ```bash
   git revert HEAD
   git push
   ```

2. **Switch to Dockerfile:**
   - In Railway settings, change from Nixpacks to Docker
   - Ensure Dockerfile has correct configuration

### Frontend Down Completely

1. **Rollback in Vercel:**
   - Dashboard → Deployments → Previous deployment → Promote

2. **Emergency static serve:**
   ```bash
   cd frontend/src
   python -m http.server 8000
   ```

## Prevention Checklist

Before deploying:
- [ ] Test all endpoints locally
- [ ] Verify environment variables
- [ ] Check file paths after reorganization
- [ ] Test with production-like settings
- [ ] Review recent changes
- [ ] Have rollback plan ready

## Getting Help

1. **Check Logs First** - Most issues are visible in logs
2. **Test Endpoints** - Use curl to isolate issues
3. **Compare Configs** - Working vs broken deployments
4. **Documentation** - Review platform-specific docs

Remember: Simple configurations are more reliable than complex ones!
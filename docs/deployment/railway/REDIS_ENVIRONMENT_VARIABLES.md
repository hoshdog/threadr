# Redis Environment Variables for Railway - Threadr Backend

This document provides the complete environment variable configuration for Redis integration on Railway.

## Current Railway Environment Variables

### Check Your Current Setup

1. **Railway Dashboard** → **Your Threadr Project** → **Variables**
2. Verify these variables exist:

```bash
# Core Variables (Already Set)
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-openai-key
CORS_ORIGINS=https://threadr-plum.vercel.app
API_KEYS=your-secure-key-1,your-secure-key-2
```

## Redis Environment Variables to Add

### Required for Redis Activation

Add this single variable to activate all Redis features:

```bash
# Redis Connection URL
REDIS_URL=rediss://default:password@host:port
```

### Optional Redis Configuration

These variables have sensible defaults but can be customized:

```bash
# Cache Configuration
CACHE_TTL_HOURS=24                    # Default: 24 hours
                                      # Recommended: 6-24 hours

# Rate Limiting (Enhanced with Redis)
RATE_LIMIT_REQUESTS=100               # Default: 50
RATE_LIMIT_WINDOW_HOURS=1             # Default: 1 hour
```

## Complete Environment Variable Setup

### Option 1: Railway Redis Plugin

If using Railway's Redis service:

```bash
# Railway automatically sets these when you add Redis service:
REDIS_URL=redis://default:password@redis.railway.internal:6379
REDIS_PRIVATE_URL=redis://default:password@host:port

# You only need to add optional configurations:
CACHE_TTL_HOURS=12
RATE_LIMIT_REQUESTS=200
```

### Option 2: Upstash Redis

If using Upstash (recommended for cost):

```bash
# Add this manually from your Upstash dashboard:
REDIS_URL=rediss://default:abc123def456@global-quality-bird-12345.upstash.io:6379

# Optional optimizations:
CACHE_TTL_HOURS=6                     # Shorter cache for better updates
RATE_LIMIT_REQUESTS=150               # Higher limits for better UX
```

## Railway Configuration Steps

### Step 1: Access Variables

1. **Railway Dashboard** → **Projects** → **Threadr**
2. Click **"Variables"** tab
3. Click **"+ New Variable"**

### Step 2: Add Redis URL

**Variable Name**: `REDIS_URL`
**Value**: Your Redis connection string

Examples:
```bash
# Railway Redis Plugin (auto-generated)
redis://default:generated-password@redis.railway.internal:6379

# Upstash Redis (from your dashboard)
rediss://default:your-password@global-bird-12345.upstash.io:6379

# External Redis provider
redis://user:password@your-redis-host.com:6379
```

### Step 3: Add Optional Variables

| Variable | Purpose | Default | Recommended |
|----------|---------|---------|-------------|
| `CACHE_TTL_HOURS` | Cache duration | 24 | 6-12 hours |
| `RATE_LIMIT_REQUESTS` | Requests per window | 50 | 100-200 |
| `RATE_LIMIT_WINDOW_HOURS` | Rate limit window | 1 | 1 hour |

### Step 4: Redeploy

After adding variables:
1. **Redeploy** your application (Railway auto-deploys on variable changes)
2. **Monitor logs**: `railway logs --tail 50`
3. **Test connection**: Check `/health` endpoint

## Environment Variable Validation

### Test Your Configuration

```bash
# Check all environment variables
railway variables

# Should show:
REDIS_URL=rediss://...
CACHE_TTL_HOURS=24
RATE_LIMIT_REQUESTS=100
```

### Verify Redis Connection

```bash
# Test Redis connection through health endpoint
curl https://threadr-production.up.railway.app/health

# Success response:
{
  "status": "healthy",
  "services": {
    "redis": "connected"    # ← This confirms Redis is working
  }
}
```

## Security Considerations

### Redis URL Security

🚨 **Important**: Redis URLs contain credentials

```bash
# CORRECT: Environment variable (secure)
REDIS_URL=rediss://default:password@host:port  # In Railway Variables

# NEVER: Hardcode in source code
redis_url = "rediss://default:password@host:port"  # ❌ Insecure
```

### Access Control

- Railway environment variables are **encrypted at rest**
- Only project members can view variable values
- Variables are **not exposed** in build logs
- Use **Railway's secrets management** for production

## Troubleshooting Environment Variables

### Issue 1: Variable Not Found

**Error**: `No REDIS_URL configured - Redis features disabled`

**Solution**:
1. Check variable name spelling: `REDIS_URL` (case sensitive)
2. Verify variable is set in **Railway Dashboard** → **Variables**
3. Redeploy after adding variables

### Issue 2: Invalid Redis URL Format

**Error**: `Redis connection failed: Invalid URL format`

**Solutions**:
```bash
# CORRECT formats:
redis://default:password@host:6379        # Standard Redis
rediss://default:password@host:6379       # SSL Redis (Upstash)
redis://user:pass@host:6379/0             # With database number

# INCORRECT formats:
redis://host:6379                         # Missing credentials
redis:password@host:6379                  # Missing protocol
rediss//default:pass@host:6379            # Typo in protocol
```

### Issue 3: SSL Certificate Issues

**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution**: Use `rediss://` (SSL) for Upstash, your code handles SSL properly:
```bash
# For Upstash (SSL required)
REDIS_URL=rediss://default:password@host:port

# For Railway Redis Plugin (standard)
REDIS_URL=redis://default:password@host:port
```

### Issue 4: Connection Timeout

**Error**: `Redis operation timeout`

**Solutions**:
1. **Check Redis service status** in Railway dashboard
2. **Verify network connectivity**:
   ```bash
   # Test from Railway shell
   railway shell
   python3 -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"
   ```
3. **Reduce timeout values** if needed (already optimized in your code)

## Performance Environment Variables

### High-Performance Configuration

For production workloads with heavy caching needs:

```bash
REDIS_URL=rediss://default:password@host:port
CACHE_TTL_HOURS=6                    # Shorter cache, fresher content
RATE_LIMIT_REQUESTS=500              # Higher limits for premium users
RATE_LIMIT_WINDOW_HOURS=1            # Standard window
```

### Memory-Optimized Configuration

For cost-conscious deployments:

```bash
REDIS_URL=rediss://default:password@host:port
CACHE_TTL_HOURS=2                    # Very short cache
RATE_LIMIT_REQUESTS=100              # Moderate limits
```

### Development Configuration

For testing and development:

```bash
REDIS_URL=redis://localhost:6379     # Local Redis
CACHE_TTL_HOURS=1                    # Short cache for testing
RATE_LIMIT_REQUESTS=1000             # High limits for testing
DEBUG=true                           # Enable debug logging
```

## Monitoring Variables

Your backend automatically tracks Redis performance. No additional variables needed for monitoring.

### Available Metrics (Built-in)

Your Redis implementation automatically provides:

- **Connection status**: Available in `/health` endpoint
- **Cache statistics**: Cache hit/miss rates
- **Memory usage**: Redis memory consumption
- **Operation counts**: Redis commands executed
- **Error rates**: Failed Redis operations

Access via:
```bash
# Health check (public)
curl https://threadr-production.up.railway.app/health

# Detailed stats (requires API key)
curl -H "X-API-Key: your-key" https://threadr-production.up.railway.app/api/analytics/redis-stats
```

## Summary

### Minimum Required Setup

To activate Redis, add just one variable:

```bash
REDIS_URL=your-redis-connection-string
```

### Optimal Production Setup

For best performance and reliability:

```bash
# Redis Connection
REDIS_URL=rediss://default:password@host:port

# Performance Tuning
CACHE_TTL_HOURS=12
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW_HOURS=1
```

### Next Steps

1. **Choose Redis Provider**: Railway Plugin or Upstash
2. **Add REDIS_URL**: Copy connection string to Railway Variables
3. **Redeploy**: Railway auto-deploys on variable changes
4. **Test**: Verify `/health` shows `"redis": "connected"`
5. **Monitor**: Check performance improvements in logs

Your backend will automatically utilize Redis for caching, rate limiting, analytics, and session management once `REDIS_URL` is configured.
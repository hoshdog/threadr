# Railway URL Scraping Fix Guide

## Issue Summary
All URL scraping is failing with 500 errors on Railway, while text input works perfectly. This is a common issue with Railway deployments due to network restrictions, SSL/TLS issues, or container configuration.

## Root Causes & Solutions

### 1. SSL/TLS Certificate Issues
**Problem**: Railway containers may not have proper CA certificates installed or httpx may have issues with SSL verification.

**Solutions Applied**:
- Added `certifi` to requirements.txt for proper CA bundle management
- Updated httpx client to use certifi's CA bundle explicitly
- Added SSL fallback mode that disables verification if SSL errors occur
- Enhanced logging to track SSL context usage

### 2. Network Egress Restrictions
**Problem**: Railway may have firewall rules or network policies blocking outbound HTTPS requests.

**Solutions Applied**:
- Increased timeout from 30s to 60s (connect timeout: 30s)
- Added comprehensive User-Agent headers to avoid bot detection
- Added retry logic with transport configuration
- Enhanced error messages to identify network vs SSL issues

### 3. DNS Resolution Issues
**Problem**: Railway containers might have DNS resolution problems for external domains.

**Solutions Applied**:
- Added `/api/test/railway-network` endpoint to test DNS resolution
- Tests multiple domains to identify patterns
- Logs resolved IPs for debugging

### 4. httpx Configuration for Railway
**Problem**: Default httpx settings may not work well in Railway's container environment.

**Solutions Applied**:
```python
# Enhanced configuration
async with httpx.AsyncClient(
    timeout=httpx.Timeout(60.0, connect=30.0),
    follow_redirects=True,
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    verify=ssl_context
) as client:
```

## Debugging Steps

### 1. Test Network Connectivity
```bash
# SSH into Railway service
railway run bash

# Test DNS
nslookup medium.com
nslookup google.com

# Test HTTPS connectivity
curl -v https://medium.com
curl -v https://httpbin.org/get

# Check CA certificates
ls -la /etc/ssl/certs/
```

### 2. Use Debug Endpoints
```bash
# Test Railway network environment
curl https://your-app.railway.app/api/test/railway-network

# Test specific URL (development mode only)
curl -X POST https://your-app.railway.app/api/test/url-check?url=https://medium.com
```

### 3. Check Logs
Look for these specific log patterns:
- "SSL error detected, retrying without verification"
- "Connection timeout - Railway may be blocking outbound connections"
- "Using CA bundle from: /path/to/certifi/cacert.pem"

## Environment Variables to Set in Railway

```bash
# Disable SSL verification (temporary workaround)
HTTPX_VERIFY_SSL=false

# Set custom CA bundle path if needed
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Increase logging
LOG_LEVEL=DEBUG

# Allow all domains (for testing only)
ALLOWED_DOMAINS=""
```

## Quick Fixes to Try

### 1. Disable SSL Verification (Temporary)
Set in Railway environment:
```
ENVIRONMENT=production
```
This triggers the SSL fallback mode automatically.

### 2. Use Railway's Built-in Proxy
If Railway provides an HTTP proxy, configure it:
```python
proxy = os.getenv("HTTP_PROXY")
if proxy:
    client = httpx.AsyncClient(proxy=proxy)
```

### 3. Switch to requests Library (Last Resort)
If httpx continues to fail, try the synchronous requests library:
```python
import requests
response = requests.get(url, timeout=30, verify=False)
```

## Monitoring

### Key Metrics to Track
1. SSL verification failures vs successes
2. Connection timeouts by domain
3. DNS resolution times
4. Response times for successful requests

### Log Patterns
```
INFO: Starting URL scrape for: https://medium.com/...
INFO: URL security validation passed
INFO: Creating httpx client with 60s timeout and certifi SSL context
INFO: Using CA bundle from: /app/.venv/lib/python3.11/site-packages/certifi/cacert.pem
INFO: Fetching URL: https://medium.com/...
INFO: Response received - Status: 200, Content-Length: 45678
```

## Testing After Deployment

1. **Basic connectivity test**:
   ```bash
   curl -X POST https://your-app.railway.app/api/generate \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-key" \
     -d '{"text": "Test text input"}'
   ```

2. **URL scraping test**:
   ```bash
   curl -X POST https://your-app.railway.app/api/generate \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-key" \
     -d '{"url": "https://medium.com/p/sample-article"}'
   ```

3. **Network diagnostic**:
   ```bash
   curl https://your-app.railway.app/api/test/railway-network
   ```

## If All Else Fails

1. **Use a proxy service**: Route requests through a proxy API like ScraperAPI
2. **Implement client-side scraping**: Move URL fetching to the frontend
3. **Use Railway's support**: They may need to whitelist domains or adjust firewall rules
4. **Consider alternative hosting**: Render.com or Fly.io may have fewer restrictions

## Update History
- 2025-01-30: Initial fix implementation
- Added certifi for SSL certificate management
- Increased timeouts to 60 seconds
- Added SSL fallback mode
- Enhanced logging throughout scraping flow
- Added comprehensive headers to avoid bot detection
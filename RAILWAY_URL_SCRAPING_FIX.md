# Railway URL Scraping Fix Guide

## Issue Summary
All URL scraping is failing with 500 errors on Railway, while text input works perfectly. This is a common issue with Railway deployments due to network restrictions, SSL/TLS issues, or container configuration.

## Enhanced Implementation (2025-07-30)

### Key Improvements Applied to `scrape_article` Function

1. **Environment-Based SSL Control**
   - Added `HTTPX_VERIFY_SSL` environment variable support
   - Automatically attempts SSL fallback on first failure
   - Checks multiple CA bundle locations for Railway compatibility

2. **Comprehensive Error Handling**
   - Better SSL error detection with expanded keyword list
   - Detailed error logging with JSON-formatted error details
   - Specific error messages for different failure types (403, 429, timeouts)

3. **Retry Mechanism with Exponential Backoff**
   - 3 retry attempts with increasing delays (1s, 2s, 4s)
   - SSL verification disabled on first SSL error
   - Preserves original error context across retries

4. **Transport Configuration**
   - Binds to all interfaces (`0.0.0.0`) in container
   - Support for HTTP/HTTPS proxy environment variables
   - Keepalive configuration optimized for Railway

5. **Enhanced Diagnostics**
   - DNS pre-resolution with IP logging
   - Response header logging for debugging
   - CA bundle location detection and logging

## Environment Variables for Railway

### Required for SSL Issues
```bash
# Disable SSL verification (if getting SSL errors)
HTTPX_VERIFY_SSL=false

# Custom CA bundle path (if Railway has specific certificates)
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```

### Optional Proxy Configuration
```bash
# If Railway provides an HTTP proxy
HTTP_PROXY=http://proxy.railway.internal:8080
HTTPS_PROXY=http://proxy.railway.internal:8080
```

### Debugging
```bash
# Increase logging verbosity
LOG_LEVEL=DEBUG
```

## Testing Endpoints

### 1. Network Diagnostics (Enhanced)
```bash
curl https://your-app.railway.app/api/test/railway-network
```

This endpoint now tests:
- CA bundle availability across multiple locations
- DNS resolution with full IP listing
- SSL verification on/off comparison
- Multiple URL fetching with same config as production
- System network interface information
- Railway-specific environment variables

### 2. URL Check (Development Only)
```bash
curl -X POST "https://your-app.railway.app/api/test/url-check?url=https://medium.com/article"
```

### 3. Production URL Scraping
```bash
curl -X POST https://your-app.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"url": "https://medium.com/p/sample-article"}'
```

## Debugging Process

### 1. Check Logs for Patterns
Look for these specific messages:
```
INFO: Environment: production, SSL verification override: true
INFO: DNS resolution for medium.com: ['104.16.120.127', '104.16.121.127']
INFO: Using CA bundle from: /app/.venv/lib/python3.11/site-packages/certifi/cacert.pem
INFO: Attempt 1/3: Creating httpx client (verify_ssl=True)
WARNING: SSL error detected, retrying without verification
INFO: Attempt 2/3: Creating httpx client (verify_ssl=False)
INFO: Response received - Status: 200, Content-Length: 45678
```

### 2. Common Error Patterns and Solutions

#### SSL Certificate Errors
```
Error: CERTIFICATE_VERIFY_FAILED
Solution: Set HTTPX_VERIFY_SSL=false in Railway environment
```

#### Connection Timeouts
```
Error: Connection timeout - Railway network may be blocking outbound connections
Solution: Contact Railway support to check firewall rules
```

#### DNS Resolution Failures
```
Error: DNS resolution failed
Solution: Check if Railway DNS is working, may need custom DNS servers
```

## Implementation Details

### SSL Fallback Logic
```python
# Automatic SSL fallback on first error
ssl_error_indicators = [
    "SSL", "ssl", "TLS", "tls",
    "certificate", "Certificate",
    "CERTIFICATE_VERIFY_FAILED",
    "unable to get local issuer certificate",
    "self signed certificate",
    "certificate verify failed"
]
```

### Transport Configuration
```python
transport=httpx.AsyncHTTPTransport(
    retries=1,
    local_address="0.0.0.0"  # Bind to all interfaces
)
```

### Retry Strategy
- Attempt 1: With SSL verification (if enabled)
- Attempt 2: Without SSL verification (if SSL error)
- Attempt 3: Final retry with exponential backoff

## Quick Fixes

### 1. Immediate SSL Bypass
Add to Railway environment:
```
HTTPX_VERIFY_SSL=false
```

### 2. Test Basic Connectivity
Use the network diagnostic endpoint to identify specific issues:
```bash
curl https://your-app.railway.app/api/test/railway-network | jq
```

### 3. Monitor Specific URL
Watch logs while testing a specific URL:
```bash
railway logs -f | grep "medium.com"
```

## If All Else Fails

1. **Contact Railway Support**
   - Request firewall rule review
   - Ask about outbound HTTPS restrictions
   - Check if specific ports are blocked

2. **Alternative Solutions**
   - Use a scraping API service (ScraperAPI, Bright Data)
   - Implement client-side URL fetching
   - Deploy a separate scraping microservice on a different platform

3. **Fallback Deployment**
   - Consider Render.com or Fly.io if Railway restrictions persist
   - Use the Dockerfile deployment method instead of nixpacks

## Update History
- 2025-01-30: Initial fix implementation
- 2025-07-30: Enhanced implementation with:
  - Retry mechanism with exponential backoff
  - Better SSL error detection
  - Proxy support
  - DNS pre-resolution
  - Comprehensive network diagnostics
  - Environment variable controls
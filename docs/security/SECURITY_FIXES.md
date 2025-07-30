# Security Fixes for Threadr Production Deployment

## Critical Security Fixes Required

### 1. Implement API Key Authentication

Add API key authentication middleware to protect endpoints:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
import secrets
import hashlib

# Store API keys securely (use environment variables or database)
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# In production, store hashed API keys
VALID_API_KEYS = {
    hashlib.sha256(os.getenv("CLIENT_API_KEY", "").encode()).hexdigest(): "client1"
}

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=403, detail="API key required")
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    if key_hash not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return VALID_API_KEYS[key_hash]

# Apply to endpoints
@app.post("/api/generate", dependencies=[Depends(verify_api_key)])
```

### 2. Add Security Headers Middleware

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["threadr.app", "*.threadr.app"])
```

### 3. Implement Proper Rate Limiting with Redis

```python
import redis
from fastapi import Request, HTTPException
import json

# Initialize Redis client
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

async def check_rate_limit_redis(request: Request, api_key: str = Depends(verify_api_key)):
    """Enhanced rate limiting with Redis"""
    # Use API key for authenticated requests, IP for anonymous
    identifier = f"api_key:{api_key}" if api_key else f"ip:{request.client.host}"
    
    # Implement sliding window rate limiting
    now = datetime.now().timestamp()
    window_start = now - (RATE_LIMIT_WINDOW_HOURS * 3600)
    
    pipe = redis_client.pipeline()
    key = f"rate_limit:{identifier}"
    
    # Remove old entries
    pipe.zremrangebyscore(key, 0, window_start)
    # Count current entries
    pipe.zcard(key)
    # Add current request
    pipe.zadd(key, {str(now): now})
    # Set expiry
    pipe.expire(key, RATE_LIMIT_WINDOW_HOURS * 3600)
    
    results = pipe.execute()
    request_count = results[1]
    
    if request_count >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW_HOURS * 3600)}
        )
```

### 4. Add Input Validation and URL Restrictions

```python
from urllib.parse import urlparse
import ipaddress

# Allowed domains for URL scraping
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "").split(",")
BLOCKED_DOMAINS = ["localhost", "127.0.0.1", "0.0.0.0", "*.internal", "*.local"]

async def validate_url_safety(url: str) -> bool:
    """Validate URL is safe to fetch"""
    parsed = urlparse(url)
    
    # Check protocol
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Only HTTP/HTTPS URLs allowed")
    
    # Check for local/internal URLs
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Block local IPs
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise HTTPException(status_code=400, detail="Internal URLs not allowed")
    except ValueError:
        # Not an IP, check domain
        pass
    
    # Check blocked domains
    for blocked in BLOCKED_DOMAINS:
        if blocked.startswith("*"):
            if hostname.endswith(blocked[1:]):
                raise HTTPException(status_code=400, detail="Domain not allowed")
        elif hostname == blocked:
            raise HTTPException(status_code=400, detail="Domain not allowed")
    
    # If whitelist exists, enforce it
    if ALLOWED_DOMAINS and ALLOWED_DOMAINS[0]:
        allowed = False
        for domain in ALLOWED_DOMAINS:
            if domain and (hostname == domain or hostname.endswith(f".{domain}")):
                allowed = True
                break
        if not allowed:
            raise HTTPException(status_code=400, detail="Domain not in allowlist")
    
    return True

# Update scrape_article function
async def scrape_article(url: str) -> Dict[str, str]:
    # Validate URL first
    await validate_url_safety(url)
    
    # Add timeout and size limits
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True, max_redirects=3) as client:
        # Add size limit check
        response = await client.get(str(url))
        if len(response.content) > 5_000_000:  # 5MB limit
            raise HTTPException(status_code=400, detail="Content too large")
        # ... rest of scraping logic
```

### 5. Secure OpenAI API Key Management

```python
# Remove file-based key loading completely
def load_openai_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return api_key

# Add key rotation support
OPENAI_API_KEYS = os.getenv("OPENAI_API_KEYS", "").split(",")  # Multiple keys for rotation
current_key_index = 0

def get_openai_client():
    global current_key_index
    if not OPENAI_API_KEYS or not OPENAI_API_KEYS[0]:
        return None
    
    # Rotate keys on error
    try:
        return OpenAI(api_key=OPENAI_API_KEYS[current_key_index])
    except:
        current_key_index = (current_key_index + 1) % len(OPENAI_API_KEYS)
        return OpenAI(api_key=OPENAI_API_KEYS[current_key_index])
```

### 6. Add Request Size Limits and Timeouts

```python
from fastapi import Request
from starlette.datastructures import Headers

# Add to FastAPI initialization
app = FastAPI(
    title="Threadr API",
    description="Convert articles and text into Twitter/X threads",
    version="1.0.0",
    lifespan=lifespan,
    # Add these security configurations
    openapi_url="/openapi.json" if ENVIRONMENT != "production" else None,  # Disable in prod
    docs_url="/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if ENVIRONMENT != "production" else None,
)

# Request size limiting middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.headers.get("content-length"):
        content_length = int(request.headers["content-length"])
        if content_length > 1_000_000:  # 1MB limit
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large"}
            )
    response = await call_next(request)
    return response
```

### 7. Implement Cloudflare Protection

Add Cloudflare in front of your Railway deployment:

1. **DNS Configuration**:
   - Point your domain to Cloudflare
   - Enable "Proxied" status (orange cloud)

2. **Cloudflare Security Settings**:
   - Enable "Under Attack Mode" if experiencing DDoS
   - Set Security Level to "High"
   - Enable Rate Limiting rules:
     ```
     Rule: Rate limit /api/* endpoints
     - Threshold: 20 requests per minute per IP
     - Action: Challenge
     ```

3. **Page Rules**:
   - Cache static assets
   - Always use HTTPS
   - Enable "Cache Everything" for GET endpoints

4. **Firewall Rules**:
   ```
   # Block suspicious user agents
   (http.user_agent contains "bot" and not http.user_agent contains "googlebot")
   
   # Geo-blocking (if needed)
   (ip.geoip.country in {"CN" "RU"} and not cf.threat_score lt 10)
   
   # Block empty user agents
   (http.user_agent eq "")
   ```

### 8. Production Environment Variables

Create secure environment variables in Railway:

```bash
# Required for production
OPENAI_API_KEY=sk-...  # From OpenAI dashboard
ENVIRONMENT=production
CORS_ORIGINS=https://threadr.vercel.app,https://www.threadr.app
REDIS_URL=redis://...  # From Upstash Redis

# Security settings
RATE_LIMIT_REQUESTS=20  # More reasonable for production
RATE_LIMIT_WINDOW_HOURS=1
MAX_CONTENT_LENGTH=50000  # 50KB limit
REQUEST_TIMEOUT=30
ALLOWED_DOMAINS=medium.com,dev.to,hashnode.dev  # Whitelist trusted sources

# API Keys for clients
CLIENT_API_KEY=generate-secure-random-key
ADMIN_API_KEY=another-secure-random-key

# Monitoring
SENTRY_DSN=https://...  # Error tracking
```

### 9. Implement Logging and Monitoring

```python
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

# Initialize Sentry for error tracking
if ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=ENVIRONMENT,
        traces_sample_rate=0.1,
    )
    app.add_middleware(SentryAsgiMiddleware)

# Add request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log suspicious activity
    if response.status_code == 429:  # Rate limited
        logger.warning(f"Rate limit hit: {request.client.host} - {request.url.path}")
    elif response.status_code >= 400:
        logger.error(f"Error response: {response.status_code} - {request.url.path}")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 10. Security Testing Checklist

Before deploying to production, test:

- [ ] API key authentication works correctly
- [ ] Rate limiting blocks after threshold
- [ ] SSRF protection blocks internal URLs
- [ ] Large payloads are rejected (>1MB)
- [ ] Security headers are present in responses
- [ ] Error messages don't leak sensitive info
- [ ] HTTPS is enforced
- [ ] Cloudflare rules are active
- [ ] Redis rate limiting persists across restarts
- [ ] OpenAI key rotation works on failure

## Implementation Priority

1. **Immediate (Before ANY production traffic)**:
   - API Key Authentication
   - Secure OpenAI key management
   - Remove debug endpoints
   - Fix CORS configuration

2. **Within 24 hours**:
   - Cloudflare setup
   - Redis rate limiting
   - Security headers
   - Input validation

3. **Within 1 week**:
   - Full monitoring setup
   - Load testing
   - Security audit
   - Penetration testing

## Security Contacts

- Report security issues to: security@threadr.app
- Security updates: https://threadr.app/security
- Status page: https://status.threadr.app
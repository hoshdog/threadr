"""
Secure version of main.py with critical security fixes implemented
This file demonstrates how to implement the security improvements
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Union
import httpx
from bs4 import BeautifulSoup
from openai import OpenAI, OpenAIError
from datetime import datetime, timedelta
import os
import asyncio
import re
from contextlib import asynccontextmanager
import logging
import sys
import hashlib
import secrets
from urllib.parse import urlparse
import ipaddress
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Security Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Production Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))
RATE_LIMIT_WINDOW_HOURS = int(os.getenv("RATE_LIMIT_WINDOW_HOURS", "1"))
MAX_TWEET_LENGTH = int(os.getenv("MAX_TWEET_LENGTH", "280"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB

# Security Settings
ALLOWED_DOMAINS = [d.strip() for d in os.getenv("ALLOWED_DOMAINS", "").split(",") if d.strip()]
BLOCKED_DOMAINS = ["localhost", "127.0.0.1", "0.0.0.0", "10.", "172.", "192.168.", ".internal", ".local"]

# API Keys (in production, use database or secure key management service)
# Store hashed keys for additional security
API_KEYS = {}
if os.getenv("CLIENT_API_KEYS"):
    for key in os.getenv("CLIENT_API_KEYS").split(","):
        if key:
            # In production, keys should be pre-hashed
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            API_KEYS[key_hash] = f"client_{len(API_KEYS) + 1}"

# Logging Configuration
logging.basicConfig(
    level=logging.INFO if ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS only in production with HTTPS
        if ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP - adjust based on your frontend needs
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.threadr.app"
        )
        
        return response

# Rate limiting storage (use Redis in production)
rate_limiter_storage: Dict[str, List[datetime]] = {}
rate_limiter_lock = asyncio.Lock()

# OpenAI Configuration
def load_openai_key():
    """Load OpenAI API key from environment only"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not found in environment variables")
        return None
    return api_key

# Initialize OpenAI client
openai_client = None
openai_available = False

def initialize_openai_client():
    """Initialize OpenAI client with proper error handling"""
    global openai_client, openai_available
    try:
        api_key = load_openai_key()
        if api_key:
            openai_client = OpenAI(api_key=api_key)
            openai_available = True
            logger.info("OpenAI client initialized successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {e}")
    
    openai_available = False
    return False

# Initialize on startup
initialize_openai_client()

# API Key Authentication
async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key and return client identifier"""
    if not api_key:
        # In production, always require API key
        if ENVIRONMENT == "production":
            raise HTTPException(
                status_code=403,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"}
            )
        return "anonymous"
    
    # Hash the provided key for comparison
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    if key_hash not in API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return API_KEYS[key_hash]

# URL Validation
async def validate_url_safety(url: str) -> bool:
    """Validate URL is safe to fetch"""
    parsed = urlparse(str(url))
    
    # Check protocol
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Only HTTP/HTTPS URLs allowed")
    
    # Check for missing hostname
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Block IP addresses and internal domains
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise HTTPException(status_code=400, detail="Internal URLs not allowed")
    except ValueError:
        # Not an IP address, check domain
        pass
    
    # Check blocked patterns
    hostname_lower = hostname.lower()
    for blocked in BLOCKED_DOMAINS:
        if blocked in hostname_lower:
            raise HTTPException(status_code=400, detail=f"Domain pattern '{blocked}' is blocked")
    
    # Enforce allowed domains if configured
    if ALLOWED_DOMAINS:
        allowed = False
        for domain in ALLOWED_DOMAINS:
            if hostname_lower == domain.lower() or hostname_lower.endswith(f".{domain.lower()}"):
                allowed = True
                break
        
        if not allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Domain not in allowlist. Allowed domains: {', '.join(ALLOWED_DOMAINS)}"
            )
    
    return True

# Enhanced rate limiting
async def check_rate_limit(request: Request, client_id: str = Depends(verify_api_key)):
    """Check rate limit with client identification"""
    # Use client ID for authenticated requests, IP for anonymous
    identifier = f"client:{client_id}" if client_id != "anonymous" else f"ip:{request.client.host}"
    current_time = datetime.now()
    
    async with rate_limiter_lock:
        # Initialize storage for identifier if needed
        if identifier not in rate_limiter_storage:
            rate_limiter_storage[identifier] = []
        
        # Clean up old requests
        rate_limiter_storage[identifier] = [
            timestamp for timestamp in rate_limiter_storage[identifier]
            if current_time - timestamp < timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
        ]
        
        # Check rate limit
        if len(rate_limiter_storage[identifier]) >= RATE_LIMIT_REQUESTS:
            oldest_request = min(rate_limiter_storage[identifier])
            reset_time = oldest_request + timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
            seconds_until_reset = int((reset_time - current_time).total_seconds())
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": seconds_until_reset
                },
                headers={
                    "Retry-After": str(seconds_until_reset),
                    "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time.timestamp()))
                }
            )
        
        # Record this request
        rate_limiter_storage[identifier].append(current_time)
        
        # Set rate limit headers
        remaining = RATE_LIMIT_REQUESTS - len(rate_limiter_storage[identifier])
        return {
            "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int((current_time + timedelta(hours=RATE_LIMIT_WINDOW_HOURS)).timestamp()))
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting Secure Threadr API in {ENVIRONMENT} mode...")
    logger.info(f"Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_HOURS} hour(s)")
    logger.info(f"API authentication: {'Required' if ENVIRONMENT == 'production' else 'Optional'}")
    logger.info(f"Allowed domains: {ALLOWED_DOMAINS if ALLOWED_DOMAINS else 'All (not recommended)'}")
    
    if not API_KEYS and ENVIRONMENT == "production":
        logger.warning("No API keys configured - authentication will fail!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Secure Threadr API...")

# Initialize FastAPI app with security settings
app = FastAPI(
    title="Threadr API",
    description="Secure API for converting articles into Twitter/X threads",
    version="2.0.0",
    lifespan=lifespan,
    # Disable docs in production
    openapi_url="/openapi.json" if ENVIRONMENT != "production" else None,
    docs_url="/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if ENVIRONMENT != "production" else None,
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Trusted host validation
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "threadr.app",
            "*.threadr.app",
            "threadr-api.railway.app",
            "*.railway.app"
        ]
    )

# Configure CORS securely
if ENVIRONMENT == "production":
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in cors_origins if origin.strip()]
    
    if not allowed_origins:
        allowed_origins = ["https://threadr.app", "https://www.threadr.app"]
else:
    # Development mode - allow localhost
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
    max_age=3600,
)

# Request size limiting middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            if size > MAX_REQUEST_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"Request too large. Maximum size: {MAX_REQUEST_SIZE} bytes"}
                )
    
    response = await call_next(request)
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} for {request.url.path} "
        f"(took {process_time:.3f}s)"
    )
    
    # Add process time header
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    
    return response

# Pydantic models with enhanced validation
class GenerateThreadRequest(BaseModel):
    url: Optional[HttpUrl] = None
    text: Optional[str] = None
    
    @validator('text')
    def validate_text_length(cls, v, values):
        if v:
            # Strip and check length
            v = v.strip()
            if len(v) > MAX_CONTENT_LENGTH:
                raise ValueError(f"Text too long. Maximum {MAX_CONTENT_LENGTH} characters allowed.")
            if len(v) < 10:
                raise ValueError("Text too short. Minimum 10 characters required.")
        return v
    
    @validator('url', always=True)
    def validate_input(cls, v, values):
        if not v and not values.get('text'):
            raise ValueError("Either 'url' or 'text' must be provided")
        if v and values.get('text'):
            raise ValueError("Provide either 'url' or 'text', not both")
        return v

class Tweet(BaseModel):
    number: int
    total: int
    content: str
    character_count: int

class GenerateThreadResponse(BaseModel):
    success: bool
    thread: List[Tweet]
    source_type: str
    title: Optional[str] = None
    processing_time: Optional[float] = None

# Secure article scraping
async def scrape_article(url: str) -> Dict[str, str]:
    """Scrape article content with security measures"""
    # Validate URL first
    await validate_url_safety(url)
    
    # Configure client with security limits
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    timeout = httpx.Timeout(10.0, connect=5.0, read=10.0)
    
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=True,
            max_redirects=3,
            # Add headers to look like a real browser
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        ) as client:
            response = await client.get(str(url))
            
            # Check response size
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > 5_000_000:  # 5MB limit
                raise HTTPException(status_code=400, detail="Content too large (>5MB)")
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if not any(ct in content_type for ct in ["text/html", "text/plain", "application/xhtml"]):
                raise HTTPException(status_code=400, detail="Invalid content type. Expected HTML or text.")
            
            response.raise_for_status()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout while fetching URL")
    except httpx.RequestError as e:
        logger.warning(f"Failed to fetch URL: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Article not found")
        raise HTTPException(status_code=400, detail=f"HTTP error {e.response.status_code}")
    
    # Parse HTML with size check
    if len(response.content) > 5_000_000:
        raise HTTPException(status_code=400, detail="Content too large after download")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = None
    if soup.title:
        title = soup.title.string
    elif soup.find('h1'):
        title = soup.find('h1').get_text()
    
    # Remove unwanted elements
    for element in soup(["script", "style", "meta", "link", "noscript"]):
        element.decompose()
    
    # Extract content
    content = ""
    article_selectors = [
        'article', 'main', '[role="main"]',
        '.article-content', '.post-content',
        '.entry-content', '.content', '#content'
    ]
    
    for selector in article_selectors:
        element = soup.select_one(selector)
        if element:
            paragraphs = element.find_all(['p', 'h2', 'h3', 'h4'])
            if paragraphs:
                content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                break
    
    if not content:
        paragraphs = soup.find_all('p')
        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
    
    # Clean and validate content
    content = re.sub(r'\s+', ' ', content).strip()
    
    if not content or len(content) < 50:
        raise HTTPException(status_code=400, detail="Could not extract sufficient content from URL")
    
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "..."
    
    return {
        "title": title.strip() if title else None,
        "content": content
    }

# Secure endpoints

@app.get("/health")
async def health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT
    }

@app.post("/api/generate", response_model=GenerateThreadResponse)
async def generate_thread(
    request: GenerateThreadRequest,
    client_id: str = Depends(verify_api_key),
    rate_limit_info: dict = Depends(check_rate_limit)
):
    """Generate a Twitter/X thread from URL or text content"""
    start_time = time.time()
    
    try:
        # Get content
        if request.url:
            article_data = await scrape_article(request.url)
            content = article_data["content"]
            title = article_data["title"]
            source_type = "url"
        else:
            content = request.text.strip()
            title = None
            source_type = "text"
        
        # Generate thread (with OpenAI if available)
        tweets = []
        if openai_available and openai_client:
            # Implement OpenAI generation (omitted for brevity)
            pass
        
        # Fallback to basic splitting
        if not tweets:
            words = content.split()
            current_tweet = []
            current_length = 0
            
            for word in words:
                word_length = len(word) + 1
                if current_length + word_length + 10 > MAX_TWEET_LENGTH:  # Reserve space for numbering
                    if current_tweet:
                        tweets.append(' '.join(current_tweet))
                    current_tweet = [word]
                    current_length = word_length
                else:
                    current_tweet.append(word)
                    current_length += word_length
            
            if current_tweet:
                tweets.append(' '.join(current_tweet))
            
            # Add numbering
            if len(tweets) > 1:
                total = len(tweets)
                tweets = [f"{i}/{total} {tweet}" for i, tweet in enumerate(tweets, 1)]
        
        # Create response
        thread = []
        for i, tweet_content in enumerate(tweets, 1):
            thread.append(Tweet(
                number=i,
                total=len(tweets),
                content=tweet_content,
                character_count=len(tweet_content)
            ))
        
        process_time = time.time() - start_time
        
        return GenerateThreadResponse(
            success=True,
            thread=thread,
            source_type=source_type,
            title=title,
            processing_time=round(process_time, 3)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error" if ENVIRONMENT == "production" else str(e)
        )

@app.get("/api/rate-limit-status")
async def rate_limit_status(
    request: Request,
    client_id: str = Depends(verify_api_key)
):
    """Check rate limit status"""
    identifier = f"client:{client_id}" if client_id != "anonymous" else f"ip:{request.client.host}"
    current_time = datetime.now()
    
    async with rate_limiter_lock:
        if identifier in rate_limiter_storage:
            requests = [
                ts for ts in rate_limiter_storage[identifier]
                if current_time - ts < timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
            ]
            requests_used = len(requests)
        else:
            requests_used = 0
    
    requests_remaining = max(0, RATE_LIMIT_REQUESTS - requests_used)
    
    return {
        "limit": RATE_LIMIT_REQUESTS,
        "remaining": requests_remaining,
        "used": requests_used,
        "window_hours": RATE_LIMIT_WINDOW_HOURS,
        "client": client_id
    }

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=429,
        content=exc.detail,
        headers=exc.headers
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting secure server on port {port}")
    
    uvicorn.run(
        "main_secure:app",
        host="0.0.0.0",
        port=port,
        log_level="info" if ENVIRONMENT == "production" else "debug",
        access_log=True
    )
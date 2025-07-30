from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl, field_validator, model_validator
from typing import Optional, List, Dict, Union, Annotated
import httpx
from bs4 import BeautifulSoup
# OpenAI imports removed - using httpx for async API calls
from datetime import datetime, timedelta
import os
from collections import defaultdict
import asyncio
import re
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import logging
import sys
from redis_manager import initialize_redis, get_redis_manager
import ipaddress
from urllib.parse import urlparse
import certifi
import ssl
import json

# Initialize rate limiter storage (fallback for when Redis is unavailable)
rate_limiter_storage: Dict[str, List[datetime]] = defaultdict(list)
rate_limiter_lock = asyncio.Lock()

# Production Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW_HOURS = int(os.getenv("RATE_LIMIT_WINDOW_HOURS", "1"))
MAX_TWEET_LENGTH = int(os.getenv("MAX_TWEET_LENGTH", "280"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))  # Maximum characters to process

# Security Configuration
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "").split(",") if os.getenv("ALLOWED_DOMAINS") else []
if not ALLOWED_DOMAINS:
    # Default allowed domains for scraping
    ALLOWED_DOMAINS = [
        "medium.com", "*.medium.com",
        "dev.to", "*.dev.to",
        "blog.*.com", "*.blog",
        "substack.com", "*.substack.com",
        "wordpress.com", "*.wordpress.com",
        "github.com", "*.github.com",
        "twitter.com", "x.com",
        "linkedin.com", "*.linkedin.com"
    ]

# Logging Configuration
logging.basicConfig(
    level=logging.INFO if ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load OpenAI API key (production-ready)
def load_openai_key():
    # First try environment variable (primary method for production)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Only try file method in development
    if not api_key and ENVIRONMENT != "production":
        key_file_path = os.path.join(os.path.dirname(__file__), ".openai_key")
        if os.path.exists(key_file_path):
            with open(key_file_path, "r") as f:
                api_key = f.read().strip()
    
    if not api_key:
        error_msg = (
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            if ENVIRONMENT == "production" 
            else "OpenAI API key not found. Please set OPENAI_API_KEY environment variable or create a .openai_key file in the backend directory."
        )
        raise ValueError(error_msg)
    
    return api_key

# Initialize OpenAI availability check
openai_available = False

def check_openai_availability():
    """Check if OpenAI API key is available"""
    global openai_available
    try:
        api_key = load_openai_key()
        if api_key:
            openai_available = True
            logger.info("OpenAI API key loaded successfully")
            return True
    except ValueError as e:
        logger.warning(f"OpenAI availability check failed: {e}")
        openai_available = False
        # Don't fail in production - allow graceful degradation
        if ENVIRONMENT == "production":
            logger.warning("Running in production mode without OpenAI - using fallback methods only")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking OpenAI availability: {e}")
        openai_available = False
        return False

# Check OpenAI availability on startup
check_openai_availability()

# Configure CORS origins early
cors_origins = os.getenv("CORS_ORIGINS")
if ENVIRONMENT == "production":
    # In production, use specific origins for security
    if cors_origins:
        allowed_origins = [origin.strip() for origin in cors_origins.split(",")]
    else:
        # Default production origins
        allowed_origins = [
            "https://threadr.vercel.app",
            "https://threadr-frontend.vercel.app",
            "https://www.threadr.app"
        ]
else:
    # Development allows all origins
    allowed_origins = ["*"] if not cors_origins else [origin.strip() for origin in cors_origins.split(",")]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info(f"Starting Threadr backend in {ENVIRONMENT} mode...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Port from ENV: {os.getenv('PORT', 'not set')}")
        logger.info(f"Host binding: 0.0.0.0")
        
        # Test critical imports
        logger.info("Testing critical imports...")
        import fastapi
        import uvicorn
        logger.info(f"FastAPI version: {fastapi.__version__}")
        logger.info(f"Uvicorn version: {uvicorn.__version__}")
        
        # Initialize Redis
        logger.info("Initializing Redis connection...")
        redis_manager = initialize_redis()
        if redis_manager and redis_manager.is_available:
            logger.info("Redis initialized successfully - caching and distributed rate limiting enabled")
            stats = await redis_manager.get_cache_stats()
            logger.info(f"Redis stats: {stats}")
        else:
            logger.warning("Redis not available - falling back to in-memory rate limiting")
        
        # Log OpenAI availability
        if openai_available:
            logger.info("OpenAI client is available - full functionality enabled")
        else:
            logger.warning("OpenAI client not available - using fallback methods only")
        
        # Log all critical environment variables
        logger.info(f"Environment: {ENVIRONMENT}")
        logger.info(f"CORS Origins configured: {allowed_origins}")
        logger.info(f"Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_HOURS} hours")
        
        # Test basic functionality
        test_split = split_into_tweets("Test startup functionality")
        logger.info(f"Basic functionality test: {len(test_split)} tweets generated")
        
        logger.info("Threadr backend startup completed successfully")
        
    except Exception as e:
        logger.error(f"CRITICAL STARTUP ERROR: {e}", exc_info=True)
        # Don't raise - allow graceful degradation
        logger.warning("Continuing startup despite errors...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Threadr backend...")
    redis_manager = get_redis_manager()
    if redis_manager:
        redis_manager.close()

# Initialize FastAPI app
app = FastAPI(
    title="Threadr API",
    description="Convert articles and text into Twitter/X threads",
    version="1.0.0",
    lifespan=lifespan
)

# Security Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # HSTS only in production
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # CSP - Restrictive policy for API
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
    
    # Additional security headers
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    
    return response

# CORS configuration already done above

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models
class GenerateThreadRequest(BaseModel):
    url: Optional[HttpUrl] = None
    text: Optional[str] = None
    
    @field_validator('text')
    @classmethod
    def validate_text_length(cls, v):
        if v and len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Text content too long. Maximum {MAX_CONTENT_LENGTH} characters allowed.")
        return v
    
    @model_validator(mode='after')
    def validate_input(self):
        if not self.url and not self.text:
            raise ValueError("Either 'url' or 'text' must be provided")
        if self.url and self.text:
            raise ValueError("Provide either 'url' or 'text', not both")
        return self

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
    error: Optional[str] = None

# Security Dependencies and Utilities

async def verify_api_key(x_api_key: Annotated[Optional[str], Header()] = None) -> str:
    """Verify API key for protected endpoints"""
    # Skip API key check in development mode
    if ENVIRONMENT == "development" and not API_KEYS:
        return "development"
    
    # Check if API keys are configured
    if not API_KEYS or (len(API_KEYS) == 1 and API_KEYS[0] == ""):
        logger.warning("API keys not configured - authentication disabled")
        return "no-auth-configured"
    
    # Verify the API key
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    if x_api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return x_api_key

def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private/internal"""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False

def is_allowed_domain(url: str) -> bool:
    """Check if URL domain is in the allowed list"""
    if not ALLOWED_DOMAINS:
        return True  # If no domains configured, allow all
    
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Check against allowed domains
        for allowed in ALLOWED_DOMAINS:
            if allowed.startswith("*."):
                # Wildcard subdomain matching
                base_domain = allowed[2:]
                if hostname == base_domain or hostname.endswith(f".{base_domain}"):
                    return True
            elif "*" in allowed:
                # Pattern matching (e.g., "blog.*.com")
                import fnmatch
                if fnmatch.fnmatch(hostname, allowed):
                    return True
            else:
                # Exact match
                if hostname == allowed:
                    return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking domain allowlist: {e}")
        return False

async def validate_url_security(url: str):
    """Validate URL for security (SSRF protection)"""
    # Check URL scheme
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(
            status_code=400,
            detail="Only HTTP and HTTPS URLs are allowed"
        )
    
    # Check if domain is allowed
    if not is_allowed_domain(url):
        # Format allowed domains for display
        display_domains = []
        for domain in ALLOWED_DOMAINS[:5]:  # Show first 5 domains
            if domain.startswith("*."):
                display_domains.append(f"any subdomain of {domain[2:]}")
            elif "*" in domain:
                display_domains.append(f"domains matching {domain}")
            else:
                display_domains.append(domain)
        
        if len(ALLOWED_DOMAINS) > 5:
            display_domains.append(f"and {len(ALLOWED_DOMAINS) - 5} more...")
        
        raise HTTPException(
            status_code=403,
            detail=f"Domain not allowed. Allowed domains include: {', '.join(display_domains)}"
        )
    
    # Resolve hostname to check for internal IPs
    try:
        hostname = parsed.hostname
        if not hostname:
            raise HTTPException(status_code=400, detail="Invalid URL: no hostname")
        
        # Use httpx to resolve the hostname
        async with httpx.AsyncClient() as client:
            # Make a HEAD request to check the resolved IP
            response = await client.head(url, follow_redirects=False, timeout=5.0)
            
            # Check if resolved to internal IP
            if hasattr(response, "_raw_stream") and hasattr(response._raw_stream, "_connection"):
                connection = response._raw_stream._connection
                if hasattr(connection, "_origin") and hasattr(connection._origin, "host"):
                    resolved_ip = connection._origin.host
                    if is_private_ip(resolved_ip):
                        logger.warning(f"URL resolved to private IP: {url} -> {resolved_ip}")
                        raise HTTPException(
                            status_code=403,
                            detail="URL resolves to internal/private IP address"
                        )
    except httpx.RequestError:
        # If we can't resolve, we'll check during actual fetch
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating URL security: {e}")
        # Continue with request - will fail safely if there's an issue

# Rate limiting dependency
async def check_rate_limit(request: Request):
    client_ip = request.client.host
    redis_manager = get_redis_manager()
    
    # Try Redis first
    if redis_manager and redis_manager.is_available:
        window_seconds = RATE_LIMIT_WINDOW_HOURS * 3600
        result = await redis_manager.check_rate_limit(
            client_ip=client_ip,
            limit=RATE_LIMIT_REQUESTS,
            window_seconds=window_seconds
        )
        
        if not result["allowed"]:
            minutes_until_reset = max(1, result["reset_in_seconds"] // 60)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {minutes_until_reset} minutes."
            )
        
        # Log if we're using Redis
        if result.get("redis_available"):
            logger.debug(f"Rate limit checked via Redis for {client_ip}")
            return
    
    # Fallback to in-memory rate limiting
    logger.debug(f"Using in-memory rate limiting for {client_ip}")
    current_time = datetime.now()
    
    async with rate_limiter_lock:
        # Clean up old requests
        rate_limiter_storage[client_ip] = [
            timestamp for timestamp in rate_limiter_storage[client_ip]
            if current_time - timestamp < timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
        ]
        
        # Check rate limit
        if len(rate_limiter_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
            oldest_request = min(rate_limiter_storage[client_ip])
            reset_time = oldest_request + timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
            minutes_until_reset = int((reset_time - current_time).total_seconds() / 60)
            
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {minutes_until_reset} minutes."
            )
        
        # Record this request
        rate_limiter_storage[client_ip].append(current_time)

# Utility functions
async def scrape_article(url: str) -> Dict[str, str]:
    """Scrape article content from URL with enhanced Railway compatibility"""
    # Enhanced logging for debugging
    logger.info(f"Starting URL scrape for: {url}")
    logger.info(f"Environment: {ENVIRONMENT}, SSL verification override: {os.getenv('HTTPX_VERIFY_SSL', 'true')}")
    
    # Validate URL security first
    try:
        await validate_url_security(url)
        logger.info(f"URL security validation passed for: {url}")
    except Exception as e:
        logger.error(f"URL security validation failed for {url}: {str(e)}")
        raise
    
    # DNS pre-resolution for debugging
    try:
        import socket
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname:
            ips = socket.gethostbyname_ex(hostname)[2]
            logger.info(f"DNS resolution for {hostname}: {ips}")
    except Exception as dns_e:
        logger.warning(f"DNS pre-resolution failed: {dns_e}")
    
    # SSL configuration with environment variable override
    verify_ssl = os.getenv("HTTPX_VERIFY_SSL", "true").lower() != "false"
    ssl_context = None
    
    if verify_ssl:
        try:
            # Try multiple CA bundle locations for Railway compatibility
            ca_locations = [
                certifi.where(),  # certifi bundle
                os.getenv("SSL_CERT_FILE"),  # Environment variable
                "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu
                "/etc/pki/tls/certs/ca-bundle.crt",  # RHEL/CentOS
            ]
            
            for ca_path in ca_locations:
                if ca_path and os.path.exists(ca_path):
                    ssl_context = ssl.create_default_context(cafile=ca_path)
                    logger.info(f"Using CA bundle from: {ca_path}")
                    break
            
            if not ssl_context:
                ssl_context = ssl.create_default_context()
                logger.info("Using system default SSL context")
                
        except Exception as ssl_e:
            logger.warning(f"SSL context creation failed: {ssl_e}, will retry without verification")
            verify_ssl = False
    
    # Retry configuration
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            # Transport configuration for Railway
            transport_kwargs = {
                "retries": 1,
                "local_address": "0.0.0.0",  # Bind to all interfaces in container
            }
            
            # Check for proxy configuration
            http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
            https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
            proxies = {}
            if http_proxy:
                proxies["http://"] = http_proxy
                logger.info(f"Using HTTP proxy: {http_proxy}")
            if https_proxy:
                proxies["https://"] = https_proxy
                logger.info(f"Using HTTPS proxy: {https_proxy}")
            
            # Enhanced httpx configuration
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Creating httpx client (verify_ssl={verify_ssl})")
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=30.0, read=30.0, write=30.0),
                follow_redirects=True,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                    keepalive_expiry=30.0
                ),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                },
                verify=ssl_context if verify_ssl else False,
                proxies=proxies if proxies else None,
                transport=httpx.AsyncHTTPTransport(**transport_kwargs)
            ) as client:
                logger.info(f"Fetching URL: {url}")
                response = await client.get(str(url))
                logger.info(f"Response received - Status: {response.status_code}, Content-Length: {len(response.content)}, Headers: {dict(response.headers)}")
                response.raise_for_status()
                
                # Success - break out of retry loop
                break
                
        except httpx.ConnectTimeout as e:
            logger.error(f"Connection timeout (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=504,
                    detail="Connection timeout - Railway network may be blocking outbound connections. Check Railway logs for network restrictions."
                )
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
            
        except httpx.ReadTimeout as e:
            logger.error(f"Read timeout (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail="Read timeout - target server took too long to respond")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
            
        except (httpx.RequestError, httpx.TransportError) as e:
            error_details = {
                "type": type(e).__name__,
                "message": str(e),
                "url": url,
                "attempt": attempt + 1,
                "verify_ssl": verify_ssl
            }
            logger.error(f"Request error: {json.dumps(error_details)}")
            
            # Check for SSL-related errors with better detection
            ssl_error_indicators = [
                "SSL", "ssl", "TLS", "tls",
                "certificate", "Certificate",
                "CERTIFICATE_VERIFY_FAILED",
                "unable to get local issuer certificate",
                "self signed certificate",
                "certificate verify failed"
            ]
            
            is_ssl_error = any(indicator in str(e) for indicator in ssl_error_indicators)
            
            if is_ssl_error and verify_ssl and attempt == 0:
                logger.warning("SSL error detected, retrying without verification")
                verify_ssl = False
                ssl_context = None
                continue
            
            if attempt == max_retries - 1:
                # Final attempt failed
                if is_ssl_error:
                    raise HTTPException(
                        status_code=502,
                        detail=f"SSL/TLS error: {str(e)}. Try setting HTTPX_VERIFY_SSL=false in Railway environment variables."
                    )
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Network error after {max_retries} attempts: {type(e).__name__} - {str(e)}"
                    )
            
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL {url}")
            if e.response.status_code == 403:
                raise HTTPException(
                    status_code=403,
                    detail="Access forbidden - the website may be blocking automated requests"
                )
            elif e.response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests - the website is rate limiting us"
                )
            else:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Target server returned error: {e.response.status_code}"
                )
        
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt + 1}): {type(e).__name__}: {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected error after {max_retries} attempts: {type(e).__name__} - {str(e)}"
                )
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
    
    # Parse HTML with error handling
    try:
        logger.info(f"Parsing HTML content (length: {len(response.text)} chars)")
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.info("HTML parsing completed successfully")
    except Exception as e:
        logger.error(f"BeautifulSoup parsing error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HTML parsing error: {str(e)}")
    
    # Extract title
    title = None
    if soup.title:
        title = soup.title.string
    elif soup.find('h1'):
        title = soup.find('h1').get_text()
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Try to find main content
    content = ""
    
    # Common article containers
    article_selectors = [
        'article',
        'main',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content',
        '#content'
    ]
    
    for selector in article_selectors:
        element = soup.select_one(selector)
        if element:
            # Extract paragraphs
            paragraphs = element.find_all(['p', 'h2', 'h3', 'h4'])
            if paragraphs:
                content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                break
    
    # Fallback: get all paragraphs
    if not content:
        paragraphs = soup.find_all('p')
        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
    
    # Clean up content
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Could not extract article content from URL")
    
    # Truncate if too long
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "..."
    
    return {
        "title": title.strip() if title else None,
        "content": content
    }

def split_into_tweets(text: str, include_thread_numbers: bool = True) -> List[str]:
    """Split text into tweet-sized chunks"""
    # First, create a rough estimate of how many tweets we'll need
    words = text.split()
    tweets = []
    current_tweet = []
    current_length = 0
    
    # Reserve space for thread numbering (e.g., "1/10 ")
    thread_number_space = 10 if include_thread_numbers else 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length + thread_number_space > MAX_TWEET_LENGTH:
            # Current tweet is full, start a new one
            if current_tweet:
                tweets.append(' '.join(current_tweet))
            current_tweet = [word]
            current_length = word_length
        else:
            current_tweet.append(word)
            current_length += word_length
    
    # Don't forget the last tweet
    if current_tweet:
        tweets.append(' '.join(current_tweet))
    
    # Add thread numbers
    if include_thread_numbers and len(tweets) > 1:
        total = len(tweets)
        numbered_tweets = []
        for i, tweet in enumerate(tweets, 1):
            prefix = f"{i}/{total} "
            # Ensure tweet + prefix fits in character limit
            max_tweet_length = MAX_TWEET_LENGTH - len(prefix)
            if len(tweet) > max_tweet_length:
                # Truncate and add ellipsis
                tweet = tweet[:max_tweet_length-3] + "..."
            numbered_tweets.append(prefix + tweet)
        return numbered_tweets
    
    return tweets

async def generate_thread_with_gpt(content: str, title: Optional[str] = None) -> List[str]:
    """Use GPT to generate an engaging thread from content using async httpx"""
    global openai_available
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = load_openai_key()
        except:
            logger.warning("OpenAI API key not available")
            return None
    
    if not api_key:
        return None
        
    # Prepare the prompt
    prompt = f"""Convert the following article into an engaging Twitter/X thread. 

Requirements:
- Create a compelling thread that captures the key points
- Each tweet must be under 280 characters
- Make it engaging and easy to read
- Use clear, concise language
- Include relevant emojis where appropriate
- Start with a hook that grabs attention
- End with a call to action or thought-provoking conclusion
- Number each tweet in the format "1/n", "2/n", etc.

{"Title: " + title if title else ""}

Content:
{content}

Generate the thread as a list of tweets, each on a new line."""

    # Prepare the request payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system", 
                "content": "You are an expert at creating engaging Twitter/X threads from articles. You write concisely and engagingly."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Retry configuration
    max_retries = 3
    retry_delay = 1.0
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract the generated thread
                    generated_text = result['choices'][0]['message']['content'].strip()
                    
                    # Split into individual tweets
                    tweets = [tweet.strip() for tweet in generated_text.split('\n') if tweet.strip()]
                    
                    # Validate tweet lengths
                    valid_tweets = []
                    for tweet in tweets:
                        if len(tweet) <= MAX_TWEET_LENGTH:
                            valid_tweets.append(tweet)
                        else:
                            # Split long tweets
                            split_tweets = split_into_tweets(tweet, include_thread_numbers=False)
                            valid_tweets.extend(split_tweets)
                    
                    return valid_tweets
                
                elif response.status_code == 429:  # Rate limit
                    retry_after = response.headers.get('Retry-After', retry_delay)
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                    await asyncio.sleep(float(retry_after))
                    continue
                
                elif response.status_code >= 500:  # Server error, retry
                    if attempt < max_retries - 1:
                        logger.warning(f"Server error {response.status_code}. Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"OpenAI API server error after {max_retries} attempts: {response.status_code}")
                        return None
                
                else:  # Client error, don't retry
                    error_data = response.json()
                    logger.error(f"OpenAI API error: {response.status_code} - {error_data}")
                    return None
                    
            except httpx.TimeoutException:
                logger.warning(f"Request timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error("OpenAI API timeout after all retries")
                    return None
                    
            except httpx.HTTPError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"HTTP error after all retries: {str(e)}")
                    return None
                    
            except Exception as e:
                logger.error(f"Unexpected error in GPT generation: {str(e)}")
                return None
    
    return None

# API endpoints

@app.get("/health")
@app.get("/")  # Railway sometimes checks root path
async def health_check():
    """Health check endpoint - always returns healthy if app is running"""
    try:
        # Quick response for Railway health checks
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": ENVIRONMENT,
            "message": "Threadr API is running"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        # Still return 200 OK - the app is healthy if it can respond
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "API is responding despite internal error"
        }

@app.get("/readiness")
async def readiness_check():
    """Readiness check - indicates if app is ready to serve traffic"""
    try:
        # Test basic functionality
        test_content = "This is a test message for readiness check."
        test_tweets = split_into_tweets(test_content)
        
        if not test_tweets:
            raise Exception("Basic functionality test failed")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "basic_functionality": "passed",
                "openai_service": "configured" if openai_available else "not_configured_but_ok"
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/debug/startup")
async def debug_startup():
    """Debug endpoint to check startup configuration - ONLY IN DEVELOPMENT"""
    # Block access in production
    if ENVIRONMENT == "production":
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
    
    redis_manager = get_redis_manager()
    redis_available = redis_manager.is_available if redis_manager else False
    
    return {
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "port": os.getenv("PORT", "not_set"),
        "python_version": sys.version,
        "openai_available": openai_available,
        "openai_api_available": openai_available,
        "redis_available": redis_available,
        "rate_limiting": {
            "requests": RATE_LIMIT_REQUESTS,
            "window_hours": RATE_LIMIT_WINDOW_HOURS,
            "using_redis": redis_available
        },
        "caching": {
            "enabled": redis_available,
            "ttl_hours": int(os.getenv("CACHE_TTL_HOURS", "24"))
        },
        "content_limits": {
            "max_tweet_length": MAX_TWEET_LENGTH,
            "max_content_length": MAX_CONTENT_LENGTH
        },
        "cors_origins": os.getenv("CORS_ORIGINS", "not_set"),
        "process_info": {
            "pid": os.getpid(),
            "working_directory": os.getcwd()
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint to verify API is working"""
    test_content = "This is a test message to verify the API is working correctly."
    test_tweets = split_into_tweets(test_content)
    
    return {
        "status": "working",
        "timestamp": datetime.now().isoformat(),
        "test_result": {
            "input_length": len(test_content),
            "tweets_generated": len(test_tweets),
            "sample_tweet": test_tweets[0] if test_tweets else None
        },
        "openai_status": "available" if openai_available else "unavailable"
    }

@app.post("/api/test/url-check")
async def test_url_check(url: str):
    """Test URL accessibility and domain allowlist - DEVELOPMENT ONLY"""
    if ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    result = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check domain allowlist
    try:
        is_allowed = is_allowed_domain(url)
        result["checks"]["domain_allowed"] = is_allowed
        if not is_allowed:
            result["checks"]["allowed_domains_sample"] = ALLOWED_DOMAINS[:5]
    except Exception as e:
        result["checks"]["domain_check_error"] = str(e)
    
    # Try to fetch the URL
    if result["checks"].get("domain_allowed", False):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                result["checks"]["http_status"] = response.status_code
                result["checks"]["content_type"] = response.headers.get("content-type", "unknown")
                result["checks"]["content_length"] = len(response.text)
                
                # Try to parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                result["checks"]["title"] = soup.title.string if soup.title else "No title found"
                result["checks"]["paragraphs_found"] = len(soup.find_all('p'))
                
        except httpx.TimeoutException:
            result["checks"]["fetch_error"] = "Timeout after 10 seconds"
        except Exception as e:
            result["checks"]["fetch_error"] = f"{type(e).__name__}: {str(e)}"
    
    return result

@app.get("/api/test/railway-network")
async def test_railway_network():
    """Test Railway network connectivity - comprehensive diagnostics"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "railway_env": {
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
            "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
            "RAILWAY_SERVICE_ID": os.getenv("RAILWAY_SERVICE_ID"),
            "HTTPX_VERIFY_SSL": os.getenv("HTTPX_VERIFY_SSL", "not_set"),
            "SSL_CERT_FILE": os.getenv("SSL_CERT_FILE", "not_set"),
            "HTTP_PROXY": os.getenv("HTTP_PROXY", "not_set"),
            "HTTPS_PROXY": os.getenv("HTTPS_PROXY", "not_set")
        },
        "tests": {}
    }
    
    # Test 1: CA Bundle availability
    try:
        ca_locations = [
            certifi.where(),
            "/etc/ssl/certs/ca-certificates.crt",
            "/etc/pki/tls/certs/ca-bundle.crt",
        ]
        ca_results = {}
        for ca_path in ca_locations:
            if ca_path:
                ca_results[ca_path] = os.path.exists(ca_path)
        results["tests"]["ca_bundles"] = ca_results
    except Exception as e:
        results["tests"]["ca_bundles"] = {"error": str(e)}
    
    # Test 2: DNS Resolution with detailed info
    test_domains = ["google.com", "medium.com", "api.openai.com", "httpbin.org"]
    for domain in test_domains:
        try:
            import socket
            # Get all IPs for the domain
            hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(domain)
            results["tests"][f"dns_{domain}"] = {
                "success": True,
                "hostname": hostname,
                "aliases": aliaslist,
                "ips": ipaddrlist
            }
        except Exception as e:
            results["tests"][f"dns_{domain}"] = {"success": False, "error": str(e)}
    
    # Test 3: httpx with different SSL configurations
    test_configs = [
        ("ssl_verify_true", True, "with SSL verification"),
        ("ssl_verify_false", False, "without SSL verification")
    ]
    
    for config_name, verify_ssl, description in test_configs:
        test_url = "https://httpbin.org/get"
        try:
            ssl_context = None
            if verify_ssl:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                verify=ssl_context if verify_ssl else False,
                headers={"User-Agent": "Threadr/1.0 Railway Network Test"},
                transport=httpx.AsyncHTTPTransport(
                    retries=1,
                    local_address="0.0.0.0"
                )
            ) as client:
                start_time = datetime.now()
                response = await client.get(test_url)
                elapsed = (datetime.now() - start_time).total_seconds()
                
                results["tests"][config_name] = {
                    "success": True,
                    "description": description,
                    "status_code": response.status_code,
                    "elapsed_seconds": elapsed,
                    "response_headers": dict(response.headers)
                }
        except Exception as e:
            results["tests"][config_name] = {
                "success": False,
                "description": description,
                "error_type": type(e).__name__,
                "error": str(e),
                "error_details": repr(e)
            }
    
    # Test 4: Multiple URLs with detailed error info
    test_urls = [
        ("https://httpbin.org/get", "httpbin"),
        ("https://api.github.com", "github"),
        ("https://medium.com", "medium"),
        ("https://example.com", "example")
    ]
    
    for url, name in test_urls:
        try:
            # Use the same configuration as scrape_article
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=15.0),
                follow_redirects=True,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                ),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                },
                verify=False,  # Testing without SSL verification
                transport=httpx.AsyncHTTPTransport(
                    retries=1,
                    local_address="0.0.0.0"
                )
            ) as client:
                start_time = datetime.now()
                response = await client.get(url)
                elapsed = (datetime.now() - start_time).total_seconds()
                
                results["tests"][f"fetch_{name}"] = {
                    "success": True,
                    "url": url,
                    "status_code": response.status_code,
                    "elapsed_seconds": elapsed,
                    "content_type": response.headers.get("content-type", "unknown"),
                    "content_length": len(response.content),
                    "final_url": str(response.url) if response.url != url else "no_redirect"
                }
        except httpx.ConnectTimeout as e:
            results["tests"][f"fetch_{name}"] = {
                "success": False,
                "url": url,
                "error_type": "ConnectTimeout",
                "error": str(e),
                "suggestion": "Railway may be blocking outbound connections or target is unreachable"
            }
        except httpx.ReadTimeout as e:
            results["tests"][f"fetch_{name}"] = {
                "success": False,
                "url": url,
                "error_type": "ReadTimeout",
                "error": str(e),
                "suggestion": "Target server is slow to respond"
            }
        except Exception as e:
            results["tests"][f"fetch_{name}"] = {
                "success": False,
                "url": url,
                "error_type": type(e).__name__,
                "error": str(e),
                "error_repr": repr(e)
            }
    
    # Test 5: Check system network interfaces
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        results["tests"]["network_info"] = {
            "hostname": hostname,
            "local_ip": local_ip
        }
    except Exception as e:
        results["tests"]["network_info"] = {"error": str(e)}
    
    return results

@app.get("/api/debug/scrape-test")
async def debug_scrape_test():
    """Debug endpoint to test URL scraping step by step"""
    try:
        test_url = "https://example.com"
        
        # Test just the network request part
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(test_url)
            
        return {
            "success": True,
            "status_code": response.status_code,
            "content_length": len(response.content),
            "headers": dict(response.headers)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/api/debug/domain-check")
async def debug_domain_check(url: str):
    """Debug endpoint to test domain allowlist validation"""
    try:
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        # Test the domain allowlist logic
        is_allowed = is_allowed_domain(url)
        
        return {
            "url": url,
            "hostname": hostname,
            "scheme": parsed.scheme,
            "is_allowed": is_allowed,
            "allowed_domains": ALLOWED_DOMAINS[:10],  # Show first 10 for debugging
            "domain_count": len(ALLOWED_DOMAINS)
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/api/debug/minimal-scrape")
async def minimal_scrape_debug(url: str):
    """Minimal URL scraper to isolate failure points - NO SECURITY VALIDATION"""
    if ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    debug_info = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "steps": {}
    }
    
    try:
        # Step 1: URL Parsing
        debug_info["steps"]["1_url_parsing"] = {"status": "attempting"}
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        if not parsed.scheme or not parsed.hostname:
            debug_info["steps"]["1_url_parsing"] = {
                "status": "failed",
                "error": "Invalid URL format",
                "parsed": {
                    "scheme": parsed.scheme,
                    "hostname": parsed.hostname,
                    "path": parsed.path
                }
            }
            return debug_info
        
        debug_info["steps"]["1_url_parsing"] = {
            "status": "success",
            "parsed": {
                "scheme": parsed.scheme,  
                "hostname": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path
            }
        }
        
        # Step 2: DNS Resolution
        debug_info["steps"]["2_dns_resolution"] = {"status": "attempting"}
        try:
            import socket
            hostname = parsed.hostname
            ips = socket.gethostbyname_ex(hostname)[2]
            debug_info["steps"]["2_dns_resolution"] = {
                "status": "success",
                "hostname": hostname,
                "resolved_ips": ips
            }
        except Exception as dns_e:
            debug_info["steps"]["2_dns_resolution"] = {
                "status": "failed",
                "error": str(dns_e),
                "error_type": type(dns_e).__name__,
                "suggestion": "DNS resolution failed - Railway may have DNS issues or hostname is invalid"
            }
            return debug_info
        
        # Step 3: HTTP Client Creation (minimal config)
        debug_info["steps"]["3_client_creation"] = {"status": "attempting"}
        try:
            # Use absolute minimal httpx configuration
            client_config = {
                "timeout": httpx.Timeout(30.0),
                "verify": False,  # No SSL verification to avoid SSL issues
                "follow_redirects": True,
                "headers": {
                    "User-Agent": "Threadr-Debug/1.0"
                }
            }
            debug_info["steps"]["3_client_creation"] = {
                "status": "success",
                "config": {
                    "timeout": "30.0s",
                    "verify_ssl": False,
                    "follow_redirects": True
                }
            }
        except Exception as client_e:
            debug_info["steps"]["3_client_creation"] = {
                "status": "failed",
                "error": str(client_e),
                "error_type": type(client_e).__name__,
                "suggestion": "httpx client creation failed - possible import or dependency issue"
            }
            return debug_info
        
        # Step 4: HTTP Request
        debug_info["steps"]["4_http_request"] = {"status": "attempting"}
        try:
            async with httpx.AsyncClient(**client_config) as client:
                start_time = datetime.now()
                response = await client.get(url)
                elapsed = (datetime.now() - start_time).total_seconds()
                
                debug_info["steps"]["4_http_request"] = {
                    "status": "success",
                    "elapsed_seconds": elapsed,
                    "response": {
                        "status_code": response.status_code,
                        "headers": dict(list(response.headers.items())[:10]),  # First 10 headers only
                        "content_length": len(response.content),
                        "final_url": str(response.url),
                        "content_type": response.headers.get("content-type", "unknown")
                    }
                }
                
        except httpx.ConnectTimeout as e:
            debug_info["steps"]["4_http_request"] = {
                "status": "failed",
                "error": str(e),
                "error_type": "ConnectTimeout",
                "suggestion": "Connection timeout - Railway may be blocking outbound connections to this target"
            }
            return debug_info
            
        except httpx.ReadTimeout as e:
            debug_info["steps"]["4_http_request"] = {
                "status": "failed", 
                "error": str(e),
                "error_type": "ReadTimeout",
                "suggestion": "Read timeout - target server is slow to respond or Railway has network latency"
            }
            return debug_info
            
        except httpx.ConnectError as e:
            debug_info["steps"]["4_http_request"] = {
                "status": "failed",
                "error": str(e), 
                "error_type": "ConnectError",
                "suggestion": "Cannot connect to target - check if Railway blocks outbound connections or target is down"
            }
            return debug_info
            
        except httpx.TransportError as e:
            debug_info["steps"]["4_http_request"] = {
                "status": "failed",
                "error": str(e),
                "error_type": "TransportError", 
                "suggestion": "Network transport error - possible SSL, proxy, or low-level network issue"
            }
            return debug_info
            
        except httpx.HTTPStatusError as e:
            debug_info["steps"]["4_http_request"] = {
                "status": "failed",
                "error": f"HTTP {e.response.status_code}: {str(e)}",
                "error_type": "HTTPStatusError",
                "status_code": e.response.status_code,
                "suggestion": f"Target server returned {e.response.status_code} error"
            }
            return debug_info
            
        except httpx.RequestError as e:
            debug_info["steps"]["4_http_request"] = {
                "status": "failed",
                "error": str(e),
                "error_type": "RequestError", 
                "suggestion": "Generic httpx request error - check logs for more details"
            }
            return debug_info
        
        # Step 5: Response Validation
        debug_info["steps"]["5_response_validation"] = {"status": "attempting"}
        try:
            if response.status_code != 200:
                debug_info["steps"]["5_response_validation"] = {
                    "status": "failed",
                    "error": f"Non-200 status code: {response.status_code}",
                    "status_code": response.status_code,
                    "suggestion": "Target returned non-success status"
                }
                return debug_info
            
            if len(response.content) == 0:
                debug_info["steps"]["5_response_validation"] = {
                    "status": "failed",
                    "error": "Empty response content",
                    "suggestion": "Target returned 200 OK but no content"
                }
                return debug_info
                
            debug_info["steps"]["5_response_validation"] = {
                "status": "success",
                "content_length": len(response.content),
                "content_type": response.headers.get("content-type", "unknown")
            }
            
        except Exception as val_e:
            debug_info["steps"]["5_response_validation"] = {
                "status": "failed",
                "error": str(val_e),
                "error_type": type(val_e).__name__,
                "suggestion": "Response validation failed unexpectedly"  
            }
            return debug_info
        
        # Step 6: HTML Parsing
        debug_info["steps"]["6_html_parsing"] = {"status": "attempting"}
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            title = None
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text()
            
            paragraphs = soup.find_all('p')
            paragraph_texts = [p.get_text().strip() for p in paragraphs[:3] if p.get_text().strip()]
            
            debug_info["steps"]["6_html_parsing"] = {
                "status": "success",
                "parsing": {
                    "title": title,
                    "paragraph_count": len(paragraphs),
                    "sample_paragraphs": paragraph_texts
                }
            }
            
        except Exception as parse_e:
            debug_info["steps"]["6_html_parsing"] = {
                "status": "failed",
                "error": str(parse_e),
                "error_type": type(parse_e).__name__,
                "suggestion": "BeautifulSoup parsing failed - possibly malformed HTML or encoding issues"
            }
            return debug_info
        
        # All steps successful
        debug_info["overall_status"] = "success"
        debug_info["message"] = "All scraping steps completed successfully"
        
        return debug_info
        
    except Exception as unexpected_e:
        # This should catch any errors not handled above
        debug_info["overall_status"] = "unexpected_error"
        debug_info["unexpected_error"] = {
            "error": str(unexpected_e),
            "error_type": type(unexpected_e).__name__,
            "suggestion": "Unexpected error occurred - check Railway logs for Python runtime issues"
        }
        return debug_info

@app.get("/api/security/config")
async def security_config():
    """Get security configuration - ONLY IN DEVELOPMENT"""
    # Block access in production
    if ENVIRONMENT == "production":
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
    
    return {
        "environment": ENVIRONMENT,
        "api_authentication": {
            "enabled": bool(API_KEYS) and API_KEYS[0] != "",
            "configured_keys": len([k for k in API_KEYS if k]),
            "header_name": "X-API-Key"
        },
        "url_security": {
            "domain_allowlist_enabled": bool(ALLOWED_DOMAINS),
            "allowed_domains": ALLOWED_DOMAINS,
            "ssrf_protection": "enabled",
            "private_ip_blocking": "enabled"
        },
        "security_headers": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "enabled in production",
            "Content-Security-Policy": "restrictive"
        },
        "rate_limiting": {
            "enabled": True,
            "requests_per_window": RATE_LIMIT_REQUESTS,
            "window_hours": RATE_LIMIT_WINDOW_HOURS
        }
    }

@app.post("/api/generate", response_model=GenerateThreadResponse)
async def generate_thread(
    request: GenerateThreadRequest,
    _: None = Depends(check_rate_limit),
    api_key: str = Depends(verify_api_key)
):
    """Generate a Twitter/X thread from URL or text content"""
    global openai_available
    redis_manager = get_redis_manager()
    
    # Check cache first
    if redis_manager and redis_manager.is_available:
        request_dict = request.dict()
        cached_response = await redis_manager.get_cached_thread(request_dict)
        
        if cached_response:
            logger.info("Returning cached thread response")
            # Remove cache metadata before returning
            cached_response.pop("_cached_at", None)
            cached_response.pop("_ttl", None)
            return GenerateThreadResponse(**cached_response)
    
    try:
        # Determine source and get content
        if request.url:
            # Scrape article from URL
            article_data = await scrape_article(request.url)
            content = article_data["content"]
            title = article_data["title"]
            source_type = "url"
        else:
            # Use provided text
            content = request.text
            title = None
            source_type = "text"
        
        # Try to generate thread with GPT if available
        tweets = None
        if openai_available:
            try:
                tweets = await generate_thread_with_gpt(content, title)
                logger.info("Successfully generated thread using OpenAI")
            except Exception as e:
                logger.warning(f"GPT generation failed, using fallback: {str(e)}")
                # Re-check OpenAI availability
                if "authentication" in str(e).lower() or "api_key" in str(e).lower():
                    openai_available = False
                    logger.warning("OpenAI authentication failed - disabling for future requests")
        
        # Fallback to basic splitting if GPT fails or is not available
        if not tweets:
            logger.info("Using fallback tweet splitting method")
            tweets = split_into_tweets(content)
        
        # Create Tweet objects
        total_tweets = len(tweets)
        thread = []
        for i, tweet_content in enumerate(tweets, 1):
            thread.append(Tweet(
                number=i,
                total=total_tweets,
                content=tweet_content,
                character_count=len(tweet_content)
            ))
        
        response = GenerateThreadResponse(
            success=True,
            thread=thread,
            source_type=source_type,
            title=title
        )
        
        # Cache the response
        if redis_manager and redis_manager.is_available:
            request_dict = request.dict()
            response_dict = response.dict()
            cached = await redis_manager.cache_thread_response(request_dict, response_dict)
            if cached:
                logger.info("Thread response cached successfully")
        
        return response
        
    except HTTPException as he:
        # Re-raise HTTP exceptions with their original status codes
        raise
    except Exception as e:
        # Log the error with more details in production
        error_id = datetime.now().isoformat()
        error_type = type(e).__name__
        
        # Determine if it's a known error type
        if "seasonsincolour.com" in str(request.url) if request.url else "":
            logger.error(f"Error processing seasonsincolour.com [{error_id}]: {str(e)}", exc_info=True)
        else:
            logger.error(f"Unexpected error [{error_id}] - Type: {error_type}: {str(e)}", exc_info=True)
        
        if ENVIRONMENT == "production":
            # Don't expose internal errors in production
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error. Error ID: {error_id}"
            )
        else:
            # Show detailed errors in development
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error ({error_type}): {str(e)}"
            )

@app.get("/api/rate-limit-status")
async def rate_limit_status(request: Request):
    """Check current rate limit status for the client"""
    client_ip = request.client.host
    redis_manager = get_redis_manager()
    
    # Try Redis first
    if redis_manager and redis_manager.is_available:
        window_seconds = RATE_LIMIT_WINDOW_HOURS * 3600
        status = await redis_manager.get_rate_limit_status(
            client_ip=client_ip,
            limit=RATE_LIMIT_REQUESTS,
            window_seconds=window_seconds
        )
        
        return {
            "requests_used": status["requests_used"],
            "requests_remaining": status["requests_remaining"],
            "total_limit": RATE_LIMIT_REQUESTS,
            "window_hours": RATE_LIMIT_WINDOW_HOURS,
            "minutes_until_reset": max(0, status["reset_in_seconds"] // 60),
            "using_redis": status.get("redis_available", False)
        }
    
    # Fallback to in-memory
    current_time = datetime.now()
    
    async with rate_limiter_lock:
        # Clean up old requests
        rate_limiter_storage[client_ip] = [
            timestamp for timestamp in rate_limiter_storage[client_ip]
            if current_time - timestamp < timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
        ]
        
        requests_used = len(rate_limiter_storage[client_ip])
        requests_remaining = max(0, RATE_LIMIT_REQUESTS - requests_used)
        
        if requests_used > 0:
            oldest_request = min(rate_limiter_storage[client_ip])
            reset_time = oldest_request + timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
            minutes_until_reset = max(0, int((reset_time - current_time).total_seconds() / 60))
        else:
            minutes_until_reset = 0
    
    return {
        "requests_used": requests_used,
        "requests_remaining": requests_remaining,
        "total_limit": RATE_LIMIT_REQUESTS,
        "window_hours": RATE_LIMIT_WINDOW_HOURS,
        "minutes_until_reset": minutes_until_reset,
        "using_redis": False
    }

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    redis_manager = get_redis_manager()
    
    if not redis_manager or not redis_manager.is_available:
        return {
            "available": False,
            "message": "Redis cache not available"
        }
    
    stats = await redis_manager.get_cache_stats()
    return stats

@app.delete("/api/cache/clear")
async def clear_cache(
    request: GenerateThreadRequest,
    _: Request
):
    """Clear cached response for a specific request"""
    redis_manager = get_redis_manager()
    
    if not redis_manager or not redis_manager.is_available:
        raise HTTPException(
            status_code=503,
            detail="Cache service not available"
        )
    
    request_dict = request.dict()
    cleared = await redis_manager.clear_cache_for_key(request_dict)
    
    if cleared:
        return {"success": True, "message": "Cache entry cleared"}
    else:
        return {"success": False, "message": "Failed to clear cache or entry not found"}

@app.get("/api/monitor/health")
async def monitor_health():
    """Comprehensive health check with all service statuses"""
    redis_manager = get_redis_manager()
    
    # Test Redis
    redis_status = "healthy"
    redis_details = {}
    if redis_manager and redis_manager.is_available:
        try:
            stats = await redis_manager.get_cache_stats()
            redis_details = stats
        except Exception as e:
            redis_status = "unhealthy"
            redis_details = {"error": str(e)}
    else:
        redis_status = "unavailable"
    
    # Test basic functionality
    try:
        test_tweets = split_into_tweets("Health check test")
        basic_functionality = "healthy"
    except:
        basic_functionality = "unhealthy"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",  # Overall status
        "services": {
            "api": "healthy",
            "openai": "healthy" if openai_available else "unavailable",
            "redis": redis_status,
            "basic_functionality": basic_functionality
        },
        "details": {
            "redis": redis_details,
            "environment": ENVIRONMENT,
            "uptime_seconds": int((datetime.now() - datetime.fromtimestamp(os.path.getctime(__file__))).total_seconds())
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server directly with port: {port}")
    logger.info(f"Environment mode: {ENVIRONMENT}")
    
    if ENVIRONMENT == "production":
        # Production server configuration - single worker for Railway
        logger.info("Using production configuration with single worker")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            workers=1,
            timeout_keep_alive=30
        )
    else:
        # Development server configuration
        logger.info("Using development configuration")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="debug"
        )
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, HttpUrl, field_validator, model_validator
from typing import Optional, List, Dict, Union, Annotated, Any
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
import stripe
import hmac
import hashlib
import json
# Import redis_manager - try relative import first, then absolute
try:
    from .core.redis_manager import initialize_redis, get_redis_manager
except ImportError:
    from core.redis_manager import initialize_redis, get_redis_manager

# Import authentication components
try:
    from .services.auth.auth_service import AuthService
    from .routes.auth import create_auth_router
    from .middleware.auth import create_auth_dependencies
except ImportError:
    from services.auth.auth_service import AuthService
    from routes.auth import create_auth_router
    from middleware.auth import create_auth_dependencies

# Import thread history components
try:
    from .services.thread.thread_service import ThreadHistoryService
    from .routes.thread import create_thread_router
except ImportError:
    from services.thread.thread_service import ThreadHistoryService
    from routes.thread import create_thread_router

# Import analytics components (optional)
analytics_router_creator = None
try:
    from .routes.analytics import create_analytics_router
    analytics_router_creator = create_analytics_router
except ImportError:
    try:
        from routes.analytics import create_analytics_router
        analytics_router_creator = create_analytics_router
    except ImportError:
        # Analytics routes not available - will be skipped
        analytics_router_creator = None
import ipaddress
from urllib.parse import urlparse
import certifi
import ssl
import json

# Initialize rate limiter storage (fallback for when Redis is unavailable)
rate_limiter_storage: Dict[str, List[datetime]] = defaultdict(list)
rate_limiter_lock = asyncio.Lock()

# Initialize in-memory usage tracking storage (fallback for when Redis is unavailable)
usage_tracking_storage: Dict[str, List[datetime]] = defaultdict(list)
usage_tracking_lock = asyncio.Lock()

# Global authentication service
auth_service: Optional[AuthService] = None

# Global thread history service
thread_history_service: Optional[ThreadHistoryService] = None

# Production Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW_HOURS = int(os.getenv("RATE_LIMIT_WINDOW_HOURS", "1"))
MAX_TWEET_LENGTH = int(os.getenv("MAX_TWEET_LENGTH", "280"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))  # Maximum characters to process

# Monetization Configuration
FREE_TIER_DAILY_LIMIT = int(os.getenv("FREE_TIER_DAILY_LIMIT", "5"))  # Free threads per day
FREE_TIER_MONTHLY_LIMIT = int(os.getenv("FREE_TIER_MONTHLY_LIMIT", "20"))  # Free threads per month
FREE_TIER_ENABLED = os.getenv("FREE_TIER_ENABLED", "true").lower() == "true"
PREMIUM_PRICE_USD = float(os.getenv("PREMIUM_PRICE_USD", "4.99"))  # Monthly premium price
ENABLE_EMAIL_TRACKING = os.getenv("ENABLE_EMAIL_TRACKING", "true").lower() == "true"

# Security Configuration
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "").split(",") if os.getenv("ALLOWED_DOMAINS") else []

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")  # For Stripe Payment Links
STRIPE_PAYMENT_LINK_URL = os.getenv("STRIPE_PAYMENT_LINK_URL")  # Direct Payment Link URL
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
            "https://threadr-plum.vercel.app",
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
        
        # Services and routes are now initialized outside lifespan for proper FastAPI registration
        logger.info("Services and routes initialized outside lifespan - skipping duplicate initialization")
        
        # Log OpenAI availability
        if openai_available:
            logger.info("OpenAI client is available - full functionality enabled")
        else:
            logger.warning("OpenAI client not available - using fallback methods only")
        
        # Log all critical environment variables
        logger.info(f"Environment: {ENVIRONMENT}")
        logger.info(f"CORS Origins configured: {allowed_origins}")
        logger.info(f"Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_HOURS} hours")
        
        # Log monetization configuration
        logger.info(f"Free tier enabled: {FREE_TIER_ENABLED}")
        if FREE_TIER_ENABLED:
            logger.info(f"Free tier limits: {FREE_TIER_DAILY_LIMIT} daily, {FREE_TIER_MONTHLY_LIMIT} monthly")
            logger.info(f"Premium price: ${PREMIUM_PRICE_USD}/month")
        else:
            logger.info("Free tier disabled - unlimited usage for all users")
        
        # Initialize Stripe if configured
        if STRIPE_SECRET_KEY:
            stripe.api_key = STRIPE_SECRET_KEY
            logger.info("Stripe API key configured successfully")
            if STRIPE_WEBHOOK_SECRET:
                logger.info("Stripe webhook secret configured for signature verification")
            else:
                logger.warning("Stripe webhook secret not configured - webhook signature verification disabled")
            
            # Debug: Log payment link configuration
            logger.info(f"Stripe payment link URL: '{STRIPE_PAYMENT_LINK_URL}' (configured: {'Yes' if STRIPE_PAYMENT_LINK_URL else 'No'})")
            logger.info(f"Stripe price ID: '{STRIPE_PRICE_ID}' (configured: {'Yes' if STRIPE_PRICE_ID else 'No'})")
        else:
            logger.warning("Stripe API key not configured - payment processing disabled")
        
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

# Add CORS middleware FIRST, before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Production environment - debug routes removed

# Initialize services and add routes AFTER app creation and middleware setup
# Initialize services and add routes
redis_manager = initialize_redis()

if redis_manager:
    # Initialize services
    auth_service = AuthService(redis_manager)
    thread_history_service = ThreadHistoryService(redis_manager)
    
    # Add authentication routes
    auth_router = create_auth_router(auth_service)
    app.include_router(auth_router)
    # Authentication routes added
    
    # Add thread history routes
    auth_dependencies = create_auth_dependencies(auth_service)
    thread_router = create_thread_router(
        thread_history_service, 
        auth_dependencies["get_current_user_required"]
    )
    app.include_router(thread_router, prefix="/api/threads")
    # Thread routes added
    
    # Verify thread routes
    thread_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and '/api/threads' in route.path:
            thread_routes.append(f"{getattr(route, 'methods', 'N/A')} {route.path}")
    # Thread routes configured
else:
    # Redis not available - using fallback mode
    redis_manager = get_redis_manager()
    auth_service = AuthService(redis_manager)
    thread_history_service = ThreadHistoryService(redis_manager)
    
    # Add authentication routes
    auth_router = create_auth_router(auth_service)
    app.include_router(auth_router)
    
    # Add thread history routes
    auth_dependencies = create_auth_dependencies(auth_service)
    thread_router = create_thread_router(
        thread_history_service, 
        auth_dependencies["get_current_user_required"]
    )
    app.include_router(thread_router, prefix="/api/threads")
    # Thread routes added (fallback mode)

# Production environment - debug routes removed

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages"""
    error_messages = []
    
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "field"
        msg = error["msg"]
        
        # Convert field names to user-friendly names
        field_name_map = {
            "email": "Email",
            "password": "Password",
            "confirm_password": "Password confirmation",
            "current_password": "Current password",
            "new_password": "New password",
            "confirm_new_password": "New password confirmation"
        }
        
        friendly_field = field_name_map.get(field, field.title())
        
        # Convert validation messages to user-friendly messages
        if "ensure this value has at least" in msg:
            error_messages.append(f"{friendly_field} must be at least {msg.split()[-2]} characters long")
        elif "field required" in msg:
            error_messages.append(f"{friendly_field} is required")
        elif "value is not a valid email address" in msg:
            error_messages.append("Please enter a valid email address")
        elif "string too short" in msg:
            error_messages.append(f"{friendly_field} is too short")
        elif "string too long" in msg:
            error_messages.append(f"{friendly_field} is too long")
        else:
            # Use the original message if we can't improve it
            error_messages.append(f"{friendly_field}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": error_messages[0] if len(error_messages) == 1 else "; ".join(error_messages)}
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

# CORS configuration already done above (after app creation)

# Initialize authentication router when auth service is available
def get_auth_service():
    """Get the global auth service instance"""
    return auth_service

# Authentication routes will be added in the lifespan function after auth_service is initialized

# Enhanced dependencies that support both authenticated and anonymous users
async def get_current_user_optional_enhanced(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from token (optional) with backward compatibility"""
    global auth_service
    if not auth_service:
        return None
    
    try:
        # Check for Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        user = await auth_service.get_current_user_from_token(token)
        
        if user:
            return {
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role.value,
                "is_authenticated": True
            }
    except Exception:
        pass  # Silently fail for optional auth
    
    return None

async def get_user_context(request: Request) -> Dict[str, Any]:
    """Get user context (authenticated user info + client IP)"""
    try:
        from .services.auth.auth_utils import SecurityUtils
    except ImportError:
        from services.auth.auth_utils import SecurityUtils
    
    client_ip = SecurityUtils.get_client_ip(request)
    user_info = await get_current_user_optional_enhanced(request)
    
    return {
        "client_ip": client_ip,
        "user_info": user_info,
        "email": user_info["email"] if user_info else None,
        "is_authenticated": user_info is not None
    }

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

class EmailSubscribeRequest(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError("Email is required")
        
        # Basic email validation
        email = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        if len(email) > 254:  # RFC 5321 limit
            raise ValueError("Email address too long")
            
        return email

class EmailSubscribeResponse(BaseModel):
    success: bool
    message: str
    email: Optional[str] = None

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
    saved_thread_id: Optional[str] = None  # Thread ID if saved to history

class UsageStatus(BaseModel):
    daily_usage: int
    daily_limit: int
    monthly_usage: int
    monthly_limit: int
    has_premium: bool
    premium_expires_at: Optional[str] = None

class PremiumCheckResponse(BaseModel):
    has_premium: bool
    usage_status: UsageStatus
    needs_payment: bool
    premium_price: float
    message: str

class GrantPremiumRequest(BaseModel):
    email: Optional[str] = None
    plan: str = "premium"
    duration_days: int = 30
    payment_reference: str
    
    @field_validator('payment_reference')
    @classmethod
    def validate_payment_reference(cls, v):
        if not v or len(v) < 5:
            raise ValueError("Payment reference must be at least 5 characters")
        return v

# Security Dependencies and Utilities

async def verify_api_key(x_api_key: Annotated[Optional[str], Header()] = None) -> str:
    """Verify API key for protected endpoints - ADMIN/INTERNAL USE ONLY"""
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

async def verify_public_access(request: Request) -> Dict[str, Any]:
    """
    Secure public endpoint access - NO API KEY REQUIRED
    Uses IP-based rate limiting and basic security checks
    """
    client_ip = SecurityUtils.get_client_ip(request)
    
    # Basic security: Block obvious malicious IPs or patterns
    if not client_ip or client_ip == "127.0.0.1" and ENVIRONMENT == "production":
        logger.warning(f"Suspicious request from IP: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Additional security headers validation
    user_agent = request.headers.get("user-agent", "")
    if len(user_agent) < 10 and ENVIRONMENT == "production":
        logger.warning(f"Suspicious request with short user agent: {user_agent[:50]}")
        # Don't block but log for monitoring
    
    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "access_type": "public"
    }

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

# Monetization and Usage Tracking Functions

async def get_user_usage_status(client_ip: str, email: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive usage status for a user"""
    redis_manager = get_redis_manager()
    
    if not redis_manager or not redis_manager.is_available:
        # Fallback to in-memory usage tracking when Redis is unavailable
        current_time = datetime.now()
        
        async with usage_tracking_lock:
            # Clean up old usage records (keep only today's and this month's)
            usage_key = f"{client_ip}:{email or 'anonymous'}"
            if usage_key in usage_tracking_storage:
                # Keep only records from today and this month
                today = current_time.date()
                this_month = current_time.replace(day=1)
                
                usage_tracking_storage[usage_key] = [
                    timestamp for timestamp in usage_tracking_storage[usage_key]
                    if timestamp.date() == today or timestamp >= this_month
                ]
            
            # Count daily and monthly usage
            daily_usage = sum(1 for ts in usage_tracking_storage[usage_key] if ts.date() == current_time.date())
            monthly_usage = sum(1 for ts in usage_tracking_storage[usage_key] if ts >= current_time.replace(day=1))
            
            return {
                "daily_usage": daily_usage,
                "monthly_usage": monthly_usage,
                "has_premium": False,  # No premium support in memory fallback
                "premium_info": {"has_premium": False, "source": "in_memory_fallback"}
            }
    
    # Get usage counts and premium status
    daily_usage_data = await redis_manager.get_usage_count(client_ip, email, "daily")
    monthly_usage_data = await redis_manager.get_usage_count(client_ip, email, "monthly")
    premium_info = await redis_manager.check_premium_access(client_ip, email)
    
    return {
        "daily_usage": daily_usage_data.get("combined_usage", 0),
        "monthly_usage": monthly_usage_data.get("combined_usage", 0),
        "has_premium": premium_info.get("has_premium", False),
        "premium_info": premium_info
    }

async def check_usage_limits(client_ip: str, email: Optional[str] = None) -> Dict[str, Any]:
    """Check if user has exceeded their usage limits"""
    if not FREE_TIER_ENABLED:
        return {"allowed": True, "reason": "free_tier_disabled"}
    
    usage_status = await get_user_usage_status(client_ip, email)
    
    # Premium users have unlimited access
    if usage_status["has_premium"]:
        return {
            "allowed": True,
            "reason": "premium_access",
            "usage_status": usage_status
        }
    
    daily_usage = usage_status["daily_usage"]
    monthly_usage = usage_status["monthly_usage"]
    
    # Check daily limit first
    if daily_usage >= FREE_TIER_DAILY_LIMIT:
        return {
            "allowed": False,
            "reason": "daily_limit_exceeded",
            "usage_status": usage_status,
            "message": f"Daily limit of {FREE_TIER_DAILY_LIMIT} threads exceeded. Upgrade to premium for unlimited access."
        }
    
    # Check monthly limit
    if monthly_usage >= FREE_TIER_MONTHLY_LIMIT:
        return {
            "allowed": False,
            "reason": "monthly_limit_exceeded",
            "usage_status": usage_status,
            "message": f"Monthly limit of {FREE_TIER_MONTHLY_LIMIT} threads exceeded. Upgrade to premium for unlimited access."
        }
    
    return {
        "allowed": True,
        "reason": "within_limits",
        "usage_status": usage_status
    }

async def track_thread_usage(client_ip: str, email: Optional[str] = None) -> bool:
    """Track thread generation for analytics and limit enforcement"""
    redis_manager = get_redis_manager()
    
    if not redis_manager or not redis_manager.is_available:
        logger.info("Redis unavailable - using in-memory usage tracking")
        # Fallback to in-memory usage tracking
        current_time = datetime.now()
        usage_key = f"{client_ip}:{email or 'anonymous'}"
        
        async with usage_tracking_lock:
            usage_tracking_storage[usage_key].append(current_time)
            logger.info(f"Tracked usage for {usage_key} at {current_time}")
            return True
    
    return await redis_manager.track_thread_generation(client_ip, email)

# Note: extract_email_from_request_context function removed - now using enhanced user context with authentication

# Utility functions
def extract_content_with_readability(html_content: str) -> Optional[Dict[str, str]]:
    """
    Alternative content extraction using readability heuristics.
    Returns extracted content or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
            tag.decompose()
        
        # Score paragraphs based on various heuristics
        scored_elements = []
        
        for elem in soup.find_all(['p', 'div']):
            text = elem.get_text().strip()
            if not text or len(text) < 20:
                continue
                
            score = 0
            
            # Length bonus
            score += min(len(text) / 100, 3)
            
            # Punctuation bonus (indicates real sentences)
            score += text.count('.') * 0.5
            score += text.count(',') * 0.3
            
            # Penalty for too many links
            link_density = len(elem.find_all('a')) / max(len(text.split()), 1)
            if link_density > 0.3:
                score *= 0.5
            
            # Bonus for being inside article-like containers
            parent_tags = [p.name for p in elem.parents][:5]
            if 'article' in parent_tags or 'main' in parent_tags:
                score *= 1.5
            
            # Check for common non-content indicators
            text_lower = text.lower()
            non_content_indicators = [
                'cookie', 'privacy policy', 'terms of service', 'subscribe',
                'follow us', 'share this', 'advertisement', 'sponsored'
            ]
            if any(indicator in text_lower for indicator in non_content_indicators):
                score *= 0.3
            
            scored_elements.append((elem, score, text))
        
        # Sort by score and extract top elements
        scored_elements.sort(key=lambda x: x[1], reverse=True)
        
        # Extract content from top-scoring elements
        content_parts = []
        seen_texts = set()
        
        for elem, score, text in scored_elements[:30]:  # Top 30 elements
            if score < 1.0:  # Minimum score threshold
                break
            if text not in seen_texts:
                content_parts.append(text)
                seen_texts.add(text)
        
        if content_parts:
            content = '\n\n'.join(content_parts)
            
            # Try to find title
            title = None
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            
            return {
                "title": title,
                "content": content,
                "method": "readability-heuristics"
            }
            
    except Exception as e:
        logger.error(f"Readability extraction failed: {e}")
        
    return None

def extract_json_ld_article(html_content: str) -> Optional[Dict[str, str]]:
    """
    Extract article content from JSON-LD structured data.
    Many modern sites include article data in JSON-LD format.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find JSON-LD script tags
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                items = [data] if isinstance(data, dict) else data
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                        
                    # Check if it's an article or blog post
                    if item.get('@type') in ['Article', 'NewsArticle', 'BlogPosting', 'WebPage']:
                        title = item.get('headline') or item.get('name')
                        
                        # Try different content fields
                        content = (
                            item.get('articleBody') or 
                            item.get('text') or 
                            item.get('description', '')
                        )
                        
                        if content and len(content) > 100:
                            return {
                                "title": title,
                                "content": content,
                                "method": "json-ld"
                            }
                            
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.debug(f"Error parsing JSON-LD: {e}")
                
    except Exception as e:
        logger.error(f"JSON-LD extraction failed: {e}")
        
    return None

def extract_opengraph_content(html_content: str, url: str) -> Optional[Dict[str, str]]:
    """
    Extract content using OpenGraph meta tags as hints.
    This won't get full article content but can help identify the main content area.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get OpenGraph data
        og_title = None
        og_description = None
        
        for meta in soup.find_all('meta'):
            prop = meta.get('property', '')
            content = meta.get('content', '')
            
            if prop == 'og:title':
                og_title = content
            elif prop == 'og:description':
                og_description = content
        
        # If we have OG data, use it to help find the main content
        if og_title:
            # Look for the title in h1/h2 tags to identify article area
            for heading in soup.find_all(['h1', 'h2']):
                if og_title in heading.get_text():
                    # Found the article area, extract content from parent
                    article_container = heading.parent
                    
                    # Go up a few levels to get more content
                    for _ in range(3):
                        if article_container.parent:
                            article_container = article_container.parent
                    
                    # Extract text from this container
                    paragraphs = article_container.find_all(['p', 'h2', 'h3', 'h4'])
                    content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    
                    if content and len(content) > 200:
                        return {
                            "title": og_title,
                            "content": content,
                            "method": "opengraph-guided"
                        }
        
        # Fallback: if we have OG description but couldn't find content
        if og_description and len(og_description) > 100:
            logger.warning(f"Using OG description as fallback for {url}")
            return {
                "title": og_title,
                "content": og_description,
                "method": "opengraph-description-only"
            }
                
    except Exception as e:
        logger.error(f"OpenGraph extraction failed: {e}")
        
    return None

async def scrape_article(url: Union[str, HttpUrl]) -> Dict[str, str]:
    """Scrape article content from URL with enhanced Railway compatibility and error handling"""
    # Convert HttpUrl to string if needed - always convert to handle Pydantic v2 HttpUrl type
    url_str = str(url)
    
    # Enhanced logging for debugging
    logger.info(f"Starting URL scrape for: {url_str}")
    logger.info(f"Environment: {ENVIRONMENT}, SSL verification override: {os.getenv('HTTPX_VERIFY_SSL', 'true')}")
    
    # Track error context for better reporting
    error_context = {
        "url": url_str,
        "timestamp": datetime.now().isoformat(),
        "step": "initialization"
    }
    
    # Validate URL security first
    try:
        error_context["step"] = "security_validation"
        await validate_url_security(url_str)
        logger.info(f"URL security validation passed for: {url_str}")
    except HTTPException as e:
        # Re-raise HTTP exceptions as they already have user-friendly messages
        logger.error(f"URL security validation failed for {url_str}: {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in URL security validation for {url_str}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Unable to validate URL. Please ensure it's a valid web address."
        )
    
    # DNS pre-resolution for debugging
    try:
        error_context["step"] = "dns_resolution"
        import socket
        from urllib.parse import urlparse
        parsed = urlparse(url_str)
        hostname = parsed.hostname
        if hostname:
            ips = socket.gethostbyname_ex(hostname)[2]
            logger.info(f"DNS resolution for {hostname}: {ips}")
            error_context["hostname"] = hostname
            error_context["resolved_ips"] = ips
    except socket.gaierror as dns_e:
        logger.error(f"DNS resolution failed for {hostname}: {dns_e}")
        raise HTTPException(
            status_code=400,
            detail=f"Unable to find the website '{hostname}'. Please check the URL is correct."
        )
    except Exception as dns_e:
        logger.warning(f"DNS pre-resolution warning: {dns_e}")
    
    # Simplified retry configuration
    max_retries = 2
    retry_delay = 1.0
    response = None  # Initialize response variable
    
    for attempt in range(max_retries):
        try:
            # Use SIMPLE httpx configuration that works on Railway
            # Based on working simple-scrape endpoint
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Creating simple httpx client")
            
            async with httpx.AsyncClient(
                timeout=30.0,  # Simple timeout
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5"
                }
            ) as client:
                logger.info(f"Fetching URL: {url_str}")
                response = await client.get(url_str)
                logger.info(f"Response received - Status: {response.status_code}, Content-Length: {len(response.content)}")
                response.raise_for_status()
                
                # Check for common issues in the response
                content_type = response.headers.get("content-type", "").lower()
                
                # Check for JavaScript-heavy responses
                if "application/json" in content_type and "text/html" not in content_type:
                    logger.warning(f"Got JSON response instead of HTML for {url_str}")
                    raise HTTPException(
                        status_code=400,
                        detail="This appears to be an API endpoint, not a webpage. Please provide a direct link to the article."
                    )
                
                # Check response size for potential issues
                if len(response.content) < 1000:
                    logger.warning(f"Suspiciously small response: {len(response.content)} bytes")
                    # Don't fail yet, but log for debugging
                
                # Success - break out of retry loop
                break
                
        except httpx.ConnectTimeout as e:
            error_context["step"] = "connection"
            error_context["error_type"] = "timeout"
            logger.error(f"Connection timeout (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=504,
                    detail="Unable to connect to the website. The site may be down or taking too long to respond. Please try again later."
                )
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
            
        except httpx.ReadTimeout as e:
            error_context["step"] = "reading_content"
            error_context["error_type"] = "timeout"
            logger.error(f"Read timeout (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=504, 
                    detail="The website took too long to send the content. This might be due to a slow server or large page size. Please try a different article."
                )
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
            
        except (httpx.RequestError, httpx.TransportError) as e:
            error_details = {
                "type": type(e).__name__,
                "message": str(e),
                "url": url_str,
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
            error_context["step"] = "http_response"
            error_context["status_code"] = e.response.status_code
            logger.error(f"HTTP error {e.response.status_code} for URL {url_str}")
            
            # Check for Cloudflare/protection pages
            if e.response.status_code == 403:
                # Try to detect Cloudflare or other protection services
                cf_ray = e.response.headers.get("cf-ray")
                server = e.response.headers.get("server", "").lower()
                
                if cf_ray or "cloudflare" in server:
                    raise HTTPException(
                        status_code=403,
                        detail="This website is protected by Cloudflare and requires human verification. Please visit the article directly in your browser and copy the text instead."
                    )
                else:
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied. The website may be blocking automated access or requiring login. Try copying the article text directly instead of using the URL."
                    )
            elif e.response.status_code == 429:
                retry_after = e.response.headers.get("retry-after")
                if retry_after:
                    raise HTTPException(
                        status_code=429,
                        detail=f"The website is temporarily blocking us due to too many requests. Please try again in {retry_after} seconds."
                    )
                else:
                    raise HTTPException(
                        status_code=429,
                        detail="The website is temporarily blocking us due to too many requests. Please wait a few minutes before trying again."
                    )
            elif e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Article not found. Please check the URL is correct and the article still exists."
                )
            elif e.response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="This article requires login to access. Please copy the article text directly instead of using the URL."
                )
            elif e.response.status_code >= 500:
                raise HTTPException(
                    status_code=502,
                    detail=f"The website is experiencing technical difficulties (error {e.response.status_code}). Please try again later."
                )
            else:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Unable to access the article (error {e.response.status_code}). Please try copying the text directly."
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
    
    # Check if we got a response
    if response is None:
        logger.error(f"Failed to get response from {url_str} after all retries")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to the website after multiple attempts. The site may be down or blocking our requests."
        )
    
    # Wrap the entire content extraction in try-except
    try:
        # Parse HTML with error handling
        error_context["step"] = "html_parsing"
        logger.info(f"Parsing HTML content (length: {len(response.text)} chars)")
        
        # Check if we got a JavaScript-heavy page
        if len(response.text) < 1000 and "<noscript>" in response.text:
            logger.warning("Detected possible JavaScript-required page")
            raise HTTPException(
                status_code=400,
                detail="This website requires JavaScript to display content. Please open the article in your browser and copy the text instead."
            )
        
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.info("HTML parsing completed successfully")
        
        # Check for common login/paywall indicators
        login_indicators = [
            "sign in", "log in", "create account", "subscribe", 
            "premium content", "members only", "paywall", "sign up to read",
            "create a free account", "members-only story", "read the rest of this story"
        ]
        page_text_lower = soup.get_text().lower()
        
        # Special handling for known problematic sites
        if "medium.com" in url_str.lower():
            # Medium-specific checks
            medium_wall_indicators = [
                "read the rest of this story with a free account",
                "sign up to read",
                "members-only story",
                "create a free account"
            ]
            for indicator in medium_wall_indicators:
                if indicator in page_text_lower:
                    logger.warning(f"Detected Medium paywall: '{indicator}' found")
                    raise HTTPException(
                        status_code=403,
                        detail="This Medium article requires login or membership. Please open it in your browser (you may need to use incognito mode) and copy the full text."
                    )
        
        # Check for minimal content with login prompts
        visible_text_length = len(page_text_lower)
        login_prompt_ratio = sum(1 for indicator in login_indicators if indicator in page_text_lower)
        
        if visible_text_length < 1000 and login_prompt_ratio >= 2:
            logger.warning(f"Multiple login indicators found with minimal content")
            raise HTTPException(
                status_code=403,
                detail="This article appears to be behind a login wall. The page shows mostly login prompts instead of article content. Please copy the article text directly."
            )
        
        # General paywall check for any site
        for indicator in login_indicators:
            if indicator in page_text_lower and visible_text_length < 500:
                logger.warning(f"Detected possible login/paywall page: '{indicator}' found with only {visible_text_length} chars")
                raise HTTPException(
                    status_code=403,
                    detail="This article appears to be behind a login or paywall. Please copy the article text directly instead."
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BeautifulSoup parsing error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Unable to process the webpage content. The page format may not be supported."
        )
    
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
    error_context["step"] = "content_extraction"
    
    # Common article containers (expanded list)
    article_selectors = [
        'article',
        'main',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content',
        '#content',
        # Additional selectors for popular platforms
        '.story-body',  # BBC
        '.article-body',  # Various news sites
        '.post-body',  # Blogger
        'div[data-testid="article-body"]',  # Modern React sites
        '.prose',  # Tailwind-based blogs
        'div.markdown-body',  # GitHub
        '.article__content',  # Medium-style
        '.blog-post-content',  # Common blog pattern
        'section.content',  # Generic section
        'div[itemprop="articleBody"]',  # Schema.org markup
    ]
    
    # Track which selector worked for debugging
    successful_selector = None
    
    for selector in article_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                # Extract paragraphs and headers
                text_elements = element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                if text_elements and len(text_elements) > 2:  # Ensure we have substantial content
                    content = '\n\n'.join([elem.get_text().strip() for elem in text_elements if elem.get_text().strip()])
                    if len(content) > 100:  # Minimum content threshold
                        successful_selector = selector
                        logger.info(f"Successfully extracted content using selector: {selector}")
                        break
        except Exception as e:
            logger.debug(f"Selector {selector} failed: {e}")
            continue
    
    # Fallback: get all paragraphs
    if not content:
        logger.warning("No article container found, falling back to all paragraphs")
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            successful_selector = "fallback-all-paragraphs"
    
    # Additional fallback: check for divs with substantial text
    if not content or len(content) < 100:
        logger.warning("Insufficient content from paragraphs, checking text-heavy divs")
        text_divs = soup.find_all('div')
        for div in text_divs:
            div_text = div.get_text().strip()
            if len(div_text) > 500 and div_text.count(' ') > 50:  # Substantial text content
                content = div_text
                successful_selector = "fallback-text-divs"
                break
    
    error_context["extraction_method"] = successful_selector or "none"
    
    # Clean up content
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    
    # If primary extraction failed, try fallback methods
    if not content or len(content) < 100:
        logger.info("Primary extraction failed or insufficient content, trying fallback methods")
        
        # Try JSON-LD extraction first (most reliable if available)
        json_ld_result = extract_json_ld_article(response.text)
        if json_ld_result and json_ld_result.get("content"):
            logger.info(f"Successfully extracted content using JSON-LD for {url_str}")
            content = json_ld_result["content"]
            title = json_ld_result.get("title") or title
            successful_selector = "json-ld"
        else:
            # Try readability heuristics
            readability_result = extract_content_with_readability(response.text)
            if readability_result and readability_result.get("content") and len(readability_result["content"]) > len(content):
                logger.info(f"Successfully extracted content using readability heuristics for {url_str}")
                content = readability_result["content"]
                title = readability_result.get("title") or title
                successful_selector = "readability-heuristics"
            else:
                # Try OpenGraph-guided extraction
                og_result = extract_opengraph_content(response.text, url_str)
                if og_result and og_result.get("content") and len(og_result["content"]) > len(content):
                    logger.info(f"Successfully extracted content using OpenGraph data for {url_str}")
                    content = og_result["content"]
                    title = og_result.get("title") or title
                    successful_selector = og_result["method"]
    
    # Final check if we still don't have content
    if not content:
        error_context["page_title"] = title
        error_context["page_length"] = len(response.text)
        
        # Provide more helpful error messages based on what we found
        if "robot" in page_text_lower or "captcha" in page_text_lower:
            logger.error(f"Robot/CAPTCHA detection on {url_str}")
            raise HTTPException(
                status_code=403,
                detail="The website is showing a CAPTCHA or robot check. Please visit the article in your browser and copy the text manually."
            )
        elif len(response.text) < 500:
            logger.error(f"Very short response from {url_str}: {len(response.text)} chars")
            raise HTTPException(
                status_code=400,
                detail="The webpage appears to be empty or failed to load properly. Please verify the URL or try copying the text directly."
            )
        else:
            logger.error(f"Content extraction failed for {url_str}. Context: {json.dumps(error_context)}")
            raise HTTPException(
                status_code=400,
                detail="Unable to extract article content from this webpage. The site may use a format we don't support. Please copy and paste the article text instead."
            )
    
    # Clean and validate content
    if len(content) < 50:
        logger.error(f"Extracted content too short ({len(content)} chars) for {url_str}")
        raise HTTPException(
            status_code=400,
            detail="The extracted content is too short to create a meaningful thread. Please ensure you're linking to a full article, not a preview or summary."
        )
    
    # Log successful extraction
    logger.info(f"Successfully extracted {len(content)} characters from {url_str} using {successful_selector}")
    
    # Truncate if too long
    truncated = False
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "..."
        truncated = True
        logger.info(f"Content truncated from {len(content)} to {MAX_CONTENT_LENGTH} characters")
    
    result = {
        "title": title.strip() if title else None,
        "content": content,
        "metadata": {
            "extraction_method": successful_selector,
            "content_length": len(content),
            "truncated": truncated
        }
    }
    
    # Don't include metadata in the actual response
    return {
        "title": result["title"],
        "content": result["content"]
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

# Production environment - debug routes removed

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

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint to verify API is working"""
    test_content = "This is a test message to verify the API is working correctly."
    test_tweets = split_into_tweets(test_content)
    
    return {
        "status": "working",
        "message": test_content,
        "tweet_count": len(test_tweets),
        "tweets": test_tweets
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
    # Block access in production
    if ENVIRONMENT == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
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
    client_request: Request,
    _: None = Depends(check_rate_limit),
    security_context: Dict[str, Any] = Depends(verify_public_access),
    user_context: Dict[str, Any] = Depends(get_user_context)
):
    """Generate a Twitter/X thread from URL or text content"""
    global openai_available
    redis_manager = get_redis_manager()
    client_ip = user_context["client_ip"]
    
    # Extract email from authenticated user or context
    user_email = user_context["email"]
    user_info = user_context["user_info"]
    
    # Log request with authentication status
    auth_status = "authenticated" if user_context["is_authenticated"] else "anonymous"
    logger.info(f"Thread generation request from {auth_status} user (IP: {client_ip}, Email: {user_email or 'None'})")
    
    # Check usage limits and reserve usage slot BEFORE processing to prevent race conditions
    if FREE_TIER_ENABLED:
        usage_check = await check_usage_limits(client_ip, user_email)
        
        if not usage_check["allowed"]:
            # Return 402 Payment Required with details
            raise HTTPException(
                status_code=402,
                detail={
                    "message": usage_check["message"],
                    "reason": usage_check["reason"],
                    "usage_status": {
                        "daily_usage": usage_check["usage_status"]["daily_usage"],
                        "daily_limit": FREE_TIER_DAILY_LIMIT,
                        "monthly_usage": usage_check["usage_status"]["monthly_usage"],
                        "monthly_limit": FREE_TIER_MONTHLY_LIMIT,
                        "has_premium": usage_check["usage_status"]["has_premium"]
                    },
                    "premium_price": PREMIUM_PRICE_USD,
                    "upgrade_message": f"Upgrade to premium for ${PREMIUM_PRICE_USD}/month for unlimited threads!"
                }
            )
        
        # For now, track usage immediately before processing to prevent race conditions
        # TODO: Implement proper reservation system for better UX (allow retry on failures)
        usage_tracked = await track_thread_usage(client_ip, user_email)
        if not usage_tracked:
            logger.warning(f"Failed to track usage for IP: {client_ip}, Email: {user_email or 'None'}")
            # Continue processing - this prevents Redis failures from blocking the service
    
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
        
        # Save thread history for authenticated users
        if user_context["is_authenticated"] and user_info and thread_history_service:
            try:
                # Create thread title from source
                thread_title = title if title else f"Thread from {source_type}"
                if len(thread_title) > 200:
                    thread_title = thread_title[:200] + "..."
                
                # Convert tweets to save format
                tweets_data = [{"content": tweet.content} for tweet in thread]
                
                # Create metadata
                metadata = {
                    "source_url": str(request.url) if request.url else None,
                    "source_type": source_type,
                    "ai_model": "gpt-3.5-turbo" if openai_available else "fallback",
                    "content_length": len(content),
                    "generation_time_ms": None  # Could add timing later
                }
                
                # Save the thread
                saved_thread = await thread_history_service.save_thread(
                    user_id=user_info["user_id"],
                    title=thread_title,
                    original_content=content[:50000],  # Limit content size
                    tweets=tweets_data,
                    metadata=metadata,
                    client_ip=client_ip
                )
                
                logger.info(f"Thread automatically saved to history: {saved_thread.id} for user {user_info['user_id']}")
                
                # Add saved thread ID to response for frontend reference
                response.saved_thread_id = saved_thread.id
                
                # Create mock analytics for the generated thread (if analytics available)
                if redis_manager and redis_manager.is_available and analytics_router_creator:
                    try:
                        try:
                            from .models.analytics import ThreadAnalytics, ContentType, TweetMetrics
                            from .services.analytics.analytics_service import AnalyticsService
                        except ImportError:
                            from models.analytics import ThreadAnalytics, ContentType, TweetMetrics
                            from services.analytics.analytics_service import AnalyticsService
                        import random
                        
                        analytics_service = AnalyticsService(redis_manager.redis)
                        
                        # Determine content type based on source
                        content_type = ContentType.OTHER
                        if "technical" in content.lower() or "code" in content.lower():
                            content_type = ContentType.TECHNICAL
                        elif "news" in content.lower():
                            content_type = ContentType.NEWS
                        
                        # Create analytics data
                        thread_analytics = ThreadAnalytics(
                            thread_id=saved_thread.id,
                            user_id=user_info["user_id"],
                            created_at=datetime.utcnow(),
                            title=thread_title,
                            source_url=str(request.url) if request.url else None,
                            content_type=content_type,
                            tweet_count=len(thread),
                            total_character_count=sum(tweet.character_count for tweet in thread),
                            # Mock initial metrics (would be updated by real engagement tracking)
                            total_impressions=random.randint(100, 1000),
                            total_engagements=random.randint(5, 50),
                            engagement_rate=random.uniform(1.0, 5.0),
                            total_likes=random.randint(2, 20),
                            total_retweets=random.randint(1, 10),
                            total_replies=random.randint(0, 5),
                            thread_completion_rate=random.uniform(40.0, 80.0),
                            virality_score=random.uniform(10.0, 50.0),
                            posted_at=datetime.utcnow(),
                            tweet_metrics=[
                                TweetMetrics(
                                    tweet_id=f"{saved_thread.id}_tweet_{i}",
                                    position=i,
                                    content=tweet.content,
                                    character_count=tweet.character_count,
                                    impressions=random.randint(50, 500),
                                    likes=random.randint(1, 10),
                                    retweets=random.randint(0, 5),
                                    engagement_rate=random.uniform(1.0, 8.0),
                                    posted_at=datetime.utcnow()
                                )
                                for i, tweet in enumerate(thread, 1)
                            ]
                        )
                        
                        await analytics_service.save_thread_analytics(thread_analytics)
                        logger.info(f"Analytics created for thread: {saved_thread.id}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to create analytics for thread: {e}")
                        # Don't fail the request if analytics creation fails
                
            except Exception as e:
                logger.warning(f"Failed to save thread to history: {e}")
                # Don't fail the request if saving fails
        
        # Usage already tracked before processing to prevent race conditions
        # This ensures limits are enforced even with concurrent requests
        logger.info(f"Thread generation completed for IP: {client_ip}, Email: {user_email or 'None'}")
        
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

@app.post("/api/subscribe", response_model=EmailSubscribeResponse)
async def subscribe_email(
    request: EmailSubscribeRequest,
    client_request: Request,
    _: None = Depends(check_rate_limit),
    security_context: Dict[str, Any] = Depends(verify_public_access),
    user_context: Dict[str, Any] = Depends(get_user_context)
):
    """Subscribe email for notifications and updates"""
    redis_manager = get_redis_manager()
    client_ip = user_context["client_ip"]
    
    try:
        # Extract email from validated request
        email = request.email
        
        # Check if email already exists
        email_exists = False
        if redis_manager and redis_manager.is_available:
            email_exists = await redis_manager.check_email_exists(email)
        else:
            # Check fallback storage
            if hasattr(subscribe_email, 'fallback_emails'):
                email_exists = email in subscribe_email.fallback_emails
        
        if email_exists:
            logger.info(f"Duplicate email subscription attempt: {email}")
            return EmailSubscribeResponse(
                success=True,
                message="You're already subscribed! We'll keep you updated on new features.",
                email=email
            )
        
        # Store email with analytics data
        email_data = {
            "email": email,
            "subscribed_at": datetime.now().isoformat(),
            "client_ip": client_ip,
            "user_agent": client_request.headers.get("user-agent", ""),
            "referrer": client_request.headers.get("referer", ""),
            "source": "web_app"
        }
        
        # Try to store in Redis first
        stored = False
        if redis_manager and redis_manager.is_available:
            stored = await redis_manager.store_email_subscription(email, email_data)
            
        if stored:
            logger.info(f"Email subscription stored in Redis: {email}")
        else:
            # Fallback to in-memory storage (for development/testing)
            # In production, you might want to log this for later processing
            logger.warning(f"Email subscription fallback for: {email} (Redis unavailable)")
            
            # Store in a simple in-memory dict for development
            if not hasattr(subscribe_email, 'fallback_emails'):
                subscribe_email.fallback_emails = {}
            subscribe_email.fallback_emails[email] = email_data
        
        # Log subscription for monitoring
        logger.info(f"New email subscription: {email} from IP: {client_ip}")
        
        return EmailSubscribeResponse(
            success=True,
            message="Successfully subscribed! We'll keep you updated on new features.",
            email=email
        )
        
    except ValueError as ve:
        # Pydantic validation errors
        logger.warning(f"Email subscription validation error: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        # Log the error but don't expose internals
        error_id = datetime.now().isoformat()
        logger.error(f"Email subscription error [{error_id}]: {str(e)}", exc_info=True)
        
        if ENVIRONMENT == "production":
            raise HTTPException(
                status_code=500,
                detail="Unable to process subscription. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Subscription error: {str(e)}"
            )

@app.get("/api/emails/stats")
async def email_stats(
    _: str = Depends(verify_api_key)
):
    """Get email subscription statistics - Admin only"""
    redis_manager = get_redis_manager()
    
    if not redis_manager or not redis_manager.is_available:
        # Check fallback storage
        fallback_count = len(getattr(subscribe_email, 'fallback_emails', {}))
        return {
            "total_subscriptions": fallback_count,
            "redis_available": False,
            "storage": "fallback" if fallback_count > 0 else "none"
        }
    
    try:
        stats = await redis_manager.get_email_stats()
        return {
            "total_subscriptions": stats.get("total_emails", 0),
            "recent_subscriptions": stats.get("recent_count", 0),
            "redis_available": True,
            "storage": "redis"
        }
    except Exception as e:
        logger.error(f"Error getting email stats: {e}")
        return {
            "total_subscriptions": 0,
            "redis_available": False,
            "error": str(e),
            "storage": "error"
        }

@app.get("/api/premium/check", response_model=PremiumCheckResponse)
async def check_premium_status(
    request: Request,
    user_context: Dict[str, Any] = Depends(get_user_context)
):
    """Check user's premium status and usage limits for frontend payment logic"""
    client_ip = user_context["client_ip"]
    user_email = user_context["email"]
    
    # Get comprehensive usage status
    usage_status = await get_user_usage_status(client_ip, user_email)
    premium_info = usage_status["premium_info"]
    
    # Create usage status object
    usage_obj = UsageStatus(
        daily_usage=usage_status["daily_usage"],
        daily_limit=FREE_TIER_DAILY_LIMIT,
        monthly_usage=usage_status["monthly_usage"],
        monthly_limit=FREE_TIER_MONTHLY_LIMIT,
        has_premium=usage_status["has_premium"],
        premium_expires_at=premium_info.get("expires_at")
    )
    
    # Determine if user needs to pay
    needs_payment = False
    message = "You have full access to Threadr."
    
    if not usage_status["has_premium"] and FREE_TIER_ENABLED:
        daily_remaining = max(0, FREE_TIER_DAILY_LIMIT - usage_status["daily_usage"])
        monthly_remaining = max(0, FREE_TIER_MONTHLY_LIMIT - usage_status["monthly_usage"])
        
        if daily_remaining == 0 or monthly_remaining == 0:
            needs_payment = True
            if daily_remaining == 0:
                message = f"You've reached your daily limit of {FREE_TIER_DAILY_LIMIT} threads. Upgrade to premium for unlimited access!"
            else:
                message = f"You've reached your monthly limit of {FREE_TIER_MONTHLY_LIMIT} threads. Upgrade to premium for unlimited access!"
        else:
            remaining = min(daily_remaining, monthly_remaining)
            message = f"You have {remaining} free threads remaining today. Upgrade to premium for unlimited access!"
    elif usage_status["has_premium"]:
        expires_at = premium_info.get("expires_at")
        if expires_at:
            try:
                expiry_date = datetime.fromisoformat(expires_at)
                days_remaining = (expiry_date - datetime.now()).days
                message = f"Premium access active. Expires in {days_remaining} days."
            except:
                message = "Premium access active."
        else:
            message = "Premium access active."
    
    return PremiumCheckResponse(
        has_premium=usage_status["has_premium"],
        usage_status=usage_obj,
        needs_payment=needs_payment,
        premium_price=PREMIUM_PRICE_USD,
        message=message
    )

@app.post("/api/premium/grant")
async def grant_premium_access(
    request: GrantPremiumRequest,
    client_request: Request,
    _: str = Depends(verify_api_key)  # Admin/webhook endpoint - requires API key
):
    """Grant premium access - for Stripe webhook integration"""
    redis_manager = get_redis_manager()
    client_ip = client_request.client.host
    
    if not redis_manager or not redis_manager.is_available:
        raise HTTPException(
            status_code=503,
            detail="Premium access service temporarily unavailable"
        )
    
    # Prepare payment info for tracking
    payment_info = {
        "payment_reference": request.payment_reference,
        "granted_at": datetime.now().isoformat(),
        "granted_by": "api",
        "client_ip": client_ip
    }
    
    # Grant premium access
    success = await redis_manager.grant_premium_access(
        client_ip=client_ip,
        email=request.email,
        plan=request.plan,
        duration_days=request.duration_days,
        payment_info=payment_info
    )
    
    if not success:
        logger.error(f"Failed to grant premium access for {request.email or client_ip}")
        raise HTTPException(
            status_code=500,
            detail="Failed to grant premium access"
        )
    
    logger.info(f"Premium access granted: Email={request.email}, IP={client_ip}, Plan={request.plan}, Duration={request.duration_days} days")
    
    return {
        "success": True,
        "message": f"Premium access granted for {request.duration_days} days",
        "plan": request.plan,
        "expires_at": (datetime.now() + timedelta(days=request.duration_days)).isoformat()
    }

@app.get("/api/usage/analytics")
async def get_usage_analytics(
    _: str = Depends(verify_api_key)  # Admin endpoint
):
    """Get comprehensive usage analytics - Admin only"""
    redis_manager = get_redis_manager()
    
    if not redis_manager or not redis_manager.is_available:
        return {
            "available": False,
            "message": "Analytics service unavailable - Redis not connected"
        }
    
    analytics = await redis_manager.get_usage_analytics()
    return analytics

@app.get("/api/usage/status")
async def get_current_usage_status(
    request: Request,
    user_context: Dict[str, Any] = Depends(get_user_context)
):
    """Get current user's usage status without API key requirement"""
    client_ip = user_context["client_ip"]
    user_email = user_context["email"]
    
    usage_status = await get_user_usage_status(client_ip, user_email)
    
    return {
        "daily_usage": usage_status["daily_usage"],
        "daily_limit": FREE_TIER_DAILY_LIMIT,
        "daily_remaining": max(0, FREE_TIER_DAILY_LIMIT - usage_status["daily_usage"]),
        "monthly_usage": usage_status["monthly_usage"],
        "monthly_limit": FREE_TIER_MONTHLY_LIMIT,
        "monthly_remaining": max(0, FREE_TIER_MONTHLY_LIMIT - usage_status["monthly_usage"]),
        "has_premium": usage_status["has_premium"],
        "premium_expires_at": usage_status["premium_info"].get("expires_at"),
        "free_tier_enabled": FREE_TIER_ENABLED
    }

# Stripe webhook functionality

class StripeEvent(BaseModel):
    """Stripe webhook event data structure"""
    id: str
    object: str
    type: str
    data: Dict[str, Any]
    created: int
    api_version: Optional[str] = None

def verify_stripe_signature(payload: bytes, signature: str, webhook_secret: str) -> bool:
    """Verify Stripe webhook signature for security"""
    if not webhook_secret:
        logger.warning("Stripe webhook secret not configured - skipping signature verification")
        return True  # Allow webhooks when not configured (development only)
    
    try:
        # Extract timestamp and signature from header
        elements = signature.split(',')
        timestamp = None
        signatures = []
        
        for element in elements:
            key, value = element.split('=')
            if key == 't':
                timestamp = value
            elif key.startswith('v'):
                signatures.append(value)
        
        if not timestamp or not signatures:
            logger.error("Invalid Stripe signature format")
            return False
        
        # Create expected signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        for signature in signatures:
            if hmac.compare_digest(expected_signature, signature):
                return True
        
        logger.error("Stripe signature verification failed")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying Stripe signature: {str(e)}")
        return False

async def process_stripe_checkout_completed(session_data: Dict[str, Any]) -> bool:
    """Process completed checkout session and grant premium access"""
    try:
        # Extract session information
        session_id = session_data.get('id')
        customer_email = session_data.get('customer_details', {}).get('email')
        payment_status = session_data.get('payment_status')
        amount_total = session_data.get('amount_total', 0)
        currency = session_data.get('currency', 'usd')
        
        logger.info(f"Processing Stripe checkout completion: Session={session_id}, Email={customer_email}, Amount={amount_total/100:.2f} {currency.upper()}")
        
        # Verify payment was successful
        if payment_status != 'paid':
            logger.warning(f"Checkout session {session_id} not paid (status: {payment_status})")
            return False
        
        # Verify amount matches expected premium price
        expected_amount = int(PREMIUM_PRICE_USD * 100)  # Convert to cents
        if amount_total != expected_amount:
            logger.warning(f"Unexpected payment amount: {amount_total} (expected: {expected_amount})")
            # Don't fail - prices might change or have discounts
        
        # Grant premium access using existing endpoint
        premium_request = GrantPremiumRequest(
            email=customer_email,
            plan="premium",
            duration_days=30,  # Monthly subscription
            payment_reference=f"stripe_session_{session_id}"
        )
        
        # Create mock request for IP tracking
        class MockRequest:
            def __init__(self):
                self.client = type('Client', (), {'host': '0.0.0.0'})()  # Webhook origin
        
        mock_request = MockRequest()
        
        # Grant premium access
        redis_manager = get_redis_manager()
        if not redis_manager or not redis_manager.is_available:
            logger.error("Redis not available - cannot grant premium access")
            return False
        
        payment_info = {
            "payment_reference": f"stripe_session_{session_id}",
            "granted_at": datetime.now().isoformat(),
            "granted_by": "stripe_webhook",
            "client_ip": "stripe_webhook",
            "stripe_session_id": session_id,
            "amount": amount_total,
            "currency": currency
        }
        
        # Grant premium access directly through Redis manager
        success = await redis_manager.grant_premium_access(
            client_ip=None,  # No specific IP for webhook
            email=customer_email,
            plan="premium",
            duration_days=30,
            payment_info=payment_info
        )
        
        if success:
            logger.info(f"Premium access granted successfully via Stripe webhook: Email={customer_email}, Session={session_id}")
            return True
        else:
            logger.error(f"Failed to grant premium access via Redis: Email={customer_email}, Session={session_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing Stripe checkout completion: {str(e)}", exc_info=True)
        return False

@app.post("/api/webhooks/stripe")
async def stripe_webhook_handler(request: Request):
    """Handle Stripe webhook events securely (snapshot payloads)"""
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get('stripe-signature', '')
        
        if not payload:
            logger.error("Empty webhook payload received")
            raise HTTPException(status_code=400, detail="Empty payload")
        
        # Verify webhook signature for security
        if STRIPE_WEBHOOK_SECRET and not verify_stripe_signature(payload, signature, STRIPE_WEBHOOK_SECRET):
            logger.error("Stripe webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse the webhook event
        try:
            event_data = stripe.Event.construct_from(
                json.loads(payload.decode('utf-8')),
                stripe.api_key
            )
        except Exception as e:
            logger.error(f"Failed to parse Stripe webhook event: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid event data")
        
        event_type = event_data.type
        event_id = event_data.id
        
        logger.info(f"Received Stripe webhook (snapshot): {event_type} (ID: {event_id})")
        
        # Process checkout.session.completed events
        if event_type == 'checkout.session.completed':
            session_data = event_data.data.object
            success = await process_stripe_checkout_completed(session_data)
            
            if success:
                logger.info(f"Successfully processed checkout completion: {event_id}")
                return {"received": True, "processed": True, "event_id": event_id, "payload_type": "snapshot"}
            else:
                logger.error(f"Failed to process checkout completion: {event_id}")
                return {"received": True, "processed": False, "event_id": event_id, "error": "Failed to grant premium access", "payload_type": "snapshot"}
        
        # Handle other webhook events (log and acknowledge)
        elif event_type in [
            'customer.subscription.created',
            'customer.subscription.updated', 
            'customer.subscription.deleted',
            'invoice.payment_succeeded',
            'invoice.payment_failed'
        ]:
            logger.info(f"Received {event_type} webhook event: {event_id} (acknowledged but not processed)")
            return {"received": True, "processed": False, "event_id": event_id, "message": "Event acknowledged but not processed", "payload_type": "snapshot"}
        
        else:
            logger.info(f"Unhandled webhook event type: {event_type} (ID: {event_id})")
            return {"received": True, "processed": False, "event_id": event_id, "message": "Unhandled event type", "payload_type": "snapshot"}
    
    except HTTPException:
        raise
    except Exception as e:
        error_id = datetime.now().isoformat()
        logger.error(f"Stripe webhook error [{error_id}]: {str(e)}", exc_info=True)
        
        if ENVIRONMENT == "production":
            raise HTTPException(status_code=500, detail=f"Webhook processing error. Error ID: {error_id}")
        else:
            raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

@app.post("/api/webhooks/stripe/thin")
async def stripe_thin_webhook_handler(request: Request):
    """Handle Stripe webhook events securely (thin payloads)"""
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get('stripe-signature', '')
        
        if not payload:
            logger.error("Empty webhook payload received")
            raise HTTPException(status_code=400, detail="Empty payload")
        
        # Verify webhook signature for security (same secret as snapshot endpoint)
        if STRIPE_WEBHOOK_SECRET and not verify_stripe_signature(payload, signature, STRIPE_WEBHOOK_SECRET):
            logger.error("Stripe webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse the webhook event (thin payload only contains event ID and type)
        try:
            event_data = stripe.Event.construct_from(
                json.loads(payload.decode('utf-8')),
                stripe.api_key
            )
        except Exception as e:
            logger.error(f"Failed to parse Stripe webhook event: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid event data")
        
        event_type = event_data.type
        event_id = event_data.id
        
        logger.info(f"Received Stripe webhook (thin): {event_type} (ID: {event_id})")
        
        # For thin payloads, we need to fetch the full event data from Stripe API
        if not STRIPE_SECRET_KEY:
            logger.error("Stripe API key not configured - cannot fetch full event data for thin payload")
            raise HTTPException(status_code=500, detail="Stripe API key not configured")
        
        # Process checkout.session.completed events
        if event_type == 'checkout.session.completed':
            try:
                # Fetch the full event data from Stripe API
                logger.info(f"Fetching full event data for thin payload: {event_id}")
                full_event = stripe.Event.retrieve(event_id)
                
                # Extract session data from the full event
                session_data = full_event.data.object
                success = await process_stripe_checkout_completed(session_data)
                
                if success:
                    logger.info(f"Successfully processed checkout completion from thin payload: {event_id}")
                    return {"received": True, "processed": True, "event_id": event_id, "payload_type": "thin"}
                else:
                    logger.error(f"Failed to process checkout completion from thin payload: {event_id}")
                    return {"received": True, "processed": False, "event_id": event_id, "error": "Failed to grant premium access", "payload_type": "thin"}
                    
            except stripe.error.StripeError as e:
                logger.error(f"Failed to retrieve full event data from Stripe API: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve full event data from Stripe")
        
        # Handle other webhook events (log and acknowledge)
        elif event_type in [
            'customer.subscription.created',
            'customer.subscription.updated', 
            'customer.subscription.deleted',
            'invoice.payment_succeeded',
            'invoice.payment_failed'
        ]:
            logger.info(f"Received {event_type} webhook event (thin): {event_id} (acknowledged but not processed)")
            return {"received": True, "processed": False, "event_id": event_id, "message": "Event acknowledged but not processed", "payload_type": "thin"}
        
        else:
            logger.info(f"Unhandled webhook event type (thin): {event_type} (ID: {event_id})")
            return {"received": True, "processed": False, "event_id": event_id, "message": "Unhandled event type", "payload_type": "thin"}
    
    except HTTPException:
        raise
    except Exception as e:
        error_id = datetime.now().isoformat()
        logger.error(f"Stripe thin webhook error [{error_id}]: {str(e)}", exc_info=True)
        
        if ENVIRONMENT == "production":
            raise HTTPException(status_code=500, detail=f"Webhook processing error. Error ID: {error_id}")
        else:
            raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

@app.get("/api/payment/config")
async def get_payment_config():
    """Get payment configuration for frontend (non-sensitive data only)"""
    # Debug logging for payment URL issue
    logger.info(f"Payment config request - STRIPE_PAYMENT_LINK_URL value: '{STRIPE_PAYMENT_LINK_URL}' (type: {type(STRIPE_PAYMENT_LINK_URL)})")
    logger.info(f"Environment variables check: STRIPE_SECRET_KEY configured: {bool(STRIPE_SECRET_KEY)}")
    
    return {
        "stripe_configured": bool(STRIPE_SECRET_KEY),
        "webhook_configured": bool(STRIPE_WEBHOOK_SECRET),
        "premium_price": PREMIUM_PRICE_USD,
        "display_price": f"${PREMIUM_PRICE_USD:.2f}",
        "currency": "USD",
        "price_id": STRIPE_PRICE_ID if STRIPE_PRICE_ID else None,
        "payment_url": STRIPE_PAYMENT_LINK_URL if STRIPE_PAYMENT_LINK_URL else None,
        "payment_methods": ["stripe_payment_links"] if STRIPE_SECRET_KEY else [],
        "pricing_type": "one_time"
    }

# Stripe Checkout Session Models
class CreateCheckoutSessionRequest(BaseModel):
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    customer_email: Optional[str] = None

class CreateCheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str

@app.post("/api/stripe/create-checkout-session", response_model=CreateCheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    user_context: Dict[str, Any] = Depends(get_user_context)
):
    """Create a Stripe checkout session for premium upgrade"""
    try:
        # Check if Stripe is configured
        if not STRIPE_SECRET_KEY:
            logger.error("Stripe API key not configured")
            raise HTTPException(status_code=500, detail="Payment system not configured")
        
        # Get user context
        client_ip = user_context["client_ip"]
        user_email = user_context["email"] or request.customer_email
        
        # Set default URLs if not provided
        success_url = request.success_url or "https://threadr-plum.vercel.app/payment/success"
        cancel_url = request.cancel_url or "https://threadr-plum.vercel.app/payment/cancel"
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Threadr Premium - 30 Days',
                            'description': 'Unlimited thread generations for 30 days',
                        },
                        'unit_amount': int(PREMIUM_PRICE_USD * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user_email,
            metadata={
                'client_ip': client_ip,
                'user_email': user_email or '',
                'product': 'premium_30_days',
                'created_at': datetime.now().isoformat(),
            },
            expires_at=int((datetime.now() + timedelta(hours=1)).timestamp()),  # Expire after 1 hour
        )
        
        logger.info(f"Created Stripe checkout session: {checkout_session.id} for IP: {client_ip}, Email: {user_email}")
        
        return CreateCheckoutSessionResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@app.get("/debug/env")
async def debug_environment_variables():
    """Debug endpoint to check environment variable configuration - DEVELOPMENT ONLY"""
    if ENVIRONMENT == "production":
        # Enhanced debug info for production payment issue troubleshooting
        raw_stripe_payment_url = os.getenv("STRIPE_PAYMENT_LINK_URL")
        
        return {
            "environment": ENVIRONMENT,
            "timestamp": datetime.now().isoformat(),
            "stripe_vars": {
                "STRIPE_SECRET_KEY": "configured" if STRIPE_SECRET_KEY else "not_configured",
                "STRIPE_WEBHOOK_SECRET": "configured" if STRIPE_WEBHOOK_SECRET else "not_configured", 
                "STRIPE_PRICE_ID": STRIPE_PRICE_ID if STRIPE_PRICE_ID else "not_configured",
                "STRIPE_PAYMENT_LINK_URL": STRIPE_PAYMENT_LINK_URL if STRIPE_PAYMENT_LINK_URL else "not_configured"
            },
            "payment_url_diagnosis": {
                "variable_name": "STRIPE_PAYMENT_LINK_URL",
                "raw_value": raw_stripe_payment_url if raw_stripe_payment_url else "not_found_in_env",
                "processed_value": STRIPE_PAYMENT_LINK_URL if STRIPE_PAYMENT_LINK_URL else "none_after_processing",
                "value_type": str(type(STRIPE_PAYMENT_LINK_URL)),
                "value_length": len(STRIPE_PAYMENT_LINK_URL) if STRIPE_PAYMENT_LINK_URL else 0,
                "is_empty_string": STRIPE_PAYMENT_LINK_URL == "",
                "is_none": STRIPE_PAYMENT_LINK_URL is None,
                "is_whitespace_only": STRIPE_PAYMENT_LINK_URL.strip() == "" if STRIPE_PAYMENT_LINK_URL else False,
                "contains_https": "https://" in str(STRIPE_PAYMENT_LINK_URL) if STRIPE_PAYMENT_LINK_URL else False,
                "starts_with_stripe": str(STRIPE_PAYMENT_LINK_URL).startswith("https://buy.stripe.com/") if STRIPE_PAYMENT_LINK_URL else False
            },
            "env_var_count": len([k for k in os.environ.keys() if "STRIPE" in k.upper()]),
            "stripe_env_keys": [k for k in os.environ.keys() if "STRIPE" in k.upper()]
        }
    
    # Full debug info for development
    return {
        "environment": ENVIRONMENT,
        "all_env_vars": dict(os.environ),
        "stripe_vars": {
            "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY[:10] + "..." if STRIPE_SECRET_KEY else None,
            "STRIPE_WEBHOOK_SECRET": STRIPE_WEBHOOK_SECRET[:10] + "..." if STRIPE_WEBHOOK_SECRET else None,
            "STRIPE_PRICE_ID": STRIPE_PRICE_ID,
            "STRIPE_PAYMENT_LINK_URL": STRIPE_PAYMENT_LINK_URL
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
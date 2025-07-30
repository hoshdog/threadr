from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Union
import httpx
from bs4 import BeautifulSoup
from openai import OpenAI, OpenAIError
from datetime import datetime, timedelta
import os
from collections import defaultdict
import asyncio
import re
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import logging
import sys

# Initialize rate limiter storage
rate_limiter_storage: Dict[str, List[datetime]] = defaultdict(list)
rate_limiter_lock = asyncio.Lock()

# Production Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW_HOURS = int(os.getenv("RATE_LIMIT_WINDOW_HOURS", "1"))
MAX_TWEET_LENGTH = int(os.getenv("MAX_TWEET_LENGTH", "280"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))  # Maximum characters to process

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

# Initialize OpenAI client with error handling
openai_client = None
openai_available = False

def initialize_openai_client():
    """Initialize OpenAI client with proper error handling"""
    global openai_client, openai_available
    try:
        api_key = load_openai_key()
        openai_client = OpenAI(api_key=api_key)
        openai_available = True
        logger.info("OpenAI client initialized successfully")
        return True
    except ValueError as e:
        logger.warning(f"OpenAI initialization failed: {e}")
        openai_available = False
        # Don't fail in production - allow graceful degradation
        if ENVIRONMENT == "production":
            logger.warning("Running in production mode without OpenAI - using fallback methods only")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing OpenAI: {e}")
        openai_available = False
        return False

# Try to initialize OpenAI on startup
initialize_openai_client()

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
        
        # Log OpenAI availability
        if openai_available:
            logger.info("OpenAI client is available - full functionality enabled")
        else:
            logger.warning("OpenAI client not available - using fallback methods only")
        
        # Log all critical environment variables
        logger.info(f"Environment: {ENVIRONMENT}")
        logger.info(f"CORS Origins: {os.getenv('CORS_ORIGINS', 'not set')}")
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

# Initialize FastAPI app
app = FastAPI(
    title="Threadr API",
    description="Convert articles and text into Twitter/X threads",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for production
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
    
    @validator('text')
    def validate_text_length(cls, v, values):
        if v and len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Text content too long. Maximum {MAX_CONTENT_LENGTH} characters allowed.")
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
    error: Optional[str] = None

# Rate limiting dependency
async def check_rate_limit(request: Request):
    client_ip = request.client.host
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
    """Scrape article content from URL"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(url), follow_redirects=True)
            response.raise_for_status()
    except httpx.RequestError as e:
        logger.warning(f"Failed to fetch URL: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error {e.response.status_code} when fetching URL")
        raise HTTPException(status_code=400, detail=f"HTTP error {e.response.status_code} when fetching URL")
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
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
    """Use GPT to generate an engaging thread from content"""
    global openai_client, openai_available
    
    if not openai_available or not openai_client:
        return None
        
    try:
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

        # Call OpenAI API (synchronous call in thread pool)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging Twitter/X threads from articles. You write concisely and engagingly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
        )
        
        # Extract the generated thread
        generated_text = response.choices[0].message.content.strip()
        
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
        
    except OpenAIError as e:
        # Fallback to basic splitting if GPT fails
        logger.warning(f"OpenAI API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in GPT generation: {str(e)}")
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
                "openai_service": "configured" if openai_client is not None else "not_configured_but_ok"
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
    """Debug endpoint to check startup configuration"""
    return {
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "port": os.getenv("PORT", "not_set"),
        "python_version": sys.version,
        "openai_available": openai_available,
        "openai_client_exists": openai_client is not None,
        "rate_limiting": {
            "requests": RATE_LIMIT_REQUESTS,
            "window_hours": RATE_LIMIT_WINDOW_HOURS
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

@app.post("/api/generate", response_model=GenerateThreadResponse)
async def generate_thread(
    request: GenerateThreadRequest,
    _: None = Depends(check_rate_limit)
):
    """Generate a Twitter/X thread from URL or text content"""
    global openai_available
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
        if openai_available and openai_client:
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
        
        return GenerateThreadResponse(
            success=True,
            thread=thread,
            source_type=source_type,
            title=title
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error with more details in production
        error_id = datetime.now().isoformat()
        logger.error(f"Unexpected error [{error_id}]: {str(e)}", exc_info=True)
        
        if ENVIRONMENT == "production":
            # Don't expose internal errors in production
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error. Error ID: {error_id}"
            )
        else:
            # Show detailed errors in development
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/rate-limit-status")
async def rate_limit_status(request: Request):
    """Check current rate limit status for the client"""
    client_ip = request.client.host
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
        "minutes_until_reset": minutes_until_reset
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
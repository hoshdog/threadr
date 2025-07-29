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

# Initialize rate limiter storage
rate_limiter_storage: Dict[str, List[datetime]] = defaultdict(list)
rate_limiter_lock = asyncio.Lock()

# Configuration
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_HOURS = 1
MAX_TWEET_LENGTH = 280
MAX_CONTENT_LENGTH = 10000  # Maximum characters to process

# Production CORS configuration
PRODUCTION_ORIGINS = [
    "https://threadr.vercel.app",
    "https://www.threadr.com",
    "https://threadr.com",
    # Add your actual production domains here
]

# Determine if we're in production
IS_PRODUCTION = os.getenv("RAILWAY_ENVIRONMENT") == "production" or os.getenv("VERCEL_ENV") == "production"

# Load OpenAI API key
def load_openai_key():
    # First try environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found, try to read from file (development only)
    if not api_key and not IS_PRODUCTION:
        key_file_path = os.path.join(os.path.dirname(__file__), ".openai_key")
        if os.path.exists(key_file_path):
            with open(key_file_path, "r") as f:
                api_key = f.read().strip()
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        )
    
    return api_key

# Initialize OpenAI client
openai_client = None
try:
    api_key = load_openai_key()
    openai_client = OpenAI(api_key=api_key)
except ValueError as e:
    print(f"Warning: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Threadr backend...")
    yield
    # Shutdown
    print("Shutting down Threadr backend...")

# Initialize FastAPI app
app = FastAPI(
    title="Threadr API",
    description="Convert articles and text into Twitter/X threads",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
if IS_PRODUCTION:
    # Production: Only allow specific origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=PRODUCTION_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    # Development: Allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
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
    # In production, use X-Forwarded-For if behind proxy
    client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
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
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except httpx.HTTPStatusError as e:
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
    global openai_client
    
    if not openai_client:
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
        print(f"OpenAI API error: {str(e)}")
        return None

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Threadr API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/generate": "Generate a thread from URL or text"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/generate", response_model=GenerateThreadResponse)
async def generate_thread(
    request: GenerateThreadRequest,
    _: None = Depends(check_rate_limit)
):
    """Generate a Twitter/X thread from URL or text content"""
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
        
        # Try to generate thread with GPT
        tweets = None
        if openai_client:
            try:
                tweets = await generate_thread_with_gpt(content, title)
            except Exception as e:
                print(f"GPT generation failed: {str(e)}")
        
        # Fallback to basic splitting if GPT fails or is not available
        if not tweets:
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
        # Log the error for debugging
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/rate-limit-status")
async def rate_limit_status(request: Request):
    """Check current rate limit status for the client"""
    # In production, use X-Forwarded-For if behind proxy
    client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
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
    uvicorn.run(app, host="0.0.0.0", port=port)
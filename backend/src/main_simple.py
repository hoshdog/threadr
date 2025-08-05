"""
Simple Railway-ready FastAPI application with minimal dependencies
Version: 2.0.1 - Updated 2025-08-05 for immediate deployment
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import sys
import logging
from typing import Optional, List, Dict, Any
import httpx
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

logger.info(f"Starting Threadr API (Simple) - Environment: {ENVIRONMENT}")

# Create FastAPI app
app = FastAPI(
    title="Threadr API",
    description="AI-powered thread generation for social media",
    version="2.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting (simple in-memory for now)
request_counts = {}

def check_rate_limit(ip: str) -> bool:
    """Simple rate limiting check"""
    # For now, always return True (no limiting)
    return True

def get_client_ip(request: Request) -> str:
    """Get client IP from request"""
    # Check various headers for real IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    if request.client:
        return request.client.host
    
    return "unknown"

# Health endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "services": {
            "core": True,
            "rate_limiting": "memory",
            "ai": "openai"
        }
    }

@app.get("/readiness")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Threadr API",
        "version": "2.0.0",
        "status": "operational",
        "environment": ENVIRONMENT,
        "docs": "/docs"
    }

# Thread generation endpoint
@app.post("/api/generate")
async def generate_thread(request: Request):
    """Generate a thread from content or URL"""
    try:
        # Get client IP for rate limiting
        client_ip = get_client_ip(request)
        
        # Check rate limit
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Parse request body
        body = await request.json()
        content = body.get("content", "")
        url = body.get("url", "")
        
        if not content and not url:
            raise HTTPException(
                status_code=400,
                detail="Either content or URL must be provided"
            )
        
        # If URL provided, scrape content
        if url:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract text content
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    content = soup.get_text()
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    if not content:
                        raise HTTPException(
                            status_code=400,
                            detail="Could not extract content from URL"
                        )
                        
            except Exception as e:
                logger.error(f"URL scraping failed: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch content from URL: {str(e)}"
                )
        
        # Generate thread (simplified version)
        # In production, this would call OpenAI API
        words = content.split()
        tweets = []
        current_tweet = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > 280:
                tweets.append(" ".join(current_tweet))
                current_tweet = [word]
                current_length = word_length
            else:
                current_tweet.append(word)
                current_length += word_length
        
        if current_tweet:
            tweets.append(" ".join(current_tweet))
        
        # Limit to 10 tweets max
        tweets = tweets[:10]
        
        return {
            "success": True,
            "tweets": tweets,
            "metadata": {
                "source": "url" if url else "text",
                "timestamp": datetime.now().isoformat(),
                "tweet_count": len(tweets),
                "ip": client_ip
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Thread generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate thread"
        )

# Template endpoints
@app.get("/api/templates")
async def get_templates():
    """Get all available templates"""
    return {
        "templates": [
            {
                "id": "1",
                "name": "Product Launch",
                "description": "Perfect for announcing new products",
                "category": "marketing",
                "isPro": False
            },
            {
                "id": "2", 
                "name": "Thread Storm",
                "description": "Create viral thread storms",
                "category": "engagement",
                "isPro": True
            },
            {
                "id": "3",
                "name": "How-To Guide",
                "description": "Step-by-step instructional threads",
                "category": "educational",
                "isPro": False
            }
        ],
        "categories": ["marketing", "engagement", "educational"]
    }

# Revenue endpoints (stub)
@app.get("/api/revenue/dashboard")
async def get_revenue_dashboard():
    """Get revenue dashboard data"""
    return {
        "metrics": {
            "total_revenue": 0.0,
            "mrr": 0.0,
            "arr": 0.0,
            "active_subscriptions": 0,
            "churn_rate": 0.0,
            "ltv": 0.0
        },
        "chart_data": {
            "daily": [],
            "monthly": []
        },
        "recent_transactions": []
    }

# Premium status endpoint
@app.get("/api/premium-status")
async def get_premium_status(request: Request):
    """Check premium status"""
    client_ip = get_client_ip(request)
    return {
        "isPremium": False,
        "expiresAt": None,
        "ip": client_ip
    }

# Usage stats endpoint
@app.get("/api/usage-stats")
async def get_usage_stats(request: Request):
    """Get usage statistics"""
    client_ip = get_client_ip(request)
    return {
        "daily": {
            "used": 0,
            "limit": 5
        },
        "monthly": {
            "used": 0,
            "limit": 20
        },
        "isPremium": False,
        "ip": client_ip
    }

# Email capture endpoint
@app.post("/api/capture-email")
async def capture_email(request: Request):
    """Capture user email"""
    try:
        body = await request.json()
        email = body.get("email")
        
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email is required"
            )
        
        # In production, save to database
        logger.info(f"Email captured: {email}")
        
        return {
            "success": True,
            "message": "Email captured successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email capture failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to capture email"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
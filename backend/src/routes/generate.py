"""
Thread Generation API Route
Handles the main /api/generate endpoint
"""

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import os
from datetime import datetime

# Import services
try:
    from ..services.thread_generator import thread_generator
    from ..core.redis_manager import get_redis_manager
except ImportError:
    from services.thread_generator import thread_generator
    from core.redis_manager import get_redis_manager

logger = logging.getLogger(__name__)

router = APIRouter()

class GenerateRequest(BaseModel):
    """Request model for thread generation"""
    content: str = Field(..., description="Content to convert into thread")
    url: Optional[str] = Field(None, description="URL to scrape content from")

class GenerateResponse(BaseModel):
    """Response model for thread generation"""
    success: bool
    tweets: Optional[list] = None
    thread_count: Optional[int] = None
    title: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    is_premium: Optional[bool] = None

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    # Check for proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    if request.client:
        return request.client.host
    
    return "unknown"

async def check_rate_limit(client_ip: str) -> Dict[str, Any]:
    """Check rate limits for the client IP"""
    try:
        redis_manager = get_redis_manager()
        if not redis_manager or not redis_manager.is_available:
            # Redis not available, allow request
            logger.warning("Redis not available for rate limiting")
            return {
                "allowed": True,
                "is_premium": False,
                "daily_used": 0,
                "daily_limit": 5,
                "monthly_used": 0,
                "monthly_limit": 20
            }
        
        # Check if user is premium
        is_premium = await redis_manager.check_premium_status(client_ip)
        if is_premium:
            return {
                "allowed": True,
                "is_premium": True,
                "daily_used": 0,
                "daily_limit": "unlimited",
                "monthly_used": 0,
                "monthly_limit": "unlimited"
            }
        
        # Check rate limits for free tier
        usage = await redis_manager.check_usage_limits(client_ip)
        
        # Free tier limits
        daily_limit = int(os.getenv("FREE_TIER_DAILY_LIMIT", "5"))
        monthly_limit = int(os.getenv("FREE_TIER_MONTHLY_LIMIT", "20"))
        
        if usage["daily"] >= daily_limit:
            return {
                "allowed": False,
                "reason": "Daily limit exceeded",
                "is_premium": False,
                "daily_used": usage["daily"],
                "daily_limit": daily_limit,
                "monthly_used": usage["monthly"],
                "monthly_limit": monthly_limit
            }
        
        if usage["monthly"] >= monthly_limit:
            return {
                "allowed": False,
                "reason": "Monthly limit exceeded",
                "is_premium": False,
                "daily_used": usage["daily"],
                "daily_limit": daily_limit,
                "monthly_used": usage["monthly"],
                "monthly_limit": monthly_limit
            }
        
        return {
            "allowed": True,
            "is_premium": False,
            "daily_used": usage["daily"],
            "daily_limit": daily_limit,
            "monthly_used": usage["monthly"],
            "monthly_limit": monthly_limit
        }
        
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        # On error, allow the request
        return {
            "allowed": True,
            "is_premium": False,
            "daily_used": 0,
            "daily_limit": 5,
            "monthly_used": 0,
            "monthly_limit": 20
        }

@router.post("/generate", response_model=GenerateResponse)
async def generate_thread(request: GenerateRequest, req: Request):
    """
    Generate a Twitter/X thread from content or URL
    
    Features:
    - URL scraping from allowed domains
    - OpenAI-powered thread generation
    - Smart content splitting
    - Rate limiting (5 daily/20 monthly for free tier)
    - Premium unlimited access
    """
    try:
        # Get client IP
        client_ip = get_client_ip(req)
        logger.info(f"Thread generation request from {client_ip}")
        
        # Check rate limits
        rate_limit = await check_rate_limit(client_ip)
        if not rate_limit["allowed"]:
            return GenerateResponse(
                success=False,
                error=rate_limit.get("reason", "Rate limit exceeded"),
                usage={
                    "daily_used": rate_limit["daily_used"],
                    "daily_limit": rate_limit["daily_limit"],
                    "monthly_used": rate_limit["monthly_used"],
                    "monthly_limit": rate_limit["monthly_limit"]
                },
                is_premium=False
            )
        
        # Generate thread
        result = await thread_generator.generate_thread(
            content=request.content,
            url=request.url
        )
        
        # Track usage if successful
        if result["success"]:
            try:
                redis_manager = get_redis_manager()
                if redis_manager and redis_manager.is_available:
                    await redis_manager.increment_usage(client_ip)
                    # Update usage counts
                    rate_limit["daily_used"] += 1
                    rate_limit["monthly_used"] += 1
            except Exception as e:
                logger.error(f"Error tracking usage: {e}")
        
        # Return response
        return GenerateResponse(
            success=result["success"],
            tweets=result.get("tweets", []),
            thread_count=result.get("thread_count", 0),
            title=result.get("title", ""),
            error=result.get("error"),
            usage={
                "daily_used": rate_limit["daily_used"],
                "daily_limit": rate_limit["daily_limit"],
                "monthly_used": rate_limit["monthly_used"],
                "monthly_limit": rate_limit["monthly_limit"]
            },
            is_premium=rate_limit["is_premium"]
        )
        
    except Exception as e:
        logger.error(f"Error in generate_thread: {e}")
        return GenerateResponse(
            success=False,
            error=str(e)
        )

@router.get("/usage-stats")
async def get_usage_stats(request: Request):
    """Get usage statistics for the current user/IP"""
    try:
        client_ip = get_client_ip(request)
        rate_limit = await check_rate_limit(client_ip)
        
        return {
            "success": True,
            "is_premium": rate_limit["is_premium"],
            "daily_used": rate_limit["daily_used"],
            "daily_limit": rate_limit["daily_limit"],
            "monthly_used": rate_limit["monthly_used"],
            "monthly_limit": rate_limit["monthly_limit"],
            "can_generate": rate_limit["allowed"]
        }
        
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/premium-status")
async def check_premium_status(request: Request):
    """Check if the current user/IP has premium access"""
    try:
        client_ip = get_client_ip(request)
        redis_manager = get_redis_manager()
        
        if not redis_manager or not redis_manager.is_available:
            return {
                "success": True,
                "is_premium": False,
                "message": "Premium status check unavailable"
            }
        
        is_premium = await redis_manager.check_premium_status(client_ip)
        premium_expires = None
        
        if is_premium:
            # Get expiration time
            try:
                premium_key = f"{redis_manager.premium_prefix}{client_ip}"
                ttl = redis_manager.client.ttl(premium_key)
                if ttl > 0:
                    from datetime import datetime, timedelta
                    premium_expires = (datetime.now() + timedelta(seconds=ttl)).isoformat()
            except:
                pass
        
        return {
            "success": True,
            "is_premium": is_premium,
            "expires_at": premium_expires
        }
        
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return {
            "success": False,
            "error": str(e)
        }
"""
Redis Manager for Threadr - Handles caching and distributed rate limiting
Supports Upstash Redis (free tier) and standard Redis installations
"""

import redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import hashlib
import logging
import os
from contextlib import contextmanager
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class RedisManager:
    """
    Manages Redis connections with support for:
    - Connection pooling
    - Graceful fallback when Redis is unavailable
    - Upstash Redis compatibility (serverless Redis)
    - Async operations using thread pool
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.client: Optional[redis.Redis] = None
        self.pool: Optional[redis.ConnectionPool] = None
        self.is_available = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache configuration
        self.cache_ttl = int(os.getenv("CACHE_TTL_HOURS", "24")) * 3600  # 24 hours default
        self.cache_prefix = "threadr:cache:"
        self.rate_limit_prefix = "threadr:ratelimit:"
        self.email_prefix = "threadr:email:"
        self.email_list_key = "threadr:emails:list"
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Redis connection with proper error handling"""
        if not self.redis_url:
            logger.warning("No REDIS_URL configured - Redis features disabled")
            self.is_available = False
            return
        
        try:
            # Parse Upstash Redis URL format
            # Upstash uses: rediss://default:password@host:port
            if self.redis_url.startswith("rediss://"):
                # SSL connection for Upstash
                self.pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    retry_on_error=[RedisConnectionError],
                    health_check_interval=30,
                    ssl_cert_reqs=None  # Upstash handles SSL
                )
            else:
                # Standard Redis connection
                self.pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    retry_on_error=[RedisConnectionError],
                    health_check_interval=30
                )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            self.client.ping()
            self.is_available = True
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e} - Falling back to in-memory operations")
            self.is_available = False
            self.client = None
    
    @contextmanager
    def _redis_operation(self):
        """Context manager for Redis operations with error handling"""
        if not self.is_available:
            yield None
            return
        
        try:
            yield self.client
        except RedisConnectionError as e:
            logger.warning(f"Redis connection lost: {e}")
            self.is_available = False
            yield None
        except RedisError as e:
            logger.error(f"Redis operation failed: {e}")
            yield None
        except Exception as e:
            logger.error(f"Unexpected Redis error: {e}")
            yield None
    
    def _generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate a unique cache key from request data"""
        # Create a deterministic string representation
        if "url" in request_data and request_data["url"]:
            key_data = f"url:{request_data['url']}"
        elif "text" in request_data and request_data["text"]:
            # Hash the text content for shorter keys
            text_hash = hashlib.sha256(request_data["text"].encode()).hexdigest()[:16]
            key_data = f"text:{text_hash}"
        else:
            return None
        
        return f"{self.cache_prefix}{key_data}"
    
    async def get_cached_thread(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached thread response from Redis"""
        cache_key = self._generate_cache_key(request_data)
        if not cache_key:
            return None
        
        def _get():
            with self._redis_operation() as r:
                if not r:
                    return None
                
                try:
                    cached_data = r.get(cache_key)
                    if cached_data:
                        return json.loads(cached_data)
                    return None
                except Exception as e:
                    logger.error(f"Error retrieving cached data: {e}")
                    return None
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _get)
    
    async def cache_thread_response(self, request_data: Dict[str, Any], response_data: Dict[str, Any]) -> bool:
        """Cache thread response in Redis"""
        cache_key = self._generate_cache_key(request_data)
        if not cache_key:
            return False
        
        def _set():
            with self._redis_operation() as r:
                if not r:
                    return False
                
                try:
                    # Add metadata
                    cache_data = {
                        **response_data,
                        "_cached_at": asyncio.get_event_loop().time(),
                        "_ttl": self.cache_ttl
                    }
                    
                    r.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(cache_data)
                    )
                    logger.info(f"Cached response for key: {cache_key}")
                    return True
                except Exception as e:
                    logger.error(f"Error caching data: {e}")
                    return False
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _set)
    
    async def check_rate_limit(self, client_ip: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """
        Check and update rate limit for a client IP
        Returns: {
            "allowed": bool,
            "requests_used": int,
            "requests_remaining": int,
            "reset_in_seconds": int
        }
        """
        rate_key = f"{self.rate_limit_prefix}{client_ip}"
        
        def _check():
            with self._redis_operation() as r:
                if not r:
                    # Fallback - allow request if Redis is down
                    return {
                        "allowed": True,
                        "requests_used": 0,
                        "requests_remaining": limit,
                        "reset_in_seconds": 0,
                        "redis_available": False
                    }
                
                try:
                    # Use Redis pipeline for atomic operations
                    pipe = r.pipeline()
                    
                    # Increment counter
                    pipe.incr(rate_key)
                    # Set expiry only if key is new
                    pipe.expire(rate_key, window_seconds)
                    # Get current value
                    pipe.get(rate_key)
                    # Get TTL
                    pipe.ttl(rate_key)
                    
                    results = pipe.execute()
                    
                    current_count = int(results[2] or 0)
                    ttl = results[3] if results[3] > 0 else window_seconds
                    
                    if current_count > limit:
                        # Rate limit exceeded
                        return {
                            "allowed": False,
                            "requests_used": current_count,
                            "requests_remaining": 0,
                            "reset_in_seconds": ttl,
                            "redis_available": True
                        }
                    
                    return {
                        "allowed": True,
                        "requests_used": current_count,
                        "requests_remaining": max(0, limit - current_count),
                        "reset_in_seconds": ttl,
                        "redis_available": True
                    }
                    
                except Exception as e:
                    logger.error(f"Rate limit check failed: {e}")
                    # Fallback - allow request
                    return {
                        "allowed": True,
                        "requests_used": 0,
                        "requests_remaining": limit,
                        "reset_in_seconds": 0,
                        "redis_available": False
                    }
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _check)
    
    async def get_rate_limit_status(self, client_ip: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """Get current rate limit status without incrementing counter"""
        rate_key = f"{self.rate_limit_prefix}{client_ip}"
        
        def _status():
            with self._redis_operation() as r:
                if not r:
                    return {
                        "requests_used": 0,
                        "requests_remaining": limit,
                        "reset_in_seconds": 0,
                        "redis_available": False
                    }
                
                try:
                    current_count = r.get(rate_key)
                    ttl = r.ttl(rate_key)
                    
                    count = int(current_count) if current_count else 0
                    ttl = ttl if ttl > 0 else 0
                    
                    return {
                        "requests_used": count,
                        "requests_remaining": max(0, limit - count),
                        "reset_in_seconds": ttl,
                        "redis_available": True
                    }
                    
                except Exception as e:
                    logger.error(f"Rate limit status check failed: {e}")
                    return {
                        "requests_used": 0,
                        "requests_remaining": limit,
                        "reset_in_seconds": 0,
                        "redis_available": False
                    }
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _status)
    
    async def clear_cache_for_key(self, request_data: Dict[str, Any]) -> bool:
        """Clear cached data for a specific request"""
        cache_key = self._generate_cache_key(request_data)
        if not cache_key:
            return False
        
        def _delete():
            with self._redis_operation() as r:
                if not r:
                    return False
                
                try:
                    r.delete(cache_key)
                    return True
                except Exception as e:
                    logger.error(f"Error clearing cache: {e}")
                    return False
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _delete)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        def _stats():
            with self._redis_operation() as r:
                if not r:
                    return {"available": False}
                
                try:
                    # Get all cache keys
                    cache_keys = list(r.scan_iter(f"{self.cache_prefix}*"))
                    rate_keys = list(r.scan_iter(f"{self.rate_limit_prefix}*"))
                    
                    # Get Redis info
                    info = r.info()
                    
                    return {
                        "available": True,
                        "cache_entries": len(cache_keys),
                        "rate_limit_entries": len(rate_keys),
                        "memory_used": info.get("used_memory_human", "N/A"),
                        "connected_clients": info.get("connected_clients", 0),
                        "uptime_seconds": info.get("uptime_in_seconds", 0)
                    }
                    
                except Exception as e:
                    logger.error(f"Error getting cache stats: {e}")
                    return {"available": False, "error": str(e)}
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _stats)
    
    async def store_email_subscription(self, email: str, email_data: Dict[str, Any]) -> bool:
        """Store email subscription with analytics data"""
        email_key = f"{self.email_prefix}{email}"
        
        def _store():
            with self._redis_operation() as r:
                if not r:
                    return False
                
                try:
                    # Use pipeline for atomic operations
                    pipe = r.pipeline()
                    
                    # Store individual email data with expiry (keep for 2 years)
                    email_ttl = 2 * 365 * 24 * 3600  # 2 years
                    pipe.setex(email_key, email_ttl, json.dumps(email_data))
                    
                    # Add to emails set for easy counting and listing
                    pipe.sadd(self.email_list_key, email)
                    
                    # Set expiry on the email list (renew each time we add)
                    pipe.expire(self.email_list_key, email_ttl)
                    
                    results = pipe.execute()
                    
                    # Check if operations succeeded
                    return all(results)
                    
                except Exception as e:
                    logger.error(f"Error storing email subscription: {e}")
                    return False
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _store)
    
    async def get_email_stats(self) -> Dict[str, Any]:
        """Get email subscription statistics"""
        def _stats():
            with self._redis_operation() as r:
                if not r:
                    return {"total_emails": 0, "recent_count": 0}
                
                try:
                    # Get total unique emails
                    total_emails = r.scard(self.email_list_key)
                    
                    # Count recent subscriptions (last 7 days)
                    recent_count = 0
                    cutoff_time = (datetime.now() - timedelta(days=7)).isoformat()
                    
                    # Get sample of emails to check recency
                    sample_emails = list(r.sscan_iter(self.email_list_key, count=100))
                    
                    for email in sample_emails:
                        email_key = f"{self.email_prefix}{email}"
                        email_data_str = r.get(email_key)
                        
                        if email_data_str:
                            try:
                                email_data = json.loads(email_data_str)
                                if email_data.get("subscribed_at", "") > cutoff_time:
                                    recent_count += 1
                            except (json.JSONDecodeError, KeyError):
                                continue
                    
                    # Estimate recent count if we have more emails than sampled
                    if len(sample_emails) == 100 and total_emails > 100:
                        recent_count = int(recent_count * (total_emails / 100))
                    
                    return {
                        "total_emails": total_emails,
                        "recent_count": recent_count,
                        "sample_size": len(sample_emails)
                    }
                    
                except Exception as e:
                    logger.error(f"Error getting email stats: {e}")
                    return {"total_emails": 0, "recent_count": 0, "error": str(e)}
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _stats)
    
    async def get_email_data(self, email: str) -> Optional[Dict[str, Any]]:
        """Get stored data for a specific email"""
        email_key = f"{self.email_prefix}{email}"
        
        def _get():
            with self._redis_operation() as r:
                if not r:
                    return None
                
                try:
                    email_data_str = r.get(email_key)
                    if email_data_str:
                        return json.loads(email_data_str)
                    return None
                except Exception as e:
                    logger.error(f"Error retrieving email data: {e}")
                    return None
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _get)
    
    async def check_email_exists(self, email: str) -> bool:
        """Check if email is already subscribed"""
        def _check():
            with self._redis_operation() as r:
                if not r:
                    return False
                
                try:
                    return r.sismember(self.email_list_key, email)
                except Exception as e:
                    logger.error(f"Error checking email existence: {e}")
                    return False
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _check)
    
    def close(self):
        """Close Redis connection and thread pool"""
        if self.client:
            self.client.close()
        if self.pool:
            self.pool.disconnect()
        self.executor.shutdown(wait=True)
        logger.info("Redis connection closed")

# Global Redis manager instance
redis_manager: Optional[RedisManager] = None

def initialize_redis():
    """Initialize the global Redis manager"""
    global redis_manager
    redis_manager = RedisManager()
    return redis_manager

def get_redis_manager() -> Optional[RedisManager]:
    """Get the global Redis manager instance"""
    return redis_manager
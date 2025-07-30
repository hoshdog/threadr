#!/usr/bin/env python3
"""
Test script for Redis caching and rate limiting functionality
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_URL = "https://example.com/test-article"
TEST_TEXT = "This is a test article about Redis caching. It should be cached for subsequent requests."

async def test_cache_functionality():
    """Test that responses are properly cached"""
    print("\n=== Testing Cache Functionality ===")
    
    async with httpx.AsyncClient() as client:
        # First request (cache miss)
        print("\n1. First request (should be cache miss)...")
        start_time = time.time()
        response1 = await client.post(
            f"{BASE_URL}/api/generate",
            json={"url": TEST_URL},
            timeout=30.0
        )
        first_request_time = time.time() - start_time
        
        if response1.status_code == 200:
            print(f"   ✓ Success (took {first_request_time:.2f}s)")
            thread1 = response1.json()
            print(f"   Generated {len(thread1['thread'])} tweets")
        else:
            print(f"   ✗ Failed: {response1.status_code} - {response1.text}")
            return
        
        # Second request (cache hit)
        print("\n2. Second request (should be cache hit)...")
        start_time = time.time()
        response2 = await client.post(
            f"{BASE_URL}/api/generate",
            json={"url": TEST_URL},
            timeout=30.0
        )
        second_request_time = time.time() - start_time
        
        if response2.status_code == 200:
            print(f"   ✓ Success (took {second_request_time:.2f}s)")
            thread2 = response2.json()
            
            # Verify it's the same response
            if thread1 == thread2:
                print("   ✓ Response matches cached version")
            else:
                print("   ✗ Response doesn't match cached version")
            
            # Cache hit should be much faster
            if second_request_time < first_request_time * 0.5:
                print(f"   ✓ Cache hit is faster ({second_request_time:.2f}s vs {first_request_time:.2f}s)")
            else:
                print(f"   ⚠ Cache might not be working (similar response times)")
        else:
            print(f"   ✗ Failed: {response2.status_code}")

async def test_rate_limiting():
    """Test Redis-based rate limiting"""
    print("\n=== Testing Rate Limiting ===")
    
    async with httpx.AsyncClient() as client:
        # Check current rate limit status
        status_response = await client.get(f"{BASE_URL}/api/rate-limit-status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"\nCurrent rate limit status:")
            print(f"  - Requests used: {status['requests_used']}")
            print(f"  - Requests remaining: {status['requests_remaining']}")
            print(f"  - Using Redis: {status.get('using_redis', False)}")
            print(f"  - Total limit: {status['total_limit']} per {status['window_hours']} hour(s)")

async def test_cache_stats():
    """Test cache statistics endpoint"""
    print("\n=== Testing Cache Statistics ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/cache/stats")
        
        if response.status_code == 200:
            stats = response.json()
            if stats.get("available"):
                print("\n✓ Redis cache is available")
                print(f"  - Cache entries: {stats.get('cache_entries', 0)}")
                print(f"  - Rate limit entries: {stats.get('rate_limit_entries', 0)}")
                print(f"  - Memory used: {stats.get('memory_used', 'N/A')}")
                print(f"  - Connected clients: {stats.get('connected_clients', 0)}")
                print(f"  - Uptime: {stats.get('uptime_seconds', 0)} seconds")
            else:
                print("\n✗ Redis cache is not available")
                print(f"  Message: {stats.get('message', 'Unknown error')}")
        else:
            print(f"\n✗ Failed to get cache stats: {response.status_code}")

async def test_health_monitoring():
    """Test comprehensive health monitoring"""
    print("\n=== Testing Health Monitoring ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/monitor/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"\nOverall status: {health['status']}")
            print("\nService statuses:")
            for service, status in health['services'].items():
                icon = "✓" if status == "healthy" else "✗"
                print(f"  {icon} {service}: {status}")
            
            if health['details'].get('redis', {}).get('available'):
                print("\nRedis details:")
                redis_details = health['details']['redis']
                for key, value in redis_details.items():
                    if key != 'available':
                        print(f"  - {key}: {value}")
        else:
            print(f"\n✗ Failed to get health status: {response.status_code}")

async def test_cache_clear():
    """Test cache clearing functionality"""
    print("\n=== Testing Cache Clear ===")
    
    async with httpx.AsyncClient() as client:
        # First, ensure something is cached
        print("\n1. Generating content to cache...")
        response = await client.post(
            f"{BASE_URL}/api/generate",
            json={"text": TEST_TEXT}
        )
        
        if response.status_code != 200:
            print(f"   ✗ Failed to generate content: {response.status_code}")
            return
        
        print("   ✓ Content generated and cached")
        
        # Clear the cache
        print("\n2. Clearing cache for this content...")
        clear_response = await client.delete(
            f"{BASE_URL}/api/cache/clear",
            json={"text": TEST_TEXT}
        )
        
        if clear_response.status_code == 200:
            result = clear_response.json()
            if result['success']:
                print("   ✓ Cache cleared successfully")
            else:
                print(f"   ✗ Failed to clear cache: {result['message']}")
        else:
            print(f"   ✗ Failed to clear cache: {clear_response.status_code}")

async def main():
    """Run all tests"""
    print(f"Testing Redis implementation at {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print(f"\n✗ Server is not responding at {BASE_URL}")
                return
    except Exception as e:
        print(f"\n✗ Cannot connect to server at {BASE_URL}: {e}")
        return
    
    print("\n✓ Server is running")
    
    # Run tests
    await test_cache_stats()
    await test_health_monitoring()
    await test_cache_functionality()
    await test_rate_limiting()
    await test_cache_clear()
    
    print(f"\n\nAll tests completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
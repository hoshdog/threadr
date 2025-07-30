#!/usr/bin/env python3
"""
Security Test Script for Threadr API
Tests all security features implemented
"""

import asyncio
import httpx
import sys
from urllib.parse import urljoin

# Test configuration
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
API_KEY = sys.argv[2] if len(sys.argv) > 2 else "test-api-key-123"

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_result(test_name: str, passed: bool, details: str = ""):
    status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
    print(f"{test_name}: {status}")
    if details:
        print(f"  → {details}")

async def test_api_authentication():
    """Test API key authentication"""
    print("\n=== Testing API Authentication ===")
    
    async with httpx.AsyncClient() as client:
        # Test without API key
        try:
            response = await client.post(
                urljoin(BASE_URL, "/api/generate"),
                json={"text": "Test content"}
            )
            print_result(
                "Reject request without API key",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            print_result("Reject request without API key", False, str(e))
        
        # Test with invalid API key
        try:
            response = await client.post(
                urljoin(BASE_URL, "/api/generate"),
                headers={"X-API-Key": "invalid-key"},
                json={"text": "Test content"}
            )
            print_result(
                "Reject request with invalid API key",
                response.status_code == 401,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            print_result("Reject request with invalid API key", False, str(e))
        
        # Test with valid API key (if configured)
        try:
            response = await client.post(
                urljoin(BASE_URL, "/api/generate"),
                headers={"X-API-Key": API_KEY},
                json={"text": "Test content for thread generation"}
            )
            print_result(
                "Accept request with valid API key",
                response.status_code in [200, 429],  # 429 if rate limited
                f"Status: {response.status_code}"
            )
        except Exception as e:
            print_result("Accept request with valid API key", False, str(e))

async def test_security_headers():
    """Test security headers"""
    print("\n=== Testing Security Headers ===")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(urljoin(BASE_URL, "/health"))
            headers = response.headers
            
            # Check each security header
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Content-Security-Policy": lambda v: "default-src" in v,
                "Permissions-Policy": lambda v: "geolocation=()" in v,
                "X-Permitted-Cross-Domain-Policies": "none"
            }
            
            for header, expected in security_headers.items():
                if callable(expected):
                    present = header.lower() in headers and expected(headers[header.lower()])
                else:
                    present = headers.get(header.lower()) == expected
                
                print_result(
                    f"Security header: {header}",
                    present,
                    f"Value: {headers.get(header.lower(), 'Not set')}"
                )
                
        except Exception as e:
            print_result("Security headers test", False, str(e))

async def test_ssrf_protection():
    """Test SSRF protection"""
    print("\n=== Testing SSRF Protection ===")
    
    test_urls = [
        ("http://localhost/admin", "Block localhost URL"),
        ("http://127.0.0.1/secret", "Block loopback IP"),
        ("http://192.168.1.1/router", "Block private IP"),
        ("http://10.0.0.1/internal", "Block internal network"),
        ("http://169.254.169.254/metadata", "Block link-local IP"),
        ("file:///etc/passwd", "Block file:// scheme"),
        ("ftp://example.com/file", "Block ftp:// scheme"),
        ("https://medium.com/article", "Allow legitimate domain"),
    ]
    
    async with httpx.AsyncClient() as client:
        for url, test_name in test_urls:
            try:
                response = await client.post(
                    urljoin(BASE_URL, "/api/generate"),
                    headers={"X-API-Key": API_KEY},
                    json={"url": url}
                )
                
                if "Block" in test_name:
                    passed = response.status_code in [400, 403]
                else:
                    passed = response.status_code in [200, 429]
                
                print_result(
                    test_name,
                    passed,
                    f"URL: {url}, Status: {response.status_code}"
                )
                
            except Exception as e:
                print_result(test_name, False, str(e))

async def test_debug_endpoints():
    """Test debug endpoint protection"""
    print("\n=== Testing Debug Endpoint Protection ===")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(urljoin(BASE_URL, "/debug/startup"))
            
            # Should be accessible in development, blocked in production
            if "production" in BASE_URL:
                passed = response.status_code == 404
            else:
                passed = response.status_code == 200
                
            print_result(
                "Debug endpoint protection",
                passed,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            print_result("Debug endpoint protection", False, str(e))

async def test_rate_limiting():
    """Test rate limiting"""
    print("\n=== Testing Rate Limiting ===")
    
    async with httpx.AsyncClient() as client:
        # Check current rate limit status
        try:
            response = await client.get(urljoin(BASE_URL, "/api/rate-limit-status"))
            if response.status_code == 200:
                data = response.json()
                print(f"Current rate limit status:")
                print(f"  - Requests used: {data.get('requests_used', 0)}")
                print(f"  - Requests remaining: {data.get('requests_remaining', 'N/A')}")
                print(f"  - Limit: {data.get('total_limit', 'N/A')} per {data.get('window_hours', 'N/A')} hour(s)")
                print_result("Rate limit status check", True)
            else:
                print_result("Rate limit status check", False, f"Status: {response.status_code}")
        except Exception as e:
            print_result("Rate limit status check", False, str(e))

async def test_public_endpoints():
    """Test public endpoints remain accessible"""
    print("\n=== Testing Public Endpoints ===")
    
    public_endpoints = [
        ("/health", "Health check"),
        ("/readiness", "Readiness check"),
        ("/api/test", "Test endpoint"),
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint, name in public_endpoints:
            try:
                response = await client.get(urljoin(BASE_URL, endpoint))
                print_result(
                    f"Public endpoint: {name}",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                print_result(f"Public endpoint: {name}", False, str(e))

async def main():
    print(f"{YELLOW}Threadr API Security Test Suite{RESET}")
    print(f"Testing API at: {BASE_URL}")
    print(f"Using API key: {API_KEY[:8]}..." if API_KEY else "No API key configured")
    
    # Run all tests
    await test_public_endpoints()
    await test_api_authentication()
    await test_security_headers()
    await test_ssrf_protection()
    await test_debug_endpoints()
    await test_rate_limiting()
    
    print(f"\n{GREEN}Security tests completed!{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
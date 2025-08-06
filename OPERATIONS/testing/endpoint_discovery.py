#!/usr/bin/env python3
"""
Endpoint Discovery Script for Threadr Backend
==============================================

This script discovers available endpoints on the backend.
"""

import requests
import json

BACKEND_URL = "https://threadr-pw0s.onrender.com"

def test_endpoint(path, method="GET"):
    """Test if an endpoint exists"""
    try:
        url = f"{BACKEND_URL}{path}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=10)
        elif method == "OPTIONS":
            response = requests.options(url, timeout=10)
        
        return {
            "path": path,
            "method": method,
            "status": response.status_code,
            "available": response.status_code != 404,
            "headers": dict(response.headers),
            "response_preview": response.text[:200] if response.text else ""
        }
    except Exception as e:
        return {
            "path": path,
            "method": method,
            "error": str(e),
            "available": False
        }

def main():
    """Discover available endpoints"""
    print(f"Discovering endpoints on: {BACKEND_URL}")
    print("=" * 60)
    
    # Common endpoints to test
    endpoints_to_test = [
        # Health/status endpoints
        ("/", "GET"),
        ("/health", "GET"),
        ("/docs", "GET"),
        ("/openapi.json", "GET"),
        
        # Auth endpoints
        ("/api/auth", "GET"),
        ("/api/auth/register", "POST"),
        ("/api/auth/login", "POST"),
        ("/api/auth/me", "GET"),
        ("/api/auth/logout", "POST"),
        ("/api/auth/session/status", "GET"),
        
        # Alternative auth paths
        ("/auth", "GET"),
        ("/auth/register", "POST"),
        ("/auth/login", "POST"),
        ("/auth/me", "GET"),
        
        # Thread endpoints
        ("/api/threads", "GET"),
        ("/api/threads/save", "POST"),
        ("/threads", "GET"),
        
        # Generate endpoint
        ("/api/generate", "POST"),
        ("/generate", "POST"),
        
        # Premium/subscription
        ("/api/premium-status", "GET"),
        ("/api/usage-stats", "GET"),
        ("/premium-status", "GET"),
        
        # Stripe webhook
        ("/api/stripe/webhook", "POST"),
        ("/stripe/webhook", "POST"),
    ]
    
    available_endpoints = []
    
    for path, method in endpoints_to_test:
        result = test_endpoint(path, method)
        
        if result.get("available"):
            status = f"[AVAILABLE] {result['status']}"
            available_endpoints.append((path, method, result['status']))
        else:
            status = f"[NOT FOUND] {result.get('status', 'ERROR')}"
        
        print(f"{method:<7} {path:<30} {status}")
        
        if result.get("error"):
            print(f"        Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("AVAILABLE ENDPOINTS SUMMARY:")
    print("=" * 60)
    
    if available_endpoints:
        for path, method, status_code in available_endpoints:
            print(f"{method:<7} {path:<30} Status: {status_code}")
    else:
        print("No endpoints found! This suggests the backend may not be running or accessible.")
    
    # Test the root endpoint in detail
    print("\n" + "=" * 60)
    print("ROOT ENDPOINT DETAILS:")
    print("=" * 60)
    
    root_result = test_endpoint("/", "GET")
    print(f"Status: {root_result.get('status', 'ERROR')}")
    print(f"Headers: {json.dumps(root_result.get('headers', {}), indent=2)}")
    print(f"Response Preview: {root_result.get('response_preview', 'No response')}")

if __name__ == "__main__":
    main()
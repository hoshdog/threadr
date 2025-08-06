#!/usr/bin/env python3
"""
Test Render.com deployment health
"""
import requests
import json
from datetime import datetime

def test_render_backend(base_url):
    """Test all endpoints on the Render deployment"""
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    print(f"\n[TESTING] Render Backend: {base_url}")
    print("=" * 60)
    
    # Test 1: Root endpoint
    try:
        print("\n1. Testing root endpoint (/)...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] App: {data.get('app', 'Unknown')}")
            print(f"   [OK] Version: {data.get('version', 'Unknown')}")
            print(f"   [OK] Deployment: {data.get('deployment', 'Unknown')}")
        else:
            print(f"   [ERROR] Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 2: Health endpoint
    try:
        print("\n2. Testing health endpoint (/health)...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Status: {data.get('status', 'Unknown')}")
            print(f"   [OK] App: {data.get('app', 'Unknown')}")
        else:
            print(f"   [ERROR] Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 3: Generate endpoint (POST)
    try:
        print("\n3. Testing generate endpoint (/api/generate)...")
        test_data = {
            "content": "This is a test tweet that should be split into multiple parts if it's long enough to exceed the Twitter character limit of 280 characters. Let's add more text to make sure it actually needs splitting. This additional sentence should push us over the limit."
        }
        response = requests.post(
            f"{base_url}/api/generate",
            json=test_data,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Success: {data.get('success', False)}")
            print(f"   [OK] Tweets generated: {data.get('count', 0)}")
            if data.get('tweets'):
                print(f"   [OK] First tweet preview: {data['tweets'][0][:50]}...")
        else:
            print(f"   [ERROR] Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 4: CORS headers
    try:
        print("\n4. Testing CORS configuration...")
        response = requests.options(
            f"{base_url}/api/generate",
            headers={"Origin": "https://threadr-nextjs.vercel.app"},
            timeout=10
        )
        cors_headers = response.headers.get('access-control-allow-origin', 'Not set')
        print(f"   CORS Allow-Origin: {cors_headers}")
        if cors_headers == "*" or "vercel.app" in cors_headers:
            print(f"   [OK] CORS configured correctly")
        else:
            print(f"   [WARNING] CORS may need configuration")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n" + "=" * 60)
    print("[SUMMARY] Deployment Test Results:")
    print("   - If all tests pass, your backend is ready!")
    print("   - Next step: Deploy frontend to Vercel")
    print("=" * 60)

if __name__ == "__main__":
    print("\n[RENDER BACKEND DEPLOYMENT TESTER]")
    print("=" * 40)
    
    backend_url = input("\nEnter your Render backend URL (e.g., https://threadr-backend.onrender.com): ").strip()
    
    if not backend_url:
        print("[ERROR] No URL provided. Exiting.")
    elif not backend_url.startswith("http"):
        print("[ERROR] Invalid URL. Must start with http:// or https://")
    else:
        test_render_backend(backend_url)
        print("\n[COMPLETE] Testing finished!")
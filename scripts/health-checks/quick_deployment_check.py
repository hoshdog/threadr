#!/usr/bin/env python3
"""
Quick deployment check for both frontend and backend
"""

import requests
import time
from datetime import datetime

def check_frontend():
    """Check if Next.js frontend is deployed"""
    try:
        # Try common Vercel URLs
        urls = [
            "https://threadr-nextjs.vercel.app",
            "https://threadr.vercel.app",
            "https://threadr-nextjs-git-main.vercel.app"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[OK] Frontend LIVE: {url}")
                    return url
            except:
                continue
                
        print("[ERROR] Frontend not accessible")
        return None
    except Exception as e:
        print(f"[ERROR] Frontend check failed: {e}")
        return None

def check_backend():
    """Check if backend is healthy"""
    try:
        response = requests.get("https://threadr-pw0s.onrender.com/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Backend HEALTHY: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"[ERROR] Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Backend check failed: {e}")
        return False

def check_api_endpoints():
    """Check critical API endpoints"""
    endpoints = [
        "/api/premium-status",
        "/api/usage-stats"
    ]
    
    base_url = "https://threadr-pw0s.onrender.com"
    working = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code != 404:
                print(f"[OK] {endpoint}: Working ({response.status_code})")
                working += 1
            else:
                print(f"[ERROR] {endpoint}: 404 Not Found")
        except Exception as e:
            print(f"[ERROR] {endpoint}: Error - {str(e)[:50]}")
    
    return working, len(endpoints)

def main():
    print("=" * 60)
    print("THREADR DEPLOYMENT QUICK CHECK")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Check frontend
    print("\n[FRONTEND CHECK]")
    frontend_url = check_frontend()
    
    # Check backend
    print("\n[BACKEND CHECK]")
    backend_ok = check_backend()
    
    # Check API endpoints
    print("\n[API ENDPOINTS CHECK]")
    working, total = check_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if frontend_url and backend_ok:
        print("*** BOTH DEPLOYMENTS SUCCESSFUL! ***")
        print(f"\nFrontend: {frontend_url}")
        print("Backend: https://threadr-pw0s.onrender.com")
        
        if working == total:
            print(f"\n[OK] All {total} API endpoints working")
            print("\n*** READY FOR TESTING! ***")
            print("\nNext steps:")
            print("1. Visit the frontend URL")
            print("2. Test thread generation")
            print("3. Test payment flow")
        else:
            print(f"\n[WARNING] {total - working} API endpoints need fixing")
            print("The 404 errors from console logs may persist")
            
    elif frontend_url:
        print("[PARTIAL] FRONTEND DEPLOYED, BACKEND ISSUES")
        print("Frontend is live but backend may have problems")
        
    elif backend_ok:
        print("[PARTIAL] BACKEND HEALTHY, FRONTEND DEPLOYING")
        print("Backend is working, frontend may still be deploying")
        
    else:
        print("[ERROR] BOTH DEPLOYMENTS HAVE ISSUES")
        print("Check deployment dashboards for errors")

if __name__ == "__main__":
    main()
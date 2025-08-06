#!/usr/bin/env python3
"""
Monitor Render deployment status
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://threadr-pw0s.onrender.com"

def check_auth_endpoints():
    """Check if auth endpoints are available"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={},  # Empty JSON to test endpoint existence
            timeout=5
        )
        # 422 means endpoint exists but needs data
        # 404 means endpoint doesn't exist
        return response.status_code != 404
    except:
        return False

def check_openapi():
    """Check OpenAPI for auth endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            auth_paths = [p for p in paths if "/auth/" in p]
            return len(auth_paths) > 0
        return False
    except:
        return False

def main():
    print("=" * 60)
    print("MONITORING RENDER DEPLOYMENT")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print("Checking every 30 seconds...")
    print("=" * 60)
    
    check_count = 0
    max_checks = 20  # 10 minutes max
    
    while check_count < max_checks:
        check_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Check auth endpoints
        auth_available = check_auth_endpoints()
        openapi_has_auth = check_openapi()
        
        if auth_available:
            print(f"\n[{current_time}] SUCCESS! Authentication deployed!")
            print("Auth endpoints are now available.")
            print("You can now proceed with testing.")
            break
        else:
            status = "Has auth in OpenAPI" if openapi_has_auth else "No auth endpoints"
            print(f"[{current_time}] Check #{check_count}: {status} - waiting...")
            
            if check_count < max_checks:
                time.sleep(30)  # Wait 30 seconds before next check
    
    if check_count >= max_checks:
        print("\n[TIMEOUT] Deployment didn't complete in 10 minutes.")
        print("Manual intervention may be required:")
        print("1. Check Render dashboard for deployment status")
        print("2. Look for build/deployment errors")
        print("3. May need to trigger manual deploy")

if __name__ == "__main__":
    main()
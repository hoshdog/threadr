#!/usr/bin/env python3
"""
Monitor Next.js deployment on Vercel
"""

import requests
import time
from datetime import datetime

# Configuration
NEXTJS_URL = "https://threadr-nextjs.vercel.app"
BACKEND_URL = "https://threadr-pw0s.onrender.com"

def check_nextjs_health():
    """Check if Next.js app is responding"""
    try:
        response = requests.get(NEXTJS_URL, timeout=10)
        return response.status_code == 200
    except:
        return False

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        data = response.json()
        return data.get("status") == "healthy"
    except:
        return False

def check_api_integration():
    """Check if Next.js can reach backend"""
    try:
        # Try to fetch usage stats through Next.js proxy
        response = requests.get(f"{NEXTJS_URL}/api/usage-stats", timeout=10)
        return response.status_code in [200, 404]  # 404 is ok, means proxy is working
    except:
        return False

def main():
    print("=" * 60)
    print("MONITORING NEXT.JS DEPLOYMENT")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Next.js URL: {NEXTJS_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    # Initial check
    print("\n[INITIAL STATUS]")
    nextjs_ready = check_nextjs_health()
    backend_ready = check_backend_health()
    api_connected = check_api_integration()
    
    print(f"Next.js App: {'READY' if nextjs_ready else 'NOT READY'}")
    print(f"Backend API: {'READY' if backend_ready else 'NOT READY'}")
    print(f"API Integration: {'CONNECTED' if api_connected else 'NOT CONNECTED'}")
    
    if not nextjs_ready:
        print("\nWaiting for Next.js deployment to complete...")
        print("This typically takes 2-5 minutes on Vercel...")
        
        # Monitor for up to 10 minutes
        for i in range(20):
            time.sleep(30)
            current_time = datetime.now().strftime('%H:%M:%S')
            
            nextjs_ready = check_nextjs_health()
            if nextjs_ready:
                print(f"\n[{current_time}] SUCCESS! Next.js deployed!")
                break
            else:
                print(f"[{current_time}] Check #{i+1}: Still deploying...")
    
    # Final status check
    print("\n" + "=" * 60)
    print("DEPLOYMENT STATUS")
    print("=" * 60)
    
    nextjs_ready = check_nextjs_health()
    backend_ready = check_backend_health()
    api_connected = check_api_integration()
    
    print(f"Next.js Frontend: {'✓ DEPLOYED' if nextjs_ready else '✗ NOT READY'}")
    print(f"Backend API: {'✓ RUNNING' if backend_ready else '✗ NOT READY'}")
    print(f"API Connection: {'✓ WORKING' if api_connected else '✗ NOT CONNECTED'}")
    
    if nextjs_ready and backend_ready:
        print("\n[SUCCESS] Both frontend and backend are operational!")
        print("\nNEXT STEPS:")
        print("1. Visit", NEXTJS_URL, "to see the app")
        print("2. Test thread generation")
        print("3. Test authentication")
        print("4. Test payment flow")
        
        if not api_connected:
            print("\n[WARNING] API connection not working.")
            print("You may need to:")
            print("1. Add CORS origins in Render dashboard")
            print("2. Configure environment variables in Vercel")
    else:
        print("\n[WAITING] Deployment in progress...")
        print("Check Vercel dashboard for deployment status")
        print("URL: https://vercel.com/dashboard")

if __name__ == "__main__":
    main()
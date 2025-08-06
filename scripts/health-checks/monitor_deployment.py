#!/usr/bin/env python3
"""
Monitor Render deployment status
Checks every 30 seconds to see when deployment switches from minimal to full
"""

import requests
import time
import json
from datetime import datetime

def check_deployment():
    """Check if deployment is using full or minimal app"""
    url = "https://threadr-pw0s.onrender.com/health"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Check if it's the minimal app
        if data.get("app") == "minimal":
            return "minimal", data
        else:
            # Full app doesn't have "app": "minimal"
            return "full", data
            
    except Exception as e:
        return "error", str(e)

def main():
    print("\n[RENDER DEPLOYMENT MONITOR]")
    print("=" * 60)
    print("Monitoring: https://threadr-pw0s.onrender.com")
    print("Checking every 30 seconds...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    last_status = None
    check_count = 0
    
    while True:
        check_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        status, data = check_deployment()
        
        if status == "error":
            print(f"[{timestamp}] Check #{check_count}: ERROR - {data}")
        elif status == "minimal":
            if last_status != "minimal":
                print(f"\n[{timestamp}] Check #{check_count}: MINIMAL APP RUNNING")
                print("    Status: Still using minimal backend")
                print("    Action Required: Sync Blueprint in Render dashboard")
            else:
                print(f"[{timestamp}] Check #{check_count}: Still minimal...", end="\r")
        elif status == "full":
            print(f"\n[{timestamp}] Check #{check_count}: FULL APP DETECTED!")
            print("    Status: Full backend is now running!")
            print("    Services:", json.dumps(data.get("services", {}), indent=8))
            print("\n[SUCCESS] Deployment switched to full backend!")
            print("You can now run the full test suite.")
            break
            
        last_status = status
        
        if status != "full":
            time.sleep(30)
    
    print("\n" + "=" * 60)
    print("Deployment monitoring complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Monitoring cancelled by user")
        print("Current status: Check manually at https://threadr-pw0s.onrender.com/health")
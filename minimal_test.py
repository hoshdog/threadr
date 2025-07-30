#!/usr/bin/env python3
"""
Minimal test to check Railway deployment status
"""

import requests
import sys

def check_railway_status():
    url = "https://threadr-production.up.railway.app/health"
    
    print("Checking Railway deployment status...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 502:
            print("\n=== DEPLOYMENT IS DOWN ===")
            print("The Railway service is not responding.")
            print("\nPossible causes:")
            print("1. Application failed to start")
            print("2. Port binding issues")
            print("3. Import errors")
            print("4. Missing environment variables")
            print("5. Railway platform issues")
            
            print("\nRecommended fixes:")
            print("1. Check Railway logs: railway logs")
            print("2. Redeploy: railway up")
            print("3. Check environment variables in Railway dashboard")
            print("4. Verify OPENAI_API_KEY is set")
            
        elif response.status_code == 200:
            print("\n=== DEPLOYMENT IS WORKING ===")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_railway_status()
#!/usr/bin/env python3
"""
Check which commit Render.com is currently running
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "https://threadr-pw0s.onrender.com"

async def check_render_commit():
    """Check current deployment status and commit info"""
    async with aiohttp.ClientSession() as session:
        
        print("RENDER.COM DEPLOYMENT COMMIT CHECK")
        print("=" * 50)
        print(f"Checking: {BASE_URL}")
        print(f"Time: {datetime.now()}")
        print()
        
        # Check if new auth diagnosis script endpoint works
        print("1. Testing for auth diagnosis script (commit 7089c9b):")
        try:
            # The test_auth_diagnosis.py script would create this endpoint pattern
            async with session.get(f"{BASE_URL}/api/auth/debug/diagnosis") as resp:
                if resp.status == 200:
                    print("   SUCCESS: Auth diagnosis endpoint found!")
                    print("   Commit 7089c9b is deployed")
                elif resp.status == 404:
                    print("   MISSING: Auth diagnosis endpoint not found")
                    print("   Commit 7089c9b NOT deployed yet")
                else:
                    print(f"   Endpoint exists but returned {resp.status}")
        except Exception as e:
            print(f"   Error checking endpoint: {e}")
        
        # Check latest version endpoint from most recent commit
        print("\n2. Testing for deployment version check (commit 9fd3968):")
        try:
            async with session.get(f"{BASE_URL}/api/deployment/version") as resp:
                if resp.status == 200:
                    version_data = await resp.json()
                    print("   SUCCESS: Version endpoint found!")
                    print(f"   Deployed commit: {version_data.get('commit_hash', 'Unknown')}")
                    print(f"   Deploy time: {version_data.get('deploy_time', 'Unknown')}")
                    print(f"   Version: {version_data.get('version', 'Unknown')}")
                elif resp.status == 404:
                    print("   MISSING: Version endpoint not found")
                    print("   Latest commit NOT deployed yet")
                else:
                    print(f"   Endpoint exists but returned {resp.status}")
        except Exception as e:
            print(f"   Error checking version: {e}")
        
        # Basic health check
        print("\n3. Basic health check:")
        try:
            async with session.get(f"{BASE_URL}/health") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    print("   Backend is running")
                    print(f"   Status: {health_data.get('status')}")
                    print(f"   Timestamp: {health_data.get('timestamp')}")
                else:
                    print(f"   Health check failed: {resp.status}")
        except Exception as e:
            print(f"   Health check error: {e}")
        
        # File existence test (if we can check it somehow)
        print("\n4. Auth endpoint test (indirect file check):")
        try:
            async with session.get(f"{BASE_URL}/api/auth/register") as resp:
                if resp.status in [405, 422]:  # Method not allowed or validation error
                    print("   Auth endpoints are working")
                elif resp.status == 404:
                    print("   Auth endpoints not found - deployment issue")
                else:
                    print(f"   Unexpected auth response: {resp.status}")
        except Exception as e:
            print(f"   Auth endpoint error: {e}")
        
        print("\n" + "=" * 50)
        
        # Render status summary
        print("\nDEPLOYMENT STATUS SUMMARY:")
        print("- If version endpoint works: Latest commits are deployed")
        print("- If auth diagnosis endpoint works: Commit 7089c9b is deployed") 
        print("- If neither work: Render hasn't pulled latest code")
        print("\nNEXT STEPS IF NOT DEPLOYED:")
        print("1. Check Render dashboard for deployment logs")
        print("2. Try manual deploy from Render dashboard") 
        print("3. Verify branch is set to 'main' in Render settings")
        print("4. Check for deployment errors in Render logs")

if __name__ == "__main__":
    asyncio.run(check_render_commit())
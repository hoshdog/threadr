#!/usr/bin/env python3
"""
Test backend authentication service directly to isolate the issue
"""

import asyncio
import aiohttp
import json

async def test_backend_services():
    """Test backend health and specific services"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    
    async with aiohttp.ClientSession() as session:
        
        # Test health check in detail
        print("=== BACKEND HEALTH CHECK ===")
        try:
            async with session.get(f"{base_url}/health") as response:
                status = response.status
                health_data = await response.json()
                
                print(f"Health Status: {status}")
                print(f"Health Response: {json.dumps(health_data, indent=2)}")
                
        except Exception as e:
            print(f"Health check failed: {str(e)}")
        
        # Test Redis connection via the health endpoint
        print("\n=== REDIS SERVICE TEST ===")
        try:
            async with session.get(f"{base_url}/health") as response:
                health_data = await response.json()
                redis_status = health_data.get('services', {}).get('redis')
                
                print(f"Redis Status: {redis_status}")
                
                if not redis_status:
                    print("ERROR: Redis is not connected!")
                else:
                    print("SUCCESS: Redis connection working")
                    
        except Exception as e:
            print(f"Redis check failed: {str(e)}")
        
        # Test database connection via the health endpoint  
        print("\n=== DATABASE SERVICE TEST ===")
        try:
            async with session.get(f"{base_url}/health") as response:
                health_data = await response.json()
                db_status = health_data.get('services', {}).get('database')
                
                print(f"Database Status: {db_status}")
                
                if not db_status:
                    print("ERROR: Database is not connected!")
                else:
                    print("SUCCESS: Database connection working")
                    
        except Exception as e:
            print(f"Database check failed: {str(e)}")
        
        # Test if auth service initialization worked
        print("\n=== AUTH SERVICE TEST ===")
        try:
            async with session.get(f"{base_url}/api/auth/session/status") as response:
                status = response.status
                session_data = await response.json()
                
                print(f"Auth Session Status: {status}")
                print(f"Session Response: {json.dumps(session_data, indent=2)}")
                
                if status != 200:
                    print("ERROR: Auth service may not be properly initialized!")
                else:
                    print("SUCCESS: Auth service responding")
                    
        except Exception as e:
            print(f"Auth service test failed: {str(e)}")
        
        # Test if the auth router is properly initialized
        print("\n=== AUTH ROUTER TEST ===")
        try:
            # The main auth router has a test endpoint that shows if it's properly initialized
            async with session.get(f"{base_url}/api/auth/") as response:
                status = response.status
                router_data = await response.json()
                
                print(f"Auth Router Status: {status}")
                print(f"Router Response: {json.dumps(router_data, indent=2)}")
                
                if "not properly initialized" in str(router_data):
                    print("ERROR: Auth router not properly initialized!")
                else:
                    print("SUCCESS: Auth router working")
                    
        except Exception as e:
            print(f"Auth router test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_backend_services())
#!/usr/bin/env python3
"""
Test JWT token creation directly to see if that's the issue
"""

import asyncio
import aiohttp
import json

async def test_jwt_environment():
    """Test if JWT environment is set up correctly"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    
    async with aiohttp.ClientSession() as session:
        
        # Test if we can trigger JWT token creation via password strength endpoint
        print("=== JWT ENVIRONMENT TEST ===")
        
        try:
            # This endpoint doesn't require auth but might use JWT utilities
            async with session.get(
                f"{base_url}/api/auth/password-strength",
                params={"password": "TestPassword123!"}
            ) as response:
                status = response.status
                data = await response.json()
                
                print(f"Password Strength Test Status: {status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if status == 200:
                    print("SUCCESS: Backend utilities are working")
                else:
                    print(f"ERROR: Backend utility endpoint failed with {status}")
                    
        except Exception as e:
            print(f"JWT Environment test failed: {str(e)}")
        
        # Test if we can get some debug information from session status
        print("\n=== DEBUG SESSION STATUS ===")
        
        try:
            async with session.get(f"{base_url}/api/auth/session/status") as response:
                status = response.status
                session_data = await response.json()
                
                print(f"Session Status: {status}")
                print(f"Session Data: {json.dumps(session_data, indent=2)}")
                
                # Look for any clues about JWT configuration
                if 'authenticated' in session_data:
                    print("SUCCESS: Auth service can process session requests")
                else:
                    print("WARNING: Unexpected session response format")
                    
        except Exception as e:
            print(f"Session status test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_jwt_environment())
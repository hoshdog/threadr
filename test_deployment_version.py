#!/usr/bin/env python3
"""
Test if deployment includes our latest changes
"""

import asyncio
import aiohttp
import json

async def test_deployment_version():
    """Test if the deployment has our latest changes"""
    
    base_url = "https://threadr-pw0s.onrender.com"
    
    async with aiohttp.ClientSession() as session:
        
        print("=== DEPLOYMENT VERSION CHECK ===")
        
        # Test the specific fix I made - if JWT secret key is not set,
        # there should be a warning logged about using auto-generated key
        
        # The health endpoint might give us clues about the deployment timestamp
        try:
            async with session.get(f"{base_url}/health") as response:
                health_data = await response.json()
                timestamp = health_data.get('timestamp')
                
                print(f"Backend Health Timestamp: {timestamp}")
                print("This shows when the backend last restarted/deployed")
                
        except Exception as e:
            print(f"Health check failed: {str(e)}")
        
        # Try a registration with very detailed error checking
        print("\n=== DETAILED REGISTRATION TEST ===")
        
        test_data = {
            "email": "detailed-test@example.com",
            "password": "DetailedTest123!",
            "confirm_password": "DetailedTest123!"
        }
        
        try:
            # Make the request with maximum debugging
            async with session.post(
                f"{base_url}/api/auth/register",
                json=test_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "DeploymentVersionTest/1.0"
                }
            ) as response:
                
                status = response.status
                headers = dict(response.headers)
                
                print(f"Registration Status: {status}")
                print(f"Response Headers: {json.dumps(headers, indent=2)}")
                
                try:
                    response_data = await response.json()
                    print(f"Response Data: {json.dumps(response_data, indent=2)}")
                except:
                    response_text = await response.text()
                    print(f"Response Text: {response_text}")
                
                # Analysis
                if status == 201:
                    print("✓ SUCCESS: Registration is working! Fix was deployed successfully.")
                elif status == 400:
                    print("✗ STILL BROKEN: 400 error suggests the fixes haven't been deployed or there's another issue")
                elif status == 500:
                    print("✗ SERVER ERROR: 500 suggests a different problem, possibly deployment issue")
                else:
                    print(f"? UNEXPECTED: Status {status} is unusual")
                    
        except Exception as e:
            print(f"Registration test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_deployment_version())
#!/usr/bin/env python3
"""
Quick diagnostic script to check database configuration issues
"""

import requests
import json
import sys

def check_database_status():
    """Check the current database status and provide diagnostics"""
    
    backend_url = "https://threadr-pw0s.onrender.com"
    
    print("Diagnosing PostgreSQL Database Configuration...")
    print(f"Backend URL: {backend_url}")
    print("=" * 50)
    
    try:
        # 1. Check health endpoint
        print("1. Checking health endpoint...")
        response = requests.get(f"{backend_url}/health", timeout=10)
        
        if response.status_code != 200:
            print(f"Health endpoint failed: HTTP {response.status_code}")
            return
            
        health_data = response.json()
        print("Health endpoint responding")
        
        # 2. Analyze database status
        print("\n2. Analyzing database status...")
        services = health_data.get('services', {})
        database_status = services.get('database', 'unknown')
        redis_status = services.get('redis', 'unknown')
        
        print(f"   Database: {database_status}")
        print(f"   Redis: {redis_status}")
        print(f"   Environment: {health_data.get('environment', 'unknown')}")
        
        # 3. Provide diagnosis
        print("\n3. Diagnosis...")
        if database_status is False:
            print("ISSUE IDENTIFIED: Database connection failed")
            print("\nMost likely causes:")
            print("   1. DATABASE_URL environment variable not set in Render")
            print("   2. PostgreSQL database not created in Render")
            print("   3. Database import modules failing")
            print("   4. PostgreSQL service not accessible")
            
            print("\nImmediate actions:")
            print("   1. Check Render Dashboard -> threadr-backend -> Environment")
            print("   2. Verify DATABASE_URL is set with PostgreSQL connection string")
            print("   3. Check Render Dashboard -> Databases for PostgreSQL instance")
            print("   4. Review deployment logs for 'Database modules not found' errors")
            
        elif database_status is True:
            print("Database connection working!")
            print("   Ready for user authentication testing")
            
        else:
            print(f"Unknown database status: {database_status}")
            
        # 4. Test authentication endpoint
        print("\n4. Testing authentication endpoint...")
        try:
            auth_test = requests.post(
                f"{backend_url}/api/auth/register",
                json={
                    "email": "test-diagnostic@example.com",
                    "password": "TestPass123",
                    "confirm_password": "TestPass123", 
                    "full_name": "Diagnostic Test"
                },
                timeout=10
            )
            
            if auth_test.status_code in [200, 201]:
                print("Authentication endpoint working")
            elif auth_test.status_code == 422:
                # Validation error - endpoint is working but data format wrong
                print("Authentication endpoint responding but validation failed")
                try:
                    error_data = auth_test.json()
                    print(f"   Validation error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print("   Could not parse error response")
            else:
                print(f"Authentication endpoint failed: HTTP {auth_test.status_code}")
                try:
                    error_data = auth_test.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {auth_test.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"Authentication endpoint unreachable: {e}")
            
        # 5. Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        if database_status is True:
            print("STATUS: Database integration SUCCESS")
            print("Next step: Test full authentication flow")
        else:
            print("STATUS: Database integration FAILED")  
            print("Next step: Fix database configuration in Render")
            
        print(f"\nFull health response:")
        print(json.dumps(health_data, indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to backend: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

if __name__ == "__main__":
    check_database_status()
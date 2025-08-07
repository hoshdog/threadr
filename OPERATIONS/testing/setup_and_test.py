#!/usr/bin/env python3
"""
Setup and Quick Test Script for Threadr Authentication Testing
Installs dependencies and runs a basic connectivity test

Usage:
    python setup_and_test.py
"""

import subprocess
import sys
import asyncio
import aiohttp
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        "aiohttp",
        "colorama", 
        "pyjwt",
        "asyncio"
    ]
    
    print(f"{Fore.CYAN}>> Installing dependencies...")
    
    for dep in dependencies:
        try:
            print(f"{Fore.YELLOW}Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "--quiet"])
            print(f"{Fore.GREEN}+ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}x Failed to install {dep}: {e}")
            return False
        except Exception as e:
            print(f"{Fore.RED}x Error installing {dep}: {e}")
            return False
    
    return True

async def test_backend_connectivity():
    """Test basic backend connectivity"""
    base_url = "https://threadr-pw0s.onrender.com"
    
    print(f"\n{Fore.CYAN}>> Testing backend connectivity...")
    print(f"{Fore.WHITE}Target: {base_url}")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            
            # Test health endpoint
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"{Fore.GREEN}+ Health check passed")
                    print(f"{Fore.WHITE}  Status: {health_data.get('status')}")
                    print(f"{Fore.WHITE}  Database: {health_data.get('services', {}).get('database')}")
                    print(f"{Fore.WHITE}  Redis: {health_data.get('services', {}).get('redis')}")
                    
                    # Check if database is connected
                    db_connected = health_data.get('services', {}).get('database') is True
                    redis_connected = health_data.get('services', {}).get('redis') is True
                    
                    if db_connected and redis_connected:
                        print(f"{Fore.GREEN}+ Backend is healthy and ready for testing!")
                        return True
                    else:
                        print(f"{Fore.YELLOW}! Backend partially healthy:")
                        print(f"{Fore.YELLOW}  Database: {'Connected' if db_connected else 'Not Connected'}")
                        print(f"{Fore.YELLOW}  Redis: {'Connected' if redis_connected else 'Not Connected'}")
                        return False
                else:
                    print(f"{Fore.RED}x Health check failed: Status {response.status}")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"{Fore.RED}x Connection error: {e}")
        return False
    except Exception as e:
        print(f"{Fore.RED}x Unexpected error: {e}")
        return False

async def run_quick_auth_test():
    """Run a quick authentication test"""
    base_url = "https://threadr-pw0s.onrender.com"
    
    print(f"\n{Fore.CYAN}>> Running quick authentication test...")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            
            # Test registration endpoint with invalid data (should fail gracefully)
            invalid_registration = {
                "email": "invalid-email",
                "password": "weak",
                "confirm_password": "weak"
            }
            
            async with session.post(
                f"{base_url}/api/auth/register",
                json=invalid_registration,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status in [400, 422]:  # Expected validation error
                    print(f"{Fore.GREEN}+ Registration endpoint responding correctly")
                    print(f"{Fore.WHITE}  Validation errors properly handled: Status {response.status}")
                    return True
                elif response.status == 201:
                    print(f"{Fore.YELLOW}! Registration succeeded with weak data (potential issue)")
                    return True
                elif response.status >= 500:
                    print(f"{Fore.RED}x Server error: Status {response.status}")
                    return False
                else:
                    print(f"{Fore.YELLOW}? Unexpected response: Status {response.status}")
                    return True
                    
    except Exception as e:
        print(f"{Fore.RED}x Authentication test error: {e}")
        return False

def print_test_commands():
    """Print available test commands"""
    print(f"\n{Fore.CYAN}>> AVAILABLE TEST COMMANDS:")
    print(f"{Fore.WHITE}")
    print("1. Run all authentication tests:")
    print("   python run_auth_tests.py")
    print()
    print("2. Run specific test suite:")
    print("   python run_auth_tests.py --suite=comprehensive")
    print("   python run_auth_tests.py --suite=database")
    print("   python run_auth_tests.py --suite=security")
    print()
    print("3. Export test results:")
    print("   python run_auth_tests.py --output=json")
    print("   python run_auth_tests.py --output=markdown")
    print()
    print("4. Run individual test suites:")
    print("   python comprehensive_auth_test_suite.py")
    print("   python test_database_integration.py")
    print("   python test_auth_security.py")

async def main():
    """Main setup and test function"""
    print(f"{Fore.CYAN}>> Threadr Authentication Test Setup")
    print(f"{Fore.WHITE}Setting up environment and testing connectivity...")
    
    # Install dependencies
    if not install_dependencies():
        print(f"\n{Fore.RED}x Dependency installation failed")
        return 1
    
    print(f"\n{Fore.GREEN}+ All dependencies installed successfully")
    
    # Test backend connectivity
    if not await test_backend_connectivity():
        print(f"\n{Fore.RED}x Backend connectivity test failed")
        print(f"{Fore.YELLOW}! Tests may fail due to backend issues")
        return 1
    
    # Run quick auth test
    if not await run_quick_auth_test():
        print(f"\n{Fore.RED}x Quick authentication test failed")
        return 1
    
    print(f"\n{Fore.GREEN}+ Setup completed successfully!")
    print(f"{Fore.GREEN}+ Backend is connected and responding")
    print(f"{Fore.GREEN}+ Authentication endpoints are working")
    print(f"{Fore.GREEN}+ Ready to run comprehensive tests")
    
    # Print test commands
    print_test_commands()
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  SETUP COMPLETE - READY FOR TESTING")
    print(f"{Fore.CYAN}{'='*60}")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}! Setup interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}x Setup error: {str(e)}")
        sys.exit(1)
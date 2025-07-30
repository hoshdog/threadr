#!/usr/bin/env python3
"""
Test script for the minimal scrape debug endpoint.
Use this to identify the exact failure point in URL scraping.
"""

import httpx
import asyncio
import sys
from datetime import datetime

async def test_minimal_scrape(base_url: str, test_url: str):
    """Test the minimal scrape endpoint with a given URL"""
    
    endpoint = f"{base_url}/api/debug/minimal-scrape"
    
    print(f"Testing minimal scrape endpoint...")
    print(f"Endpoint: {endpoint}")
    print(f"Test URL: {test_url}")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(endpoint, params={"url": test_url})
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"[OK] Endpoint responded successfully")
                print(f"Environment: {result.get('environment', 'unknown')}")
                print(f"Timestamp: {result.get('timestamp', 'unknown')}")
                print()
                
                # Analyze each step
                steps = result.get('steps', {})
                for step_name, step_data in steps.items():
                    success = step_data.get('success', False)
                    status = "[PASS]" if success else "[FAIL]"
                    
                    print(f"{status} Step: {step_name}")
                    
                    if success:
                        # Show key details for successful steps
                        if step_name == "url_parsing":
                            print(f"   Hostname: {step_data.get('hostname')}")
                            print(f"   Scheme: {step_data.get('scheme')}")
                        elif step_name == "dns_resolution":
                            print(f"   Resolved IPs: {step_data.get('resolved_ips')}")
                        elif step_name == "http_request":
                            print(f"   Status Code: {step_data.get('status_code')}")
                            print(f"   Content Length: {step_data.get('content_length')} bytes")
                            print(f"   Content Type: {step_data.get('content_type')}")
                        elif step_name == "html_parsing":
                            print(f"   Title: {step_data.get('title')}")
                            print(f"   Paragraphs Found: {step_data.get('paragraph_count')}")
                    else:
                        # Show error details for failed steps
                        print(f"   [ERROR] Error Type: {step_data.get('error_type')}")
                        print(f"   [ERROR] Error: {step_data.get('error')}")
                        if step_data.get('suggestion'):
                            print(f"   [HINT] Suggestion: {step_data.get('suggestion')}")
                    
                    print()
                
                # Summary
                summary = result.get('summary', {})
                successful = summary.get('successful_steps', 0)
                total = summary.get('total_steps', 0)
                overall_success = summary.get('overall_success', False)
                failure_point = summary.get('failure_point')
                
                print("=" * 60)
                print(f"SUMMARY: {successful}/{total} steps successful")
                
                if overall_success:
                    print("[SUCCESS] All steps completed successfully!")
                    print("The scraping pipeline is working correctly.")
                else:
                    print(f"[WARNING] Failed at step: {failure_point}")
                    print("This is where you need to focus your debugging efforts.")
                
            else:
                print(f"[ERROR] HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {response.text}")
                    
    except httpx.ConnectError as e:
        print(f"[ERROR] Connection Error: Cannot connect to {base_url}")
        print(f"Make sure the server is running and accessible.")
        print(f"Error: {e}")
    except httpx.TimeoutException as e:
        print(f"[ERROR] Timeout Error: Request took too long")
        print(f"Error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {type(e).__name__}")
        print(f"Error: {e}")

async def main():
    """Main function to run the test"""
    
    # Default configuration
    base_url = "http://localhost:8001"  # Development server
    test_urls = [
        "https://example.com",  # Simple test
        "https://medium.com/@example/test",  # Medium (if allowed)
        "https://httpbin.org/html",  # Testing service
    ]
    
    # Check command line arguments
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        test_urls = [sys.argv[2]]
    
    print(f"Minimal Scrape Debug Test")
    print(f"Base URL: {base_url}")
    print(f"Test URLs: {test_urls}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    for i, test_url in enumerate(test_urls, 1):
        if len(test_urls) > 1:
            print(f"Test {i}/{len(test_urls)}")
        
        await test_minimal_scrape(base_url, test_url)
        
        if i < len(test_urls):
            print()
            print("-" * 60)
            print()

if __name__ == "__main__":
    print("Usage:")
    print("  python test_minimal_scrape.py [BASE_URL] [TEST_URL]")
    print("  python test_minimal_scrape.py http://localhost:8001")
    print("  python test_minimal_scrape.py https://your-app.railway.app https://example.com")
    print()
    
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test script for the HTTP configuration debug endpoint.
Tests the new /debug/http-config-test endpoint to identify problematic configurations.
"""

import requests
import json
from datetime import datetime

def test_http_config_debug():
    """Test the HTTP configuration debug endpoint"""
    print("=" * 80)
    print("HTTP Configuration Debug Test")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test with local server first
    base_url = "http://localhost:8001"
    endpoint = "/debug/http-config-test"
    test_url = "https://httpbin.org/get"
    
    try:
        print(f"Testing endpoint: {base_url}{endpoint}")
        print(f"Test target URL: {test_url}")
        print("-" * 40)
        
        # Make request to debug endpoint
        response = requests.get(
            f"{base_url}{endpoint}",
            params={"url": test_url},
            timeout=120  # Give it time to run all tests
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("[SUCCESS] DEBUG ENDPOINT ACCESSIBLE")
            print(f"Total tests: {data['summary']['total_tests']}")
            print(f"Successes: {data['summary']['successes']}")
            print(f"Failures: {data['summary']['failures']}")
            print()
            
            # Show analysis
            print("ANALYSIS:")
            print(f"Last successful config: {data['summary']['last_successful_config']}")
            print(f"First failing config: {data['summary']['first_failing_config']}")
            print(f"Suspected culprit: {data['analysis']['suspected_culprit']}")
            print(f"Recommendation: {data['analysis']['recommendation']}")
            print()
            
            # Show detailed results
            print("DETAILED RESULTS:")
            print("=" * 50)
            
            for test_name, result in data['detailed_results'].items():
                status_icon = "[PASS]" if result['status'] == 'SUCCESS' else "[FAIL]"
                print(f"{status_icon} {test_name}:")
                print(f"   Config: {result['config']}")
                
                if result['status'] == 'SUCCESS':
                    print(f"   Status Code: {result['status_code']}")
                    print(f"   Content Length: {result['content_length']}")
                else:
                    print(f"   Error: {result['error_type']}: {result['error']}")
                print()
            
            # Key findings
            print("KEY FINDINGS:")
            if data['summary']['first_failing_config'] == 'test_5_local_address':
                print("[CRITICAL] local_address='0.0.0.0' is causing failures!")
                print("   This confirms the suspected issue with Railway container networking.")
                print("   The complex scrape_article function fails because of this binding.")
                print()
                print("SOLUTION:")
                print("   Remove the local_address parameter from transport configuration.")
                print("   Update line 509 in scrape_article function.")
            elif data['summary']['failures'] == 0:
                print("[SUCCESS] All configurations work locally.")
                print("   The issue may be Railway-specific networking restrictions.")
                print("   Deploy this debug endpoint to Railway to test in production.")
            else:
                print(f"[WARNING] Unexpected failure pattern: {data['summary']['first_failing_config']}")
                print("   Further investigation needed.")
            
        else:
            print(f"[FAIL] DEBUG ENDPOINT FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] CONNECTION ERROR: Local server not running?")
        print("   Start the server with: cd backend && uvicorn main:app --reload --port 8001")
        
    except Exception as e:
        print(f"[ERROR] UNEXPECTED ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_http_config_debug()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("1. If local tests identify local_address as the culprit:")
    print("   - Remove local_address='0.0.0.0' from scrape_article function")
    print("   - Deploy the fix to Railway")
    print("2. If local tests all pass:")
    print("   - Deploy this debug endpoint to Railway")
    print("   - Test against Railway production environment")
    print("3. Compare results between local and Railway environments")
    print("=" * 80)
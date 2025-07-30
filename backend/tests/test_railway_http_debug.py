#!/usr/bin/env python3
"""
Test the HTTP configuration debug endpoint on Railway production environment.
This will identify which specific configuration causes failures in Railway's containerized environment.
"""

import requests
import json
from datetime import datetime
import time

def test_railway_debug():
    """Test the HTTP configuration debug endpoint on Railway"""
    print("=" * 80)
    print("Railway HTTP Configuration Debug Test")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Railway production URL
    railway_url = "https://threadr-production-6ef6.up.railway.app"
    endpoint = "/debug/http-config-test"
    test_url = "https://httpbin.org/get"
    
    try:
        print(f"Testing Railway endpoint: {railway_url}{endpoint}")
        print(f"Test target URL: {test_url}")
        print("-" * 40)
        
        # Wait a moment for Railway deployment
        print("Waiting for Railway deployment to complete...")
        time.sleep(10)
        
        # Make request to debug endpoint
        response = requests.get(
            f"{railway_url}{endpoint}",
            params={"url": test_url},
            timeout=180  # Give Railway more time
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("[SUCCESS] Railway Debug Endpoint Accessible")
            print(f"Total tests: {data['summary']['total_tests']}")
            print(f"Successes: {data['summary']['successes']}")
            print(f"Failures: {data['summary']['failures']}")
            print()
            
            # Show analysis
            print("RAILWAY ANALYSIS:")
            print(f"Last successful config: {data['summary']['last_successful_config']}")
            print(f"First failing config: {data['summary']['first_failing_config']}")
            print(f"Suspected culprit: {data['analysis']['suspected_culprit']}")
            print(f"Recommendation: {data['analysis']['recommendation']}")
            print()
            
            # Show detailed results - focus on failures
            print("RAILWAY DETAILED RESULTS:")
            print("=" * 50)
            
            failing_tests = []
            passing_tests = []
            
            for test_name, result in data['detailed_results'].items():
                if result['status'] == 'FAILED':
                    failing_tests.append((test_name, result))
                else:
                    passing_tests.append((test_name, result))
            
            # Show failing tests first
            if failing_tests:
                print("FAILING CONFIGURATIONS:")
                for test_name, result in failing_tests:
                    print(f"[FAIL] {test_name}:")
                    print(f"   Config: {result['config']}")
                    print(f"   Error: {result['error_type']}: {result['error']}")
                    print()
            
            # Show passing tests
            if passing_tests:
                print("PASSING CONFIGURATIONS:")
                for test_name, result in passing_tests:
                    print(f"[PASS] {test_name}:")
                    print(f"   Config: {result['config']}")
                    print(f"   Status Code: {result['status_code']}")
                    print(f"   Content Length: {result['content_length']}")
                    print()
            
            # Critical findings
            print("CRITICAL RAILWAY FINDINGS:")
            print("=" * 60)
            
            if data['summary']['first_failing_config'] == 'test_5_local_address':
                print("[CRITICAL] CONFIRMED: local_address='0.0.0.0' fails on Railway!")
                print("ROOT CAUSE IDENTIFIED:")
                print("- Railway containers cannot bind to 0.0.0.0 for outbound connections")
                print("- This is why scrape_article function returns 500 errors")
                print("- Simple requests work because they don't use local_address binding")
                print()
                print("IMMEDIATE FIX REQUIRED:")
                print("1. Remove local_address='0.0.0.0' from line 509 in scrape_article")
                print("2. Update transport_kwargs to only include retries")
                print("3. Redeploy to Railway")
                
            elif data['summary']['failures'] == 0:
                print("[UNEXPECTED] All configurations pass on Railway too!")
                print("This suggests the issue might be:")
                print("- Target URL specific (different domains behave differently)")
                print("- SSL-related with specific certificates")
                print("- Intermittent Railway networking issues")
                print("- Race conditions or timing issues")
                
            elif data['summary']['failures'] > 0:
                first_fail = data['summary']['first_failing_config']
                print(f"[IDENTIFIED] Railway fails at: {first_fail}")
                print("This is the exact configuration causing scrape_article failures!")
                
                # Find the specific failure
                for test_name, result in failing_tests:
                    if test_name == first_fail:
                        print(f"Error details: {result['error']}")
                        print(f"Error type: {result['error_type']}")
                        break
            
        else:
            print(f"[FAIL] Railway Debug Endpoint Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 404:
                print("Deployment may not be complete yet. Wait a few minutes and retry.")
            elif response.status_code == 500:
                print("Railway internal error - check Railway logs for details")
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out - Railway may be slow or overloaded")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - Railway deployment may not be ready")
        print("Wait a few minutes for Railway deployment to complete")
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")

def compare_local_vs_railway():
    """Quick comparison of local vs Railway simple requests"""
    print("\n" + "=" * 80)
    print("LOCAL vs RAILWAY COMPARISON")
    print("=" * 80)
    
    # Test simple requests on both environments
    urls = [
        ("Local", "http://localhost:8001/api/debug/scrape-test"),
        ("Railway", "https://threadr-production-6ef6.up.railway.app/api/debug/scrape-test")
    ]
    
    for env_name, url in urls:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                print(f"{env_name}: {'[PASS]' if success else '[FAIL]'}")
                if not success:
                    print(f"  Error: {data.get('error', 'Unknown')}")
            else:
                print(f"{env_name}: [FAIL] HTTP {response.status_code}")
        except Exception as e:
            print(f"{env_name}: [ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_railway_debug()
    compare_local_vs_railway()
    
    print("\n" + "=" * 80)
    print("NEXT ACTIONS BASED ON RESULTS:")
    print("1. If local_address identified as culprit:")
    print("   - Apply fix to scrape_article function immediately")
    print("2. If different config identified:")
    print("   - Apply specific fix for that configuration")
    print("3. If all pass on Railway too:")
    print("   - Test with different target URLs")
    print("   - Check for intermittent issues")
    print("=" * 80)
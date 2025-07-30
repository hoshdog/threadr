#!/usr/bin/env python3
"""
Quick scraping test script using curl commands
Tests all endpoints with various URLs and reports results
"""

import subprocess
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def run_curl(command):
    """Run a curl command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "command": command
        }

def pretty_print_json(json_str):
    """Pretty print JSON string"""
    try:
        data = json.loads(json_str)
        return json.dumps(data, indent=2)
    except:
        return json_str

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n" + "="*60)
    print("TESTING HEALTH ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ("Basic Health", f"curl -X GET {BASE_URL}/health"),
        ("Root Health", f"curl -X GET {BASE_URL}/"),
        ("Readiness", f"curl -X GET {BASE_URL}/readiness"),
        ("API Test", f"curl -X GET {BASE_URL}/api/test"),
        ("Monitor Health", f"curl -X GET {BASE_URL}/api/monitor/health")
    ]
    
    for name, command in endpoints:
        print(f"\n[{name}]")
        print(f"Command: {command}")
        result = run_curl(command)
        
        if result["success"]:
            print("✅ Success")
            print("Response:")
            print(pretty_print_json(result["stdout"]))
        else:
            print("❌ Failed")
            print(f"Error: {result['stderr']}")

def test_debug_endpoints():
    """Test debug endpoints"""
    print("\n" + "="*60)
    print("TESTING DEBUG ENDPOINTS")
    print("="*60)
    
    test_urls = [
        ("Medium", "https://medium.com/@example/test-article"),
        ("Dev.to", "https://dev.to/test/article"),
        ("HTTPBin", "https://httpbin.org/html"),
        ("Example.com", "https://example.com")
    ]
    
    # Test simple scrape
    print("\n--- Simple Scrape Endpoint ---")
    for name, url in test_urls:
        print(f"\n[{name}]")
        command = f'curl -X GET "{BASE_URL}/api/debug/simple-scrape?url={url}"'
        print(f"Command: {command}")
        result = run_curl(command)
        
        if result["success"]:
            print("✅ Request completed")
            try:
                data = json.loads(result["stdout"])
                print(f"Success: {data.get('success', 'N/A')}")
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"Content Length: {data.get('content_length', 'N/A')}")
                if data.get('error'):
                    print(f"Error: {data['error']}")
            except:
                print("Response:", result["stdout"][:200] + "...")
        else:
            print("❌ Failed")
            print(f"Error: {result['stderr']}")
    
    # Test scrape comparison
    print("\n--- Scrape Test Endpoint ---")
    command = f"curl -X GET {BASE_URL}/api/debug/scrape-test"
    print(f"Command: {command}")
    result = run_curl(command)
    
    if result["success"]:
        print("✅ Success")
        try:
            data = json.loads(result["stdout"])
            print("Simple approach:", data.get('simple_approach', {}).get('success'))
            print("Complex approach:", data.get('complex_approach', {}).get('success'))
        except:
            print("Response:", result["stdout"][:200] + "...")
    else:
        print("❌ Failed")

def test_generate_endpoint():
    """Test main generate endpoint"""
    print("\n" + "="*60)
    print("TESTING MAIN GENERATE ENDPOINT")
    print("="*60)
    
    test_cases = [
        {
            "name": "URL - Medium",
            "data": {"url": "https://medium.com/@test/sample-article"}
        },
        {
            "name": "URL - Dev.to",
            "data": {"url": "https://dev.to/test/sample-post"}
        },
        {
            "name": "Direct Text",
            "data": {"text": "This is a test article about web scraping. Web scraping is the process of extracting data from websites. It involves making HTTP requests to web pages and parsing the HTML content. Python libraries like BeautifulSoup make this easier. Always respect robots.txt and rate limits."}
        },
        {
            "name": "URL - HTTPBin",
            "data": {"url": "https://httpbin.org/html"}
        }
    ]
    
    for test in test_cases:
        print(f"\n[{test['name']}]")
        data_json = json.dumps(test['data'])
        command = f'curl -X POST {BASE_URL}/api/generate -H "Content-Type: application/json" -d \'{data_json}\''
        print(f"Command: {command}")
        result = run_curl(command)
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                print(f"✅ Success: {data.get('success', False)}")
                print(f"Source Type: {data.get('source_type', 'N/A')}")
                print(f"Title: {data.get('title', 'N/A')}")
                
                if data.get('thread'):
                    print(f"Tweets Generated: {len(data['thread'])}")
                    print(f"First Tweet: {data['thread'][0]['content'][:100]}...")
                
                if data.get('error'):
                    print(f"Error: {data['error']}")
                    
                if data.get('detail'):
                    print(f"Error Detail: {data['detail']}")
                    
            except Exception as e:
                print(f"Parse error: {e}")
                print("Raw response:", result["stdout"][:300] + "...")
        else:
            print("❌ Request failed")
            print(f"Error: {result['stderr']}")

def test_network_diagnostics():
    """Test network diagnostic endpoints"""
    print("\n" + "="*60)
    print("TESTING NETWORK DIAGNOSTICS")
    print("="*60)
    
    # Test Railway network
    print("\n[Railway Network Test]")
    command = f"curl -X GET {BASE_URL}/api/test/railway-network"
    result = run_curl(command)
    
    if result["success"]:
        try:
            data = json.loads(result["stdout"])
            print("✅ Network test completed")
            
            # Show test results
            if 'tests' in data:
                for test_name, test_result in data['tests'].items():
                    if isinstance(test_result, dict):
                        status = test_result.get('success', test_result.get('status'))
                        print(f"  {test_name}: {'✅' if status else '❌'}")
        except:
            print("Response:", result["stdout"][:200] + "...")
    else:
        print("❌ Failed")
    
    # Test HTTP config
    print("\n[HTTP Configuration Test]")
    command = f'curl -X GET "{BASE_URL}/debug/http-config-test?url=https://httpbin.org/get"'
    result = run_curl(command)
    
    if result["success"]:
        try:
            data = json.loads(result["stdout"])
            print("✅ HTTP config test completed")
            if 'summary' in data:
                print(f"  Successes: {data['summary']['successes']}")
                print(f"  Failures: {data['summary']['failures']}")
                
            if 'analysis' in data:
                print(f"  Suspected issue: {data['analysis'].get('suspected_culprit', 'None')}")
        except:
            print("Response:", result["stdout"][:200] + "...")
    else:
        print("❌ Failed")

def test_ssl_handling():
    """Test SSL/TLS handling"""
    print("\n" + "="*60)
    print("TESTING SSL/TLS HANDLING")
    print("="*60)
    
    ssl_test_urls = [
        ("Standard HTTPS", "https://httpbin.org/get"),
        ("Self-signed cert", "https://self-signed.badssl.com/"),
        ("Expired cert", "https://expired.badssl.com/"),
        ("Wrong hostname", "https://wrong.host.badssl.com/")
    ]
    
    for name, url in ssl_test_urls:
        print(f"\n[{name}]")
        command = f'curl -X GET "{BASE_URL}/api/debug/minimal-scrape?url={url}"'
        print(f"Testing: {url}")
        result = run_curl(command)
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                
                # Check overall status
                overall = data.get('overall_status', 'unknown')
                if overall == 'success':
                    print("✅ SSL test passed")
                else:
                    print(f"⚠️  Status: {overall}")
                    
                # Check SSL-specific step
                if 'steps' in data and '4_http_request' in data['steps']:
                    http_step = data['steps']['4_http_request']
                    if http_step['status'] != 'success':
                        print(f"  Error: {http_step.get('error', 'Unknown')}")
                        print(f"  Suggestion: {http_step.get('suggestion', 'None')}")
                        
            except:
                print("Response:", result["stdout"][:200] + "...")
        else:
            print("❌ Request failed")

def main():
    """Run all tests"""
    print(f"\n🚀 Starting Threadr Scraping Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    # Check if backend is running
    print("\nChecking backend availability...")
    result = run_curl(f"curl -s -o /dev/null -w '%{{http_code}}' {BASE_URL}/health")
    
    if not result["success"] or result["stdout"].strip() != "200":
        print("❌ Backend is not running or not accessible!")
        print(f"Please ensure the backend is running on {BASE_URL}")
        return
    
    print("✅ Backend is running\n")
    
    # Run all test suites
    test_health_endpoints()
    test_debug_endpoints()
    test_generate_endpoint()
    test_network_diagnostics()
    test_ssl_handling()
    
    print("\n" + "="*60)
    print("✨ TESTING COMPLETE")
    print("="*60)
    print("\nCheck the output above for any ❌ failures or ⚠️  warnings")
    print("Successful tests are marked with ✅")

if __name__ == "__main__":
    main()
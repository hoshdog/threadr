"""
Comprehensive test suite for web scraping functionality
Tests the main /api/generate endpoint and debug endpoints with various URLs
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import quote


class ScrapingTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "endpoints": {},
            "summary": {
                "total_tests": 0,
                "successes": 0,
                "failures": 0,
                "warnings": 0
            }
        }
        
    async def test_endpoint(self, 
                          endpoint: str, 
                          method: str = "GET", 
                          data: Optional[Dict] = None,
                          params: Optional[Dict] = None,
                          description: str = "") -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "request": {
                "data": data,
                "params": params
            },
            "response": None,
            "error": None,
            "status": "pending"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        params=params
                    )
                elif method.upper() == "POST":
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        json=data
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                result["response"] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:500]
                }
                
                if response.status_code == 200:
                    result["status"] = "success"
                    self.results["summary"]["successes"] += 1
                else:
                    result["status"] = "failed"
                    self.results["summary"]["failures"] += 1
                    
        except httpx.TimeoutException as e:
            result["error"] = {
                "type": "TimeoutException",
                "message": str(e),
                "details": "Request timed out after 30 seconds"
            }
            result["status"] = "timeout"
            self.results["summary"]["failures"] += 1
            
        except httpx.ConnectError as e:
            result["error"] = {
                "type": "ConnectError",
                "message": str(e),
                "details": "Could not connect to server"
            }
            result["status"] = "connection_error"
            self.results["summary"]["failures"] += 1
            
        except Exception as e:
            result["error"] = {
                "type": type(e).__name__,
                "message": str(e),
                "details": repr(e)
            }
            result["status"] = "error"
            self.results["summary"]["failures"] += 1
        
        self.results["summary"]["total_tests"] += 1
        return result
    
    async def test_health_endpoints(self):
        """Test all health check endpoints"""
        print("\n=== Testing Health Endpoints ===")
        
        health_endpoints = [
            ("/health", "Basic health check"),
            ("/", "Root health check"),
            ("/readiness", "Readiness check"),
            ("/api/test", "API test endpoint"),
            ("/api/monitor/health", "Comprehensive health monitor")
        ]
        
        results = []
        for endpoint, description in health_endpoints:
            print(f"Testing {endpoint}...")
            result = await self.test_endpoint(endpoint, description=description)
            results.append(result)
            print(f"  Status: {result['status']}")
            
        self.results["endpoints"]["health"] = results
        
    async def test_debug_endpoints(self):
        """Test debug endpoints with various URLs"""
        print("\n=== Testing Debug Endpoints ===")
        
        test_urls = [
            "https://medium.com/@example/test-article",
            "https://dev.to/test/article",
            "https://blog.example.com/post",
            "https://httpbin.org/html"
        ]
        
        debug_tests = []
        
        # Test simple scrape
        print("\n--- Testing /api/debug/simple-scrape ---")
        for url in test_urls:
            print(f"Testing URL: {url}")
            result = await self.test_endpoint(
                "/api/debug/simple-scrape",
                params={"url": url},
                description=f"Simple scrape of {url}"
            )
            debug_tests.append(result)
            print(f"  Status: {result['status']}")
            if result['response'] and result['response']['body']:
                body = result['response']['body']
                if isinstance(body, dict):
                    print(f"  Success: {body.get('success', 'N/A')}")
                    print(f"  Title: {body.get('title', 'N/A')}")
                    
        # Test scrape test endpoint
        print("\n--- Testing /api/debug/scrape-test ---")
        result = await self.test_endpoint(
            "/api/debug/scrape-test",
            description="Compare simple vs complex scraping approaches"
        )
        debug_tests.append(result)
        print(f"  Status: {result['status']}")
        
        # Test minimal scrape
        print("\n--- Testing /api/debug/minimal-scrape ---")
        for url in test_urls[:2]:  # Test first 2 URLs
            print(f"Testing URL: {url}")
            result = await self.test_endpoint(
                "/api/debug/minimal-scrape",
                params={"url": url},
                description=f"Minimal scrape debug of {url}"
            )
            debug_tests.append(result)
            print(f"  Status: {result['status']}")
            
        self.results["endpoints"]["debug"] = debug_tests
        
    async def test_generate_endpoint(self):
        """Test the main /api/generate endpoint with various content sources"""
        print("\n=== Testing Main Generate Endpoint ===")
        
        test_cases = [
            {
                "name": "Medium article",
                "data": {"url": "https://medium.com/@test/sample-article"},
                "description": "Generate thread from Medium URL"
            },
            {
                "name": "Dev.to article", 
                "data": {"url": "https://dev.to/test/sample-post"},
                "description": "Generate thread from Dev.to URL"
            },
            {
                "name": "Direct text",
                "data": {"text": "This is a test article about web scraping. Web scraping is the process of extracting data from websites. It involves making HTTP requests to web pages and parsing the HTML content to extract useful information. Python libraries like BeautifulSoup and httpx make this process easier. However, it's important to respect robots.txt files and rate limits when scraping websites."},
                "description": "Generate thread from direct text input"
            },
            {
                "name": "Substack article",
                "data": {"url": "https://example.substack.com/p/test-post"},
                "description": "Generate thread from Substack URL"
            },
            {
                "name": "Generic blog",
                "data": {"url": "https://blog.example.com/2024/01/test-article"},
                "description": "Generate thread from generic blog URL"
            }
        ]
        
        generate_results = []
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            result = await self.test_endpoint(
                "/api/generate",
                method="POST",
                data=test_case["data"],
                description=test_case["description"]
            )
            generate_results.append(result)
            
            print(f"  Status: {result['status']}")
            if result['response'] and result['response']['body']:
                body = result['response']['body']
                if isinstance(body, dict):
                    print(f"  Success: {body.get('success', 'N/A')}")
                    print(f"  Source Type: {body.get('source_type', 'N/A')}")
                    if body.get('thread'):
                        print(f"  Tweets Generated: {len(body['thread'])}")
                    if body.get('error'):
                        print(f"  Error: {body['error']}")
                        
        self.results["endpoints"]["generate"] = generate_results
        
    async def test_network_connectivity(self):
        """Test network connectivity from the backend"""
        print("\n=== Testing Network Connectivity ===")
        
        network_tests = []
        
        # Test railway network endpoint
        result = await self.test_endpoint(
            "/api/test/railway-network",
            description="Comprehensive Railway network diagnostics"
        )
        network_tests.append(result)
        print(f"Railway network test status: {result['status']}")
        
        # Test HTTP config
        test_urls = [
            "https://httpbin.org/get",
            "https://example.com",
            "https://medium.com"
        ]
        
        for url in test_urls:
            result = await self.test_endpoint(
                "/debug/http-config-test",
                params={"url": url},
                description=f"HTTP configuration test with {url}"
            )
            network_tests.append(result)
            print(f"HTTP config test for {url}: {result['status']}")
            
        self.results["endpoints"]["network"] = network_tests
        
    async def test_ssl_tls_handling(self):
        """Test SSL/TLS handling with various configurations"""
        print("\n=== Testing SSL/TLS Handling ===")
        
        ssl_tests = []
        
        # URLs with different SSL configurations
        ssl_test_urls = [
            ("https://httpbin.org/get", "Standard SSL"),
            ("https://self-signed.badssl.com/", "Self-signed certificate"),
            ("https://expired.badssl.com/", "Expired certificate"),
            ("https://wrong.host.badssl.com/", "Wrong hostname"),
        ]
        
        for url, description in ssl_test_urls:
            print(f"\nTesting SSL: {description}")
            result = await self.test_endpoint(
                "/api/debug/simple-scrape",
                params={"url": url},
                description=f"SSL test - {description}"
            )
            ssl_tests.append(result)
            print(f"  Status: {result['status']}")
            
        self.results["endpoints"]["ssl"] = ssl_tests
        
    async def analyze_results(self):
        """Analyze test results and identify patterns"""
        print("\n=== Analysis ===")
        
        analysis = {
            "patterns": [],
            "recommendations": [],
            "critical_issues": []
        }
        
        # Check for timeout patterns
        timeout_count = sum(1 for endpoint_group in self.results["endpoints"].values() 
                          for test in endpoint_group 
                          if test.get("status") == "timeout")
        
        if timeout_count > 2:
            analysis["patterns"].append("Multiple timeout errors detected")
            analysis["recommendations"].append("Consider increasing timeout values or checking network latency")
            
        # Check for SSL errors
        ssl_errors = []
        for endpoint_group in self.results["endpoints"].values():
            for test in endpoint_group:
                if test.get("error") and "ssl" in str(test["error"]).lower():
                    ssl_errors.append(test)
                    
        if ssl_errors:
            analysis["patterns"].append(f"SSL/TLS errors detected in {len(ssl_errors)} tests")
            analysis["recommendations"].append("Consider disabling SSL verification for development or fixing certificate issues")
            
        # Check for connection errors
        connection_errors = sum(1 for endpoint_group in self.results["endpoints"].values()
                               for test in endpoint_group
                               if test.get("status") == "connection_error")
        
        if connection_errors > 0:
            analysis["critical_issues"].append(f"{connection_errors} connection errors - backend may not be running")
            
        # Check generate endpoint specifically
        generate_tests = self.results["endpoints"].get("generate", [])
        generate_failures = [t for t in generate_tests if t.get("status") != "success"]
        
        if generate_failures:
            analysis["critical_issues"].append(f"Main /api/generate endpoint has {len(generate_failures)} failures")
            
        self.results["analysis"] = analysis
        
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*50)
        print("TESTING SUMMARY")
        print("="*50)
        
        summary = self.results["summary"]
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"Successes: {summary['successes']} ({summary['successes']/summary['total_tests']*100:.1f}%)")
        print(f"Failures: {summary['failures']} ({summary['failures']/summary['total_tests']*100:.1f}%)")
        
        if self.results.get("analysis"):
            analysis = self.results["analysis"]
            
            if analysis["critical_issues"]:
                print("\n⚠️  CRITICAL ISSUES:")
                for issue in analysis["critical_issues"]:
                    print(f"  - {issue}")
                    
            if analysis["patterns"]:
                print("\n📊 PATTERNS DETECTED:")
                for pattern in analysis["patterns"]:
                    print(f"  - {pattern}")
                    
            if analysis["recommendations"]:
                print("\n💡 RECOMMENDATIONS:")
                for rec in analysis["recommendations"]:
                    print(f"  - {rec}")
                    
    async def run_all_tests(self):
        """Run all test suites"""
        print(f"Starting comprehensive scraping tests at {datetime.now().isoformat()}")
        print(f"Target: {self.base_url}")
        
        # Check if backend is running
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                print("✅ Backend is running")
        except:
            print("❌ Backend is not running or not accessible")
            print(f"Please ensure the backend is running on {self.base_url}")
            return
        
        # Run test suites
        await self.test_health_endpoints()
        await self.test_debug_endpoints()
        await self.test_generate_endpoint()
        await self.test_network_connectivity()
        await self.test_ssl_tls_handling()
        
        # Analyze results
        await self.analyze_results()
        
        # Print summary
        self.print_summary()
        
        # Save detailed results
        with open("scraping_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to scraping_test_results.json")


async def main():
    """Main test runner"""
    tester = ScrapingTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
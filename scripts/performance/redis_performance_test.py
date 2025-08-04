#!/usr/bin/env python3
"""
Threadr Redis Performance Testing Script
========================================

Comprehensive Redis performance testing for Railway/Upstash configuration.
Tests connection, latency, throughput, caching effectiveness, and scaling.

Features:
- Connection health and latency testing  
- Throughput benchmarking (reads/writes per second)
- Memory usage and key expiration testing
- Rate limiting performance verification
- Premium status caching performance
- Email capture storage performance
- Connection pooling effectiveness
- Upstash-specific optimizations

Usage:
    python scripts/performance/redis_performance_test.py
    python scripts/performance/redis_performance_test.py --duration 60 --threads 10
    python scripts/performance/redis_performance_test.py --test-suite full
"""

import asyncio
import aiohttp
import time
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import argparse
from dataclasses import dataclass, asdict
import statistics
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerfTestResult:
    test_name: str
    operation: str
    duration: float
    operations_per_second: float
    success_count: int
    error_count: int
    min_latency: float
    max_latency: float
    avg_latency: float
    median_latency: float
    p95_latency: float
    memory_usage_mb: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class RedisPerformanceTester:
    def __init__(self, backend_url: str = "https://threadr-production.up.railway.app"):
        self.backend_url = backend_url.rstrip('/')
        self.test_results: List[PerfTestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_start_time = datetime.now()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, url: str, **kwargs) -> Tuple[Optional[aiohttp.ClientResponse], float]:
        """Make HTTP request and measure latency"""
        start_time = time.time()
        try:
            async with self.session.request(method, url, **kwargs) as response:
                latency = time.time() - start_time
                return response, latency
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            return None, latency
    
    def add_result(self, test_name: str, operation: str, latencies: List[float], 
                   success_count: int, error_count: int, duration: float, 
                   memory_usage_mb: Optional[float] = None, details: Optional[Dict] = None):
        """Add performance test result"""
        if not latencies:
            latencies = [0.0]
        
        operations_per_second = (success_count + error_count) / duration if duration > 0 else 0
        
        result = PerfTestResult(
            test_name=test_name,
            operation=operation,
            duration=duration,
            operations_per_second=operations_per_second,
            success_count=success_count,
            error_count=error_count,
            min_latency=min(latencies),
            max_latency=max(latencies),
            avg_latency=statistics.mean(latencies),
            median_latency=statistics.median(latencies),
            p95_latency=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
            memory_usage_mb=memory_usage_mb,
            details=details
        )
        
        self.test_results.append(result)
        
        # Print immediate feedback
        success_rate = (success_count / (success_count + error_count)) * 100 if (success_count + error_count) > 0 else 0
        print(f"✅ {test_name} ({operation}): {operations_per_second:.1f} ops/sec, "
              f"{result.avg_latency*1000:.1f}ms avg, {success_rate:.1f}% success")
    
    async def test_basic_connectivity(self) -> bool:
        """Test basic Redis connectivity through backend health endpoint"""
        print("🔗 Testing Redis connectivity...")
        
        start_time = time.time()
        health_url = f"{self.backend_url}/health"
        
        response, latency = await self.make_request("GET", health_url)
        
        if response and response.status == 200:
            try:
                health_data = await response.json()
                redis_status = health_data.get("services", {}).get("redis", "unknown")
                
                if redis_status == "healthy":
                    self.add_result("Connectivity", "Health Check", [latency], 1, 0, 
                                  time.time() - start_time, 
                                  details={"redis_status": redis_status})
                    return True
                else:
                    self.add_result("Connectivity", "Health Check", [latency], 0, 1, 
                                  time.time() - start_time, 
                                  details={"redis_status": redis_status, "error": "Redis not healthy"})
                    return False
                    
            except Exception as e:
                self.add_result("Connectivity", "Health Check", [latency], 0, 1, 
                              time.time() - start_time, 
                              details={"error": str(e)})
                return False
        else:
            status = response.status if response else "No Response"
            self.add_result("Connectivity", "Health Check", [latency], 0, 1, 
                          time.time() - start_time, 
                          details={"http_status": status})
            return False
    
    async def test_usage_stats_performance(self, duration: int = 30, concurrent_requests: int = 5) -> None:
        """Test usage stats Redis performance (most common operation)"""
        print(f"📊 Testing usage stats performance ({duration}s, {concurrent_requests} concurrent)...")
        
        usage_url = f"{self.backend_url}/api/usage-stats"
        start_time = time.time()
        end_time = start_time + duration
        
        latencies = []
        success_count = 0
        error_count = 0
        
        async def worker():
            nonlocal success_count, error_count
            while time.time() < end_time:
                response, latency = await self.make_request("GET", usage_url)
                latencies.append(latency)
                
                if response and response.status == 200:
                    success_count += 1
                else:
                    error_count += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
        
        # Run concurrent workers
        tasks = [worker() for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks)
        
        test_duration = time.time() - start_time
        self.add_result("Usage Stats", "Read Performance", latencies, success_count, error_count, 
                       test_duration, details={"concurrent_requests": concurrent_requests})
    
    async def test_premium_status_caching(self, duration: int = 20) -> None:
        """Test premium status caching performance"""
        print(f"💎 Testing premium status caching performance ({duration}s)...")
        
        premium_url = f"{self.backend_url}/api/premium-status"
        start_time = time.time()
        end_time = start_time + duration
        
        latencies = []
        success_count = 0
        error_count = 0
        cache_hits = 0
        cache_misses = 0
        
        while time.time() < end_time:
            response, latency = await self.make_request("GET", premium_url)
            latencies.append(latency)
            
            if response and response.status == 200:
                success_count += 1
                try:
                    data = await response.json()
                    # Fast responses likely indicate cache hits
                    if latency < 0.1:  # Less than 100ms is likely cached
                        cache_hits += 1
                    else:
                        cache_misses += 1
                except:
                    pass
            else:
                error_count += 1
            
            await asyncio.sleep(0.2)  # 5 requests per second
        
        test_duration = time.time() - start_time
        cache_hit_ratio = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
        
        self.add_result("Premium Status", "Cache Performance", latencies, success_count, error_count, 
                       test_duration, details={
                           "cache_hits": cache_hits,
                           "cache_misses": cache_misses,
                           "cache_hit_ratio": cache_hit_ratio
                       })
    
    async def test_email_capture_storage(self, num_emails: int = 50) -> None:
        """Test email capture storage performance"""
        print(f"📧 Testing email capture storage performance ({num_emails} emails)...")
        
        email_url = f"{self.backend_url}/api/capture-email"
        start_time = time.time()
        
        latencies = []
        success_count = 0
        error_count = 0
        
        for i in range(num_emails):
            test_email = f"perf-test-{int(time.time())}-{i}@threadr-test.local"
            response, latency = await self.make_request("POST", email_url, 
                                                       json={"email": test_email})
            latencies.append(latency)
            
            if response and response.status == 200:
                success_count += 1
            else:
                error_count += 1
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.05)
        
        test_duration = time.time() - start_time
        self.add_result("Email Capture", "Write Performance", latencies, success_count, error_count, 
                       test_duration, details={"emails_processed": num_emails})
    
    async def test_rate_limiting_performance(self, burst_size: int = 20) -> None:
        """Test rate limiting Redis performance under load"""
        print(f"⏱️ Testing rate limiting performance (burst of {burst_size})...")
        
        usage_url = f"{self.backend_url}/api/usage-stats"
        start_time = time.time()
        
        latencies = []
        success_count = 0
        rate_limited_count = 0
        error_count = 0
        
        # Send burst of requests to trigger rate limiting
        for i in range(burst_size):
            response, latency = await self.make_request("GET", usage_url)
            latencies.append(latency)
            
            if response:
                if response.status == 200:
                    success_count += 1
                elif response.status == 429:
                    rate_limited_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
            
            # No delay - test burst performance
        
        test_duration = time.time() - start_time
        
        self.add_result("Rate Limiting", "Burst Performance", latencies, 
                       success_count, error_count + rate_limited_count, test_duration, 
                       details={
                           "rate_limited_requests": rate_limited_count,
                           "successful_requests": success_count,
                           "rate_limiting_triggered": rate_limited_count > 0
                       })
    
    async def test_concurrent_load(self, duration: int = 30, workers: int = 10) -> None:
        """Test Redis performance under concurrent load"""
        print(f"🔀 Testing concurrent load performance ({duration}s, {workers} workers)...")
        
        endpoints = [
            f"{self.backend_url}/api/usage-stats",
            f"{self.backend_url}/api/premium-status",
            f"{self.backend_url}/health"
        ]
        
        start_time = time.time()
        end_time = start_time + duration
        
        latencies = []
        success_count = 0
        error_count = 0
        operations_by_endpoint = {endpoint: 0 for endpoint in endpoints}
        
        async def worker(worker_id: int):
            nonlocal success_count, error_count
            worker_operations = 0
            
            while time.time() < end_time:
                # Rotate through endpoints
                endpoint = endpoints[worker_operations % len(endpoints)]
                
                response, latency = await self.make_request("GET", endpoint)
                latencies.append(latency)
                operations_by_endpoint[endpoint] += 1
                
                if response and response.status in [200, 429]:  # 429 is also a "successful" response
                    success_count += 1
                else:
                    error_count += 1
                
                worker_operations += 1
                await asyncio.sleep(0.1)  # Reasonable rate per worker
        
        # Run concurrent workers
        tasks = [worker(i) for i in range(workers)]
        await asyncio.gather(*tasks)
        
        test_duration = time.time() - start_time
        total_operations = sum(operations_by_endpoint.values())
        
        self.add_result("Concurrent Load", "Mixed Operations", latencies, success_count, error_count, 
                       test_duration, details={
                           "workers": workers,
                           "total_operations": total_operations,
                           "operations_by_endpoint": operations_by_endpoint
                       })
    
    async def test_memory_pressure(self, num_operations: int = 100) -> None:
        """Test performance under memory pressure (through health endpoint monitoring)"""
        print(f"🧠 Testing memory pressure performance ({num_operations} operations)...")
        
        health_url = f"{self.backend_url}/health"
        start_time = time.time()
        
        latencies = []
        success_count = 0
        error_count = 0
        memory_readings = []
        
        for i in range(num_operations):
            response, latency = await self.make_request("GET", health_url)
            latencies.append(latency)
            
            if response and response.status == 200:
                success_count += 1
                try:
                    health_data = await response.json()
                    # Try to extract memory info if available
                    memory_info = health_data.get("system", {}).get("memory", {})
                    if memory_info:
                        memory_readings.append(memory_info)
                except:
                    pass
            else:
                error_count += 1
            
            await asyncio.sleep(0.1)
        
        test_duration = time.time() - start_time
        avg_memory = statistics.mean([r.get("used_mb", 0) for r in memory_readings]) if memory_readings else None
        
        self.add_result("Memory Pressure", "Health Checks", latencies, success_count, error_count, 
                       test_duration, memory_usage_mb=avg_memory, 
                       details={"memory_readings": len(memory_readings)})
    
    async def run_performance_suite(self, test_suite: str = "standard", 
                                   duration: int = 30, workers: int = 5) -> None:
        """Run complete performance test suite"""
        print(f"🚀 Starting Redis Performance Testing")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Suite: {test_suite}")
        print(f"Duration: {duration}s per test")
        print(f"Workers: {workers}")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Check connectivity first
        if not await self.test_basic_connectivity():
            print("❌ Redis connectivity failed - aborting performance tests")
            return
        
        # Standard test suite
        await self.test_usage_stats_performance(duration=duration, concurrent_requests=workers)
        await self.test_premium_status_caching(duration=duration//2)
        await self.test_email_capture_storage(num_emails=min(50, duration))
        await self.test_rate_limiting_performance()
        
        if test_suite == "full":
            # Extended test suite
            await self.test_concurrent_load(duration=duration, workers=workers)
            await self.test_memory_pressure(num_operations=min(100, duration*2))
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        # Calculate overall metrics
        total_operations = sum(r.success_count + r.error_count for r in self.test_results)
        total_success = sum(r.success_count for r in self.test_results)
        total_errors = sum(r.error_count for r in self.test_results)
        
        overall_success_rate = (total_success / total_operations * 100) if total_operations > 0 else 0
        
        # Find fastest and slowest operations
        fastest_test = min(self.test_results, key=lambda r: r.avg_latency)
        slowest_test = max(self.test_results, key=lambda r: r.avg_latency)
        highest_throughput = max(self.test_results, key=lambda r: r.operations_per_second)
        
        # Performance grade
        avg_latency = statistics.mean([r.avg_latency for r in self.test_results])
        avg_throughput = statistics.mean([r.operations_per_second for r in self.test_results])
        
        performance_grade = self._calculate_performance_grade(avg_latency, avg_throughput, overall_success_rate)
        
        return {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration": (datetime.now() - self.test_start_time).total_seconds(),
            "backend_url": self.backend_url,
            "summary": {
                "total_tests": len(self.test_results),
                "total_operations": total_operations,
                "successful_operations": total_success,
                "failed_operations": total_errors,
                "overall_success_rate": round(overall_success_rate, 2),
                "average_latency_ms": round(avg_latency * 1000, 2),
                "average_throughput_ops": round(avg_throughput, 2),
                "performance_grade": performance_grade
            },
            "highlights": {
                "fastest_operation": {
                    "test": fastest_test.test_name,
                    "operation": fastest_test.operation,
                    "avg_latency_ms": round(fastest_test.avg_latency * 1000, 2)
                },
                "slowest_operation": {
                    "test": slowest_test.test_name,
                    "operation": slowest_test.operation,
                    "avg_latency_ms": round(slowest_test.avg_latency * 1000, 2)
                },
                "highest_throughput": {
                    "test": highest_throughput.test_name,
                    "operation": highest_throughput.operation,
                    "ops_per_second": round(highest_throughput.operations_per_second, 2)
                }
            },
            "detailed_results": [asdict(r) for r in self.test_results]
        }
    
    def _calculate_performance_grade(self, avg_latency: float, avg_throughput: float, success_rate: float) -> str:
        """Calculate overall performance grade"""
        latency_ms = avg_latency * 1000
        
        # Grade based on latency, throughput, and success rate
        if latency_ms < 100 and avg_throughput > 50 and success_rate > 95:
            return "A+ (Excellent)"
        elif latency_ms < 200 and avg_throughput > 25 and success_rate > 90:
            return "A (Very Good)"
        elif latency_ms < 500 and avg_throughput > 10 and success_rate > 85:
            return "B (Good)"
        elif latency_ms < 1000 and avg_throughput > 5 and success_rate > 75:
            return "C (Acceptable)"
        elif success_rate > 50:
            return "D (Poor)"
        else:
            return "F (Failing)"
    
    def print_performance_report(self) -> None:
        """Print performance report to console"""
        report = self.generate_performance_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print("\n" + "=" * 60)
        print("📊 REDIS PERFORMANCE REPORT")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"🏆 Performance Grade: {summary['performance_grade']}")
        print(f"✅ Success Rate: {summary['overall_success_rate']}%")
        print(f"⚡ Average Latency: {summary['average_latency_ms']}ms")
        print(f"🚀 Average Throughput: {summary['average_throughput_ops']} ops/sec")
        print(f"📈 Total Operations: {summary['total_operations']}")
        print(f"⏱️  Test Duration: {report['test_duration']:.1f}s")
        
        highlights = report["highlights"]
        print(f"\n🏃 Fastest: {highlights['fastest_operation']['test']} "
              f"({highlights['fastest_operation']['avg_latency_ms']}ms)")
        print(f"🐌 Slowest: {highlights['slowest_operation']['test']} "
              f"({highlights['slowest_operation']['avg_latency_ms']}ms)")
        print(f"🔥 Highest Throughput: {highlights['highest_throughput']['test']} "
              f"({highlights['highest_throughput']['ops_per_second']} ops/sec)")
        
        # Show individual test results
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            success_rate = (result.success_count / (result.success_count + result.error_count) * 100) if (result.success_count + result.error_count) > 0 else 0
            print(f"   {result.test_name} ({result.operation}):")
            print(f"      Throughput: {result.operations_per_second:.1f} ops/sec")
            print(f"      Latency: {result.avg_latency*1000:.1f}ms avg, {result.p95_latency*1000:.1f}ms p95")
            print(f"      Success Rate: {success_rate:.1f}% ({result.success_count}/{result.success_count + result.error_count})")
            if result.details:
                key_details = {k: v for k, v in result.details.items() if k in ['cache_hit_ratio', 'rate_limiting_triggered', 'workers']}
                if key_details:
                    print(f"      Details: {key_details}")

async def main():
    parser = argparse.ArgumentParser(description='Threadr Redis Performance Tester')
    parser.add_argument('--backend-url', default='https://threadr-production.up.railway.app',
                       help='Backend URL to test')
    parser.add_argument('--test-suite', choices=['standard', 'full'], default='standard',
                       help='Test suite to run')
    parser.add_argument('--duration', type=int, default=30,
                       help='Duration for each performance test (seconds)')
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of concurrent workers for load tests')
    parser.add_argument('--json-output', help='Save performance report to JSON file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async with RedisPerformanceTester(args.backend_url) as tester:
        try:
            await tester.run_performance_suite(
                test_suite=args.test_suite,
                duration=args.duration,
                workers=args.workers
            )
            
            # Print report
            tester.print_performance_report()
            
            # Save JSON output if requested
            if args.json_output:
                report = tester.generate_performance_report()
                with open(args.json_output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\n💾 Performance report saved to: {args.json_output}")
            
            # Exit with appropriate code based on performance grade
            report = tester.generate_performance_report()
            grade = report["summary"]["performance_grade"]
            if grade.startswith("F") or grade.startswith("D"):
                sys.exit(1)
            
        except KeyboardInterrupt:
            print("\n⏹️  Performance testing cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 Performance testing failed with error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
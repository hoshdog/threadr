#!/usr/bin/env python3
"""
Threadr API Security Monitoring Script
======================================

Monitors API key security implementation and environment variable configuration.
Detects security issues, misconfigurations, and provides recommendations.

Features:
- API key environment variable validation
- Frontend security configuration check
- Backend API authentication verification
- Security headers analysis
- Rate limiting effectiveness monitoring
- Security vulnerability detection

Usage:
    python scripts/monitoring/api_security_monitor.py
    python scripts/monitoring/api_security_monitor.py --continuous --interval 300
    python scripts/monitoring/api_security_monitor.py --alerts-webhook https://hooks.slack.com/...
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
from urllib.parse import urljoin, urlparse
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
    category: str  # "API_KEY", "HEADERS", "RATE_LIMITING", "CONFIGURATION"
    title: str
    description: str
    recommendation: str
    detected_at: str
    endpoint: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class APISecurityMonitor:
    def __init__(self, frontend_url: str = "https://threadr-plum.vercel.app", 
                 backend_url: str = "https://threadr-production.up.railway.app"):
        self.frontend_url = frontend_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/')
        self.issues: List[SecurityIssue] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitoring_start = datetime.now()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_issue(self, severity: str, category: str, title: str, description: str, 
                  recommendation: str, endpoint: Optional[str] = None, 
                  details: Optional[Dict] = None):
        """Add a security issue to the monitoring results"""
        issue = SecurityIssue(
            severity=severity,
            category=category,
            title=title,
            description=description,
            recommendation=recommendation,
            detected_at=datetime.now().isoformat(),
            endpoint=endpoint,
            details=details
        )
        self.issues.append(issue)
        
        # Log immediately
        severity_symbol = {
            "CRITICAL": "🚨",
            "HIGH": "🔴", 
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "INFO": "ℹ️"
        }.get(severity, "❓")
        
        print(f"{severity_symbol} [{severity}] {category}: {title}")
        if logger.level <= logging.DEBUG:
            print(f"   Description: {description}")
            print(f"   Recommendation: {recommendation}")
    
    async def make_request(self, method: str, url: str, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Make HTTP request with error handling and security analysis"""
        try:
            async with self.session.request(method, url, **kwargs) as response:
                return response
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            return None
    
    async def check_api_key_environment_vars(self) -> None:
        """Check if API keys are properly configured in environment variables"""
        print("🔍 Checking API key environment variable configuration...")
        
        # Check frontend config.js for API key exposure
        try:
            config_url = f"{self.frontend_url}/config.js"
            response = await self.make_request("GET", config_url)
            
            if response and response.status == 200:
                config_content = await response.text()
                
                # Check for hardcoded API keys
                hardcoded_key_pattern = r"['\"]([A-Za-z0-9_-]{30,})['\"]"
                potential_keys = re.findall(hardcoded_key_pattern, config_content)
                
                for key in potential_keys:
                    if len(key) > 20 and not key.startswith('http'):
                        self.add_issue(
                            "HIGH", "API_KEY", "Potential Hardcoded API Key",
                            f"Found potential API key in frontend config: {key[:10]}...",
                            "Move API key to Vercel environment variables and use window.THREADR_API_KEY",
                            config_url
                        )
                
                # Check for fallback key usage warning
                if "Using fallback API key" in config_content:
                    self.add_issue(
                        "MEDIUM", "API_KEY", "Fallback API Key Warning",
                        "Frontend is configured to warn about fallback API key usage",
                        "Ensure THREADR_API_KEY environment variable is set in Vercel",
                        config_url
                    )
                
                # Check for proper environment variable detection
                if "window.THREADR_API_KEY" in config_content:
                    self.add_issue(
                        "INFO", "CONFIGURATION", "Environment Variable Check Implemented",
                        "Frontend properly checks for environment variable API key",
                        "Verify that Vercel environment variable is actually set",
                        config_url
                    )
            
        except Exception as e:
            self.add_issue(
                "MEDIUM", "CONFIGURATION", "Config Check Failed",
                f"Could not analyze frontend configuration: {str(e)}",
                "Manually verify frontend config.js is accessible and properly configured"
            )
    
    async def test_api_authentication(self) -> None:
        """Test API authentication mechanisms"""
        print("🔐 Testing API authentication mechanisms...")
        
        test_endpoints = [
            ("/api/generate", "POST", {"content": "test", "input_type": "content"}),
            ("/api/usage-stats", "GET", None),
            ("/api/premium-status", "GET", None)
        ]
        
        for endpoint, method, data in test_endpoints:
            url = f"{self.backend_url}{endpoint}"
            
            # Test without API key
            try:
                if method == "GET":
                    response = await self.make_request("GET", url)
                else:
                    response = await self.make_request("POST", url, json=data)
                
                if response:
                    if response.status == 401:
                        self.add_issue(
                            "INFO", "API_KEY", f"Authentication Required for {endpoint}",
                            f"Endpoint properly requires authentication (401 response)",
                            "This is correct behavior - no action needed",
                            url
                        )
                    elif response.status == 403:
                        self.add_issue(
                            "INFO", "API_KEY", f"Access Forbidden for {endpoint}",
                            f"Endpoint properly rejects unauthorized requests (403 response)",
                            "This is correct behavior - no action needed",
                            url
                        )
                    elif response.status == 200:
                        self.add_issue(
                            "HIGH", "API_KEY", f"No Authentication Required for {endpoint}",
                            f"Endpoint allows access without authentication",
                            "Implement API key authentication for this endpoint",
                            url
                        )
                    elif response.status == 429:
                        self.add_issue(
                            "INFO", "RATE_LIMITING", f"Rate Limiting Active for {endpoint}",
                            f"Rate limiting is working (429 response)",
                            "Rate limiting is protecting the endpoint",
                            url
                        )
                    else:
                        self.add_issue(
                            "MEDIUM", "API_KEY", f"Unexpected Response for {endpoint}",
                            f"Endpoint returned unexpected status {response.status}",
                            "Review endpoint authentication configuration",
                            url
                        )
                
            except Exception as e:
                self.add_issue(
                    "LOW", "CONFIGURATION", f"Test Failed for {endpoint}",
                    f"Could not test endpoint: {str(e)}",
                    "Verify endpoint is accessible and properly configured"
                )
    
    async def check_security_headers(self) -> None:
        """Check for security headers in API responses"""
        print("🛡️ Analyzing security headers...")
        
        # Test main endpoints for security headers
        test_urls = [
            f"{self.backend_url}/health",
            f"{self.frontend_url}/",
            f"{self.frontend_url}/config.js"
        ]
        
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,  # Should exist
            "Content-Security-Policy": None,  # Should exist
        }
        
        for url in test_urls:
            try:
                response = await self.make_request("GET", url)
                
                if response:
                    headers = dict(response.headers)
                    
                    for header_name, expected_value in required_headers.items():
                        if header_name not in headers:
                            severity = "MEDIUM" if header_name.startswith("X-") else "LOW"
                            self.add_issue(
                                severity, "HEADERS", f"Missing Security Header: {header_name}",
                                f"Response from {url} missing {header_name} header",
                                f"Add {header_name} header to improve security",
                                url
                            )
                        elif expected_value and isinstance(expected_value, list):
                            if headers[header_name] not in expected_value:
                                self.add_issue(
                                    "LOW", "HEADERS", f"Suboptimal {header_name} Header",
                                    f"Header value '{headers[header_name]}' could be improved",
                                    f"Consider using one of: {', '.join(expected_value)}",
                                    url
                                )
                        elif expected_value and headers[header_name] != expected_value:
                            self.add_issue(
                                "LOW", "HEADERS", f"Incorrect {header_name} Header",
                                f"Expected '{expected_value}', got '{headers[header_name]}'",
                                f"Update header to '{expected_value}'",
                                url
                            )
                
            except Exception as e:
                self.add_issue(
                    "LOW", "HEADERS", f"Header Check Failed for {url}",
                    f"Could not analyze headers: {str(e)}",
                    "Manually verify security headers are properly configured"
                )
    
    async def test_rate_limiting_effectiveness(self) -> None:
        """Test rate limiting configuration and effectiveness"""
        print("⏱️ Testing rate limiting effectiveness...")
        
        # Test rate limiting on usage-stats endpoint (should be less aggressive)
        usage_url = f"{self.backend_url}/api/usage-stats"
        
        # Make multiple quick requests to test rate limiting
        request_count = 10
        successful_requests = 0
        rate_limited_requests = 0
        
        start_time = time.time()
        
        for i in range(request_count):
            try:
                response = await self.make_request("GET", usage_url)
                
                if response:
                    if response.status == 200:
                        successful_requests += 1
                    elif response.status == 429:
                        rate_limited_requests += 1
                
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.debug(f"Request {i} failed: {str(e)}")
        
        duration = time.time() - start_time
        
        if rate_limited_requests > 0:
            self.add_issue(
                "INFO", "RATE_LIMITING", "Rate Limiting Active",
                f"Rate limiting triggered after {successful_requests} requests in {duration:.2f}s",
                "Rate limiting is working correctly",
                usage_url,
                {
                    "successful_requests": successful_requests,
                    "rate_limited_requests": rate_limited_requests,
                    "duration": duration
                }
            )
        else:
            severity = "HIGH" if successful_requests == request_count else "MEDIUM"
            self.add_issue(
                severity, "RATE_LIMITING", "No Rate Limiting Detected",
                f"All {request_count} requests succeeded without rate limiting",
                "Verify rate limiting configuration - may be too permissive",
                usage_url,
                {
                    "successful_requests": successful_requests,
                    "rate_limited_requests": rate_limited_requests,
                    "duration": duration
                }
            )
    
    async def check_redis_security(self) -> None:
        """Check Redis configuration security through health endpoint"""
        print("🔴 Checking Redis security configuration...")
        
        try:
            health_url = f"{self.backend_url}/health"
            response = await self.make_request("GET", health_url)
            
            if response and response.status == 200:
                health_data = await response.json()
                redis_info = health_data.get("services", {}).get("redis", {})
                
                if isinstance(redis_info, dict):
                    # Check if Redis connection info is exposed
                    sensitive_keys = ["host", "password", "url", "connection_string"]
                    exposed_info = []
                    
                    for key in sensitive_keys:
                        if key in redis_info:
                            exposed_info.append(key)
                    
                    if exposed_info:
                        self.add_issue(
                            "HIGH", "CONFIGURATION", "Redis Connection Info Exposed",
                            f"Health endpoint exposes Redis connection details: {', '.join(exposed_info)}",
                            "Remove sensitive Redis information from health endpoint response",
                            health_url,
                            {"exposed_keys": exposed_info}
                        )
                    else:
                        self.add_issue(
                            "INFO", "CONFIGURATION", "Redis Connection Info Secure",
                            "Health endpoint does not expose sensitive Redis information",
                            "Continue monitoring for any configuration changes",
                            health_url
                        )
                
        except Exception as e:
            self.add_issue(
                "LOW", "CONFIGURATION", "Redis Security Check Failed",
                f"Could not analyze Redis security configuration: {str(e)}",
                "Manually verify Redis connection information is not exposed"
            )
    
    async def run_security_scan(self) -> None:
        """Run complete security scan"""
        print(f"🔒 Starting Threadr API Security Monitoring")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Scan started: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run all security checks
        await self.check_api_key_environment_vars()
        await self.test_api_authentication()
        await self.check_security_headers()
        await self.test_rate_limiting_effectiveness()
        await self.check_redis_security()
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        issues_by_severity = {}
        issues_by_category = {}
        
        for issue in self.issues:
            # Group by severity
            if issue.severity not in issues_by_severity:
                issues_by_severity[issue.severity] = []
            issues_by_severity[issue.severity].append(issue)
            
            # Group by category
            if issue.category not in issues_by_category:
                issues_by_category[issue.category] = []
            issues_by_category[issue.category].append(issue)
        
        # Calculate risk score
        severity_weights = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 2, "INFO": 0}
        risk_score = sum(severity_weights.get(issue.severity, 0) for issue in self.issues)
        max_possible_score = len(self.issues) * 10
        risk_percentage = (risk_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "scan_duration": (datetime.now() - self.monitoring_start).total_seconds(),
            "frontend_url": self.frontend_url,
            "backend_url": self.backend_url,
            "summary": {
                "total_issues": len(self.issues),
                "issues_by_severity": {k: len(v) for k, v in issues_by_severity.items()},
                "issues_by_category": {k: len(v) for k, v in issues_by_category.items()},
                "risk_score": risk_score,
                "risk_percentage": round(risk_percentage, 1),
                "security_status": self._get_security_status(risk_percentage)
            },
            "issues": [asdict(issue) for issue in self.issues]
        }
    
    def _get_security_status(self, risk_percentage: float) -> str:
        """Determine overall security status based on risk percentage"""
        if risk_percentage <= 10:
            return "EXCELLENT"
        elif risk_percentage <= 25:
            return "GOOD"
        elif risk_percentage <= 50:
            return "MODERATE"
        elif risk_percentage <= 75:
            return "CONCERNING"
        else:
            return "CRITICAL"
    
    def print_security_report(self) -> None:
        """Print security report to console"""
        report = self.generate_security_report()
        
        print("\n" + "=" * 60)
        print("🔒 SECURITY MONITORING REPORT")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"🚨 Critical Issues: {summary['issues_by_severity'].get('CRITICAL', 0)}")
        print(f"🔴 High Issues: {summary['issues_by_severity'].get('HIGH', 0)}")
        print(f"🟡 Medium Issues: {summary['issues_by_severity'].get('MEDIUM', 0)}")
        print(f"🟢 Low Issues: {summary['issues_by_severity'].get('LOW', 0)}")
        print(f"ℹ️  Info Items: {summary['issues_by_severity'].get('INFO', 0)}")
        print(f"📊 Risk Score: {summary['risk_score']} ({summary['risk_percentage']}%)")
        print(f"🛡️  Security Status: {summary['security_status']}")
        
        # Show critical and high issues
        critical_high_issues = [i for i in self.issues if i.severity in ["CRITICAL", "HIGH"]]
        if critical_high_issues:
            print(f"\n🚨 PRIORITY SECURITY ISSUES:")
            for issue in critical_high_issues:
                print(f"   [{issue.severity}] {issue.title}")
                print(f"      Description: {issue.description}")
                print(f"      Recommendation: {issue.recommendation}")
                if issue.endpoint:
                    print(f"      Endpoint: {issue.endpoint}")
                print()

async def send_webhook_alert(webhook_url: str, report: Dict[str, Any]) -> None:
    """Send security alert to webhook (Slack, Discord, etc.)"""
    try:
        summary = report["summary"]
        critical_issues = summary['issues_by_severity'].get('CRITICAL', 0)
        high_issues = summary['issues_by_severity'].get('HIGH', 0)
        
        if critical_issues > 0 or high_issues > 0:
            alert_message = {
                "text": f"🚨 Threadr Security Alert",
                "attachments": [
                    {
                        "color": "danger" if critical_issues > 0 else "warning",
                        "fields": [
                            {"title": "Critical Issues", "value": str(critical_issues), "short": True},
                            {"title": "High Issues", "value": str(high_issues), "short": True},
                            {"title": "Risk Score", "value": f"{summary['risk_score']} ({summary['risk_percentage']}%)", "short": True},
                            {"title": "Security Status", "value": summary['security_status'], "short": True}
                        ],
                        "timestamp": report["scan_timestamp"]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=alert_message) as response:
                    if response.status == 200:
                        print(f"✅ Alert sent to webhook")
                    else:
                        print(f"❌ Failed to send webhook alert: {response.status}")
        
    except Exception as e:
        print(f"❌ Webhook alert failed: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description='Threadr API Security Monitor')
    parser.add_argument('--frontend-url', default='https://threadr-plum.vercel.app',
                       help='Frontend URL to monitor')
    parser.add_argument('--backend-url', default='https://threadr-production.up.railway.app',
                       help='Backend URL to monitor')
    parser.add_argument('--json-output', help='Save security report to JSON file')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    parser.add_argument('--alerts-webhook', help='Webhook URL for security alerts')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async def run_scan():
        async with APISecurityMonitor(args.frontend_url, args.backend_url) as monitor:
            await monitor.run_security_scan()
            
            # Print report
            monitor.print_security_report()
            
            # Save JSON output if requested
            if args.json_output:
                report = monitor.generate_security_report()
                with open(args.json_output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\n💾 Security report saved to: {args.json_output}")
            
            # Send webhook alert if configured
            if args.alerts_webhook:
                report = monitor.generate_security_report()
                await send_webhook_alert(args.alerts_webhook, report)
            
            # Return critical issues count for exit code
            critical_issues = len([i for i in monitor.issues if i.severity == "CRITICAL"])
            return critical_issues
    
    try:
        if args.continuous:
            print(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
            while True:
                critical_issues = await run_scan()
                print(f"\n⏰ Next scan in {args.interval} seconds...")
                await asyncio.sleep(args.interval)
        else:
            critical_issues = await run_scan()
            
            # Exit with error code if critical issues found
            if critical_issues > 0:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⏹️  Security monitoring cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Security monitoring failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
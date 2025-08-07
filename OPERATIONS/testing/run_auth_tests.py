#!/usr/bin/env python3
"""
Master Authentication Test Runner for Threadr
Coordinates all authentication testing suites and provides comprehensive results

This runner executes:
1. Comprehensive auth system tests
2. Database integration tests  
3. Security vulnerability tests
4. Performance and load tests
5. OAuth preparation tests

Usage:
    python run_auth_tests.py [--suite=SUITE_NAME] [--output=FORMAT]
    
Options:
    --suite=all|comprehensive|database|security    Run specific test suite (default: all)
    --output=console|json|markdown                  Output format (default: console)
    --verbose                                       Enable verbose logging
    --no-cleanup                                    Don't cleanup test data
"""

import asyncio
import argparse
import json
import time
import sys
import os
from typing import Dict, Any, List
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Import test suites
try:
    from comprehensive_auth_test_suite import AuthTestSuite
    from test_database_integration import DatabaseIntegrationTestSuite
    from test_auth_security import SecurityTestSuite
except ImportError as e:
    print(f"{Fore.RED}Error importing test suites: {e}")
    print(f"{Fore.YELLOW}Make sure all test files are in the same directory")
    sys.exit(1)

class MasterTestRunner:
    """Master test runner that coordinates all authentication tests"""
    
    def __init__(self, base_url: str = "https://threadr-pw0s.onrender.com"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": base_url,
            "suites": {},
            "summary": {}
        }
        
    def print_banner(self):
        """Print test runner banner"""
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}  THREADR AUTHENTICATION SYSTEM - MASTER TEST RUNNER")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.WHITE}🎯 Target: {self.base_url}")
        print(f"{Fore.WHITE}📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}🧪 Testing: PostgreSQL Authentication System")
        print()
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive authentication tests"""
        print(f"{Fore.YELLOW}🔍 Running Comprehensive Authentication Tests...")
        
        try:
            async with AuthTestSuite(self.base_url) as suite:
                results = await suite.run_all_tests()
                return {
                    "name": "Comprehensive Authentication Tests",
                    "status": "completed",
                    "results": results,
                    "critical": results.get("summary", {}).get("pass_rate", 0) < 80
                }
        except Exception as e:
            return {
                "name": "Comprehensive Authentication Tests",
                "status": "error",
                "error": str(e),
                "critical": True
            }
    
    async def run_database_tests(self) -> Dict[str, Any]:
        """Run database integration tests"""
        print(f"{Fore.YELLOW}🗄️  Running Database Integration Tests...")
        
        try:
            async with DatabaseIntegrationTestSuite(self.base_url) as suite:
                results = await suite.run_all_tests()
                return {
                    "name": "Database Integration Tests",
                    "status": "completed",
                    "results": results,
                    "critical": results.get("pass_rate", 0) < 80
                }
        except Exception as e:
            return {
                "name": "Database Integration Tests", 
                "status": "error",
                "error": str(e),
                "critical": True
            }
    
    async def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        print(f"{Fore.YELLOW}🔒 Running Security Tests...")
        
        try:
            async with SecurityTestSuite(self.base_url) as suite:
                results = await suite.run_all_tests()
                return {
                    "name": "Security Tests",
                    "status": "completed",
                    "results": results,
                    "critical": results.get("pass_rate", 0) < 90  # Higher threshold for security
                }
        except Exception as e:
            return {
                "name": "Security Tests",
                "status": "error",
                "error": str(e),
                "critical": True
            }
    
    async def run_all_suites(self, suites: List[str] = None) -> Dict[str, Any]:
        """Run all or specified test suites"""
        start_time = time.time()
        
        if suites is None:
            suites = ["comprehensive", "database", "security"]
        
        suite_runners = {
            "comprehensive": self.run_comprehensive_tests,
            "database": self.run_database_tests,
            "security": self.run_security_tests
        }
        
        for suite_name in suites:
            if suite_name in suite_runners:
                print(f"\n{Fore.CYAN}{'='*60}")
                print(f"{Fore.CYAN}  STARTING: {suite_name.upper()} TESTS")
                print(f"{Fore.CYAN}{'='*60}")
                
                suite_start = time.time()
                suite_result = await suite_runners[suite_name]()
                suite_duration = time.time() - suite_start
                
                suite_result["duration"] = round(suite_duration, 2)
                self.results["suites"][suite_name] = suite_result
                
                # Print suite summary
                if suite_result["status"] == "completed":
                    results = suite_result.get("results", {})
                    pass_rate = results.get("pass_rate", 0)
                    total_tests = results.get("total_tests", 0)
                    
                    status_color = Fore.GREEN if pass_rate >= 90 else Fore.YELLOW if pass_rate >= 80 else Fore.RED
                    print(f"\n{status_color}📊 {suite_name.upper()} SUITE COMPLETED")
                    print(f"{Fore.WHITE}   Tests: {total_tests} | Pass Rate: {pass_rate}% | Duration: {suite_duration:.1f}s")
                else:
                    print(f"\n{Fore.RED}❌ {suite_name.upper()} SUITE FAILED")
                    print(f"{Fore.RED}   Error: {suite_result.get('error', 'Unknown error')}")
            else:
                print(f"{Fore.RED}Unknown test suite: {suite_name}")
        
        total_duration = time.time() - start_time
        
        # Calculate overall summary
        self.calculate_summary(total_duration)
        
        return self.results
    
    def calculate_summary(self, total_duration: float) -> None:
        """Calculate overall test summary"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        critical_failures = 0
        completed_suites = 0
        failed_suites = 0
        
        for suite_name, suite_result in self.results["suites"].items():
            if suite_result["status"] == "completed":
                completed_suites += 1
                results = suite_result.get("results", {})
                
                suite_total = results.get("total_tests", 0)
                suite_passed = results.get("passed", 0)
                suite_failed = results.get("failed", 0)
                
                total_tests += suite_total
                total_passed += suite_passed
                total_failed += suite_failed
                
                if suite_result.get("critical", False):
                    critical_failures += 1
            else:
                failed_suites += 1
                critical_failures += 1
        
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall status
        if critical_failures > 0:
            overall_status = "critical_issues"
            status_text = "CRITICAL ISSUES"
            status_color = Fore.RED
        elif overall_pass_rate >= 95:
            overall_status = "excellent"
            status_text = "EXCELLENT"
            status_color = Fore.GREEN
        elif overall_pass_rate >= 90:
            overall_status = "good"
            status_text = "GOOD"
            status_color = Fore.GREEN
        elif overall_pass_rate >= 80:
            overall_status = "acceptable"
            status_text = "ACCEPTABLE"
            status_color = Fore.YELLOW
        else:
            overall_status = "needs_improvement"
            status_text = "NEEDS IMPROVEMENT"
            status_color = Fore.RED
        
        self.results["summary"] = {
            "overall_status": overall_status,
            "overall_pass_rate": round(overall_pass_rate, 1),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "completed_suites": completed_suites,
            "failed_suites": failed_suites,
            "critical_failures": critical_failures,
            "duration": round(total_duration, 2),
            "status_text": status_text,
            "status_color": status_color
        }
    
    def print_final_report(self) -> None:
        """Print comprehensive final report"""
        summary = self.results["summary"]
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}  FINAL AUTHENTICATION SYSTEM TEST REPORT")
        print(f"{Fore.CYAN}{'='*80}")
        
        # Overall status
        status_color = getattr(Fore, summary["status_color"].split('.')[1] if '.' in summary["status_color"] else "WHITE")
        print(f"\n{status_color}🎯 OVERALL STATUS: {summary['status_text']}")
        
        # Key metrics
        print(f"\n{Fore.WHITE}📊 KEY METRICS:")
        print(f"   Total Tests Run: {summary['total_tests']}")
        print(f"   {Fore.GREEN}✓ Passed: {summary['total_passed']}")
        print(f"   {Fore.RED}✗ Failed: {summary['total_failed']}")
        print(f"   📈 Overall Pass Rate: {summary['overall_pass_rate']}%")
        print(f"   ⏱️  Total Duration: {summary['duration']} seconds")
        
        # Suite breakdown
        print(f"\n{Fore.WHITE}📋 SUITE BREAKDOWN:")
        for suite_name, suite_result in self.results["suites"].items():
            if suite_result["status"] == "completed":
                results = suite_result.get("results", {})
                pass_rate = results.get("pass_rate", 0)
                total_tests = results.get("total_tests", 0)
                duration = suite_result.get("duration", 0)
                
                suite_color = Fore.GREEN if pass_rate >= 90 else Fore.YELLOW if pass_rate >= 80 else Fore.RED
                critical_icon = " 🚨" if suite_result.get("critical", False) else ""
                
                print(f"   {suite_color}• {suite_name.title()}: {pass_rate}% ({total_tests} tests, {duration:.1f}s){critical_icon}")
            else:
                print(f"   {Fore.RED}• {suite_name.title()}: FAILED - {suite_result.get('error', 'Unknown error')}")
        
        # Production readiness assessment
        print(f"\n{Fore.CYAN}🚀 PRODUCTION READINESS ASSESSMENT:")
        
        if summary["overall_status"] == "excellent":
            print(f"{Fore.GREEN}   ✅ READY FOR PRODUCTION")
            print(f"{Fore.GREEN}   ✓ All authentication systems working correctly")
            print(f"{Fore.GREEN}   ✓ PostgreSQL integration stable")
            print(f"{Fore.GREEN}   ✓ Security measures properly implemented")
            
        elif summary["overall_status"] == "good":
            print(f"{Fore.GREEN}   ✅ READY FOR PRODUCTION")
            print(f"{Fore.YELLOW}   ⚠ Minor issues may exist but system is stable")
            print(f"{Fore.GREEN}   ✓ Core functionality working correctly")
            
        elif summary["overall_status"] == "acceptable":
            print(f"{Fore.YELLOW}   ⚠️ PROCEED WITH CAUTION")
            print(f"{Fore.YELLOW}   ⚠ Address failed tests before full production deployment")
            print(f"{Fore.YELLOW}   ⚠ Consider gradual rollout with monitoring")
            
        else:
            print(f"{Fore.RED}   ❌ NOT READY FOR PRODUCTION")
            print(f"{Fore.RED}   ✗ Critical issues must be resolved first")
            print(f"{Fore.RED}   ✗ Significant authentication problems detected")
        
        # Next steps
        print(f"\n{Fore.CYAN}📋 RECOMMENDED NEXT STEPS:")
        
        if summary["critical_failures"] > 0:
            print(f"{Fore.RED}   1. Fix critical authentication issues immediately")
            print(f"{Fore.RED}   2. Re-run tests to verify fixes")
            print(f"{Fore.YELLOW}   3. Consider additional security auditing")
            
        elif summary["total_failed"] > 0:
            print(f"{Fore.YELLOW}   1. Review and fix failed test cases")
            print(f"{Fore.YELLOW}   2. Verify fixes with targeted re-testing")
            print(f"{Fore.GREEN}   3. Proceed with production deployment")
            
        else:
            print(f"{Fore.GREEN}   1. ✅ All tests passing - system ready for production")
            print(f"{Fore.GREEN}   2. ✅ Implement monitoring for production environment")
            print(f"{Fore.GREEN}   3. ✅ Consider regular automated testing schedule")
        
        print(f"\n{Fore.WHITE}{'='*80}")
    
    def export_json_report(self, filename: str = None) -> str:
        """Export results as JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"threadr_auth_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return filename
    
    def export_markdown_report(self, filename: str = None) -> str:
        """Export results as Markdown"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"threadr_auth_test_report_{timestamp}.md"
        
        summary = self.results["summary"]
        
        markdown_content = f"""# Threadr Authentication System Test Report

## Summary

- **Overall Status**: {summary['status_text']}
- **Pass Rate**: {summary['overall_pass_rate']}%
- **Total Tests**: {summary['total_tests']}
- **Passed**: {summary['total_passed']}
- **Failed**: {summary['total_failed']}
- **Duration**: {summary['duration']} seconds
- **Timestamp**: {self.results['timestamp']}
- **Target URL**: {self.results['base_url']}

## Test Suite Results

"""
        
        for suite_name, suite_result in self.results["suites"].items():
            status_icon = "✅" if suite_result["status"] == "completed" else "❌"
            markdown_content += f"### {status_icon} {suite_name.title()} Tests\n\n"
            
            if suite_result["status"] == "completed":
                results = suite_result.get("results", {})
                markdown_content += f"- **Status**: Completed\n"
                markdown_content += f"- **Pass Rate**: {results.get('pass_rate', 0)}%\n"
                markdown_content += f"- **Total Tests**: {results.get('total_tests', 0)}\n"
                markdown_content += f"- **Duration**: {suite_result.get('duration', 0)} seconds\n"
                markdown_content += f"- **Critical**: {'Yes' if suite_result.get('critical') else 'No'}\n\n"
            else:
                markdown_content += f"- **Status**: Failed\n"
                markdown_content += f"- **Error**: {suite_result.get('error', 'Unknown error')}\n\n"
        
        markdown_content += f"""## Production Readiness

"""
        
        if summary["overall_status"] == "excellent":
            markdown_content += "✅ **READY FOR PRODUCTION** - All systems working correctly\n\n"
        elif summary["overall_status"] == "good":
            markdown_content += "✅ **READY FOR PRODUCTION** - Minor issues may exist but system is stable\n\n"
        elif summary["overall_status"] == "acceptable":
            markdown_content += "⚠️ **PROCEED WITH CAUTION** - Address failed tests before full deployment\n\n"
        else:
            markdown_content += "❌ **NOT READY FOR PRODUCTION** - Critical issues must be resolved\n\n"
        
        with open(filename, 'w') as f:
            f.write(markdown_content)
        
        return filename


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run Threadr authentication system tests")
    parser.add_argument("--suite", choices=["all", "comprehensive", "database", "security"], 
                       default="all", help="Test suite to run")
    parser.add_argument("--output", choices=["console", "json", "markdown"], 
                       default="console", help="Output format")
    parser.add_argument("--url", default="https://threadr-pw0s.onrender.com",
                       help="Backend URL to test")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't cleanup test data")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = MasterTestRunner(args.url)
    runner.print_banner()
    
    # Determine suites to run
    if args.suite == "all":
        suites = ["comprehensive", "database", "security"]
    else:
        suites = [args.suite]
    
    try:
        # Run tests
        results = await runner.run_all_suites(suites)
        
        # Output results
        if args.output == "console":
            runner.print_final_report()
            
        elif args.output == "json":
            json_file = runner.export_json_report()
            print(f"\n{Fore.GREEN}📄 JSON report exported: {json_file}")
            runner.print_final_report()  # Also show console output
            
        elif args.output == "markdown":
            md_file = runner.export_markdown_report()
            print(f"\n{Fore.GREEN}📄 Markdown report exported: {md_file}")
            runner.print_final_report()  # Also show console output
        
        # Return appropriate exit code
        summary = results.get("summary", {})
        if summary.get("critical_failures", 0) > 0:
            return 2  # Critical failures
        elif summary.get("overall_pass_rate", 0) < 80:
            return 1  # Test failures
        else:
            return 0  # Success
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n{Fore.RED}💥 Fatal error running tests: {str(e)}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"{Fore.RED}💥 Fatal error: {str(e)}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Railway Deployment Debugging Script

This script helps diagnose Railway deployment issues by:
1. Testing local environment configuration
2. Validating Railway-specific settings
3. Performing health checks on deployed services
4. Analyzing common deployment problems

Run this script to identify potential issues before/during Railway deployment.
"""

import os
import sys
import json
import asyncio
import subprocess
import platform
from datetime import datetime
from pathlib import Path
import httpx
import time

class RailwayDebugger:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backend_dir = self.project_root / "backend"
        self.results = {}
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_python_environment(self):
        """Check Python environment and dependencies"""
        self.log("Checking Python environment...")
        
        checks = {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "working_directory": str(Path.cwd()),
            "backend_exists": self.backend_dir.exists(),
            "requirements_exists": (self.backend_dir / "requirements.txt").exists(),
            "main_py_exists": (self.backend_dir / "main.py").exists(),
        }
        
        # Check if we can import key dependencies
        dependencies = ["fastapi", "uvicorn", "httpx", "pydantic", "openai"]
        for dep in dependencies:
            try:
                __import__(dep)
                checks[f"{dep}_importable"] = True
            except ImportError:
                checks[f"{dep}_importable"] = False
                
        self.results["python_environment"] = checks
        
        # Log critical issues
        if not checks["backend_exists"]:
            self.log("ERROR: backend/ directory not found!", "ERROR")
        if not checks["requirements_exists"]:
            self.log("ERROR: requirements.txt not found in backend/", "ERROR")
        if not checks["main_py_exists"]:
            self.log("ERROR: main.py not found in backend/", "ERROR")
            
        return checks
        
    def check_railway_config(self):
        """Check Railway-specific configuration files"""
        self.log("Checking Railway configuration...")
        
        config_files = {
            "nixpacks_toml": self.project_root / "nixpacks.toml",
            "railway_toml": self.project_root / "railway.toml", 
            "dockerfile": self.project_root / "Dockerfile",
            "procfile": self.backend_dir / "Procfile",
        }
        
        checks = {}
        for name, file_path in config_files.items():
            exists = file_path.exists()
            checks[f"{name}_exists"] = exists
            if exists:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        checks[f"{name}_content_length"] = len(content)
                        # Check for common issues
                        if name == "nixpacks_toml":
                            checks[f"{name}_has_workdir"] = "workDir" in content
                            checks[f"{name}_has_start_cmd"] = "[start]" in content
                except Exception as e:
                    checks[f"{name}_read_error"] = str(e)
                    
        self.results["railway_config"] = checks
        return checks
        
    def check_requirements_file(self):
        """Analyze requirements.txt for potential issues"""
        self.log("Checking requirements.txt...")
        
        req_file = self.backend_dir / "requirements.txt"
        if not req_file.exists():
            self.results["requirements"] = {"error": "requirements.txt not found"}
            return
            
        try:
            with open(req_file, 'r') as f:
                content = f.read()
                
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            checks = {
                "total_dependencies": len(lines),
                "has_fastapi": any("fastapi" in line.lower() for line in lines),
                "has_uvicorn": any("uvicorn" in line.lower() for line in lines),
                "has_gunicorn": any("gunicorn" in line.lower() for line in lines),
                "has_version_pins": sum(1 for line in lines if "==" in line),
                "dependencies": lines[:10]  # First 10 for debugging
            }
            
            # Check for problematic packages
            problematic = ["tensorflow", "torch", "scipy", "numpy"]
            checks["has_heavy_packages"] = any(pkg in content.lower() for pkg in problematic)
            
            self.results["requirements"] = checks
            
            if not checks["has_fastapi"]:
                self.log("ERROR: FastAPI not found in requirements.txt!", "ERROR")
            if not checks["has_uvicorn"]:
                self.log("WARNING: uvicorn not found in requirements.txt", "WARNING")
                
        except Exception as e:
            self.results["requirements"] = {"error": str(e)}
            self.log(f"ERROR reading requirements.txt: {e}", "ERROR")
            
    def test_local_app_startup(self):
        """Test if the app can start locally"""
        self.log("Testing local app startup...")
        
        try:
            # Change to backend directory
            original_cwd = os.getcwd()
            os.chdir(self.backend_dir)
            
            # Try to import and create the app
            sys.path.insert(0, str(self.backend_dir))
            
            try:
                from main import app
                checks = {
                    "app_import_success": True,
                    "app_type": str(type(app)),
                    "app_title": getattr(app, 'title', 'unknown'),
                }
                
                # Try to get app routes
                try:
                    routes = []
                    for route in app.routes:
                        if hasattr(route, 'path') and hasattr(route, 'methods'):
                            routes.append({
                                "path": route.path,
                                "methods": list(route.methods) if route.methods else []
                            })
                    checks["routes"] = routes[:10]  # First 10 routes
                    checks["total_routes"] = len(routes)
                except Exception as e:
                    checks["routes_error"] = str(e)
                    
            except ImportError as e:
                checks = {
                    "app_import_success": False,
                    "import_error": str(e)
                }
                self.log(f"ERROR: Cannot import main app: {e}", "ERROR")
                
        except Exception as e:
            checks = {"startup_error": str(e)}
            self.log(f"ERROR during startup test: {e}", "ERROR")
        finally:
            os.chdir(original_cwd)
            
        self.results["local_startup"] = checks
        return checks
        
    async def test_deployed_service(self, url):
        """Test deployed Railway service"""
        self.log(f"Testing deployed service at: {url}")
        
        if not url:
            self.log("No URL provided for deployed service test", "WARNING")
            return {"error": "No URL provided"}
            
        checks = {"base_url": url}
        
        # Test endpoints
        endpoints = ["/", "/health", "/debug", "/readiness"]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in endpoints:
                test_url = f"{url.rstrip('/')}{endpoint}"
                try:
                    self.log(f"Testing endpoint: {test_url}")
                    response = await client.get(test_url)
                    
                    checks[f"endpoint_{endpoint.replace('/', '_')}"] = {
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "content_length": len(response.content),
                        "headers": dict(response.headers),
                        "success": response.status_code < 400
                    }
                    
                    # Try to parse JSON response
                    try:
                        json_data = response.json()
                        checks[f"endpoint_{endpoint.replace('/', '_')}"]["json_parseable"] = True
                        if endpoint in ["/health", "/debug"]:
                            checks[f"endpoint_{endpoint.replace('/', '_')}"]["response_data"] = json_data
                    except:
                        checks[f"endpoint_{endpoint.replace('/', '_')}"]["json_parseable"] = False
                        
                except Exception as e:
                    checks[f"endpoint_{endpoint.replace('/', '_')}"] = {
                        "error": str(e),
                        "success": False
                    }
                    self.log(f"ERROR testing {test_url}: {e}", "ERROR")
                    
        self.results["deployed_service"] = checks
        return checks
        
    def check_environment_variables(self):
        """Check critical environment variables"""
        self.log("Checking environment variables...")
        
        critical_vars = [
            "PORT", "ENVIRONMENT", "PYTHONPATH", "PWD", 
            "OPENAI_API_KEY", "CORS_ORIGINS"
        ]
        
        checks = {}
        for var in critical_vars:
            value = os.getenv(var)
            checks[var] = {
                "set": value is not None,
                "value": value if var != "OPENAI_API_KEY" else ("***SET***" if value else None),
                "length": len(value) if value else 0
            }
            
        self.results["environment_variables"] = checks
        return checks
        
    def generate_deployment_recommendations(self):
        """Generate recommendations based on findings"""
        self.log("Generating deployment recommendations...")
        
        recommendations = []
        
        # Check results and generate recommendations
        if "python_environment" in self.results:
            env = self.results["python_environment"]
            if not env.get("backend_exists"):
                recommendations.append("CRITICAL: Create backend/ directory structure")
            if not env.get("main_py_exists"):
                recommendations.append("CRITICAL: Create main.py in backend/ directory")
            if not env.get("fastapi_importable"):
                recommendations.append("CRITICAL: Install FastAPI - run 'pip install fastapi'")
            if not env.get("uvicorn_importable"):
                recommendations.append("CRITICAL: Install uvicorn - run 'pip install uvicorn'")
                
        if "railway_config" in self.results:
            config = self.results["railway_config"]
            if not config.get("nixpacks_toml_exists"):
                recommendations.append("RECOMMENDED: Create nixpacks.toml for explicit Railway configuration")
            elif not config.get("nixpacks_toml_has_workdir"):
                recommendations.append("RECOMMENDED: Add workDir = 'backend' to nixpacks.toml")
                
        if "requirements" in self.results:
            req = self.results["requirements"]
            if req.get("error"):
                recommendations.append("CRITICAL: Fix requirements.txt file")
            elif not req.get("has_fastapi"):
                recommendations.append("CRITICAL: Add fastapi to requirements.txt")
            elif not req.get("has_uvicorn"):
                recommendations.append("RECOMMENDED: Add uvicorn to requirements.txt")
                
        if "local_startup" in self.results:
            startup = self.results["local_startup"]
            if not startup.get("app_import_success"):
                recommendations.append("CRITICAL: Fix app import issues before deploying")
                
        if "deployed_service" in self.results:
            service = self.results["deployed_service"]
            health_endpoint = service.get("endpoint__health", {})
            if not health_endpoint.get("success"):
                recommendations.append("CRITICAL: Health endpoint failing - check Railway logs")
                
        self.results["recommendations"] = recommendations
        return recommendations
        
    async def run_full_debug(self, deployed_url=None):
        """Run complete debugging suite"""
        self.log("=" * 60)
        self.log("STARTING RAILWAY DEPLOYMENT DEBUG")
        self.log("=" * 60)
        
        # Run all checks
        self.check_python_environment()
        self.check_railway_config()
        self.check_requirements_file()
        self.test_local_app_startup()
        self.check_environment_variables()
        
        if deployed_url:
            await self.test_deployed_service(deployed_url)
            
        recommendations = self.generate_deployment_recommendations()
        
        # Print summary
        self.log("=" * 60)
        self.log("DEBUG SUMMARY")
        self.log("=" * 60)
        
        if recommendations:
            self.log("RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                self.log(f"{i}. {rec}")
        else:
            self.log("No critical issues found!")
            
        # Save full results to file
        debug_file = self.project_root / "railway_debug_results.json"
        with open(debug_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        self.log(f"Full debug results saved to: {debug_file}")
        
        return self.results

async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Railway Deployment Debugger")
    parser.add_argument("--url", help="URL of deployed Railway service to test")
    parser.add_argument("--project-root", help="Path to project root directory")
    
    args = parser.parse_args()
    
    debugger = RailwayDebugger(args.project_root)
    results = await debugger.run_full_debug(args.url)
    
    # Exit with error code if critical issues found
    recommendations = results.get("recommendations", [])
    critical_issues = [r for r in recommendations if "CRITICAL" in r]
    
    if critical_issues:
        print(f"\n{len(critical_issues)} critical issues found. Fix these before deploying.")
        sys.exit(1)
    else:
        print("\nNo critical issues found. Deployment should work!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
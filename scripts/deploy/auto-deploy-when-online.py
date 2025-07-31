#!/usr/bin/env python3
"""
Automated Deployment Script for Threadr
Deploys as soon as network connectivity is restored
"""

import asyncio
import aiohttp
import subprocess
import time
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class NetworkAwareDeployer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.max_retries = 5
        self.retry_delay = 30  # seconds
        self.network_check_interval = 10  # seconds
        
    async def check_network_connectivity(self) -> bool:
        """Check if we have network connectivity to deployment services"""
        test_urls = [
            "https://github.com",
            "https://api.railway.app", 
            "https://api.vercel.com",
            "https://google.com"
        ]
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for url in test_urls:
                try:
                    async with session.get(url) as response:
                        if response.status < 500:  # Any response is good
                            print(f"✅ Network connectivity confirmed: {url}")
                            return True
                except Exception as e:
                    print(f"❌ Failed to reach {url}: {str(e)}")
                    continue
        
        return False
    
    def check_git_status(self) -> Dict:
        """Check if we have commits ready to push"""
        try:
            # Check if we're ahead of origin
            result = subprocess.run([
                "git", "status", "--porcelain", "-b"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return {"error": "Git status failed", "can_push": False}
            
            status_output = result.stdout.strip()
            
            # Check for unpushed commits
            ahead_result = subprocess.run([
                "git", "rev-list", "--count", "HEAD", "^origin/main"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            commits_ahead = int(ahead_result.stdout.strip()) if ahead_result.returncode == 0 else 0
            
            return {
                "commits_ahead": commits_ahead,
                "can_push": commits_ahead > 0,
                "working_tree_clean": len([line for line in status_output.split('\\n') if line and not line.startswith('##')]) == 0
            }
            
        except Exception as e:
            return {"error": str(e), "can_push": False}
    
    def push_to_github(self) -> bool:
        """Push commits to GitHub"""
        print("📤 Pushing commits to GitHub...")
        
        try:
            # Push to origin main
            result = subprocess.run([
                "git", "push", "origin", "main"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Successfully pushed to GitHub")
                print(f"Output: {result.stdout}")
                return True
            else:
                print(f"❌ Git push failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Git push error: {str(e)}")
            return False
    
    async def trigger_railway_deployment(self) -> bool:
        """Trigger Railway deployment after GitHub push"""
        print("🚂 Triggering Railway deployment...")
        
        # Railway should auto-deploy from GitHub, but we can also trigger manually
        try:
            result = subprocess.run([
                "railway", "up", "--detach"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Railway deployment triggered")
                return True
            else:
                print(f"⚠️  Railway CLI trigger failed: {result.stderr}")
                print("ℹ️  Railway should auto-deploy from GitHub push")
                return True  # Still consider success if GitHub push worked
                
        except subprocess.TimeoutExpired:
            print("⏰ Railway deployment trigger timeout")
            return True  # Auto-deploy should still work
        except Exception as e:
            print(f"⚠️  Railway trigger error: {str(e)}")
            return True  # Auto-deploy should still work
    
    async def trigger_vercel_deployment(self) -> bool:
        """Trigger Vercel deployment after GitHub push"""
        print("▲ Triggering Vercel deployment...")
        
        try:
            # Vercel should auto-deploy from GitHub, but we can trigger manually
            result = subprocess.run([
                "vercel", "--prod", "--yes"
            ], capture_output=True, text=True, timeout=300, cwd=self.project_root / "frontend")
            
            if result.returncode == 0:
                print("✅ Vercel deployment triggered")
                return True
            else:
                print(f"⚠️  Vercel CLI trigger failed: {result.stderr}")
                print("ℹ️  Vercel should auto-deploy from GitHub push")
                return True  # Still consider success if GitHub push worked
                
        except subprocess.TimeoutExpired:
            print("⏰ Vercel deployment trigger timeout")
            return True  # Auto-deploy should still work
        except Exception as e:
            print(f"⚠️  Vercel trigger error: {str(e)}")
            return True  # Auto-deploy should still work
    
    async def wait_for_deployment_completion(self) -> Dict:
        """Wait for deployments to complete and verify"""
        print("⏳ Waiting for deployments to complete...")
        
        backend_url = "https://threadr-production.up.railway.app"
        frontend_url = "https://threadr-plum.vercel.app"
        
        max_wait = 300  # 5 minutes
        check_interval = 15  # 15 seconds
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < max_wait:
                try:
                    # Check backend
                    async with session.get(f"{backend_url}/health", timeout=10) as response:
                        backend_status = response.status == 200
                except:
                    backend_status = False
                
                try:
                    # Check frontend
                    async with session.get(frontend_url, timeout=10) as response:
                        frontend_status = response.status == 200
                except:
                    frontend_status = False
                
                if backend_status and frontend_status:
                    print("✅ Both deployments are live!")
                    return {"backend": True, "frontend": True, "success": True}
                
                elapsed = int(time.time() - start_time)
                print(f"⏳ Waiting... ({elapsed}s) Backend: {'✅' if backend_status else '❌'} Frontend: {'✅' if frontend_status else '❌'}")
                
                await asyncio.sleep(check_interval)
        
        print("⚠️  Deployment verification timeout")
        return {"backend": backend_status, "frontend": frontend_status, "success": False}
    
    async def run_post_deployment_tests(self) -> bool:
        """Run verification tests after deployment"""
        print("🧪 Running post-deployment tests...")
        
        try:
            # Run the verification script against production
            result = subprocess.run([
                "python", "scripts/deploy/local-verification.py",
                "--backend-url", "https://threadr-production.up.railway.app",
                "--frontend-url", "https://threadr-plum.vercel.app"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Post-deployment tests passed!")
                return True
            else:
                print(f"❌ Post-deployment tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            return False
    
    def save_deployment_log(self, deployment_result: Dict) -> str:
        """Save deployment log for reference"""
        log_path = self.project_root / f"deployment-log-{int(time.time())}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "deployment_result": deployment_result,
            "git_status": self.check_git_status(),
            "network_restored": True
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"📄 Deployment log saved: {log_path}")
        return str(log_path)
    
    async def deploy_when_online(self) -> Dict:
        """Main deployment workflow when network is restored"""
        print("🚀 Starting Automated Deployment When Online")
        print("=" * 50)
        
        deployment_result = {
            "started_at": datetime.now().isoformat(),
            "steps": {},
            "success": False
        }
        
        # Step 1: Wait for network connectivity
        print("🌐 Waiting for network connectivity...")
        while not await self.check_network_connectivity():
            print(f"⏳ Network not available, checking again in {self.network_check_interval}s...")
            await asyncio.sleep(self.network_check_interval)
        
        deployment_result["steps"]["network_check"] = {"success": True, "timestamp": datetime.now().isoformat()}
        
        # Step 2: Check git status
        git_status = self.check_git_status()
        deployment_result["steps"]["git_status"] = git_status
        
        if not git_status.get("can_push", False):
            print("⚠️  No commits to push or git issues detected")
            deployment_result["success"] = False
            return deployment_result
        
        print(f"📊 Found {git_status['commits_ahead']} commits ready to push")
        
        # Step 3: Push to GitHub
        push_success = self.push_to_github()
        deployment_result["steps"]["github_push"] = {"success": push_success, "timestamp": datetime.now().isoformat()}
        
        if not push_success:
            print("❌ GitHub push failed, aborting deployment")
            deployment_result["success"] = False
            return deployment_result
        
        # Step 4: Trigger deployments
        railway_success = await self.trigger_railway_deployment()
        deployment_result["steps"]["railway_deploy"] = {"success": railway_success, "timestamp": datetime.now().isoformat()}
        
        vercel_success = await self.trigger_vercel_deployment()  
        deployment_result["steps"]["vercel_deploy"] = {"success": vercel_success, "timestamp": datetime.now().isoformat()}
        
        # Step 5: Wait for completion
        completion_status = await self.wait_for_deployment_completion()
        deployment_result["steps"]["deployment_verification"] = completion_status
        
        # Step 6: Run tests
        tests_passed = await self.run_post_deployment_tests()
        deployment_result["steps"]["post_deployment_tests"] = {"success": tests_passed, "timestamp": datetime.now().isoformat()}
        
        # Final result
        deployment_result["success"] = (push_success and 
                                      completion_status.get("success", False) and 
                                      tests_passed)
        deployment_result["completed_at"] = datetime.now().isoformat()
        
        # Save log
        log_path = self.save_deployment_log(deployment_result)
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 DEPLOYMENT SUMMARY")
        print("=" * 50)
        
        if deployment_result["success"]:
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("✅ GitHub push completed")
            print("✅ Railway deployment live")
            print("✅ Vercel deployment live") 
            print("✅ Post-deployment tests passed")
            print(f"🌐 Backend: https://threadr-production.up.railway.app")
            print(f"🌐 Frontend: https://threadr-plum.vercel.app")
        else:
            print("❌ DEPLOYMENT FAILED")
            print("Check individual steps above for details")
        
        print(f"📄 Full log: {log_path}")
        
        return deployment_result

async def main():
    """Main script entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-deploy Threadr when network is restored")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--check-interval", type=int, default=10, help="Network check interval (seconds)")
    parser.add_argument("--immediate", action="store_true", help="Deploy immediately if network is available")
    
    args = parser.parse_args()
    
    deployer = NetworkAwareDeployer(os.path.abspath(args.project_root))
    deployer.network_check_interval = args.check_interval
    
    if args.immediate:
        # Check network once and deploy if available
        if await deployer.check_network_connectivity():
            result = await deployer.deploy_when_online()
            exit(0 if result["success"] else 1)
        else:
            print("❌ Network not available for immediate deployment")
            exit(1)
    else:
        # Wait for network and then deploy
        result = await deployer.deploy_when_online()
        exit(0 if result["success"] else 1)

if __name__ == "__main__":
    asyncio.run(main())
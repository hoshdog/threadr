#!/usr/bin/env python3
"""
Manual Railway Deployment Script for Threadr
Alternative deployment methods when GitHub push is not available
"""

import os
import subprocess
import json
import time
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

class RailwayManualDeployer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_path = self.project_root / "backend"
        
    def check_railway_cli(self) -> bool:
        """Check if Railway CLI is installed and logged in"""
        try:
            result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Railway CLI found: {result.stdout.strip()}")
                
                # Check login status
                login_result = subprocess.run(["railway", "whoami"], capture_output=True, text=True)
                if login_result.returncode == 0:
                    print(f"✅ Logged in as: {login_result.stdout.strip()}")
                    return True
                else:
                    print("❌ Not logged in to Railway. Run: railway login")
                    return False
            else:
                print("❌ Railway CLI not found. Install: npm install -g @railway/cli")
                return False
        except FileNotFoundError:
            print("❌ Railway CLI not found. Install: npm install -g @railway/cli")
            return False
    
    def create_deployment_package(self) -> str:
        """Create a deployment package with only necessary files"""
        print("📦 Creating deployment package...")
        
        # Files to include in deployment
        include_patterns = [
            "backend/src/**/*.py",
            "backend/requirements.txt",
            "backend/runtime.txt",
            "nixpacks.toml",
            "backend/__init__.py"
        ]
        
        # Create temporary directory for deployment package
        temp_dir = tempfile.mkdtemp()
        deploy_dir = Path(temp_dir) / "threadr-deploy"
        deploy_dir.mkdir()
        
        # Copy backend files
        backend_deploy = deploy_dir / "backend"
        backend_deploy.mkdir()
        
        # Copy main backend files
        files_to_copy = [
            "backend/src/main.py",
            "backend/src/redis_manager.py", 
            "backend/src/__init__.py",
            "backend/requirements.txt",
            "backend/runtime.txt",
            "backend/__init__.py"
        ]
        
        for file_path in files_to_copy:
            src = self.project_root / file_path
            if src.exists():
                # Maintain directory structure
                rel_path = Path(file_path)
                dest = deploy_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                import shutil
                shutil.copy2(src, dest)
                print(f"  📄 Copied {file_path}")
        
        # Copy nixpacks.toml to root
        nixpacks_src = self.project_root / "nixpacks.toml"
        if nixpacks_src.exists():
            import shutil
            shutil.copy2(nixpacks_src, deploy_dir / "nixpacks.toml")
            print(f"  📄 Copied nixpacks.toml")
        
        print(f"✅ Deployment package created at: {deploy_dir}")
        return str(deploy_dir)
    
    def deploy_via_cli(self, package_dir: str) -> bool:
        """Deploy using Railway CLI from package directory"""
        print("🚀 Deploying via Railway CLI...")
        
        original_cwd = os.getcwd()
        
        try:
            os.chdir(package_dir)
            
            # Link to project (assumes project is already created)
            print("🔗 Linking to Railway project...")
            link_result = subprocess.run([
                "railway", "link", "--environment", "production"
            ], capture_output=True, text=True)
            
            if link_result.returncode != 0:
                print(f"⚠️  Link result: {link_result.stderr}")
                print("📝 You may need to run 'railway link' manually")
            
            # Deploy
            print("🚀 Starting deployment...")
            deploy_result = subprocess.run([
                "railway", "up", "--detach"
            ], capture_output=True, text=True, timeout=300)
            
            if deploy_result.returncode == 0:
                print("✅ Deployment initiated successfully!")
                print(f"📋 Output: {deploy_result.stdout}")
                return True
            else:
                print(f"❌ Deployment failed: {deploy_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Deployment timeout - check Railway dashboard")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {str(e)}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def deploy_via_zip_upload(self) -> str:
        """Create ZIP file for manual upload to Railway dashboard"""
        print("📦 Creating ZIP for manual upload...")
        
        zip_path = self.project_root / f"threadr-deploy-{int(time.time())}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add backend files
            backend_files = [
                "backend/src/main.py",
                "backend/src/redis_manager.py",
                "backend/src/__init__.py", 
                "backend/requirements.txt",
                "backend/runtime.txt",
                "backend/__init__.py"
            ]
            
            for file_path in backend_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    zipf.write(full_path, file_path)
                    print(f"  📄 Added {file_path}")
            
            # Add nixpacks.toml
            nixpacks_path = self.project_root / "nixpacks.toml"
            if nixpacks_path.exists():
                zipf.write(nixpacks_path, "nixpacks.toml")
                print(f"  📄 Added nixpacks.toml")
        
        print(f"✅ ZIP created: {zip_path}")
        print(f"📤 Manual upload instructions:")
        print(f"   1. Go to Railway dashboard")
        print(f"   2. Select your project")
        print(f"   3. Go to Settings > Deploy")
        print(f"   4. Upload {zip_path}")
        
        return str(zip_path)
    
    def validate_deployment_files(self) -> bool:
        """Validate all required deployment files exist"""
        print("✅ Validating deployment files...")
        
        required_files = [
            "backend/src/main.py",
            "backend/src/redis_manager.py",
            "backend/requirements.txt",
            "nixpacks.toml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print("✅ All required files present")
        return True
    
    def get_deployment_status(self) -> Dict:
        """Get current deployment status from Railway"""
        try:
            result = subprocess.run([
                "railway", "status"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "error", "error": result.stderr}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def deploy(self, method: str = "auto") -> bool:
        """Main deployment method"""
        print("🚀 Starting Railway Manual Deployment")
        print("=" * 50)
        
        # Validate files
        if not self.validate_deployment_files():
            return False
        
        if method == "auto" or method == "cli":
            # Try CLI deployment first
            if self.check_railway_cli():
                package_dir = self.create_deployment_package()
                success = self.deploy_via_cli(package_dir)
                
                if success:
                    print("\n✅ Railway deployment completed successfully!")
                    
                    # Show status
                    status = self.get_deployment_status()
                    if status["status"] == "success":
                        print(f"📊 Status: {status['output']}")
                    
                    return True
                else:
                    print("\n⚠️  CLI deployment failed, creating ZIP for manual upload...")
                    method = "zip"
            else:
                print("\n⚠️  Railway CLI not available, creating ZIP for manual upload...")
                method = "zip"
        
        if method == "zip":
            # Create ZIP for manual upload
            zip_path = self.deploy_via_zip_upload()
            print(f"\n📦 ZIP file ready for manual upload: {zip_path}")
            return True
        
        return False

def main():
    """Main deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manual Railway Deployment for Threadr")
    parser.add_argument("--method", choices=["auto", "cli", "zip"], default="auto",
                       help="Deployment method (auto, cli, zip)")
    parser.add_argument("--project-root", default=".",
                       help="Project root directory")
    
    args = parser.parse_args()
    
    deployer = RailwayManualDeployer(os.path.abspath(args.project_root))
    success = deployer.deploy(args.method)
    
    if not success:
        print("\n❌ Deployment failed!")
        exit(1)
    else:
        print("\n🎉 Deployment process completed!")

if __name__ == "__main__":
    main()
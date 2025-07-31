#!/usr/bin/env python3
"""
Manual Vercel Deployment Script for Threadr Frontend
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

class VercelManualDeployer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_path = self.project_root / "frontend"
        
    def check_vercel_cli(self) -> bool:
        """Check if Vercel CLI is installed and logged in"""
        try:
            result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Vercel CLI found: {result.stdout.strip()}")
                
                # Check login status by trying to list projects
                whoami_result = subprocess.run(["vercel", "whoami"], capture_output=True, text=True)
                if whoami_result.returncode == 0:
                    print(f"✅ Logged in as: {whoami_result.stdout.strip()}")
                    return True
                else:
                    print("❌ Not logged in to Vercel. Run: vercel login")
                    return False
            else:
                print("❌ Vercel CLI not found. Install: npm install -g vercel")
                return False
        except FileNotFoundError:
            print("❌ Vercel CLI not found. Install: npm install -g vercel")
            return False
    
    def validate_frontend_files(self) -> bool:
        """Validate all required frontend files exist"""
        print("✅ Validating frontend files...")
        
        required_files = [
            "frontend/src/index.html",
            "frontend/src/config.js",
            "frontend/vercel.json",
            "frontend/package.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print("✅ All required frontend files present")
        return True
    
    def update_config_for_production(self) -> bool:
        """Update config.js with production backend URL"""
        print("⚙️  Updating config for production...")
        
        config_path = self.frontend_path / "src" / "config.js"
        
        if not config_path.exists():
            print(f"❌ Config file not found: {config_path}")
            return False
        
        try:
            # Read current config
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Create backup
            backup_path = config_path.with_suffix('.js.backup')
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"📄 Backup created: {backup_path}")
            
            # Update for production (ensure Railway URL is used)
            production_config = '''// Threadr Frontend Configuration
const CONFIG = {
    // API Configuration
    API_BASE_URL: 'https://threadr-production.up.railway.app',
    
    // Feature Flags
    ENABLE_EMAIL_CAPTURE: true,
    ENABLE_USAGE_TRACKING: true,
    ENABLE_PREMIUM_FEATURES: true,
    
    // UI Configuration
    MAX_TWEET_LENGTH: 280,
    DEFAULT_THREAD_LENGTH: 5,
    
    // Development flags
    DEBUG: false,
    LOG_LEVEL: 'error'
};

// Export for use in HTML
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}
'''
            
            with open(config_path, 'w') as f:
                f.write(production_config)
            
            print("✅ Config updated for production")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update config: {str(e)}")
            return False
    
    def create_deployment_package(self) -> str:
        """Create a clean deployment package"""
        print("📦 Creating frontend deployment package...")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        deploy_dir = Path(temp_dir) / "threadr-frontend"
        deploy_dir.mkdir()
        
        # Copy frontend files
        import shutil
        
        files_to_copy = [
            ("frontend/src/index.html", "index.html"),
            ("frontend/src/config.js", "config.js"),
            ("frontend/vercel.json", "vercel.json"),
            ("frontend/package.json", "package.json")
        ]
        
        for src_path, dest_name in files_to_copy:
            src = self.project_root / src_path
            if src.exists():
                dest = deploy_dir / dest_name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                print(f"  📄 Copied {src_path} -> {dest_name}")
        
        print(f"✅ Deployment package created at: {deploy_dir}")
        return str(deploy_dir)
    
    def deploy_via_cli(self, package_dir: str) -> bool:
        """Deploy using Vercel CLI"""
        print("🚀 Deploying via Vercel CLI...")
        
        original_cwd = os.getcwd()
        
        try:
            os.chdir(package_dir)
            
            # Deploy to production
            print("🚀 Starting production deployment...")
            deploy_result = subprocess.run([
                "vercel", "--prod", "--yes"
            ], capture_output=True, text=True, timeout=300)
            
            if deploy_result.returncode == 0:
                print("✅ Deployment successful!")
                
                # Extract URL from output
                output_lines = deploy_result.stdout.strip().split('\n')
                url = None
                for line in output_lines:
                    if 'https://' in line and 'vercel.app' in line:
                        url = line.strip()
                        break
                
                if url:
                    print(f"🌐 Deployed to: {url}")
                else:
                    print(f"📋 Output: {deploy_result.stdout}")
                
                return True
            else:
                print(f"❌ Deployment failed: {deploy_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Deployment timeout - check Vercel dashboard")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {str(e)}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def deploy_via_drag_drop(self) -> str:
        """Create ZIP for drag-and-drop deployment"""
        print("📦 Creating ZIP for drag-and-drop deployment...")
        
        zip_path = self.project_root / f"threadr-frontend-{int(time.time())}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add only the files needed for static deployment
            files_to_add = [
                ("frontend/src/index.html", "index.html"),
                ("frontend/src/config.js", "config.js")
            ]
            
            for src_path, zip_name in files_to_add:
                full_path = self.project_root / src_path
                if full_path.exists():
                    zipf.write(full_path, zip_name)
                    print(f"  📄 Added {zip_name}")
        
        print(f"✅ ZIP created: {zip_path}")
        print("\n📤 Drag-and-drop deployment instructions:")
        print("   1. Go to https://vercel.com/new")
        print("   2. Drag and drop the ZIP file")
        print("   3. Configure project name as 'threadr'")
        print("   4. Deploy!")
        
        return str(zip_path)
    
    def create_manual_upload_instructions(self) -> str:
        """Create instructions for manual file upload"""
        instructions = f"""
# Manual Vercel Deployment Instructions for Threadr

## Method 1: Vercel CLI (Recommended)
1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Navigate to frontend directory: `cd {self.frontend_path}`
4. Deploy: `vercel --prod`

## Method 2: Drag & Drop (Simple)
1. Create a folder with these files:
   - index.html (from frontend/src/index.html)
   - config.js (from frontend/src/config.js)
2. Zip the folder
3. Go to https://vercel.com/new
4. Drag and drop the ZIP file
5. Set project name to 'threadr'
6. Deploy

## Method 3: GitHub Integration (When network returns)
1. Push changes to GitHub
2. Go to Vercel dashboard
3. Trigger new deployment
4. Or set up auto-deployment

## Important Configuration
Make sure config.js has the production backend URL:
```javascript
const CONFIG = {{
    API_BASE_URL: 'https://threadr-production.up.railway.app',
    // ... other config
}};
```

## Verification
After deployment:
1. Visit your Vercel URL
2. Test thread generation
3. Check network requests go to Railway backend
4. Verify email capture works
5. Test premium features

## Current Production URLs
- Backend: https://threadr-production.up.railway.app
- Frontend: https://threadr-plum.vercel.app (update after new deployment)
"""
        
        instructions_path = self.project_root / "MANUAL_VERCEL_DEPLOYMENT.md"
        with open(instructions_path, 'w') as f:
            f.write(instructions)
        
        print(f"📋 Instructions saved to: {instructions_path}")
        return str(instructions_path)
    
    def deploy(self, method: str = "auto") -> bool:
        """Main deployment method"""
        print("🚀 Starting Vercel Manual Deployment")
        print("=" * 50)
        
        # Validate files
        if not self.validate_frontend_files():
            return False
        
        # Update config for production
        if not self.update_config_for_production():
            return False
        
        if method == "auto" or method == "cli":
            # Try CLI deployment first
            if self.check_vercel_cli():
                package_dir = self.create_deployment_package()
                success = self.deploy_via_cli(package_dir)
                
                if success:
                    print("\n✅ Vercel deployment completed successfully!")
                    return True
                else:
                    print("\n⚠️  CLI deployment failed, creating files for manual upload...")
                    method = "manual"
            else:
                print("\n⚠️  Vercel CLI not available, creating files for manual upload...")
                method = "manual"
        
        if method == "manual" or method == "zip":
            # Create manual deployment options
            zip_path = self.deploy_via_drag_drop()
            instructions_path = self.create_manual_upload_instructions()
            
            print(f"\n📦 Files ready for manual deployment:")
            print(f"   ZIP: {zip_path}")
            print(f"   Instructions: {instructions_path}")
            
            return True
        
        return False
    
    def restore_config_backup(self) -> bool:
        """Restore config from backup after deployment"""
        config_path = self.frontend_path / "src" / "config.js"
        backup_path = config_path.with_suffix('.js.backup')
        
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, config_path)
            backup_path.unlink()  # Delete backup
            print("✅ Config restored from backup")
            return True
        
        return False

def main():
    """Main deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manual Vercel Deployment for Threadr")
    parser.add_argument("--method", choices=["auto", "cli", "manual", "zip"], default="auto",
                       help="Deployment method")
    parser.add_argument("--project-root", default=".",
                       help="Project root directory")
    parser.add_argument("--restore-config", action="store_true",
                       help="Restore config backup after deployment")
    
    args = parser.parse_args()
    
    deployer = VercelManualDeployer(os.path.abspath(args.project_root))
    
    if args.restore_config:
        deployer.restore_config_backup()
        return
    
    success = deployer.deploy(args.method)
    
    if not success:
        print("\n❌ Deployment preparation failed!")
        exit(1)
    else:
        print("\n🎉 Deployment process completed!")
        print("\n💡 Don't forget to restore config backup for local development:")
        print(f"   python {__file__} --restore-config")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Check deployment version on Render to verify latest code is deployed.
This will help identify if Render is running old code.
"""

import os
import sys
from datetime import datetime

def check_deployment():
    """Check deployment version and available files."""
    print("=" * 60)
    print("🔍 RENDER DEPLOYMENT VERSION CHECK")
    print("=" * 60)
    
    # Check current time
    print(f"\n📅 Current Time: {datetime.utcnow().isoformat()}Z")
    
    # Check working directory
    print(f"\n📁 Working Directory: {os.getcwd()}")
    
    # Check Python path
    print(f"\n🐍 Python Path:")
    for path in sys.path[:5]:
        print(f"  - {path}")
    
    # Check if our test files exist
    print("\n📋 Checking for Authentication Test Files:")
    
    test_files = [
        "test_auth_diagnosis.py",
        "test_auth_fixes.py", 
        "test_simple_auth.py",
        "simple_test_httpx.py",
        "quick_test.py",
        "setup_and_test.py"
    ]
    
    testing_dir = "/opt/render/project/src/OPERATIONS/testing"
    
    # First check if testing directory exists
    if os.path.exists(testing_dir):
        print(f"✅ Testing directory exists: {testing_dir}")
        
        # List all files in testing directory
        print("\n📂 Files in testing directory:")
        try:
            files = os.listdir(testing_dir)
            for file in sorted(files):
                if file.endswith('.py'):
                    file_path = os.path.join(testing_dir, file)
                    file_stat = os.stat(file_path)
                    file_time = datetime.fromtimestamp(file_stat.st_mtime)
                    print(f"  {'✅' if file in test_files else '📄'} {file} (Modified: {file_time.isoformat()})")
        except Exception as e:
            print(f"  ❌ Error listing files: {e}")
    else:
        print(f"❌ Testing directory NOT FOUND: {testing_dir}")
        
    # Check git information if available
    print("\n🔧 Git Information:")
    try:
        import subprocess
        
        # Get current commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd='/opt/render/project/src')
        if result.returncode == 0:
            print(f"  Current commit: {result.stdout.strip()[:10]}")
        else:
            print(f"  Git not available or not a git repository")
            
        # Get last commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True, cwd='/opt/render/project/src')
        if result.returncode == 0:
            print(f"  Last commit message: {result.stdout.strip()[:100]}")
    except Exception as e:
        print(f"  Git check failed: {e}")
    
    # Check environment variables that might indicate deployment version
    print("\n🌍 Environment Variables (deployment related):")
    deployment_vars = [
        "RENDER_GIT_COMMIT",
        "RENDER_GIT_BRANCH", 
        "RENDER_SERVICE_NAME",
        "RENDER_INSTANCE_ID",
        "RENDER",
        "IS_PULL_REQUEST"
    ]
    
    for var in deployment_vars:
        value = os.getenv(var)
        if value:
            print(f"  {var}: {value}")
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS:")
    
    # Provide diagnosis
    if os.path.exists(testing_dir):
        auth_diagnosis_path = os.path.join(testing_dir, "test_auth_diagnosis.py")
        if os.path.exists(auth_diagnosis_path):
            print("✅ test_auth_diagnosis.py EXISTS - Deployment is up to date!")
        else:
            print("❌ test_auth_diagnosis.py NOT FOUND - Deployment is outdated!")
            print("\n🔧 SOLUTION:")
            print("1. Go to Render Dashboard")
            print("2. Click on your backend service")  
            print("3. Go to 'Settings' → 'Build & Deploy'")
            print("4. Click 'Manual Deploy' → 'Deploy latest commit'")
            print("5. Wait for deployment to complete (5-10 minutes)")
    else:
        print("❌ CRITICAL: Testing directory doesn't exist!")
        print("Render deployment is severely outdated or misconfigured")
    
    print("=" * 60)

if __name__ == "__main__":
    check_deployment()
#!/usr/bin/env python3
"""
Railway 502 Error Debugging Script
This script helps identify and fix 502 "Application failed to respond" errors
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def run_command(cmd, cwd=None):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_file_exists(path):
    """Check if file exists and print status"""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {path}")
    return exists

def test_local_startup():
    """Test if the app starts locally"""
    print_section("TESTING LOCAL STARTUP")
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("✗ Backend directory not found!")
        return False
    
    # Test importing main module
    print("Testing Python imports...")
    os.chdir("backend")
    success, stdout, stderr = run_command("python -c \"import main; print('Import successful')\"")
    
    if success:
        print("✓ Python imports working")
    else:
        print(f"✗ Import failed: {stderr}")
        return False
    
    # Test starting uvicorn
    print("\nTesting uvicorn startup (will run for 5 seconds)...")
    process = subprocess.Popen([
        "python", "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--workers", "1"
    ])
    
    time.sleep(3)  # Give it time to start
    
    # Test if server responds
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Local server started successfully")
            print(f"✓ Health check response: {response.json()}")
            success = True
        else:
            print(f"✗ Health check failed with status: {response.status_code}")
            success = False
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not connect to local server: {e}")
        success = False
    
    # Kill the test server
    process.terminate()
    process.wait()
    
    return success

def check_railway_config():
    """Check Railway configuration files"""
    print_section("CHECKING RAILWAY CONFIGURATION")
    
    # Go back to root directory
    os.chdir("..")
    
    files_to_check = [
        "nixpacks.toml",
        "backend/main.py",
        "backend/requirements.txt",
        "backend/runtime.txt"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if not check_file_exists(file_path):
            all_exist = False
    
    if all_exist:
        print("\n✓ All required files exist")
    else:
        print("\n✗ Some required files are missing")
    
    # Check nixpacks.toml content
    print("\nChecking nixpacks.toml configuration...")
    try:
        with open("nixpacks.toml", "r") as f:
            content = f.read()
            if "workDir = \"backend\"" in content:
                print("✓ Working directory set to backend")
            else:
                print("✗ Working directory not set correctly")
            
            if "uvicorn main:app" in content:
                print("✓ Uvicorn command found")
            else:
                print("✗ Uvicorn command not found")
                
    except Exception as e:
        print(f"✗ Error reading nixpacks.toml: {e}")

def generate_fix_commands():
    """Generate Railway debugging commands"""
    print_section("RAILWAY DEBUGGING COMMANDS")
    
    print("Run these commands to debug your Railway deployment:\n")
    
    print("1. Check Railway logs:")
    print("   railway logs --tail 100\n")
    
    print("2. Check environment variables:")
    print("   railway variables\n")
    
    print("3. Test in Railway shell:")
    print("   railway shell")
    print("   cd backend")
    print("   python -c \"import main; print('Import OK')\"")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000\n")
    
    print("4. Deploy with current fixes:")
    print("   railway up\n")
    
    print("5. Monitor deployment:")
    print("   railway logs --follow\n")
    
    print("6. If still failing, try fallback config:")
    print("   cp nixpacks_fallback.toml nixpacks.toml")
    print("   railway up\n")

def main():
    print_section("THREADR RAILWAY 502 ERROR DEBUGGER")
    print("This script will help identify and fix Railway deployment issues")
    
    # Test local functionality first
    if test_local_startup():
        print("\n✅ Local startup test PASSED")
        print("The issue is likely Railway-specific configuration")
    else:
        print("\n❌ Local startup test FAILED") 
        print("Fix local issues before deploying to Railway")
        return
    
    # Check Railway configuration
    check_railway_config()
    
    # Generate debugging commands
    generate_fix_commands()
    
    print_section("SUMMARY")
    print("1. ✓ Local application works correctly")
    print("2. Next step: Run Railway debugging commands above")
    print("3. Most likely fix: Updated nixpacks.toml should resolve the issue")
    print("4. If issues persist, try the fallback configuration")

if __name__ == "__main__":
    main()
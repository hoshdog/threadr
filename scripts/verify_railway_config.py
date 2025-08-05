#!/usr/bin/env python3
"""Verify Railway configuration before deployment"""

import os
import sys
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def check_config_files():
    """Check all Railway configuration files"""
    print("🔍 RAILWAY CONFIGURATION VERIFICATION")
    print("=" * 60)
    
    configs = {
        "railway.json": "Highest priority - overrides everything",
        "nixpacks.toml": "Build configuration",
        "Dockerfile": "Docker deployment (should be disabled)",
        "Procfile": "Legacy deployment (should not exist)",
        "backend/Procfile": "Backend Procfile (should not exist)"
    }
    
    found_configs = []
    
    for config, description in configs.items():
        if os.path.exists(config):
            found_configs.append(config)
            print(f"✅ Found: {config}")
            print(f"   Purpose: {description}")
            
            # Show content for key files
            if config == "railway.json":
                with open(config, 'r') as f:
                    data = json.load(f)
                    start_cmd = data.get('deploy', {}).get('startCommand', 'NOT SET')
                    print(f"   Start Command: {start_cmd}")
                    if "main_minimal" in start_cmd:
                        print(f"   ✅ Correctly points to main_minimal.py")
                    else:
                        print(f"   ❌ Does NOT point to main_minimal.py!")
                        
            elif config == "nixpacks.toml":
                with open(config, 'r') as f:
                    content = f.read()
                    if "main_minimal" in content:
                        print(f"   ✅ References main_minimal.py")
                    else:
                        print(f"   ❌ Does NOT reference main_minimal.py!")
        else:
            print(f"❌ Not found: {config}")
            
    return found_configs

def verify_file_structure():
    """Verify the Python files exist"""
    print("\n📁 FILE STRUCTURE VERIFICATION")
    print("-" * 60)
    
    critical_files = [
        ("backend/src/main_minimal.py", "Target deployment file"),
        ("backend/src/main.py", "Old file (should exist but not be used)"),
        ("backend/requirements.txt", "Python dependencies")
    ]
    
    all_good = True
    
    for filepath, description in critical_files:
        if os.path.exists(filepath):
            print(f"✅ {filepath}")
            print(f"   Purpose: {description}")
            
            # Check file size
            size = os.path.getsize(filepath)
            print(f"   Size: {size} bytes")
            
            if filepath == "backend/src/main_minimal.py" and size < 100:
                print(f"   ⚠️  WARNING: File seems too small!")
                all_good = False
        else:
            print(f"❌ MISSING: {filepath}")
            print(f"   Purpose: {description}")
            all_good = False
            
    return all_good

def check_potential_conflicts():
    """Check for files that might confuse Railway"""
    print("\n⚠️  CONFLICT CHECK")
    print("-" * 60)
    
    conflict_files = [
        "Dockerfile",
        "app.py",
        "main.py",
        "backend/app.py",
        "backend/main.py",
        "backend/Dockerfile",
        "backend/railway.json"
    ]
    
    conflicts = []
    
    for filepath in conflict_files:
        if os.path.exists(filepath):
            conflicts.append(filepath)
            print(f"⚠️  Potential conflict: {filepath}")
            
    if not conflicts:
        print("✅ No conflicting files found")
        
    return conflicts

def verify_paths():
    """Verify the paths in configuration match actual structure"""
    print("\n🛤️  PATH VERIFICATION")
    print("-" * 60)
    
    # Check if railway.json start command will work
    if os.path.exists("railway.json"):
        with open("railway.json", 'r') as f:
            data = json.load(f)
            start_cmd = data.get('deploy', {}).get('startCommand', '')
            
        if "cd backend" in start_cmd:
            print("✅ Start command changes to backend directory")
            
            # Extract the uvicorn command
            if "uvicorn src.main_minimal:app" in start_cmd:
                print("✅ Uvicorn command looks correct")
                
                # Verify the actual path
                test_path = "backend/src/main_minimal.py"
                if os.path.exists(test_path):
                    print(f"✅ Path verified: {test_path} exists")
                else:
                    print(f"❌ ERROR: {test_path} does NOT exist!")
            else:
                print("❌ Uvicorn command doesn't reference main_minimal")
        else:
            print("⚠️  Start command doesn't change directory")

def generate_report():
    """Generate deployment readiness report"""
    print("\n📋 DEPLOYMENT READINESS REPORT")
    print("=" * 60)
    
    ready = True
    
    # Check configurations
    configs = check_config_files()
    if "railway.json" in configs:
        print("\n✅ railway.json present - will override all other configs")
    elif "nixpacks.toml" in configs:
        print("\n⚠️  Using nixpacks.toml - make sure Railway reads it")
    else:
        print("\n❌ No deployment configuration found!")
        ready = False
        
    # Check files
    if not verify_file_structure():
        ready = False
        
    # Check conflicts
    conflicts = check_potential_conflicts()
    if "Dockerfile" in conflicts:
        print("\n❌ Dockerfile exists - will override railway.json!")
        ready = False
        
    # Verify paths
    verify_paths()
    
    print("\n" + "=" * 60)
    if ready:
        print("✅ READY FOR DEPLOYMENT")
        print("\nNext steps:")
        print("1. Commit changes: git add -A && git commit -m 'Force Railway main_minimal.py'")
        print("2. Push to trigger deployment: git push origin main")
        print("3. Monitor Railway logs for 'main_minimal'")
    else:
        print("❌ NOT READY - Fix issues above first!")
        
    print("\n💡 PRO TIP: If deployment still fails, delete and recreate Railway service")

if __name__ == "__main__":
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    print("Railway Configuration Verification")
    print("Current directory:", os.getcwd())
    print()
    
    generate_report()
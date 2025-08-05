#!/usr/bin/env python3
"""Diagnose why Railway is ignoring nixpacks.toml"""

import os
import sys
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def check_file_exists(filepath):
    """Check if a file exists and print status"""
    exists = os.path.exists(filepath)
    print(f"{'✓' if exists else '✗'} {filepath}: {'EXISTS' if exists else 'NOT FOUND'}")
    return exists

def analyze_nixpacks_config():
    """Analyze nixpacks.toml configuration"""
    print("\n📋 NIXPACKS.TOML ANALYSIS")
    print("-" * 60)
    
    nixpacks_path = "nixpacks.toml"
    if not check_file_exists(nixpacks_path):
        print("❌ CRITICAL: nixpacks.toml not found in root!")
        return False
        
    with open(nixpacks_path, 'r') as f:
        content = f.read()
        
    print("\n🔍 Checking start command:")
    if "main_minimal" in content:
        print("✅ main_minimal.py is specified in start command")
    else:
        print("❌ main_minimal.py NOT found in start command")
        
    if "workDir" in content:
        print("✅ workDir is set")
    else:
        print("⚠️  workDir not set - might cause path issues")
        
    return True

def check_python_triggers():
    """Check for files that trigger Python buildpack"""
    print("\n🐍 PYTHON BUILDPACK TRIGGERS")
    print("-" * 60)
    
    triggers = {
        "runtime.txt": "Specifies Python version - OVERRIDES nixpacks",
        "pyproject.toml": "Python project config - OVERRIDES nixpacks",
        "Pipfile": "Pipenv config - OVERRIDES nixpacks",
        "setup.py": "Python package setup - might trigger buildpack",
        "setup.cfg": "Python package config - might trigger buildpack"
    }
    
    found_triggers = []
    
    # Check root directory
    print("\n📁 Root directory:")
    for file, desc in triggers.items():
        if check_file_exists(file):
            found_triggers.append((file, desc))
            
    # Check backend directory
    print("\n📁 Backend directory:")
    for file, desc in triggers.items():
        backend_path = f"backend/{file}"
        if check_file_exists(backend_path):
            found_triggers.append((backend_path, desc))
            
    if found_triggers:
        print("\n⚠️  FOUND PYTHON BUILDPACK TRIGGERS:")
        for file, desc in found_triggers:
            print(f"   - {file}: {desc}")
    else:
        print("\n✅ No Python buildpack triggers found")
        
    return found_triggers

def check_procfile():
    """Check for Procfile which overrides everything"""
    print("\n📄 PROCFILE CHECK")
    print("-" * 60)
    
    procfiles = ["Procfile", "backend/Procfile"]
    found = False
    
    for procfile in procfiles:
        if check_file_exists(procfile):
            found = True
            with open(procfile, 'r') as f:
                print(f"\n⚠️  Found {procfile}:")
                print(f"   Content: {f.read().strip()}")
                
    if not found:
        print("✅ No Procfile found (good - nixpacks can work)")
        
    return found

def check_railway_config():
    """Check for Railway-specific config files"""
    print("\n🚂 RAILWAY CONFIG CHECK")
    print("-" * 60)
    
    configs = ["railway.json", "railway.toml", ".railway/config.json"]
    found = False
    
    for config in configs:
        if check_file_exists(config):
            found = True
            print(f"⚠️  Found {config} - might override nixpacks")
            
    if not found:
        print("✅ No Railway config files found (nixpacks should work)")
        
    return found

def check_docker():
    """Check for Dockerfile which has highest priority"""
    print("\n🐳 DOCKERFILE CHECK")
    print("-" * 60)
    
    dockerfiles = ["Dockerfile", "backend/Dockerfile"]
    found = False
    
    for dockerfile in dockerfiles:
        if check_file_exists(dockerfile):
            found = True
            print(f"⚠️  Found {dockerfile} - OVERRIDES nixpacks!")
            
    if not found:
        print("✅ No Dockerfile found (nixpacks can work)")
        
    return found

def verify_main_files():
    """Verify the Python files exist"""
    print("\n🐍 PYTHON FILES CHECK")
    print("-" * 60)
    
    files_to_check = [
        "backend/src/main.py",
        "backend/src/main_minimal.py",
        "backend/src/main_simple.py"
    ]
    
    for file in files_to_check:
        check_file_exists(file)

def suggest_fixes():
    """Suggest fixes based on findings"""
    print("\n💡 SUGGESTED FIXES")
    print("=" * 60)
    
    print("""
1. REMOVE PYTHON BUILDPACK TRIGGERS:
   - Delete or rename runtime.txt in backend/
   - Delete or rename pyproject.toml in backend/
   - These files force Railway to use Python buildpack

2. CHECK RAILWAY DASHBOARD:
   - Go to Settings → Build & Deploy
   - Look for "Start Command" override
   - Remove any custom command

3. FORCE NIXPACKS:
   - Add to nixpacks.toml:
     [phases.setup]
     nixPkgs = ["python311"]
     
4. ALTERNATIVE: USE DOCKERFILE:
   - Create a Dockerfile that uses main_minimal.py
   - Railway will use Dockerfile over everything else

5. VERIFY PATH IS CORRECT:
   - Current: exec uvicorn src.main_minimal:app
   - Should work with workDir = "backend"
   - File exists at: backend/src/main_minimal.py
""")

def main():
    print("=" * 60)
    print("🔍 RAILWAY NIXPACKS DIAGNOSTIC")
    print("=" * 60)
    print("Analyzing why Railway ignores nixpacks.toml...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"\n📁 Working directory: {os.getcwd()}")
    
    # Run all checks
    nixpacks_ok = analyze_nixpacks_config()
    triggers = check_python_triggers()
    has_procfile = check_procfile()
    has_railway_config = check_railway_config()
    has_dockerfile = check_docker()
    verify_main_files()
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    if has_dockerfile:
        print("❌ Dockerfile found - will override nixpacks.toml")
    elif has_procfile:
        print("❌ Procfile found - will override nixpacks.toml")
    elif triggers:
        print("❌ Python buildpack triggers found - will override nixpacks.toml")
        print("   Remove these files to use nixpacks!")
    elif has_railway_config:
        print("⚠️  Railway config found - might override nixpacks.toml")
    else:
        print("✅ No overrides found - nixpacks.toml should work")
        print("   Check Railway dashboard for manual overrides")
        
    suggest_fixes()

if __name__ == "__main__":
    main()
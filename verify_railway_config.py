#!/usr/bin/env python3
"""
Railway Configuration Verification Script
Checks for any remaining gunicorn references that could cause deployment issues
"""

import os
import glob
from pathlib import Path

def check_file_for_gunicorn(filepath):
    """Check if a file contains problematic gunicorn references"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            gunicorn_lines = []
            for i, line in enumerate(lines, 1):
                if 'gunicorn' in line.lower():
                    # Skip lines that are explicitly disabling gunicorn
                    if ('NO_GUNICORN' in line or 
                        'disable' in line.lower() or
                        'RAILWAY_NO_GUNICORN' in line):
                        continue
                    # Skip comments that mention gunicorn negatively
                    if (line.strip().startswith('#') and 
                        ('not' in line.lower() or 'no' in line.lower() or 'disable' in line.lower())):
                        continue
                    gunicorn_lines.append(f"Line {i}: {line.strip()}")
            return gunicorn_lines
    except Exception as e:
        return [f"Error reading file: {e}"]

def main():
    """Main verification function"""
    print("Railway Configuration Verification")
    print("=====================================")
    
    # Check key configuration files
    config_files = [
        'nixpacks.toml',
        'backend/requirements.txt',
        'backend/pyproject.toml',
        'requirements_minimal.txt',
        'Dockerfile'
    ]
    
    issues_found = False
    
    for file_path in config_files:
        if os.path.exists(file_path):
            gunicorn_refs = check_file_for_gunicorn(file_path)
            if gunicorn_refs:
                print(f"[X] ISSUE: {file_path} contains gunicorn references:")
                for ref in gunicorn_refs:
                    print(f"    {ref}")
                issues_found = True
            else:
                print(f"[OK] CLEAN: {file_path}")
        else:
            print(f"[!] MISSING: {file_path}")
    
    # Check for backup nixpacks files
    print("\nChecking for conflicting nixpacks files...")
    nixpacks_files = glob.glob("nixpacks*.toml")
    active_nixpacks = []
    disabled_nixpacks = []
    
    for file in nixpacks_files:
        if file.endswith('.disabled'):
            disabled_nixpacks.append(file)
        else:
            active_nixpacks.append(file)
    
    if len(active_nixpacks) > 1:
        print(f"[X] MULTIPLE ACTIVE NIXPACKS: {active_nixpacks}")
        print("   Railway may be confused by multiple nixpacks files!")
        issues_found = True
    elif len(active_nixpacks) == 1:
        print(f"[OK] SINGLE NIXPACKS: {active_nixpacks[0]}")
    
    if disabled_nixpacks:
        print(f"[OK] DISABLED BACKUPS: {disabled_nixpacks}")
    
    # Check current nixpacks.toml configuration
    print(f"\nVerifying nixpacks.toml configuration...")
    if os.path.exists('nixpacks.toml'):
        with open('nixpacks.toml', 'r') as f:
            content = f.read()
            if 'uvicorn' in content and 'gunicorn' not in content:
                print("[OK] nixpacks.toml uses uvicorn only")
            elif 'gunicorn' in content:
                print("[X] nixpacks.toml contains gunicorn references")
                issues_found = True
            else:
                print("[!] nixpacks.toml doesn't specify server type clearly")
    
    # Final verdict
    print(f"\n{'='*50}")
    if not issues_found:
        print("CONFIGURATION CLEAN!")
        print("Railway should now use uvicorn from nixpacks.toml")
        print("\nNext steps:")
        print("1. Clear Railway build cache (redeploy)")
        print("2. Check Railway logs for 'uvicorn' startup messages")
        print("3. Verify no gunicorn error messages")
    else:
        print("ISSUES FOUND!")
        print("Please fix the issues above before redeploying to Railway")
    
    return not issues_found

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
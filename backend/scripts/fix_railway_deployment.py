#!/usr/bin/env python3
"""
Quick Railway Deployment Fix Script

This script automates the process of switching to minimal Railway configuration
to isolate and fix deployment issues.

Usage: python fix_railway_deployment.py [--restore]
"""

import os
import shutil
import sys
from pathlib import Path

def backup_file(file_path):
    """Create backup of existing file"""
    if file_path.exists():
        backup_path = Path(str(file_path) + ".backup")
        shutil.copy2(file_path, backup_path)
        print(f"✓ Backed up {file_path} to {backup_path}")
        return True
    return False

def restore_file(file_path):
    """Restore file from backup"""
    backup_path = Path(str(file_path) + ".backup")
    if backup_path.exists():
        shutil.copy2(backup_path, file_path)
        print(f"✓ Restored {file_path} from backup")
        return True
    else:
        print(f"✗ No backup found for {file_path}")
        return False

def setup_minimal_config():
    """Switch to minimal Railway configuration"""
    project_root = Path.cwd()
    backend_dir = project_root / "backend"
    
    print("Setting up minimal Railway configuration for debugging...")
    print("=" * 50)
    
    # 1. Backup and replace nixpacks.toml
    nixpacks_original = project_root / "nixpacks.toml"
    nixpacks_minimal = project_root / "nixpacks_minimal.toml"
    
    if nixpacks_minimal.exists():
        backup_file(nixpacks_original)
        shutil.copy2(nixpacks_minimal, nixpacks_original)
        print("✓ Switched to minimal nixpacks.toml")
    else:
        print("✗ nixpacks_minimal.toml not found")
    
    # 2. Backup and replace requirements.txt
    requirements_original = backend_dir / "requirements.txt"
    requirements_minimal = backend_dir / "requirements_minimal.txt"
    
    if requirements_minimal.exists():
        backup_file(requirements_original)
        shutil.copy2(requirements_minimal, requirements_original)
        print("✓ Switched to minimal requirements.txt")
    else:
        print("✗ requirements_minimal.txt not found")
    
    # 3. Backup main.py and switch to test app (optional)
    main_py = backend_dir / "main.py"
    test_app = backend_dir / "test_railway_app.py"
    
    if test_app.exists():
        print("\n📋 Optional: Switch to test app for maximum isolation?")
        print("   This replaces your main.py with a minimal test app.")
        response = input("   Switch to test app? (y/N): ").strip().lower()
        
        if response == 'y':
            backup_file(main_py)
            shutil.copy2(test_app, main_py)
            print("✓ Switched to test app (test_railway_app.py)")
        else:
            print("✓ Keeping your current main.py")
    
    # 4. Create/update Procfile for minimal deployment
    procfile = backend_dir / "Procfile"
    procfile_minimal = backend_dir / "Procfile_minimal"
    
    if procfile_minimal.exists():
        backup_file(procfile)
        shutil.copy2(procfile_minimal, procfile)
        print("✓ Updated Procfile with minimal configuration")
    
    print("\n" + "=" * 50)
    print("✅ Minimal configuration setup complete!")
    print("\nNext steps:")
    print("1. Test locally: cd backend && python main.py")
    print("2. Deploy to Railway: git add . && git commit -m 'minimal config' && git push")
    print("3. Check Railway logs for any remaining issues")
    print("4. Run: python railway_debug.py --url YOUR_RAILWAY_URL")
    print("\nTo restore original files: python fix_railway_deployment.py --restore")

def restore_original_config():
    """Restore original configuration from backups"""
    project_root = Path.cwd()
    backend_dir = project_root / "backend"
    
    print("Restoring original Railway configuration...")
    print("=" * 50)
    
    files_to_restore = [
        project_root / "nixpacks.toml",
        backend_dir / "requirements.txt",
        backend_dir / "main.py",
        backend_dir / "Procfile"
    ]
    
    restored_count = 0
    for file_path in files_to_restore:
        if restore_file(file_path):
            restored_count += 1
    
    print(f"\n✅ Restored {restored_count} files from backups")
    print("\nNext steps:")
    print("1. Test locally to ensure everything works")
    print("2. Deploy to Railway when ready")

def main():
    """Main execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_original_config()
    else:
        setup_minimal_config()

if __name__ == "__main__":
    main()
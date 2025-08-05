#!/usr/bin/env python3
"""
Root Directory Organization Script
Moves files from cluttered root to organized structure
"""

import os
import shutil
from pathlib import Path

# Define file movements
FILE_MOVEMENTS = {
    # Documentation files to move to docs/
    'docs/deployment': [
        'DEPLOY_NEXTJS_NOW.md',
        'NEXTJS_DEPLOYMENT_GUIDE.md',
        'RAILWAY_DEPLOYMENT_FIX_STATUS.md',
        'RAILWAY_SUBSCRIPTION_DEPLOYMENT_VERIFICATION.md',
        'VERCEL_DEPLOYMENT_READY.md',
        'VERCEL_ROOT_DIRECTORY_FIX.md',
        'VERCEL_DEPLOYMENT_404_FIX.md',
    ],
    'docs/development': [
        'STRIPE_RAILWAY_SETUP_INSTRUCTIONS.md',
        'STRIPE_SUBSCRIPTION_VERIFICATION_GUIDE.md',
        'SUBSCRIPTION_MODEL_TRANSFORMATION_COMPLETE.md',
    ],
    'docs/project': [
        'SESSION_ACCOMPLISHMENTS_SUMMARY.md',
        'ROOT_DIRECTORY_ORGANIZED.md',
        'IMMEDIATE_RAILWAY_FIX_REQUIRED.md',
    ],
    'archive/test-files': [
        'alpine-debug.html',
        'debug-test.html',
        'logo-diagnostic.html',
        'logo-test.html',
        'templates-debug.html',
    ],
    'archive/legacy-configs': [
        'config-secure.js',
        'config.js',
    ],
    'docs/guides': [
        'CRITICAL_RAILWAY_ENVIRONMENT_VARIABLES.md',
    ],
}

def create_directories(base_path):
    """Create necessary directories if they don't exist"""
    for dir_path in FILE_MOVEMENTS.keys():
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"[DIR] Ensured directory exists: {dir_path}")

def move_file_safely(src, dst):
    """Move file with safety checks"""
    try:
        if src.exists():
            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if destination already exists
            if dst.exists():
                print(f"[SKIP] Destination already exists: {dst.name}")
                return False
            
            # Move the file
            shutil.move(str(src), str(dst))
            print(f"[MOVED] {src.name} -> {dst.parent.relative_to(src.parent.parent)}/{dst.name}")
            return True
        else:
            print(f"[NOT FOUND] {src.name}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to move {src.name}: {e}")
        return False

def main():
    """Main organization function"""
    print("Root Directory Organization Script")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    moved_count = 0
    
    # Create necessary directories
    create_directories(project_root)
    
    print("\nMoving files...")
    print("-" * 60)
    
    # Process file movements
    for target_dir, files in FILE_MOVEMENTS.items():
        for file_name in files:
            src = project_root / file_name
            dst = project_root / target_dir / file_name
            
            if move_file_safely(src, dst):
                moved_count += 1
    
    # Move duplicate logos directory if it exists
    root_logos = project_root / 'logos'
    if root_logos.exists() and root_logos.is_dir():
        archive_logos = project_root / 'archive' / 'duplicate-logos'
        if move_file_safely(root_logos, archive_logos):
            print(f"[MOVED] logos directory -> archive/duplicate-logos")
            moved_count += 1
    
    print("\n" + "=" * 60)
    print("ORGANIZATION SUMMARY")
    print("=" * 60)
    print(f"Total files moved: {moved_count}")
    
    # List remaining files in root
    print("\nRemaining files in root directory:")
    remaining_files = []
    for item in project_root.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            remaining_files.append(item.name)
    
    if remaining_files:
        for file in sorted(remaining_files):
            print(f"  - {file}")
    else:
        print("  [Root directory is clean!]")
    
    print("\nCore directories:")
    core_dirs = ['backend', 'frontend', 'threadr-nextjs', 'docs', 'scripts', 'archive']
    for dir_name in core_dirs:
        if (project_root / dir_name).exists():
            print(f"  - {dir_name}/")
    
    print("\nOrganization complete!")

if __name__ == "__main__":
    main()
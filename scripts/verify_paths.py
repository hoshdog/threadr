#!/usr/bin/env python3
"""Verify paths for Railway deployment"""

import os
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def verify_railway_paths():
    """Verify all paths referenced in Railway config"""
    print("🔍 Railway Path Verification")
    print("=" * 60)
    
    # Get repo root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    print(f"📁 Repository root: {repo_root}")
    
    # Check critical files
    critical_files = [
        ("nixpacks.toml", "Railway build configuration"),
        ("railway.json", "Railway override configuration"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/src/main_minimal.py", "Target application file"),
        ("backend/src/main.py", "Old application file"),
        ("backend/src/__init__.py", "Python package marker")
    ]
    
    print("\n📋 File Verification:")
    all_good = True
    
    for filepath, description in critical_files:
        path = Path(filepath)
        exists = path.exists()
        symbol = "✅" if exists else "❌"
        print(f"{symbol} {filepath}")
        print(f"   Purpose: {description}")
        
        if exists and filepath.endswith('.py'):
            size = path.stat().st_size
            print(f"   Size: {size} bytes")
            
        if not exists and "main_minimal.py" in filepath:
            all_good = False
            print("   ⚠️  CRITICAL: Target file missing!")
    
    # Check directory structure
    print("\n📁 Directory Structure:")
    backend_dir = Path("backend")
    if backend_dir.exists():
        print("✅ backend/ directory exists")
        
        src_dir = backend_dir / "src"
        if src_dir.exists():
            print("✅ backend/src/ directory exists")
            
            # List Python files in src
            py_files = list(src_dir.glob("*.py"))
            print(f"   Found {len(py_files)} Python files:")
            for f in py_files[:5]:  # Show first 5
                print(f"   - {f.name}")
        else:
            print("❌ backend/src/ directory missing!")
            all_good = False
    else:
        print("❌ backend/ directory missing!")
        all_good = False
    
    # Verify Railway commands will work
    print("\n🚀 Railway Command Verification:")
    
    # Test pip install path
    req_path = Path("backend/requirements.txt")
    if req_path.exists():
        print("✅ pip install -r backend/requirements.txt → Will work")
    else:
        print("❌ pip install -r backend/requirements.txt → Will fail")
        all_good = False
    
    # Test start command path
    main_path = Path("backend/src/main_minimal.py")
    if main_path.exists():
        print("✅ cd backend && uvicorn src.main_minimal:app → Will work")
    else:
        print("❌ cd backend && uvicorn src.main_minimal:app → Will fail")
        all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All paths verified! Ready for deployment")
        print("\nNext step: git add -A && git commit -m 'Fix Railway paths' && git push")
    else:
        print("❌ Path issues found! Fix before deploying")
        
    return all_good

if __name__ == "__main__":
    verify_railway_paths()
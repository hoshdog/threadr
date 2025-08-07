#!/usr/bin/env python3
"""
Render deployment diagnostic script.
Shows exactly what paths and modules are available during startup.
"""

import os
import sys
from pathlib import Path
import importlib.util

def diagnose_render_environment():
    """Diagnose the Render deployment environment for debugging imports."""
    
    print("="*60)
    print("RENDER DEPLOYMENT DIAGNOSTIC")
    print("="*60)
    
    # Environment information
    print(f"\n[ENV] ENVIRONMENT INFORMATION:")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Script location: {__file__}")
    print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not set')}")
    print(f"   PYTHONPATH: {os.getenv('PYTHONPATH', 'not set')}")
    print(f"   BYPASS_DATABASE: {os.getenv('BYPASS_DATABASE', 'not set')}")
    
    # Python path
    print(f"\n[PATH] PYTHON PATH:")
    for i, path in enumerate(sys.path[:10]):  # Show first 10 entries
        print(f"   [{i}] {path}")
    if len(sys.path) > 10:
        print(f"   ... and {len(sys.path) - 10} more entries")
    
    # Directory structure exploration
    print(f"\n[DIR] DIRECTORY STRUCTURE:")
    
    current_dir = Path(os.getcwd())
    print(f"   Current directory: {current_dir}")
    
    # Look for common structure patterns
    search_paths = [
        current_dir,
        current_dir / "src", 
        current_dir / "backend",
        current_dir / "backend" / "src",
        current_dir.parent,
        current_dir.parent / "src",
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            print(f"   [OK] EXISTS: {search_path}")
            
            # Look for database directory
            db_path = search_path / "database"
            if db_path.exists():
                print(f"      |-- [DIR] database/ directory found")
                config_py = db_path / "config.py"
                if config_py.exists():
                    print(f"          |-- [FILE] config.py found")
                else:
                    print(f"          |-- [MISSING] config.py NOT found")
            else:
                print(f"      |-- [MISSING] database/ directory NOT found")
        else:
            print(f"   [MISSING] NOT EXISTS: {search_path}")
    
    # Test specific module imports
    print(f"\n[IMPORT] MODULE IMPORT TESTS:")
    
    test_imports = [
        "database",
        "database.config", 
        "src.database",
        "src.database.config",
        "backend.src.database.config",
        "backend.database.config"
    ]
    
    for module_name in test_imports:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                print(f"   [OK] {module_name}: {spec.origin}")
            else:
                print(f"   [FAIL] {module_name}: spec found but no origin")
        except (ImportError, ModuleNotFoundError, ValueError):
            print(f"   [FAIL] {module_name}: not found")
        except Exception as e:
            print(f"   [ERROR] {module_name}: error - {e}")
    
    # Look for __init__.py files
    print(f"\n[INIT] __init__.py FILE CHECK:")
    
    init_paths = [
        current_dir / "__init__.py",
        current_dir / "src" / "__init__.py", 
        current_dir / "src" / "database" / "__init__.py",
        current_dir / "database" / "__init__.py",
    ]
    
    for init_path in init_paths:
        if init_path.exists():
            print(f"   [OK] {init_path}")
        else:
            print(f"   [MISSING] {init_path} (missing)")
    
    print(f"\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    diagnose_render_environment()
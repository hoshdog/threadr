#!/usr/bin/env python3
"""
Test script to verify database imports work correctly in Render environment.
This simulates the import patterns used in main.py.
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory and parent directories to Python path (same as main.py)
current_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(current_dir))  # /backend/src
sys.path.insert(0, str(current_dir.parent))  # /backend
sys.path.insert(0, str(current_dir.parent.parent))  # /project_root

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_imports():
    """Test database imports with the same patterns as main.py."""
    
    # Import attempts (same as main.py)
    import_attempts = [
        # Direct import (works in shell/manual commands)
        ("database.config", "database"),
        # Src prefixed (standard structure)
        ("src.database.config", "src.database"), 
        # Absolute path attempts for Render
        ("backend.src.database.config", "backend.src.database"),
        ("backend.database.config", "backend.database")
    ]
    
    init_db = None
    engine = None
    models = None
    
    logger.info("Testing database imports...")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path includes: {sys.path[:5]}")  # Show first 5 entries
    
    for config_path, models_path in import_attempts:
        try:
            logger.info(f"Attempting database import: {config_path}")
            config_module = __import__(config_path, fromlist=['init_db', 'engine'])
            models_module = __import__(models_path, fromlist=['models'])
            
            init_db = getattr(config_module, 'init_db', None)
            engine = getattr(config_module, 'engine', None)
            models = models_module
            
            if init_db and engine:
                logger.info(f"[SUCCESS] Database imports work from: {config_path}")
                logger.info(f"   - init_db: {type(init_db)}")
                logger.info(f"   - engine: {type(engine)}")
                logger.info(f"   - models module: {models}")
                return True
            else:
                logger.warning(f"[PARTIAL] Partial success for {config_path}: missing components")
                
        except ImportError as e:
            logger.debug(f"[FAIL] Import attempt failed for {config_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error for {config_path}: {e}")
            continue
    
    logger.error("[FAILED] Could not import database components from any path")
    return False

if __name__ == "__main__":
    success = test_database_imports()
    
    if success:
        print("\n[SUCCESS] DATABASE IMPORTS TEST PASSED")
        print("The import patterns in main.py should work correctly.")
    else:
        print("\n[FAILED] DATABASE IMPORTS TEST FAILED") 
        print("There may be issues with the module structure or import paths.")
        
    # Also test BYPASS_DATABASE setting
    bypass = os.getenv("BYPASS_DATABASE", "false").lower() == "true"
    print(f"\n[CONFIG] BYPASS_DATABASE setting: {bypass}")
    if bypass:
        print("   Database initialization will be skipped.")
    else:
        print("   Database initialization will be attempted.")
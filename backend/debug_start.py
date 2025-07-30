#!/usr/bin/env python3
"""
Debug startup script for Railway deployment issues
This script helps identify common deployment problems
"""

import os
import sys
import logging
import traceback
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - DEBUG - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables and configuration"""
    logger.info("=== ENVIRONMENT CHECK ===")
    
    # Check critical environment variables
    critical_vars = ["PORT", "ENVIRONMENT"]
    optional_vars = ["OPENAI_API_KEY", "CORS_ORIGINS"]
    
    for var in critical_vars:
        value = os.getenv(var)
        logger.info(f"{var}: {value if value else 'NOT SET'}")
        if not value:
            logger.warning(f"Critical variable {var} is not set!")
    
    for var in optional_vars:
        value = os.getenv(var)
        logger.info(f"{var}: {'SET' if value else 'NOT SET'}")
    
    # Check port
    port = os.getenv("PORT")
    if port:
        try:
            port_num = int(port)
            logger.info(f"Port parsed successfully: {port_num}")
        except ValueError:
            logger.error(f"Invalid PORT value: {port}")
    
    logger.info("=== END ENVIRONMENT CHECK ===\n")

def check_dependencies():
    """Check if all required packages are available"""
    logger.info("=== DEPENDENCY CHECK ===")
    
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "httpx", 
        "beautifulsoup4", "openai"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package}: Available")
        except ImportError as e:
            logger.error(f"✗ {package}: NOT AVAILABLE - {e}")
    
    logger.info("=== END DEPENDENCY CHECK ===\n")

def test_app_import():
    """Test if the main app can be imported without errors"""
    logger.info("=== APP IMPORT TEST ===")
    
    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try to import the app
        from main import app
        logger.info("✓ App imported successfully")
        
        # Check if app is a FastAPI instance
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            logger.info("✓ App is a valid FastAPI instance")
        else:
            logger.error("✗ App is not a FastAPI instance")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to import app: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    
    finally:
        logger.info("=== END APP IMPORT TEST ===\n")

def test_health_endpoint():
    """Test the health endpoint"""
    logger.info("=== HEALTH ENDPOINT TEST ===")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        logger.info(f"Health endpoint status: {response.status_code}")
        logger.info(f"Health endpoint response: {response.json()}")
        
        if response.status_code == 200:
            logger.info("✓ Health endpoint is working")
            return True
        else:
            logger.error(f"✗ Health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Health endpoint test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    
    finally:
        logger.info("=== END HEALTH ENDPOINT TEST ===\n")

def main():
    """Run all diagnostic checks"""
    logger.info(f"Starting Railway deployment debug at {datetime.now().isoformat()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("")
    
    # Run all checks
    check_environment()
    check_dependencies()
    
    app_imported = test_app_import()
    if app_imported:
        test_health_endpoint()
    
    logger.info("=== SUMMARY ===")
    logger.info("If all checks passed, your app should start successfully.")
    logger.info("If any checks failed, fix those issues before deploying.")
    logger.info("===============")

if __name__ == "__main__":
    main()
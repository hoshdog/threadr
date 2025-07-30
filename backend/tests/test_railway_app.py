#!/usr/bin/env python3
"""
Minimal Railway-compatible FastAPI test app for debugging deployment issues.

This is a bare-bones FastAPI application to verify that basic Railway deployment works.
Use this to isolate deployment issues from application complexity.
"""

import os
import sys
import logging
from datetime import datetime
from fastapi import FastAPI
import uvicorn

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create minimal FastAPI app
app = FastAPI(
    title="Railway Test App",
    description="Minimal FastAPI app to test Railway deployment",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint - basic functionality test"""
    return {
        "message": "Railway FastAPI Test App is running!",
        "timestamp": datetime.now().isoformat(),
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "not_set"),
        "python_version": sys.version
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check environment"""
    return {
        "timestamp": datetime.now().isoformat(),
        "environment_variables": {
            "PORT": os.getenv("PORT", "not_set"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "not_set"),
            "PYTHONPATH": os.getenv("PYTHONPATH", "not_set"),
            "PWD": os.getenv("PWD", "not_set"),
        },
        "system_info": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "process_id": os.getpid(),
            "python_executable": sys.executable,
            "python_path": sys.path[:5]  # First 5 entries only
        },
        "request_info": {
            "app_name": app.title,
            "app_version": app.version
        }
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Test endpoint working",
        "timestamp": datetime.now().isoformat(),
        "test_data": {
            "string": "Hello Railway!",
            "number": 42,
            "boolean": True,
            "array": [1, 2, 3, "test"]
        }
    }

# Main execution
if __name__ == "__main__":
    # Get port from environment
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting Railway Test App on port {port}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Run with uvicorn
    uvicorn.run(
        "test_railway_app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
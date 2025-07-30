"""
Minimal FastAPI app for Railway deployment testing
Use this if the main app fails to deploy
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from datetime import datetime

# Create minimal app
app = FastAPI(
    title="Threadr API - Minimal Version",
    description="Minimal version for deployment testing",
    version="0.1.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Threadr API - Minimal Version",
        "status": "working",
        "port": os.getenv("PORT", "not_set"),
        "environment": os.getenv("ENVIRONMENT", "not_set"),
        "python_version": sys.version,
        "working_directory": os.getcwd()
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "port": os.getenv("PORT", "not_set"),
        "environment": os.getenv("ENVIRONMENT", "not_set")
    }

@app.get("/test")
def test_endpoint():
    """Test endpoint to verify deployment"""
    return {
        "status": "test_passed",
        "message": "Railway deployment is working",
        "environment_variables": {
            "PORT": os.getenv("PORT"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT"),
            "PYTHONPATH": os.getenv("PYTHONPATH"),
        },
        "system_info": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "python_path": sys.path[:3]  # Show first 3 entries
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
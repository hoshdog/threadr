"""
Ultra-minimal FastAPI test for Railway deployment
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")
logger.info(f"PORT environment variable: {os.getenv('PORT', 'NOT_SET')}")

# Test imports
try:
    from fastapi import FastAPI
    logger.info("✓ FastAPI import successful")
except ImportError as e:
    logger.error(f"✗ FastAPI import failed: {e}")

try:
    from fastapi.middleware.cors import CORSMiddleware
    logger.info("✓ CORS middleware import successful")
except ImportError as e:
    logger.error(f"✗ CORS middleware import failed: {e}")

# Create minimal app
app = FastAPI(title="Railway Deployment Test")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://threadr-plum.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Railway deployment test successful!",
        "port": os.getenv("PORT", "unknown"),
        "cwd": os.getcwd(),
        "python_path": sys.path[:3]  # First 3 entries
    }

@app.get("/health")
def health():
    return {"status": "healthy", "deployment": "test"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting uvicorn on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
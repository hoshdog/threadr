"""
Minimal FastAPI test to debug Railway deployment issues
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal FastAPI app
app = FastAPI(
    title="Threadr API - Minimal Test",
    description="Minimal test version for debugging",
    version="1.0.0"
)

# Add CORS
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    allowed_origins = [
        "https://threadr-plum.vercel.app",
        "https://threadr.vercel.app",
    ]
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Threadr API is running (minimal test version)", "status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "threadr-api",
        "version": "1.0.0-minimal",
        "environment": ENVIRONMENT
    }

@app.get("/readiness")
async def readiness():
    """Readiness probe for Kubernetes"""
    return {
        "status": "ready",
        "service": "threadr-api",
        "checks": {
            "app": "ok"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
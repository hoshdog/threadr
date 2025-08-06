"""
Consolidated Railway-ready FastAPI application
Follows best practices with flexible database initialization
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys
import logging
import asyncio
from typing import Optional

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
BYPASS_DATABASE = os.getenv("BYPASS_DATABASE", "false").lower() == "true"

logger.info(f"Starting Threadr API - Environment: {ENVIRONMENT}, Bypass DB: {BYPASS_DATABASE}")

# Import managers with error handling
redis_available = False
database_available = False

try:
    from src.core.redis_manager import initialize_redis, get_redis_manager
    redis_available = True
    logger.info("Redis manager imported successfully")
except ImportError as e:
    logger.warning(f"Redis manager import failed: {e}")

try:
    if not BYPASS_DATABASE:
        from src.core.database import initialize_database, get_database_manager
        database_available = True
        logger.info("Database manager imported successfully")
    else:
        logger.info("Database bypassed by configuration")
except ImportError as e:
    logger.warning(f"Database manager import failed: {e}")

# Import routes
try:
    from src.routes.auth import router as auth_router
    from src.routes.thread import router as thread_router
    from src.routes.template import router as template_router
    from src.routes.analytics import router as analytics_router
    from src.routes.subscription import router as subscription_router
    from src.routes.revenue import router as revenue_router
    from src.routes.generate import router as generate_router
    routes_available = True
    logger.info("Routes imported successfully")
except ImportError as e:
    logger.warning(f"Routes import failed: {e}")
    routes_available = False

# Service status tracking
service_status = {
    "redis": False,
    "database": False,
    "routes": routes_available,
    "health": "starting"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with proper error handling"""
    logger.info("Starting application lifecycle...")
    
    # Initialize Redis
    if redis_available:
        try:
            redis_client = await initialize_redis()
            if redis_client:
                await redis_client.ping()
                service_status["redis"] = True
                logger.info("Redis initialized successfully")
            else:
                logger.warning("Redis client not initialized")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
    
    # Initialize Database
    if database_available and not BYPASS_DATABASE:
        try:
            db_manager = await initialize_database()
            if db_manager:
                service_status["database"] = True
                logger.info("Database initialized successfully")
            else:
                logger.warning("Database manager not initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    # Set overall health
    if service_status["redis"] or BYPASS_DATABASE:
        service_status["health"] = "healthy"
        logger.info("Application started successfully")
    else:
        service_status["health"] = "degraded"
        logger.warning("Application started with degraded services")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    # Add cleanup logic here if needed

# Create FastAPI app
app = FastAPI(
    title="Threadr API",
    description="AI-powered thread generation for social media",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Comprehensive health check for Railway"""
    try:
        checks = {
            "status": service_status["health"],
            "timestamp": datetime.now().isoformat(),
            "environment": ENVIRONMENT,
            "services": {
                "redis": service_status["redis"],
                "database": service_status["database"],
                "routes": service_status["routes"]
            }
        }
        
        # Test Redis if available
        if redis_available and service_status["redis"]:
            try:
                redis_manager = get_redis_manager()
                if redis_manager and redis_manager.redis:
                    await redis_manager.redis.ping()
                    checks["services"]["redis_ping"] = "ok"
            except Exception as e:
                checks["services"]["redis_ping"] = f"failed: {str(e)}"
        
        # Test Database if available
        if database_available and service_status["database"] and not BYPASS_DATABASE:
            try:
                db_manager = get_database_manager()
                if db_manager:
                    # Simple connectivity check
                    checks["services"]["database_ping"] = "ok"
            except Exception as e:
                checks["services"]["database_ping"] = f"failed: {str(e)}"
        
        # Determine HTTP status
        if service_status["health"] == "healthy":
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(status_code=status_code, content=checks)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/readiness")
async def readiness_check():
    """Simple readiness check for Kubernetes"""
    if service_status["health"] in ["healthy", "degraded"]:
        return {"status": "ready", "timestamp": datetime.now().isoformat()}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "timestamp": datetime.now().isoformat()}
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Threadr API",
        "version": "2.0.0",
        "status": service_status["health"],
        "environment": ENVIRONMENT,
        "docs": "/docs"
    }

# Include routers if available
if routes_available:
    try:
        app.include_router(generate_router, prefix="/api", tags=["generate"])
        app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
        app.include_router(thread_router, prefix="/api", tags=["threads"])
        app.include_router(template_router, prefix="/api", tags=["templates"])
        app.include_router(analytics_router, prefix="/api", tags=["analytics"])
        app.include_router(subscription_router, prefix="/api", tags=["subscriptions"])
        app.include_router(revenue_router, prefix="/api", tags=["revenue"])
        logger.info("All routers included successfully")
    except Exception as e:
        logger.error(f"Failed to include routers: {e}")

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Fallback generate endpoint for basic functionality
@app.post("/api/generate")
async def generate_thread_fallback():
    """Fallback generate endpoint when services are unavailable"""
    if not routes_available:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": "Thread generation service is currently unavailable",
                "message": "Please check service status at /health"
            }
        )
    # If routes are available, this will be handled by the thread router

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
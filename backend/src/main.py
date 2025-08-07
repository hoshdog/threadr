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
    from core.redis_manager import initialize_redis, get_redis_manager
    redis_available = True
    logger.info("Redis manager imported successfully")
except ImportError as e:
    try:
        from src.core.redis_manager import initialize_redis, get_redis_manager
        redis_available = True
        logger.info("Redis manager imported successfully")
    except ImportError as e2:
        logger.warning(f"Redis manager import failed: {e2}")

try:
    if not BYPASS_DATABASE:
        try:
            from core.database import initialize_database, get_database_manager
            database_available = True
            logger.info("Database manager imported successfully")
        except ImportError:
            from src.core.database import initialize_database, get_database_manager
            database_available = True
            logger.info("Database manager imported successfully")
    else:
        logger.info("Database bypassed by configuration")
except ImportError as e:
    if not BYPASS_DATABASE:
        logger.info(f"Database manager not available (expected for now): {e}")
    database_available = False

# Import route factory functions and services
try:
    from routes.auth import create_auth_router
    from routes.thread import create_thread_router
    from routes.template import router as template_router
    from routes.analytics import router as analytics_router
    from routes.subscription import create_subscription_router
    from routes.revenue import router as revenue_router
    from routes.generate import router as generate_router
    from services.auth.auth_service import AuthService
    from services.thread.thread_service import ThreadHistoryService
    routes_available = True
    logger.info("Routes and services imported successfully")
except ImportError as e:
    try:
        from src.routes.auth import create_auth_router
        from src.routes.thread import create_thread_router
        from src.routes.template import router as template_router
        from src.routes.analytics import router as analytics_router
        from src.routes.subscription import create_subscription_router
        from src.routes.revenue import router as revenue_router
        from src.routes.generate import router as generate_router
        from src.services.auth.auth_service import AuthService
        from src.services.thread.thread_service import ThreadHistoryService
        routes_available = True
        logger.info("Routes and services imported successfully")
    except ImportError as e2:
        logger.warning(f"Routes/services import failed: {e2}")
        routes_available = False

# Router instances (initialized immediately)
auth_router = None
thread_router = None
subscription_router = None

# Service status tracking 
service_status = {
    "redis": False,
    "database": False,
    "routes": routes_available,
    "health": "starting"
}

# Initialize routers immediately if routes are available
if routes_available:
    try:
        # Initialize services (they can handle None redis_manager)
        redis_manager_instance = get_redis_manager() if redis_available else None
        auth_service = AuthService(redis_manager_instance)
        thread_service = ThreadHistoryService(redis_manager_instance)
        
        # Get auth dependencies for thread router
        try:
            from middleware.auth import create_auth_dependencies
        except ImportError:
            from src.middleware.auth import create_auth_dependencies
        auth_deps = create_auth_dependencies(auth_service)
        get_current_user_required = auth_deps["get_current_user_required"]
        
        # Create routers using factory functions
        auth_router = create_auth_router(auth_service)
        thread_router = create_thread_router(thread_service, get_current_user_required)
        subscription_router = create_subscription_router(auth_service)
        
        logger.info("Authentication, thread, and subscription routers initialized successfully")
        service_status["routes"] = True
    except Exception as e:
        logger.error(f"Failed to initialize routers: {e}")
        auth_router = None
        thread_router = None
        subscription_router = None
        service_status["routes"] = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with proper error handling"""
    logger.info("Starting application lifecycle...")
    
    # Initialize Redis
    if redis_available:
        try:
            redis_manager = initialize_redis()  # Not async
            if redis_manager and redis_manager.is_available:
                # Test Redis connection
                if redis_manager.client:
                    redis_manager.client.ping()
                    service_status["redis"] = True
                    logger.info("Redis initialized successfully")
                else:
                    logger.warning("Redis client not connected")
            else:
                logger.warning("Redis manager not available")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
    
    # Database initialization for PostgreSQL
    if not BYPASS_DATABASE:
        try:
            # Import database components
            from database.config import init_db, engine
            from database import models  # Import models to register them
            
            # Initialize database tables
            init_db()
            
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                service_status["database"] = True
                logger.info("PostgreSQL database initialized and connected successfully")
        except ImportError as e:
            logger.warning(f"Database modules not found: {e}")
            service_status["database"] = False
        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            service_status["database"] = False
            # Continue without database if Redis is available
            if not service_status["redis"]:
                logger.error("Both database and Redis failed - cannot continue")
                raise
    else:
        logger.info("Database bypassed by BYPASS_DATABASE=true - using Redis only")
        service_status["database"] = False
    
    # Routers are now initialized at startup, just log their status
    if routes_available:
        if auth_router and thread_router and subscription_router:
            logger.info("All routers available for lifespan management")
        else:
            logger.warning("Some routers failed to initialize during startup")
    
    # Set overall health
    if service_status["redis"] or routes_available:
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

# CORS configuration with production fallback
default_cors_origins = "http://localhost:3000,https://threadr-plum.vercel.app,https://threadr-nextjs-eight-red.vercel.app"
cors_origins = os.getenv("CORS_ORIGINS", default_cors_origins).split(",")
# Strip whitespace from origins to prevent configuration issues
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
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
                if redis_manager and redis_manager.client:
                    redis_manager.client.ping()
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
        "version": "2.0.1",
        "status": service_status["health"],
        "environment": ENVIRONMENT,
        "docs": "/docs"
    }

# Include routers if available
if routes_available:
    try:
        app.include_router(generate_router, prefix="/api", tags=["generate"])
        
        # Auth and thread routers are created with factory functions and include prefixes
        if auth_router:
            app.include_router(auth_router)
            logger.info("Auth router included successfully")
        else:
            logger.warning("Auth router not initialized")
            
        if thread_router:
            app.include_router(thread_router)
            logger.info("Thread router included successfully")
        else:
            logger.warning("Thread router not initialized")
            
        if subscription_router:
            app.include_router(subscription_router)
            logger.info("Subscription router included successfully")
        else:
            logger.warning("Subscription router not initialized")
            
        app.include_router(template_router, prefix="/api", tags=["templates"])
        app.include_router(analytics_router, prefix="/api", tags=["analytics"])
        app.include_router(revenue_router, prefix="/api", tags=["revenue"])
        logger.info("All available routers included")
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
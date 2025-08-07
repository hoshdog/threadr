"""
Database configuration for PostgreSQL with SQLAlchemy.
Production-ready with connection pooling and monitoring.
"""

import os
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Database URLs from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://threadr_user:password@localhost/threadr_db"
)

# Convert postgres:// to postgresql:// for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Async database URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Database configuration
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# Create engines with production settings
engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using
    echo=DB_ECHO,
    connect_args={
        "connect_timeout": 10,
        "application_name": "threadr_backend",
        "options": "-c statement_timeout=30000"  # 30 second statement timeout
    }
)

# Async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=DB_ECHO,
    connect_args={
        "server_settings": {
            "application_name": "threadr_backend_async"
        },
        "command_timeout": 30
    }
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Connection pool monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log new connections and set connection parameters."""
    connection_record.info['pid'] = os.getpid()
    logger.debug(f"New database connection established: PID={os.getpid()}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Monitor connection checkouts from pool."""
    pid = os.getpid()
    if connection_record.info.get('pid') != pid:
        connection_record.dbapi_connection = None
        logger.warning(f"Connection record PID mismatch, invalidating connection")

# Dependency injection for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency for getting database session.
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

# Context managers for manual session handling
@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@asynccontextmanager
async def get_async_db_session():
    """Async context manager for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Database health check
async def check_database_health() -> dict:
    """
    Check database connectivity and pool status.
    Returns health status dictionary.
    """
    try:
        # Check sync connection
        with get_db_session() as db:
            db.execute("SELECT 1")
        
        # Check async connection
        async with get_async_db_session() as db:
            await db.execute("SELECT 1")
        
        # Get pool statistics
        pool_status = engine.pool.status()
        
        return {
            "status": "healthy",
            "pool_size": engine.pool.size(),
            "checked_in_connections": engine.pool.checkedin(),
            "overflow": engine.pool.overflow(),
            "total": engine.pool.checkedout(),
            "pool_status": pool_status
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Initialize database tables
def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

async def init_async_db():
    """Create all database tables asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully (async)")

# Cleanup function for graceful shutdown
def close_db():
    """Close all database connections."""
    engine.dispose()
    logger.info("Database connections closed")

async def close_async_db():
    """Close all async database connections."""
    await async_engine.dispose()
    logger.info("Async database connections closed")
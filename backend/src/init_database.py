#!/usr/bin/env python3
"""
Initialize PostgreSQL database for Threadr.
Run this script to create all database tables.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables."""
    try:
        # Import database components
        logger.info("Importing database components...")
        from database.config import engine, Base, DATABASE_URL
        from database import models  # Import all models to register them
        
        # Log connection details (without password)
        db_url_safe = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configuration error'
        logger.info(f"Connecting to database: ...@{db_url_safe}")
        
        # Test connection first
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✅ Database connection successful!")
            
            # Get PostgreSQL version
            version = conn.execute("SELECT version()").scalar()
            logger.info(f"PostgreSQL version: {version.split(',')[0]}")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        with engine.connect() as conn:
            # Check what tables were created
            result = conn.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename;
            """)
            tables = [row[0] for row in result]
            
            logger.info(f"✅ Successfully created {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table}")
        
        # Create required indexes if not exists
        logger.info("Ensuring indexes are created...")
        with engine.connect() as conn:
            # Add any custom indexes here if needed
            pass
        
        logger.info("=" * 50)
        logger.info("✅ DATABASE INITIALIZATION COMPLETE!")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Provide helpful error messages
        if "could not connect to server" in str(e):
            logger.error("Cannot connect to database. Please check:")
            logger.error("1. DATABASE_URL environment variable is set correctly")
            logger.error("2. PostgreSQL service is running on Render")
            logger.error("3. You're using the Internal Database URL")
        elif "password authentication failed" in str(e):
            logger.error("Authentication failed. Please check:")
            logger.error("1. DATABASE_URL has the correct password")
            logger.error("2. Copy the Internal Database URL from Render dashboard")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            logger.error("Database does not exist. Please check:")
            logger.error("1. Database name in DATABASE_URL is correct")
            logger.error("2. Database was created on Render")
        
        return False

if __name__ == "__main__":
    logger.info("Starting Threadr database initialization...")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        logger.error("❌ DATABASE_URL environment variable not set!")
        logger.error("Please set it in Render environment variables")
        sys.exit(1)
    
    # Check if we should bypass database
    if os.getenv("BYPASS_DATABASE", "false").lower() == "true":
        logger.warning("⚠️ BYPASS_DATABASE is set to true!")
        logger.warning("Database will not be used. Set BYPASS_DATABASE=false to enable PostgreSQL")
        sys.exit(1)
    
    # Run initialization
    success = init_database()
    sys.exit(0 if success else 1)
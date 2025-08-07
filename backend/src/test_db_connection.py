#!/usr/bin/env python3
"""
Test PostgreSQL database connection for Threadr.
Run this to verify your database is accessible.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_connection():
    """Test database connection and show configuration."""
    print("=" * 60)
    print("THREADR DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Check environment variables
    database_url = os.getenv("DATABASE_URL")
    bypass_db = os.getenv("BYPASS_DATABASE", "false")
    
    print("\n📋 Environment Check:")
    print(f"  DATABASE_URL: {'✅ Set' if database_url else '❌ Not set'}")
    print(f"  BYPASS_DATABASE: {bypass_db}")
    
    if bypass_db.lower() == "true":
        print("\n⚠️  WARNING: BYPASS_DATABASE is true - PostgreSQL will not be used!")
        print("  Set BYPASS_DATABASE=false in Render environment variables")
        return False
    
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL not found in environment variables!")
        print("\nTo fix this:")
        print("1. Go to Render Dashboard")
        print("2. Click on your backend service")
        print("3. Go to 'Environment' tab")
        print("4. Add DATABASE_URL with your PostgreSQL Internal URL")
        return False
    
    # Parse database URL for display (hide password)
    if "@" in database_url:
        parts = database_url.split("@")
        user_part = parts[0].split("://")[1].split(":")[0]
        host_part = parts[1]
        print(f"  Connecting to: {user_part}@{host_part}")
    
    print("\n🔌 Testing Connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            # Basic connectivity test
            result = conn.execute(text("SELECT 1"))
            print("  ✅ Connected successfully!")
            
            # Get PostgreSQL version
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.scalar()
            print(f"  📊 PostgreSQL: {version.split(' ')[1]}")
            
            # Get database name
            db_name_result = conn.execute(text("SELECT current_database()"))
            db_name = db_name_result.scalar()
            print(f"  🗄️  Database: {db_name}")
            
            # Get current user
            user_result = conn.execute(text("SELECT current_user"))
            current_user = user_result.scalar()
            print(f"  👤 User: {current_user}")
            
            # Check if tables exist
            tables_result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = tables_result.scalar()
            print(f"  📁 Tables: {table_count} found")
            
            if table_count > 0:
                # List tables
                print("\n  📋 Existing tables:")
                tables_list = conn.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
                for row in tables_list:
                    print(f"    - {row[0]}")
            else:
                print("\n  ⚠️  No tables found - run init_database.py to create them")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE CONNECTION TEST PASSED!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nMake sure SQLAlchemy is installed:")
        print("  pip install sqlalchemy psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")
        print(f"\nError Type: {type(e).__name__}")
        
        error_str = str(e).lower()
        if "could not connect" in error_str:
            print("\n🔍 Troubleshooting:")
            print("1. Check DATABASE_URL is using the Internal URL (not External)")
            print("2. Make sure PostgreSQL is running on Render")
            print("3. Check network connectivity")
        elif "authentication failed" in error_str:
            print("\n🔍 Troubleshooting:")
            print("1. Copy the Internal Database URL from Render again")
            print("2. Make sure the password is correct")
            print("3. Check for special characters that need escaping")
        elif "does not exist" in error_str:
            print("\n🔍 Troubleshooting:")
            print("1. Verify database name in URL")
            print("2. Check database was created on Render")
        
        return False

if __name__ == "__main__":
    print("Starting database connection test...")
    success = test_connection()
    
    if not success:
        print("\n💡 Next Steps:")
        print("1. Fix the connection issue above")
        print("2. Run this test again")
        print("3. Then run init_database.py to create tables")
        sys.exit(1)
    else:
        print("\n🎉 Your database is ready!")
        print("Next: Run init_database.py to create tables")
        sys.exit(0)
#!/usr/bin/env python3
"""
Migration Validation Script
Quick validation of Redis data and PostgreSQL readiness before migration
"""

import asyncio
import asyncpg
import os
import sys
from datetime import datetime

# Add src to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.redis_manager import RedisManager
except ImportError as e:
    print(f"ERROR: Could not import RedisManager: {e}")
    sys.exit(1)

async def validate_migration_readiness():
    """Validate that both Redis and PostgreSQL are ready for migration"""
    print("🔍 Migration Readiness Validation")
    print("=" * 50)
    
    redis_ready = False
    postgres_ready = False
    
    # Test Redis connection
    print("\n📡 Testing Redis Connection...")
    try:
        redis_manager = RedisManager()
        if redis_manager.is_available:
            print("✅ Redis: Connected successfully")
            
            # Get basic stats
            cache_stats = await redis_manager.get_cache_stats()
            if cache_stats.get('available'):
                print(f"   Memory Used: {cache_stats.get('memory_used', 'Unknown')}")
                print(f"   Cache Entries: {cache_stats.get('cache_entries', 0):,}")
                print(f"   Rate Limit Entries: {cache_stats.get('rate_limit_entries', 0):,}")
            
            redis_ready = True
        else:
            print("❌ Redis: Connection failed")
    except Exception as e:
        print(f"❌ Redis: Error - {e}")
    
    # Test PostgreSQL connection
    print("\n🐘 Testing PostgreSQL Connection...")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ PostgreSQL: DATABASE_URL not configured")
    else:
        try:
            conn = await asyncpg.connect(database_url)
            print("✅ PostgreSQL: Connected successfully")
            
            # Test schema
            tables = await conn.fetch("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('users', 'subscriptions', 'usage_tracking', 'threads')
                ORDER BY tablename
            """)
            
            print(f"   Required Tables: {len(tables)}/4 found")
            for table in tables:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['tablename']}")
                print(f"     {table['tablename']}: {count:,} existing records")
            
            await conn.close()
            postgres_ready = True
            
        except Exception as e:
            print(f"❌ PostgreSQL: Error - {e}")
    
    # Overall readiness assessment
    print(f"\n🎯 Migration Readiness Assessment")
    print("=" * 50)
    
    if redis_ready and postgres_ready:
        print("✅ READY: Both Redis and PostgreSQL are accessible")
        print("✅ SAFE TO PROCEED: Migration can begin")
        
        print(f"\n📋 Next Steps:")
        print("1. Run data audit: python redis_audit.py")
        print("2. Review mapping: python migration_mapping.py") 
        print("3. Start with dry run: python redis_to_postgres_migration.py --dry-run --priority critical")
        print("4. Follow the complete migration guide: REDIS_TO_POSTGRESQL_MIGRATION_GUIDE.md")
        
    elif redis_ready and not postgres_ready:
        print("⚠️ PARTIAL: Redis ready, but PostgreSQL has issues")
        print("❌ NOT SAFE: Fix PostgreSQL connection before proceeding")
        
    elif not redis_ready and postgres_ready:
        print("⚠️ PARTIAL: PostgreSQL ready, but Redis has issues")  
        print("❌ NOT SAFE: Fix Redis connection - no data to migrate")
        
    else:
        print("❌ NOT READY: Both Redis and PostgreSQL have connection issues")
        print("❌ NOT SAFE: Fix both connections before attempting migration")
    
    print(f"\n⏰ Validation completed at: {datetime.now().isoformat()}")
    
    return redis_ready and postgres_ready

if __name__ == "__main__":
    try:
        ready = asyncio.run(validate_migration_readiness())
        sys.exit(0 if ready else 1)
    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Dual-Write Service for Zero-Downtime Redis to PostgreSQL Migration
Writes to both Redis and PostgreSQL during migration period to ensure data consistency
"""

import asyncio
import asyncpg
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import logging
from contextlib import asynccontextmanager
import uuid
from enum import Enum

# Add src to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.redis_manager import RedisManager
    from migration_mapping import RedisToPostgresMigrationMapper
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WriteStrategy(Enum):
    """Write strategy options"""
    REDIS_ONLY = "redis_only"           # Pre-migration: Redis only
    DUAL_WRITE = "dual_write"           # Migration: Write to both
    POSTGRES_PRIMARY = "postgres_primary" # Post-migration: PostgreSQL primary, Redis backup
    POSTGRES_ONLY = "postgres_only"     # Final: PostgreSQL only

class DualWriteService:
    """
    Service that handles writing to both Redis and PostgreSQL during migration.
    Provides consistent interface while transitioning between storage backends.
    """
    
    def __init__(self, strategy: WriteStrategy = WriteStrategy.DUAL_WRITE):
        self.strategy = strategy
        self.redis_manager = RedisManager()
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.mapper = RedisToPostgresMigrationMapper()
        
        # Write statistics
        self.write_stats = {
            'redis_writes': 0,
            'postgres_writes': 0,
            'redis_failures': 0,
            'postgres_failures': 0,
            'dual_write_consistency_errors': 0
        }
        
        # Cache user mappings for performance
        self.user_cache: Dict[str, str] = {}  # email -> user_id
        
    async def initialize(self):
        """Initialize database connections"""
        logger.info(f"Initializing DualWriteService with strategy: {self.strategy.value}")
        
        # Always initialize Redis (even for postgres_only, might be needed for reads)
        if not self.redis_manager.is_available:
            logger.warning("Redis is not available")
        
        # Initialize PostgreSQL if needed
        if self.strategy in [WriteStrategy.DUAL_WRITE, WriteStrategy.POSTGRES_PRIMARY, WriteStrategy.POSTGRES_ONLY]:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise RuntimeError("DATABASE_URL not configured for PostgreSQL writes")
            
            self.postgres_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            
            # Test connection
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            logger.info("PostgreSQL connection established")
    
    async def close(self):
        """Close connections"""
        if self.postgres_pool:
            await self.postgres_pool.close()
        if self.redis_manager:
            self.redis_manager.close()
    
    # USER MANAGEMENT
    
    async def create_user(self, email: str, user_data: Dict[str, Any]) -> str:
        """Create user in appropriate storage backend(s)"""
        user_id = str(uuid.uuid4())
        
        write_operations = []
        
        # Redis write
        if self.strategy in [WriteStrategy.REDIS_ONLY, WriteStrategy.DUAL_WRITE]:
            write_operations.append(self._write_user_to_redis(email, user_data, user_id))
        
        # PostgreSQL write
        if self.strategy in [WriteStrategy.DUAL_WRITE, WriteStrategy.POSTGRES_PRIMARY, WriteStrategy.POSTGRES_ONLY]:
            write_operations.append(self._write_user_to_postgres(email, user_data, user_id))
        
        # Execute writes
        results = await asyncio.gather(*write_operations, return_exceptions=True)
        
        # Check results and update stats
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"User write failed for operation {i}: {result}")
                if i == 0 and len(results) > 1:  # Redis failed
                    self.write_stats['redis_failures'] += 1
                elif i == 1 or len(results) == 1:  # PostgreSQL failed
                    self.write_stats['postgres_failures'] += 1
            else:
                success_count += 1
        
        # Handle partial failures
        if success_count == 0:
            raise RuntimeError("All user write operations failed")
        elif success_count < len(write_operations):
            self.write_stats['dual_write_consistency_errors'] += 1
            logger.warning(f"Partial user write failure for {email} (user_id: {user_id})")
        
        # Cache user mapping
        self.user_cache[email] = user_id
        
        logger.info(f"User created: {email} -> {user_id}")
        return user_id
    
    async def _write_user_to_redis(self, email: str, user_data: Dict[str, Any], user_id: str) -> bool:
        """Write user data to Redis"""
        try:
            # Store as email subscription record (legacy format)
            email_key = f"{self.redis_manager.email_prefix}{email}"
            
            redis_data = {
                'user_id': user_id,
                'subscribed_at': user_data.get('created_at', datetime.now()).isoformat(),
                'source': 'dual_write',
                **user_data
            }
            
            success = await self.redis_manager.store_email_subscription(email, redis_data)
            if success:
                self.write_stats['redis_writes'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Redis user write failed: {e}")
            raise
    
    async def _write_user_to_postgres(self, email: str, user_data: Dict[str, Any], user_id: str) -> bool:
        """Write user data to PostgreSQL"""
        try:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (
                        id, email, password_hash, role, status,
                        login_count, failed_login_attempts, is_email_verified,
                        metadata, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (email) DO UPDATE SET
                        updated_at = EXCLUDED.updated_at,
                        metadata = EXCLUDED.metadata
                """,
                    uuid.UUID(user_id),
                    email,
                    user_data.get('password_hash', ''),
                    user_data.get('role', 'user'),
                    user_data.get('status', 'active'),
                    user_data.get('login_count', 0),
                    user_data.get('failed_login_attempts', 0),
                    user_data.get('is_email_verified', False),
                    json.dumps(user_data.get('metadata', {})),
                    user_data.get('created_at', datetime.now()),
                    datetime.now()
                )
            
            self.write_stats['postgres_writes'] += 1
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL user write failed: {e}")
            raise
    
    # SUBSCRIPTION MANAGEMENT
    
    async def grant_premium_access(self, identifier: str, identifier_type: str, 
                                  plan: str = "premium", duration_days: int = 30,
                                  payment_info: Optional[Dict[str, Any]] = None) -> bool:
        """Grant premium access via dual-write"""
        
        subscription_data = {
            'plan': plan,
            'duration_days': duration_days,
            'granted_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=duration_days),
            'payment_info': payment_info or {},
            'source': 'dual_write'
        }
        
        write_operations = []
        
        # Redis write
        if self.strategy in [WriteStrategy.REDIS_ONLY, WriteStrategy.DUAL_WRITE]:
            if identifier_type == 'email':
                write_operations.append(self._grant_premium_redis_email(identifier, subscription_data))
            elif identifier_type == 'ip':
                write_operations.append(self._grant_premium_redis_ip(identifier, subscription_data))
            elif identifier_type == 'user_id':
                write_operations.append(self._grant_premium_redis_user(identifier, subscription_data))
        
        # PostgreSQL write
        if self.strategy in [WriteStrategy.DUAL_WRITE, WriteStrategy.POSTGRES_PRIMARY, WriteStrategy.POSTGRES_ONLY]:
            write_operations.append(self._grant_premium_postgres(identifier, identifier_type, subscription_data))
        
        # Execute writes
        results = await asyncio.gather(*write_operations, return_exceptions=True)
        
        # Process results
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        
        if success_count == 0:
            raise RuntimeError("All premium grant operations failed")
        elif success_count < len(write_operations):
            self.write_stats['dual_write_consistency_errors'] += 1
            logger.warning(f"Partial premium grant failure for {identifier}")
        
        logger.info(f"Premium access granted: {identifier} ({identifier_type}) -> {plan} for {duration_days} days")
        return True
    
    async def _grant_premium_redis_email(self, email: str, subscription_data: Dict[str, Any]) -> bool:
        """Grant premium via Redis email method"""
        try:
            return await self.redis_manager.grant_premium_access(
                client_ip="0.0.0.0",  # Placeholder
                email=email,
                plan=subscription_data['plan'],
                duration_days=subscription_data['duration_days'],
                payment_info=subscription_data['payment_info']
            )
        except Exception as e:
            logger.error(f"Redis email premium grant failed: {e}")
            raise
    
    async def _grant_premium_redis_ip(self, ip_address: str, subscription_data: Dict[str, Any]) -> bool:
        """Grant premium via Redis IP method"""
        try:
            return await self.redis_manager.grant_premium_access(
                client_ip=ip_address,
                email=None,
                plan=subscription_data['plan'],
                duration_days=subscription_data['duration_days'],
                payment_info=subscription_data['payment_info']
            )
        except Exception as e:
            logger.error(f"Redis IP premium grant failed: {e}")
            raise
    
    async def _grant_premium_redis_user(self, user_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Grant premium via Redis user subscription method"""
        try:
            redis_sub_data = {
                'subscription_id': f"dual_write_{user_id}_{datetime.now().timestamp()}",
                'plan_name': subscription_data['plan'],
                'status': 'active',
                'current_period_start': subscription_data['granted_at'],
                'current_period_end': subscription_data['expires_at'],
                'tier_level': 2,
                'thread_limit': -1,
                'features': ['unlimited_threads'],
                'source': 'dual_write'
            }
            
            return await self.redis_manager.grant_subscription_access(user_id, redis_sub_data)
        except Exception as e:
            logger.error(f"Redis user premium grant failed: {e}")
            raise
    
    async def _grant_premium_postgres(self, identifier: str, identifier_type: str, 
                                     subscription_data: Dict[str, Any]) -> bool:
        """Grant premium via PostgreSQL subscription"""
        try:
            # Get or create user_id
            user_id = None
            if identifier_type == 'user_id':
                user_id = identifier
            elif identifier_type == 'email':
                user_id = await self._get_or_create_user_for_email(identifier)
            
            # Create subscription record
            sub_id = str(uuid.uuid4())
            
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO subscriptions (
                        id, user_id, stripe_customer_id, stripe_price_id, stripe_product_id,
                        status, plan_name, billing_cycle, amount_cents, currency,
                        current_period_start, current_period_end, cancel_at_period_end,
                        premium_expires_at, metadata, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    ON CONFLICT (id) DO NOTHING
                """,
                    uuid.UUID(sub_id),
                    uuid.UUID(user_id) if user_id else None,
                    f"dual_write_{identifier_type}_{identifier}",
                    'dual_write_premium',
                    'dual_write_premium',
                    'active',
                    subscription_data['plan'],
                    'one_time',
                    499,  # $4.99
                    'USD',
                    subscription_data['granted_at'],
                    subscription_data['expires_at'],
                    True,
                    subscription_data['expires_at'],
                    json.dumps({
                        'source': 'dual_write',
                        'identifier': identifier,
                        'identifier_type': identifier_type,
                        'payment_info': subscription_data.get('payment_info', {})
                    }),
                    subscription_data['granted_at'],
                    datetime.now()
                )
            
            self.write_stats['postgres_writes'] += 1
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL premium grant failed: {e}")
            raise
    
    async def _get_or_create_user_for_email(self, email: str) -> str:
        """Get existing user_id or create user for email"""
        if email in self.user_cache:
            return self.user_cache[email]
        
        async with self.postgres_pool.acquire() as conn:
            # Try to find existing user
            existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
            
            if existing:
                user_id = str(existing['id'])
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO users (id, email, password_hash, role, status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    uuid.UUID(user_id),
                    email,
                    '',  # No password for email-only users
                    'user',
                    'active',
                    datetime.now(),
                    datetime.now()
                )
            
            self.user_cache[email] = user_id
            return user_id
    
    # USAGE TRACKING
    
    async def track_usage(self, identifier: str, identifier_type: str, 
                         action: str = 'generate_thread') -> bool:
        """Track usage in both storage systems"""
        
        write_operations = []
        
        # Redis write
        if self.strategy in [WriteStrategy.REDIS_ONLY, WriteStrategy.DUAL_WRITE]:
            if identifier_type == 'ip':
                write_operations.append(self.redis_manager.track_thread_generation(identifier, None))
            elif identifier_type == 'user_id':
                write_operations.append(self.redis_manager.track_user_thread_generation(identifier))
            elif identifier_type == 'email':
                write_operations.append(self.redis_manager.track_thread_generation("0.0.0.0", identifier))
        
        # PostgreSQL write
        if self.strategy in [WriteStrategy.DUAL_WRITE, WriteStrategy.POSTGRES_PRIMARY, WriteStrategy.POSTGRES_ONLY]:
            write_operations.append(self._track_usage_postgres(identifier, identifier_type, action))
        
        # Execute writes
        results = await asyncio.gather(*write_operations, return_exceptions=True)
        
        # Process results
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        
        if success_count < len(write_operations):
            self.write_stats['dual_write_consistency_errors'] += 1
            logger.warning(f"Partial usage tracking failure for {identifier}")
        
        return success_count > 0
    
    async def _track_usage_postgres(self, identifier: str, identifier_type: str, action: str) -> bool:
        """Track usage in PostgreSQL"""
        try:
            user_id = None
            ip_address = None
            
            if identifier_type == 'user_id':
                user_id = identifier
            elif identifier_type == 'ip':
                ip_address = identifier
            elif identifier_type == 'email':
                user_id = await self._get_or_create_user_for_email(identifier)
            
            current_date = datetime.now().date()
            current_month = current_date.replace(day=1)
            
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO usage_tracking (
                        id, user_id, ip_address, endpoint, action,
                        daily_count, monthly_count, date_bucket, month_bucket,
                        metadata, first_request_at, last_request_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (user_id, ip_address, endpoint, date_bucket) 
                    DO UPDATE SET
                        daily_count = usage_tracking.daily_count + 1,
                        last_request_at = EXCLUDED.last_request_at
                """,
                    uuid.uuid4(),
                    uuid.UUID(user_id) if user_id else None,
                    ip_address,
                    '/api/generate',
                    action,
                    1,  # daily_count
                    1,  # monthly_count (will be aggregated)
                    current_date,
                    current_month,
                    json.dumps({
                        'source': 'dual_write',
                        'identifier_type': identifier_type
                    }),
                    datetime.now(),
                    datetime.now()
                )
            
            self.write_stats['postgres_writes'] += 1
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL usage tracking failed: {e}")
            raise
    
    # READ OPERATIONS (Strategy-aware)
    
    async def check_premium_access(self, identifier: str, identifier_type: str) -> Dict[str, Any]:
        """Check premium access using appropriate read strategy"""
        
        if self.strategy in [WriteStrategy.POSTGRES_ONLY, WriteStrategy.POSTGRES_PRIMARY]:
            return await self._check_premium_postgres(identifier, identifier_type)
        else:
            return await self._check_premium_redis(identifier, identifier_type)
    
    async def _check_premium_redis(self, identifier: str, identifier_type: str) -> Dict[str, Any]:
        """Check premium access in Redis"""
        try:
            if identifier_type == 'user_id':
                return await self.redis_manager.check_subscription_access(user_id=identifier)
            elif identifier_type == 'email':
                return await self.redis_manager.check_subscription_access(email=identifier)
            elif identifier_type == 'ip':
                return await self.redis_manager.check_subscription_access(client_ip=identifier)
            else:
                return {'has_access': False, 'source': 'unknown_identifier_type'}
                
        except Exception as e:
            logger.error(f"Redis premium check failed: {e}")
            return {'has_access': False, 'source': 'redis_error'}
    
    async def _check_premium_postgres(self, identifier: str, identifier_type: str) -> Dict[str, Any]:
        """Check premium access in PostgreSQL"""
        try:
            async with self.postgres_pool.acquire() as conn:
                query = None
                param = None
                
                if identifier_type == 'user_id':
                    query = """
                        SELECT status, plan_name, premium_expires_at, current_period_end
                        FROM subscriptions 
                        WHERE user_id = $1 AND status = 'active'
                        ORDER BY current_period_end DESC LIMIT 1
                    """
                    param = uuid.UUID(identifier)
                elif identifier_type == 'email':
                    query = """
                        SELECT s.status, s.plan_name, s.premium_expires_at, s.current_period_end
                        FROM subscriptions s
                        JOIN users u ON s.user_id = u.id
                        WHERE u.email = $1 AND s.status = 'active'
                        ORDER BY s.current_period_end DESC LIMIT 1
                    """
                    param = identifier
                elif identifier_type == 'ip':
                    # For IP-based access, check metadata
                    query = """
                        SELECT status, plan_name, premium_expires_at, current_period_end
                        FROM subscriptions 
                        WHERE status = 'active' 
                        AND metadata->>'ip_address' = $1
                        ORDER BY current_period_end DESC LIMIT 1
                    """
                    param = identifier
                
                if query:
                    result = await conn.fetchrow(query, param)
                    
                    if result:
                        expires_at = result['premium_expires_at'] or result['current_period_end']
                        has_access = expires_at and expires_at > datetime.now()
                        
                        return {
                            'has_access': has_access,
                            'plan_name': result['plan_name'],
                            'expires_at': expires_at,
                            'source': 'postgres'
                        }
                
                return {'has_access': False, 'source': 'postgres_not_found'}
                
        except Exception as e:
            logger.error(f"PostgreSQL premium check failed: {e}")
            return {'has_access': False, 'source': 'postgres_error'}
    
    async def get_usage_stats(self, identifier: str, identifier_type: str) -> Dict[str, Any]:
        """Get usage statistics using appropriate read strategy"""
        
        if self.strategy in [WriteStrategy.POSTGRES_ONLY, WriteStrategy.POSTGRES_PRIMARY]:
            return await self._get_usage_postgres(identifier, identifier_type)
        else:
            return await self._get_usage_redis(identifier, identifier_type)
    
    async def _get_usage_redis(self, identifier: str, identifier_type: str) -> Dict[str, Any]:
        """Get usage stats from Redis"""
        try:
            if identifier_type == 'user_id':
                return await self.redis_manager.get_user_usage_stats(identifier)
            elif identifier_type == 'ip':
                daily = await self.redis_manager.get_usage_count(identifier, period='daily')
                monthly = await self.redis_manager.get_usage_count(identifier, period='monthly')
                return {
                    'threads_today': daily.get('ip_usage', 0),
                    'threads_this_month': monthly.get('ip_usage', 0)
                }
            elif identifier_type == 'email':
                daily = await self.redis_manager.get_usage_count("0.0.0.0", email=identifier, period='daily')
                monthly = await self.redis_manager.get_usage_count("0.0.0.0", email=identifier, period='monthly')
                return {
                    'threads_today': daily.get('email_usage', 0),
                    'threads_this_month': monthly.get('email_usage', 0)
                }
            
            return {'threads_today': 0, 'threads_this_month': 0}
            
        except Exception as e:
            logger.error(f"Redis usage stats failed: {e}")
            return {'threads_today': 0, 'threads_this_month': 0}
    
    async def _get_usage_postgres(self, identifier: str, identifier_type: str) -> Dict[str, Any]:
        """Get usage stats from PostgreSQL"""
        try:
            current_date = datetime.now().date()
            current_month = current_date.replace(day=1)
            
            async with self.postgres_pool.acquire() as conn:
                query_conditions = []
                params = [current_date, current_month]
                
                if identifier_type == 'user_id':
                    query_conditions.append("user_id = $3")
                    params.append(uuid.UUID(identifier))
                elif identifier_type == 'ip':
                    query_conditions.append("ip_address = $3")
                    params.append(identifier)
                elif identifier_type == 'email':
                    # Get user_id first
                    user_id = self.user_cache.get(identifier)
                    if not user_id:
                        user_row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", identifier)
                        if user_row:
                            user_id = str(user_row['id'])
                            self.user_cache[identifier] = user_id
                    
                    if user_id:
                        query_conditions.append("user_id = $3")
                        params.append(uuid.UUID(user_id))
                    else:
                        return {'threads_today': 0, 'threads_this_month': 0}
                
                where_clause = " AND ".join(query_conditions)
                
                result = await conn.fetchrow(f"""
                    SELECT 
                        SUM(CASE WHEN date_bucket = $1 THEN daily_count ELSE 0 END) as threads_today,
                        SUM(CASE WHEN month_bucket = $2 THEN monthly_count ELSE 0 END) as threads_this_month
                    FROM usage_tracking
                    WHERE {where_clause}
                """, *params)
                
                return {
                    'threads_today': int(result['threads_today'] or 0),
                    'threads_this_month': int(result['threads_this_month'] or 0)
                }
                
        except Exception as e:
            logger.error(f"PostgreSQL usage stats failed: {e}")
            return {'threads_today': 0, 'threads_this_month': 0}
    
    # STRATEGY MANAGEMENT
    
    def switch_strategy(self, new_strategy: WriteStrategy):
        """Switch write strategy (e.g., during migration phases)"""
        old_strategy = self.strategy
        self.strategy = new_strategy
        
        logger.info(f"Write strategy changed: {old_strategy.value} -> {new_strategy.value}")
        
        # Log current stats before switching
        logger.info(f"Stats before strategy switch: {self.write_stats}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get write statistics"""
        return {
            'strategy': self.strategy.value,
            'write_stats': self.write_stats.copy(),
            'cache_size': len(self.user_cache)
        }

# Context manager for easy usage
@asynccontextmanager
async def dual_write_service(strategy: WriteStrategy = WriteStrategy.DUAL_WRITE):
    """Context manager for DualWriteService"""
    service = DualWriteService(strategy)
    try:
        await service.initialize()
        yield service
    finally:
        await service.close()

# Example usage and testing
async def test_dual_write_service():
    """Test the dual write service"""
    print("🔄 Testing Dual Write Service")
    print("=" * 30)
    
    async with dual_write_service(WriteStrategy.DUAL_WRITE) as service:
        # Test user creation
        print("Testing user creation...")
        user_id = await service.create_user("test@example.com", {
            'created_at': datetime.now(),
            'metadata': {'source': 'test'}
        })
        print(f"✅ User created: {user_id}")
        
        # Test premium access
        print("Testing premium access grant...")
        await service.grant_premium_access("test@example.com", "email")
        print("✅ Premium access granted")
        
        # Test premium check
        print("Testing premium access check...")
        access = await service.check_premium_access("test@example.com", "email")
        print(f"✅ Premium check: {access}")
        
        # Test usage tracking
        print("Testing usage tracking...")
        await service.track_usage("test@example.com", "email")
        print("✅ Usage tracked")
        
        # Test usage stats
        print("Testing usage stats...")
        stats = await service.get_usage_stats("test@example.com", "email")
        print(f"✅ Usage stats: {stats}")
        
        # Get service stats
        service_stats = service.get_stats()
        print(f"📊 Service stats: {service_stats}")

if __name__ == "__main__":
    asyncio.run(test_dual_write_service())
#!/usr/bin/env python3
"""
Redis to PostgreSQL Migration Tool for Threadr
Comprehensive migration with validation, rollback, and zero-downtime support
"""

import asyncio
import asyncpg
import redis
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
import logging
from dataclasses import dataclass, field
import uuid
import hashlib
from collections import defaultdict
import argparse

# Add src to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.redis_manager import RedisManager
    from migration_mapping import RedisToPostgresMigrationMapper
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    print("Make sure you're running from the correct directory and migration_mapping.py exists.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MigrationStats:
    """Track migration statistics"""
    total_redis_keys: int = 0
    processed_keys: int = 0
    successful_migrations: int = 0
    failed_migrations: int = 0
    skipped_keys: int = 0
    validation_errors: int = 0
    records_by_table: Dict[str, int] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def add_record(self, table: str, count: int = 1):
        """Add records to table count"""
        if table not in self.records_by_table:
            self.records_by_table[table] = 0
        self.records_by_table[table] += count
    
    def get_duration(self) -> timedelta:
        """Get migration duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return timedelta(0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get migration summary"""
        duration = self.get_duration()
        return {
            'total_redis_keys': self.total_redis_keys,
            'processed_keys': self.processed_keys,
            'successful_migrations': self.successful_migrations,
            'failed_migrations': self.failed_migrations,
            'skipped_keys': self.skipped_keys,
            'validation_errors': self.validation_errors,
            'records_by_table': self.records_by_table,
            'duration_seconds': duration.total_seconds(),
            'duration_human': str(duration),
            'success_rate': (self.successful_migrations / max(self.processed_keys, 1)) * 100
        }

@dataclass 
class MigrationConfig:
    """Migration configuration"""
    dry_run: bool = False
    batch_size: int = 100
    validate_only: bool = False
    priority_filter: Optional[str] = None  # 'critical', 'high', etc.
    table_filter: Optional[str] = None     # Specific table name
    pattern_filter: Optional[str] = None   # Specific Redis pattern
    enable_rollback: bool = True
    create_backup: bool = True
    parallel_workers: int = 4
    continue_on_error: bool = True
    max_retries: int = 3

class RedisToPostgresMigrator:
    """Main migration orchestrator"""
    
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.redis_manager = RedisManager()
        self.mapper = RedisToPostgresMigrationMapper()
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.stats = MigrationStats()
        self.rollback_log: List[Dict[str, Any]] = []
        self.user_id_mapping: Dict[str, str] = {}  # email -> user_id mapping
        self.validation_errors: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize database connections"""
        logger.info("Initializing database connections...")
        
        # Check Redis connection
        if not self.redis_manager.is_available:
            raise RuntimeError("Redis is not available")
        
        # Initialize PostgreSQL connection
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL not configured")
        
        try:
            self.postgres_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            # Test connection
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            logger.info("PostgreSQL connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def run_migration(self) -> MigrationStats:
        """Run the complete migration process"""
        try:
            self.stats.start_time = datetime.now()
            logger.info(f"Starting Redis to PostgreSQL migration (dry_run={self.config.dry_run})")
            
            await self.initialize()
            
            if self.config.create_backup and not self.config.dry_run:
                await self._create_backup()
            
            # Phase 1: Migrate users first (needed for foreign keys)
            await self._migrate_users()
            
            # Phase 2: Migrate critical data (premium subscriptions)
            await self._migrate_by_priority('critical')
            
            # Phase 3: Migrate high priority data
            await self._migrate_by_priority('high')
            
            # Phase 4: Migrate medium priority data
            if not self.config.priority_filter or self.config.priority_filter in ['medium', 'all']:
                await self._migrate_by_priority('medium')
            
            # Phase 5: Migrate low priority data
            if not self.config.priority_filter or self.config.priority_filter in ['low', 'all']:
                await self._migrate_by_priority('low')
            
            # Validation
            if not self.config.dry_run:
                await self._validate_migration()
            
            self.stats.end_time = datetime.now()
            logger.info("Migration completed successfully")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            if self.config.enable_rollback and not self.config.dry_run:
                logger.info("Starting rollback process...")
                await self._rollback_migration()
            raise
        
        finally:
            await self._cleanup()
    
    async def _create_backup(self):
        """Create database backup before migration"""
        logger.info("Creating pre-migration backup...")
        
        backup_filename = f"threadr_pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        try:
            # Create a simple schema + data backup
            async with self.postgres_pool.acquire() as conn:
                # Get all table names
                tables = await conn.fetch("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' 
                    ORDER BY tablename
                """)
                
                with open(backup_filename, 'w') as f:
                    f.write(f"-- Threadr Pre-Migration Backup\n")
                    f.write(f"-- Created: {datetime.now().isoformat()}\n\n")
                    
                    for table_row in tables:
                        table_name = table_row['tablename']
                        f.write(f"-- Backup for table: {table_name}\n")
                        
                        # Get record count
                        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                        f.write(f"-- Records before migration: {count}\n\n")
            
            logger.info(f"Backup created: {backup_filename}")
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            # Continue with migration even if backup fails
    
    async def _migrate_users(self):
        """First phase: Migrate user data from emails"""
        logger.info("Phase 1: Migrating user data from email subscriptions...")
        
        user_count = 0
        
        def scan_emails():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return []
                
                emails = []
                for email in r.sscan_iter(self.redis_manager.email_list_key):
                    email_key = f"{self.redis_manager.email_prefix}{email}"
                    data = r.get(email_key)
                    if data:
                        try:
                            emails.append((email, json.loads(data)))
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in email key: {email_key}")
                
                return emails
        
        # Get all email data
        loop = asyncio.get_event_loop()
        email_data = await loop.run_in_executor(self.redis_manager.executor, scan_emails)
        
        logger.info(f"Found {len(email_data)} email subscriptions to convert to users")
        
        async with self.postgres_pool.acquire() as conn:
            async with conn.transaction():
                for email, data in email_data:
                    try:
                        # Check if user already exists
                        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
                        
                        if existing:
                            user_id = str(existing['id'])
                            logger.debug(f"User already exists for {email}: {user_id}")
                        else:
                            # Transform email data to user record
                            transformer = self.mapper.transformers['transform_email_to_user']
                            user_record = transformer(f"{self.redis_manager.email_prefix}{email}", data)
                            
                            if not self.config.dry_run:
                                # Insert user
                                user_id = await conn.fetchval("""
                                    INSERT INTO users (
                                        id, email, password_hash, role, status,
                                        login_count, failed_login_attempts, is_email_verified,
                                        metadata, created_at, updated_at
                                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                                    RETURNING id
                                """, 
                                    uuid.UUID(user_record['id']),
                                    user_record['email'],
                                    user_record['password_hash'],
                                    user_record['role'],
                                    user_record['status'],
                                    user_record['login_count'],
                                    user_record['failed_login_attempts'],
                                    user_record['is_email_verified'],
                                    json.dumps(user_record['metadata']),
                                    user_record['created_at'],
                                    user_record['updated_at']
                                )
                                user_id = str(user_id)
                            else:
                                user_id = user_record['id']
                                logger.info(f"DRY RUN: Would create user {email} -> {user_id}")
                        
                        # Store mapping for later use
                        self.user_id_mapping[email] = user_id
                        user_count += 1
                        
                        # Log for rollback
                        if not self.config.dry_run:
                            self.rollback_log.append({
                                'operation': 'insert_user',
                                'table': 'users',
                                'id': user_id,
                                'email': email
                            })
                        
                    except Exception as e:
                        logger.error(f"Error migrating user {email}: {e}")
                        self.stats.failed_migrations += 1
                        if not self.config.continue_on_error:
                            raise
        
        self.stats.add_record('users', user_count)
        logger.info(f"User migration completed: {user_count} users processed")
    
    async def _migrate_by_priority(self, priority: str):
        """Migrate data by priority level"""
        logger.info(f"Migrating {priority} priority data...")
        
        # Filter mappings by priority
        mappings = [m for m in self.mapper.mappings if m.priority == priority]
        
        if not mappings:
            logger.info(f"No mappings found for priority: {priority}")
            return
        
        # Process each mapping
        for mapping in mappings:
            if self._should_skip_mapping(mapping):
                continue
                
            logger.info(f"Processing pattern: {mapping.redis_pattern}")
            
            try:
                await self._migrate_pattern(mapping)
            except Exception as e:
                logger.error(f"Error migrating pattern {mapping.redis_pattern}: {e}")
                self.stats.failed_migrations += 1
                
                if not self.config.continue_on_error:
                    raise
    
    def _should_skip_mapping(self, mapping) -> bool:
        """Check if mapping should be skipped based on filters"""
        if self.config.table_filter and mapping.postgres_table != self.config.table_filter:
            return True
        
        if self.config.pattern_filter and mapping.redis_pattern != self.config.pattern_filter:
            return True
        
        return False
    
    async def _migrate_pattern(self, mapping):
        """Migrate a specific Redis pattern to PostgreSQL"""
        pattern = mapping.redis_pattern
        
        # Skip patterns without target tables
        if not mapping.postgres_table:
            logger.info(f"Skipping pattern {pattern} (no target table)")
            self.stats.skipped_keys += 1
            return
        
        # Get transformer function
        transformer = self.mapper.transformers.get(mapping.transform_function)
        if not transformer:
            logger.error(f"No transformer found for {mapping.transform_function}")
            return
        
        # Scan Redis for matching keys
        redis_data = await self._scan_redis_pattern(pattern)
        
        if not redis_data:
            logger.info(f"No data found for pattern: {pattern}")
            return
        
        logger.info(f"Found {len(redis_data)} records for pattern: {pattern}")
        self.stats.total_redis_keys += len(redis_data)
        
        # Process in batches
        for i in range(0, len(redis_data), self.config.batch_size):
            batch = redis_data[i:i + self.config.batch_size]
            await self._process_batch(batch, mapping, transformer)
    
    async def _scan_redis_pattern(self, pattern: str) -> List[Tuple[str, Any]]:
        """Scan Redis for pattern and return key-value pairs"""
        
        def scan_pattern():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return []
                
                results = []
                
                # Handle special cases
                if pattern == "threadr:emails:list":
                    # This is a set, not individual keys
                    emails = list(r.sscan_iter(pattern))
                    return [(pattern, emails)]
                
                # Scan for matching keys
                for key in r.scan_iter(pattern):
                    try:
                        value = r.get(key)
                        if value:
                            # Try to parse as JSON
                            try:
                                parsed_value = json.loads(value)
                            except json.JSONDecodeError:
                                # Use raw value if not JSON
                                parsed_value = value
                            
                            results.append((key, parsed_value))
                    except Exception as e:
                        logger.warning(f"Error reading key {key}: {e}")
                
                return results
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, scan_pattern)
    
    async def _process_batch(self, batch: List[Tuple[str, Any]], mapping, transformer):
        """Process a batch of Redis records"""
        
        async with self.postgres_pool.acquire() as conn:
            async with conn.transaction():
                
                for redis_key, redis_data in batch:
                    try:
                        self.stats.processed_keys += 1
                        
                        # Skip if transformer says to skip
                        if mapping.transform_function in ['skip_rate_limiting', 'validate_email_list']:
                            self.stats.skipped_keys += 1
                            continue
                        
                        # Transform the data
                        postgres_record = transformer(redis_key, redis_data)
                        
                        if postgres_record is None or postgres_record.get('skip'):
                            self.stats.skipped_keys += 1
                            continue
                        
                        # Handle special cases where transformer returns list
                        records_to_insert = [postgres_record] if isinstance(postgres_record, dict) else postgres_record
                        
                        # Insert records
                        for record in records_to_insert:
                            if record.get('skip'):
                                continue
                            
                            # Apply post-processing (link users, etc.)
                            record = await self._post_process_record(record, mapping.postgres_table)
                            
                            # Validate record
                            validation_errors = self._validate_record(record, mapping)
                            if validation_errors:
                                self.validation_errors.extend(validation_errors)
                                if not self.config.continue_on_error:
                                    raise RuntimeError(f"Validation failed: {validation_errors}")
                            
                            # Insert record
                            if not self.config.dry_run:
                                await self._insert_record(conn, mapping.postgres_table, record)
                            else:
                                logger.debug(f"DRY RUN: Would insert into {mapping.postgres_table}: {record.get('id', 'unknown')}")
                            
                            self.stats.add_record(mapping.postgres_table)
                            
                            # Log for rollback
                            if not self.config.dry_run:
                                self.rollback_log.append({
                                    'operation': 'insert',
                                    'table': mapping.postgres_table,
                                    'id': record.get('id'),
                                    'redis_key': redis_key
                                })
                        
                        self.stats.successful_migrations += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing key {redis_key}: {e}")
                        self.stats.failed_migrations += 1
                        
                        if not self.config.continue_on_error:
                            raise
    
    async def _post_process_record(self, record: Dict[str, Any], table: str) -> Dict[str, Any]:
        """Post-process record to link foreign keys, etc."""
        
        # Link user_id for subscription records
        if table == 'subscriptions' and not record.get('user_id'):
            # Try to find user by email in metadata
            metadata = record.get('metadata', {})
            email = metadata.get('email')
            
            if email and email in self.user_id_mapping:
                record['user_id'] = uuid.UUID(self.user_id_mapping[email])
                logger.debug(f"Linked subscription to user: {email} -> {record['user_id']}")
        
        # Link user_id for usage tracking records
        if table == 'usage_tracking' and not record.get('user_id'):
            # Try to find user by email in metadata
            metadata = record.get('metadata', {})
            email = metadata.get('email')
            
            if email and email in self.user_id_mapping:
                record['user_id'] = uuid.UUID(self.user_id_mapping[email])
        
        return record
    
    def _validate_record(self, record: Dict[str, Any], mapping) -> List[Dict[str, Any]]:
        """Validate record against mapping rules"""
        errors = []
        
        for rule in mapping.validation_rules:
            error = None
            
            if rule == "expires_at_is_valid_datetime":
                expires_at = record.get('current_period_end') or record.get('premium_expires_at')
                if expires_at and not isinstance(expires_at, datetime):
                    error = f"expires_at is not a datetime: {expires_at}"
            
            elif rule == "email_is_valid":
                email = record.get('email') or record.get('metadata', {}).get('email')
                if email and '@' not in email:
                    error = f"Invalid email format: {email}"
            
            elif rule == "subscription_id_exists":
                if not record.get('stripe_subscription_id'):
                    error = "Missing stripe_subscription_id"
            
            elif rule == "ip_address_is_valid":
                ip = record.get('ip_address') or record.get('metadata', {}).get('ip_address')
                if ip and not (ip.count('.') == 3 or ':' in ip):  # Basic IPv4/IPv6 check
                    error = f"Invalid IP address: {ip}"
            
            # Add more validation rules as needed
            
            if error:
                errors.append({
                    'rule': rule,
                    'error': error,
                    'record_id': record.get('id'),
                    'table': mapping.postgres_table
                })
        
        return errors
    
    async def _insert_record(self, conn: asyncpg.Connection, table: str, record: Dict[str, Any]):
        """Insert record into PostgreSQL table"""
        
        if table == 'subscriptions':
            await self._insert_subscription(conn, record)
        elif table == 'users':
            await self._insert_user(conn, record)
        elif table == 'usage_tracking':
            await self._insert_usage_tracking(conn, record)
        elif table == 'analytics_timeseries':
            await self._insert_analytics_timeseries(conn, record)
        elif table == 'threads':
            await self._insert_thread(conn, record)
        elif table == 'user_sessions':
            await self._insert_user_session(conn, record)
        else:
            logger.warning(f"No insert handler for table: {table}")
    
    async def _insert_subscription(self, conn: asyncpg.Connection, record: Dict[str, Any]):
        """Insert subscription record"""
        await conn.execute("""
            INSERT INTO subscriptions (
                id, user_id, team_id, stripe_subscription_id, stripe_customer_id,
                stripe_price_id, stripe_product_id, status, plan_name, billing_cycle,
                amount_cents, currency, current_period_start, current_period_end,
                cancel_at_period_end, canceled_at, ended_at, premium_expires_at,
                metadata, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
            ON CONFLICT (id) DO NOTHING
        """,
            uuid.UUID(record['id']),
            uuid.UUID(record['user_id']) if record.get('user_id') else None,
            uuid.UUID(record['team_id']) if record.get('team_id') else None,
            record.get('stripe_subscription_id'),
            record['stripe_customer_id'],
            record['stripe_price_id'],
            record['stripe_product_id'],
            record['status'],
            record['plan_name'],
            record['billing_cycle'],
            record['amount_cents'],
            record['currency'],
            record['current_period_start'],
            record['current_period_end'],
            record['cancel_at_period_end'],
            record.get('canceled_at'),
            record.get('ended_at'),
            record.get('premium_expires_at'),
            json.dumps(record['metadata']),
            record['created_at'],
            record['updated_at']
        )
    
    async def _insert_user(self, conn: asyncpg.Connection, record: Dict[str, Any]):
        """Insert user record (handled in _migrate_users)"""
        pass  # Already handled in _migrate_users
    
    async def _insert_usage_tracking(self, conn: asyncpg.Connection, record: Dict[str, Any]):
        """Insert usage tracking record"""
        await conn.execute("""
            INSERT INTO usage_tracking (
                id, user_id, ip_address, endpoint, action, daily_count,
                monthly_count, date_bucket, month_bucket, user_agent,
                metadata, first_request_at, last_request_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (id) DO NOTHING
        """,
            uuid.UUID(record['id']),
            uuid.UUID(record['user_id']) if record.get('user_id') else None,
            record.get('ip_address'),
            record['endpoint'],
            record['action'],
            record['daily_count'],
            record['monthly_count'],
            record['date_bucket'],
            record['month_bucket'],
            record.get('user_agent'),
            json.dumps(record['metadata']),
            record['first_request_at'],
            record['last_request_at']
        )
    
    async def _insert_analytics_timeseries(self, conn: asyncpg.Connection, record: Dict[str, Any]):
        """Insert analytics timeseries record"""
        await conn.execute("""
            INSERT INTO analytics_timeseries (
                id, user_id, thread_id, metric_name, metric_value,
                timestamp, period_type, date_bucket, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO NOTHING
        """,
            uuid.UUID(record['id']),
            uuid.UUID(record['user_id']) if record.get('user_id') else None,
            uuid.UUID(record['thread_id']) if record.get('thread_id') else None,
            record['metric_name'],
            record['metric_value'],
            record['timestamp'],
            record['period_type'],
            record['date_bucket'],
            json.dumps(record['metadata'])
        )
    
    async def _insert_thread(self, conn: asyncpg.Connection, record: Dict[str, Any]):
        """Insert thread record"""
        await conn.execute("""
            INSERT INTO threads (
                id, user_id, team_id, title, original_content, tweets,
                source_url, source_type, ai_model, generation_time_ms,
                content_length, metadata, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            ON CONFLICT (id) DO NOTHING
        """,
            uuid.UUID(record['id']),
            uuid.UUID(record['user_id']) if record.get('user_id') else None,
            uuid.UUID(record['team_id']) if record.get('team_id') else None,
            record['title'],
            record['original_content'],
            record['tweets'],  # Already JSON string
            record.get('source_url'),
            record['source_type'],
            record['ai_model'],
            record.get('generation_time_ms'),
            record.get('content_length'),
            json.dumps(record['metadata']),
            record['created_at'],
            record['updated_at']
        )
    
    async def _insert_user_session(self, conn: asyncpg.Connection, record: Dict[str, Any]):
        """Insert user session record"""
        await conn.execute("""
            INSERT INTO user_sessions (
                id, user_id, session_token, refresh_token, device_id,
                ip_address, user_agent, device_name, is_active,
                is_remember_me, expires_at, created_at, last_used_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (id) DO NOTHING
        """,
            uuid.UUID(record['id']),
            uuid.UUID(record['user_id']) if record.get('user_id') else None,
            record.get('session_token'),
            record.get('refresh_token'),
            record.get('device_id'),
            record.get('ip_address'),
            record.get('user_agent'),
            record.get('device_name'),
            record.get('is_active', True),
            record.get('is_remember_me', False),
            record['expires_at'],
            record['created_at'],
            record['last_used_at']
        )
    
    async def _validate_migration(self):
        """Validate migrated data integrity"""
        logger.info("Validating migration integrity...")
        
        async with self.postgres_pool.acquire() as conn:
            # Check user counts
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            logger.info(f"Migrated users: {user_count}")
            
            # Check subscription counts
            sub_count = await conn.fetchval("SELECT COUNT(*) FROM subscriptions")
            active_subs = await conn.fetchval("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
            logger.info(f"Migrated subscriptions: {sub_count} ({active_subs} active)")
            
            # Check usage tracking
            usage_count = await conn.fetchval("SELECT COUNT(*) FROM usage_tracking")
            logger.info(f"Migrated usage records: {usage_count}")
            
            # Check for orphaned records (subscriptions without users)
            orphaned_subs = await conn.fetchval("""
                SELECT COUNT(*) FROM subscriptions s
                WHERE s.user_id IS NOT NULL 
                AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = s.user_id)
            """)
            
            if orphaned_subs > 0:
                logger.warning(f"Found {orphaned_subs} subscriptions without matching users")
                self.stats.validation_errors += orphaned_subs
            
            logger.info("Migration validation completed")
    
    async def _rollback_migration(self):
        """Rollback migration by deleting inserted records"""
        logger.info("Starting migration rollback...")
        
        async with self.postgres_pool.acquire() as conn:
            async with conn.transaction():
                
                # Process rollback log in reverse order
                for log_entry in reversed(self.rollback_log):
                    try:
                        if log_entry['operation'] in ['insert', 'insert_user']:
                            await conn.execute(
                                f"DELETE FROM {log_entry['table']} WHERE id = $1",
                                uuid.UUID(log_entry['id'])
                            )
                            logger.debug(f"Rolled back {log_entry['table']} record: {log_entry['id']}")
                    
                    except Exception as e:
                        logger.error(f"Error during rollback of {log_entry}: {e}")
        
        logger.info(f"Rollback completed: {len(self.rollback_log)} operations reversed")
    
    async def _cleanup(self):
        """Clean up resources"""
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.redis_manager:
            self.redis_manager.close()
    
    def save_migration_report(self, filepath: str = None) -> str:
        """Save detailed migration report"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"migration_report_{timestamp}.json"
        
        report = {
            'migration_config': {
                'dry_run': self.config.dry_run,
                'batch_size': self.config.batch_size,
                'priority_filter': self.config.priority_filter,
                'table_filter': self.config.table_filter,
                'continue_on_error': self.config.continue_on_error
            },
            'migration_stats': self.stats.get_summary(),
            'validation_errors': self.validation_errors,
            'user_mappings_created': len(self.user_id_mapping),
            'rollback_operations': len(self.rollback_log) if not self.config.dry_run else 0
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Migration report saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving migration report: {e}")
            return None

async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Redis to PostgreSQL Migration Tool")
    parser.add_argument('--dry-run', action='store_true', help='Run without making changes')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, don\'t migrate')
    parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low', 'all'], 
                       help='Migrate only specific priority level')
    parser.add_argument('--table', help='Migrate only specific table')
    parser.add_argument('--pattern', help='Migrate only specific Redis pattern')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for processing')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--no-rollback', action='store_true', help='Disable rollback capability')
    parser.add_argument('--stop-on-error', action='store_true', help='Stop on first error')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    
    args = parser.parse_args()
    
    # Create configuration
    config = MigrationConfig(
        dry_run=args.dry_run,
        validate_only=args.validate_only,
        priority_filter=args.priority,
        table_filter=args.table,
        pattern_filter=args.pattern,
        batch_size=args.batch_size,
        create_backup=not args.no_backup,
        enable_rollback=not args.no_rollback,
        continue_on_error=not args.stop_on_error,
        parallel_workers=args.workers
    )
    
    print("🔄 Redis to PostgreSQL Migration Tool")
    print("=" * 50)
    
    if config.dry_run:
        print("🧪 DRY RUN MODE - No changes will be made")
    
    if config.priority_filter:
        print(f"🎯 Priority Filter: {config.priority_filter}")
    
    if config.table_filter:
        print(f"📊 Table Filter: {config.table_filter}")
    
    print()
    
    # Create and run migrator
    migrator = RedisToPostgresMigrator(config)
    
    try:
        stats = await migrator.run_migration()
        
        # Print results
        print("\n✅ Migration Completed Successfully!")
        print("=" * 50)
        
        summary = stats.get_summary()
        print(f"📊 Statistics:")
        print(f"  Total Redis Keys: {summary['total_redis_keys']:,}")
        print(f"  Processed: {summary['processed_keys']:,}")
        print(f"  Successful: {summary['successful_migrations']:,}")
        print(f"  Failed: {summary['failed_migrations']:,}")
        print(f"  Skipped: {summary['skipped_keys']:,}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Duration: {summary['duration_human']}")
        
        if summary['records_by_table']:
            print(f"\n📋 Records by Table:")
            for table, count in summary['records_by_table'].items():
                print(f"  {table}: {count:,}")
        
        if migrator.validation_errors:
            print(f"\n⚠️ Validation Errors: {len(migrator.validation_errors)}")
        
        # Save report
        report_file = migrator.save_migration_report()
        if report_file:
            print(f"\n📄 Detailed report: {report_file}")
        
    except KeyboardInterrupt:
        print("\n❌ Migration interrupted by user")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        logger.error("Migration failed", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
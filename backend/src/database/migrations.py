"""
Database migration utilities for Threadr
Handles schema changes, data migrations, and Redis to PostgreSQL migration
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .config import get_db_session, engine
from .models import Base, User, Team, Thread, Subscription, UsageTracking, UserSession
from ..core.redis_manager import get_redis_client

logger = logging.getLogger(__name__)

# ============================================================================
# SCHEMA MANAGEMENT
# ============================================================================

class DatabaseMigrator:
    """Handle database schema creation and migrations"""
    
    def __init__(self):
        self.redis_client = None
        self.migrations_completed = set()
    
    def create_all_tables(self, drop_existing: bool = False):
        """Create all database tables"""
        try:
            if drop_existing:
                logger.warning("Dropping all existing tables...")
                Base.metadata.drop_all(bind=engine)
            
            logger.info("Creating all database tables...")
            Base.metadata.create_all(bind=engine)
            
            # Verify table creation
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Created {len(tables)} tables: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return False
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists"""
        try:
            inspector = inspect(engine)
            return table_name in inspector.get_table_names()
        except Exception as e:
            logger.error(f"Failed to check if table {table_name} exists: {e}")
            return False
    
    def get_database_schema_version(self) -> str:
        """Get current schema version from database"""
        try:
            with get_db_session() as db:
                # Check if schema_version table exists
                if not self.check_table_exists('schema_version'):
                    return "0.0.0"
                
                result = db.execute(text("""
                    SELECT version FROM schema_version 
                    ORDER BY applied_at DESC 
                    LIMIT 1
                """))
                row = result.fetchone()
                return row[0] if row else "0.0.0"
        except Exception as e:
            logger.error(f"Failed to get schema version: {e}")
            return "0.0.0"
    
    def create_schema_version_table(self):
        """Create schema version tracking table"""
        try:
            with get_db_session() as db:
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(20) NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        applied_by VARCHAR(100) DEFAULT CURRENT_USER
                    )
                """))
                db.commit()
                logger.info("Schema version table created")
        except Exception as e:
            logger.error(f"Failed to create schema version table: {e}")
            raise
    
    def record_migration(self, version: str, description: str):
        """Record a completed migration"""
        try:
            with get_db_session() as db:
                db.execute(text("""
                    INSERT INTO schema_version (version, description)
                    VALUES (:version, :description)
                """), {"version": version, "description": description})
                db.commit()
                logger.info(f"Recorded migration: {version} - {description}")
        except Exception as e:
            logger.error(f"Failed to record migration: {e}")

# ============================================================================
# REDIS TO POSTGRESQL MIGRATION
# ============================================================================

class RedisToPostgresMigrator:
    """Migrate data from Redis to PostgreSQL"""
    
    def __init__(self):
        self.redis_client = None
        self.migrated_counts = {
            'users': 0,
            'threads': 0,
            'subscriptions': 0,
            'usage_tracking': 0,
            'sessions': 0,
            'emails': 0
        }
    
    async def initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await get_redis_client()
            if not self.redis_client:
                raise Exception("Failed to connect to Redis")
            logger.info("Redis connection established for migration")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def migrate_all_data(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate all data from Redis to PostgreSQL"""
        logger.info(f"Starting Redis to PostgreSQL migration (dry_run={dry_run})")
        
        if not self.redis_client:
            await self.initialize_redis()
        
        migration_results = {}
        
        try:
            # Migrate in order (respecting dependencies)
            migration_results['users'] = await self.migrate_users(dry_run)
            migration_results['subscriptions'] = await self.migrate_subscriptions(dry_run)
            migration_results['threads'] = await self.migrate_threads(dry_run)
            migration_results['usage_tracking'] = await self.migrate_usage_tracking(dry_run)
            migration_results['sessions'] = await self.migrate_sessions(dry_run)
            migration_results['emails'] = await self.migrate_email_list(dry_run)
            
            # Summary
            total_migrated = sum(result.get('migrated', 0) for result in migration_results.values())
            total_errors = sum(result.get('errors', 0) for result in migration_results.values())
            
            logger.info(f"Migration completed: {total_migrated} records migrated, {total_errors} errors")
            
            return {
                'success': True,
                'total_migrated': total_migrated,
                'total_errors': total_errors,
                'details': migration_results,
                'dry_run': dry_run
            }
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'partial_results': migration_results,
                'dry_run': dry_run
            }
    
    async def migrate_users(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate user data from Redis"""
        logger.info("Migrating users from Redis...")
        
        migrated = 0
        errors = 0
        error_details = []
        
        try:
            # Get all user keys from Redis
            user_keys = await self.redis_client.keys("user:*")
            logger.info(f"Found {len(user_keys)} user records in Redis")
            
            with get_db_session() as db:
                for key in user_keys:
                    try:
                        # Get user data from Redis
                        user_data = await self.redis_client.hgetall(key)
                        if not user_data:
                            continue
                        
                        # Parse user ID from key
                        user_id = key.decode('utf-8').split(':')[1]
                        
                        # Check if user already exists in PostgreSQL
                        existing_user = db.query(User).filter(User.id == user_id).first()
                        if existing_user:
                            logger.debug(f"User {user_id} already exists, skipping")
                            continue
                        
                        if not dry_run:
                            # Create User object
                            user = User(
                                id=user_id,
                                email=user_data.get(b'email', b'').decode('utf-8'),
                                password_hash=user_data.get(b'password_hash', b'').decode('utf-8'),
                                role=user_data.get(b'role', b'user').decode('utf-8'),
                                status=user_data.get(b'status', b'active').decode('utf-8'),
                                is_email_verified=user_data.get(b'is_email_verified', b'false').decode('utf-8').lower() == 'true',
                                created_at=datetime.fromisoformat(user_data.get(b'created_at', datetime.utcnow().isoformat()).decode('utf-8')),
                                login_count=int(user_data.get(b'login_count', b'0')),
                                metadata=json.loads(user_data.get(b'metadata', b'{}').decode('utf-8'))
                            )
                            
                            db.add(user)
                            db.flush()  # Get the ID without committing
                        
                        migrated += 1
                        if migrated % 100 == 0:
                            logger.info(f"Migrated {migrated} users...")
                            if not dry_run:
                                db.commit()
                        
                    except Exception as e:
                        errors += 1
                        error_msg = f"Failed to migrate user {key}: {e}"
                        logger.error(error_msg)
                        error_details.append(error_msg)
                
                if not dry_run:
                    db.commit()
            
            self.migrated_counts['users'] = migrated
            logger.info(f"User migration completed: {migrated} migrated, {errors} errors")
            
            return {
                'migrated': migrated,
                'errors': errors,
                'error_details': error_details[:10]  # Limit error details
            }
            
        except Exception as e:
            logger.error(f"User migration failed: {e}")
            return {
                'migrated': migrated,
                'errors': errors + 1,
                'error_details': [str(e)]
            }
    
    async def migrate_threads(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate thread data from Redis"""
        logger.info("Migrating threads from Redis...")
        
        migrated = 0
        errors = 0
        error_details = []
        
        try:
            # Get all thread keys from Redis
            thread_keys = await self.redis_client.keys("thread:*")
            logger.info(f"Found {len(thread_keys)} thread records in Redis")
            
            with get_db_session() as db:
                for key in thread_keys:
                    try:
                        # Get thread data from Redis
                        thread_data_str = await self.redis_client.get(key)
                        if not thread_data_str:
                            continue
                        
                        thread_data = json.loads(thread_data_str)
                        thread_id = thread_data.get('id')
                        
                        # Check if thread already exists
                        existing_thread = db.query(Thread).filter(Thread.id == thread_id).first()
                        if existing_thread:
                            continue
                        
                        if not dry_run:
                            # Create Thread object
                            thread = Thread(
                                id=thread_id,
                                user_id=thread_data.get('user_id'),
                                title=thread_data.get('title', ''),
                                original_content=thread_data.get('original_content', ''),
                                tweets=thread_data.get('tweets', []),
                                metadata=thread_data.get('metadata', {}),
                                source_url=thread_data.get('source_url'),
                                source_type=thread_data.get('source_type', 'text'),
                                ai_model=thread_data.get('ai_model', 'gpt-3.5-turbo'),
                                generation_time_ms=thread_data.get('generation_time_ms'),
                                content_length=thread_data.get('content_length'),
                                view_count=thread_data.get('view_count', 0),
                                copy_count=thread_data.get('copy_count', 0),
                                is_favorite=thread_data.get('is_favorite', False),
                                is_archived=thread_data.get('is_archived', False),
                                created_at=datetime.fromisoformat(thread_data.get('created_at', datetime.utcnow().isoformat())),
                                updated_at=datetime.fromisoformat(thread_data.get('updated_at', datetime.utcnow().isoformat()))
                            )
                            
                            db.add(thread)
                            db.flush()
                        
                        migrated += 1
                        if migrated % 50 == 0:
                            logger.info(f"Migrated {migrated} threads...")
                            if not dry_run:
                                db.commit()
                        
                    except Exception as e:
                        errors += 1
                        error_msg = f"Failed to migrate thread {key}: {e}"
                        logger.error(error_msg)
                        error_details.append(error_msg)
                
                if not dry_run:
                    db.commit()
            
            self.migrated_counts['threads'] = migrated
            logger.info(f"Thread migration completed: {migrated} migrated, {errors} errors")
            
            return {
                'migrated': migrated,
                'errors': errors,
                'error_details': error_details[:10]
            }
            
        except Exception as e:
            logger.error(f"Thread migration failed: {e}")
            return {
                'migrated': migrated,
                'errors': errors + 1,
                'error_details': [str(e)]
            }
    
    async def migrate_subscriptions(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate subscription data from Redis"""
        logger.info("Migrating subscriptions from Redis...")
        
        migrated = 0
        errors = 0
        error_details = []
        
        try:
            # Get premium users from Redis
            premium_keys = await self.redis_client.keys("premium:*")
            logger.info(f"Found {len(premium_keys)} premium records in Redis")
            
            with get_db_session() as db:
                for key in premium_keys:
                    try:
                        # Get premium data
                        premium_data = await self.redis_client.hgetall(key)
                        if not premium_data:
                            continue
                        
                        user_id = key.decode('utf-8').split(':')[1]
                        
                        # Check if subscription already exists
                        existing_sub = db.query(Subscription).filter(
                            Subscription.user_id == user_id
                        ).first()
                        if existing_sub:
                            continue
                        
                        if not dry_run:
                            # Create Subscription object
                            expires_at_str = premium_data.get(b'expires_at', b'').decode('utf-8')
                            expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else datetime.utcnow() + timedelta(days=30)
                            
                            subscription = Subscription(
                                user_id=user_id,
                                stripe_customer_id=premium_data.get(b'stripe_customer_id', b'').decode('utf-8') or f'migrated_{user_id}',
                                stripe_price_id=premium_data.get(b'stripe_price_id', b'price_migrated').decode('utf-8'),
                                stripe_product_id=premium_data.get(b'stripe_product_id', b'prod_migrated').decode('utf-8'),
                                status='active',
                                plan_name='Premium (Migrated)',
                                billing_cycle='one_time',
                                amount_cents=499,  # $4.99
                                currency='USD',
                                current_period_start=datetime.utcnow(),
                                current_period_end=expires_at,
                                premium_expires_at=expires_at,
                                metadata={'migrated_from_redis': True}
                            )
                            
                            db.add(subscription)
                            db.flush()
                        
                        migrated += 1
                        
                    except Exception as e:
                        errors += 1
                        error_msg = f"Failed to migrate subscription {key}: {e}"
                        logger.error(error_msg)
                        error_details.append(error_msg)
                
                if not dry_run:
                    db.commit()
            
            self.migrated_counts['subscriptions'] = migrated
            logger.info(f"Subscription migration completed: {migrated} migrated, {errors} errors")
            
            return {
                'migrated': migrated,
                'errors': errors,
                'error_details': error_details[:10]
            }
            
        except Exception as e:
            logger.error(f"Subscription migration failed: {e}")
            return {
                'migrated': migrated,
                'errors': errors + 1,
                'error_details': [str(e)]
            }
    
    async def migrate_usage_tracking(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate usage tracking data from Redis"""
        logger.info("Migrating usage tracking from Redis...")
        
        migrated = 0
        errors = 0
        error_details = []
        
        try:
            # Get usage tracking keys
            usage_keys = await self.redis_client.keys("usage:*")
            rate_limit_keys = await self.redis_client.keys("rate_limit:*")
            
            all_keys = usage_keys + rate_limit_keys
            logger.info(f"Found {len(all_keys)} usage tracking records in Redis")
            
            with get_db_session() as db:
                for key in all_keys:
                    try:
                        usage_data = await self.redis_client.hgetall(key)
                        if not usage_data:
                            continue
                        
                        key_str = key.decode('utf-8')
                        parts = key_str.split(':')
                        
                        if len(parts) >= 3:
                            ip_or_user = parts[1]
                            endpoint = parts[2] if len(parts) > 2 else 'unknown'
                            
                            # Check if this is an IP or user ID
                            user_id = None
                            ip_address = None
                            
                            try:
                                # Try to parse as UUID (user_id)
                                import uuid
                                uuid.UUID(ip_or_user)
                                user_id = ip_or_user
                            except:
                                # Treat as IP address
                                ip_address = ip_or_user
                            
                            if not dry_run:
                                usage_record = UsageTracking(
                                    user_id=user_id,
                                    ip_address=ip_address,
                                    endpoint=endpoint,
                                    action='generate_thread',
                                    daily_count=int(usage_data.get(b'daily_count', b'1')),
                                    monthly_count=int(usage_data.get(b'monthly_count', b'1')),
                                    date_bucket=datetime.utcnow().date(),
                                    month_bucket=datetime.utcnow().replace(day=1).date(),
                                    metadata={'migrated_from_redis': True}
                                )
                                
                                db.add(usage_record)
                                db.flush()
                            
                            migrated += 1
                        
                    except Exception as e:
                        errors += 1
                        error_msg = f"Failed to migrate usage tracking {key}: {e}"
                        logger.error(error_msg)
                        error_details.append(error_msg)
                
                if not dry_run:
                    db.commit()
            
            self.migrated_counts['usage_tracking'] = migrated
            logger.info(f"Usage tracking migration completed: {migrated} migrated, {errors} errors")
            
            return {
                'migrated': migrated,
                'errors': errors,
                'error_details': error_details[:10]
            }
            
        except Exception as e:
            logger.error(f"Usage tracking migration failed: {e}")
            return {
                'migrated': migrated,
                'errors': errors + 1,
                'error_details': [str(e)]
            }
    
    async def migrate_sessions(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate session data from Redis"""
        logger.info("Migrating sessions from Redis...")
        
        migrated = 0
        errors = 0
        
        try:
            # Sessions in Redis are typically stored with expiration
            # We'll migrate any that exist but they may expire soon
            session_keys = await self.redis_client.keys("session:*")
            logger.info(f"Found {len(session_keys)} session records in Redis")
            
            # Note: Sessions are temporary by nature, so we'll just log the count
            # In practice, new sessions will be created in PostgreSQL going forward
            
            return {
                'migrated': 0,  # Sessions not migrated - they're temporary
                'errors': 0,
                'note': f'Found {len(session_keys)} sessions in Redis - these will expire naturally'
            }
            
        except Exception as e:
            logger.error(f"Session migration check failed: {e}")
            return {'migrated': 0, 'errors': 1, 'error_details': [str(e)]}
    
    async def migrate_email_list(self, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate email list from Redis"""
        logger.info("Migrating email list from Redis...")
        
        migrated = 0
        errors = 0
        
        try:
            # Get all emails from the set
            emails = await self.redis_client.smembers("email_list")
            logger.info(f"Found {len(emails)} emails in Redis email list")
            
            # Store in metadata table or log for manual processing
            # This would typically go to a separate email marketing system
            
            if emails and not dry_run:
                # Could create a simple email_list table or export to CSV
                email_list = [email.decode('utf-8') for email in emails]
                logger.info(f"Email list for export: {len(email_list)} addresses")
                
                # For now, just log - in practice you'd export to marketing tool
                with open('/tmp/migrated_emails.txt', 'w') as f:
                    for email in email_list:
                        f.write(f"{email}\n")
                
                migrated = len(email_list)
            
            return {
                'migrated': migrated,
                'errors': errors,
                'note': 'Emails exported to file for marketing system import'
            }
            
        except Exception as e:
            logger.error(f"Email list migration failed: {e}")
            return {'migrated': 0, 'errors': 1, 'error_details': [str(e)]}

# ============================================================================
# MIGRATION COMMANDS
# ============================================================================

async def run_full_migration(dry_run: bool = False) -> Dict[str, Any]:
    """Run complete migration from Redis to PostgreSQL"""
    logger.info("Starting full database migration...")
    
    # Initialize migrator
    migrator = DatabaseMigrator()
    redis_migrator = RedisToPostgresMigrator()
    
    try:
        # Step 1: Ensure database schema is up to date
        logger.info("Step 1: Checking database schema...")
        if not migrator.check_table_exists('users'):
            logger.info("Creating database tables...")
            if not migrator.create_all_tables():
                raise Exception("Failed to create database tables")
        
        # Step 2: Create schema version tracking
        migrator.create_schema_version_table()
        
        # Step 3: Migrate data from Redis
        logger.info("Step 2: Migrating data from Redis...")
        migration_results = await redis_migrator.migrate_all_data(dry_run)
        
        # Step 4: Record migration completion
        if not dry_run and migration_results.get('success'):
            migrator.record_migration("1.0.0", "Initial migration from Redis to PostgreSQL")
        
        logger.info("Full migration completed successfully")
        return {
            'success': True,
            'schema_created': True,
            'data_migration': migration_results
        }
        
    except Exception as e:
        logger.error(f"Full migration failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ============================================================================
# VALIDATION
# ============================================================================

def validate_migration() -> Dict[str, Any]:
    """Validate that migration completed successfully"""
    logger.info("Validating migration...")
    
    validation_results = {}
    
    try:
        with get_db_session() as db:
            # Count records in each table
            validation_results['user_count'] = db.query(User).count()
            validation_results['thread_count'] = db.query(Thread).count()
            validation_results['subscription_count'] = db.query(Subscription).count()
            validation_results['usage_tracking_count'] = db.query(UsageTracking).count()
            
            # Check for data integrity
            users_with_threads = db.execute(text("""
                SELECT COUNT(DISTINCT u.id) 
                FROM users u 
                JOIN threads t ON u.id = t.user_id
            """)).scalar()
            
            validation_results['users_with_threads'] = users_with_threads
            validation_results['orphaned_threads'] = validation_results['thread_count'] - users_with_threads
            
            # Check subscription data
            active_subscriptions = db.query(Subscription).filter(
                Subscription.status == 'active'
            ).count()
            validation_results['active_subscriptions'] = active_subscriptions
            
            logger.info(f"Migration validation: {validation_results}")
            return {
                'success': True,
                'validation_results': validation_results
            }
            
    except Exception as e:
        logger.error(f"Migration validation failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
# Redis to PostgreSQL Migration Guide for Threadr

## 🎯 Executive Summary

This guide provides a comprehensive, production-ready migration strategy to move Threadr's data from Redis to PostgreSQL while maintaining **zero downtime** and **no data loss**. The migration preserves all critical business data including premium subscriptions, user data, and usage analytics.

### Critical Business Impact
- **💰 Revenue Protection**: All premium user subscriptions preserved
- **📊 Analytics Continuity**: Usage tracking and metrics maintained  
- **🔒 Zero Downtime**: Dual-write strategy ensures continuous service
- **🛡️ Rollback Ready**: Full rollback capability if issues arise

## 📋 Pre-Migration Checklist

### 1. Environment Verification
```bash
# Verify database connections
cd backend/
python -c "import os; print('REDIS_URL:', bool(os.getenv('REDIS_URL')))"
python -c "import os; print('DATABASE_URL:', bool(os.getenv('DATABASE_URL')))"

# Test connections
python -c "
import asyncio
import asyncpg
import redis
import os

async def test_connections():
    # Test PostgreSQL
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.execute('SELECT 1')
        await conn.close()
        print('✅ PostgreSQL: Connected')
    except Exception as e:
        print(f'❌ PostgreSQL: {e}')
    
    # Test Redis
    try:
        r = redis.from_url(os.getenv('REDIS_URL'))
        r.ping()
        print('✅ Redis: Connected')
    except Exception as e:
        print(f'❌ Redis: {e}')

asyncio.run(test_connections())
"
```

### 2. Database Schema Initialization
```bash
# Ensure PostgreSQL schema is up to date
psql $DATABASE_URL -f database_schema.sql
```

### 3. Backup Creation
```bash
# Create database backup
pg_dump $DATABASE_URL > "threadr_pre_migration_$(date +%Y%m%d_%H%M%S).sql"

# Create Redis backup (optional but recommended)
redis-cli --rdb "redis_backup_$(date +%Y%m%d_%H%M%S).rdb"
```

## 🔍 Phase 1: Data Audit

Run the Redis audit tool to understand current data volumes:

```bash
cd backend/scripts/
python redis_audit.py
```

**Expected Output:**
- Total Redis keys and distribution
- Premium user counts (CRITICAL for revenue)
- Email subscription volumes
- Usage tracking data volumes
- Memory usage analysis
- Migration priority assessment

**⚠️ STOP CONDITIONS:**
- If audit shows >50K premium users, consider staged migration
- If Redis memory >2GB, plan for extended migration time
- If any critical data patterns missing, investigate before proceeding

## 🗺️ Phase 2: Migration Mapping Analysis

Analyze how Redis data maps to PostgreSQL:

```bash
python migration_mapping.py
```

This generates:
- `redis_postgres_mapping_[timestamp].json` - Detailed mapping documentation
- Validation rules for each data type
- Dependency analysis between different data patterns
- Migration complexity assessment

**Key Mappings:**
- `threadr:premium:*` → `subscriptions` table (CRITICAL)
- `threadr:email:*` → `users` table (HIGH)
- `threadr:usage:*` → `usage_tracking` table (HIGH)
- `threadr:cache:*` → `threads` table (MEDIUM)

## 🚀 Phase 3: Zero-Downtime Migration Execution

### 3.1 Enable Dual-Write Mode

**⚠️ IMPORTANT**: This step starts writing to both Redis and PostgreSQL. Do not proceed unless you're ready to commit to the migration.

```bash
# Start dual-write mode (writes to both systems)
python dual_write_service.py
```

### 3.2 Migrate Existing Data

Run the migration with comprehensive validation:

```bash
# DRY RUN FIRST (highly recommended)
python redis_to_postgres_migration.py --dry-run --priority critical

# Review dry run output, then run actual migration
python redis_to_postgres_migration.py --priority critical --batch-size 100

# If critical data migration successful, continue with high priority
python redis_to_postgres_migration.py --priority high --batch-size 100

# Continue with remaining priorities
python redis_to_postgres_migration.py --priority medium --batch-size 100
python redis_to_postgres_migration.py --priority low --batch-size 100
```

**Migration Parameters:**
- `--dry-run`: Test migration without making changes
- `--priority [critical|high|medium|low]`: Migrate specific priority level
- `--batch-size 100`: Process 100 records at a time
- `--table [table_name]`: Migrate specific table only
- `--continue-on-error`: Continue if non-critical errors occur
- `--no-rollback`: Disable automatic rollback (not recommended)

### 3.3 Validation Phase

After each priority level, validate data integrity:

```bash
# Validate critical data (premium subscriptions)
python -c "
import asyncio
import asyncpg
import os

async def validate_premium_data():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Check subscription counts
    total_subs = await conn.fetchval('SELECT COUNT(*) FROM subscriptions')
    active_subs = await conn.fetchval('SELECT COUNT(*) FROM subscriptions WHERE status = \\'active\\'')
    premium_subs = await conn.fetchval('SELECT COUNT(*) FROM subscriptions WHERE premium_expires_at > NOW()')
    
    print(f'📊 Subscription Validation:')
    print(f'  Total subscriptions: {total_subs}')
    print(f'  Active subscriptions: {active_subs}')
    print(f'  Premium (not expired): {premium_subs}')
    
    # Check user counts
    total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
    print(f'  Total users: {total_users}')
    
    await conn.close()

asyncio.run(validate_premium_data())
"
```

## 🔄 Phase 4: Production Cutover

### 4.1 Switch to PostgreSQL Primary

```bash
# Update application configuration to use PostgreSQL as primary
# This should be done via environment variables or configuration management

# For testing, you can switch the dual-write service:
python -c "
import asyncio
from scripts.dual_write_service import dual_write_service, WriteStrategy

async def switch_to_postgres_primary():
    async with dual_write_service(WriteStrategy.POSTGRES_PRIMARY) as service:
        # Test critical operations
        access = await service.check_premium_access('test@example.com', 'email')
        stats = await service.get_usage_stats('192.168.1.1', 'ip')
        print(f'✅ PostgreSQL primary mode: Premium check = {access}, Usage = {stats}')

asyncio.run(switch_to_postgres_primary())
"
```

### 4.2 Monitor Performance

```bash
# Monitor PostgreSQL performance
psql $DATABASE_URL -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
  pg_stat_get_tuples_inserted(pg_class.oid) as inserts,
  pg_stat_get_tuples_updated(pg_class.oid) as updates
FROM pg_tables 
JOIN pg_class ON pg_tables.tablename = pg_class.relname
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Check application health
curl -s https://threadr-pw0s.onrender.com/health | jq '.database'
```

### 4.3 Gradual Redis Phase-Out

```bash
# Week 1: PostgreSQL primary, Redis backup
# Week 2: Monitor for any issues
# Week 3: Switch to PostgreSQL only (still keep Redis running)
# Week 4: If stable, can stop using Redis for new operations
```

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Migration Fails with Validation Errors

```bash
# Check specific validation errors
python redis_to_postgres_migration.py --validate-only --priority critical

# Fix common issues:
# - Invalid email formats: Update email validation rules
# - Missing user IDs: Ensure user creation runs first
# - Date format issues: Check datetime parsing in transformers
```

#### 2. Partial Data Migration

```bash
# Check what was migrated successfully
psql $DATABASE_URL -c "
SELECT 
  'subscriptions' as table, COUNT(*) as migrated_count
FROM subscriptions 
WHERE metadata->>'source' LIKE '%redis%'
UNION ALL
SELECT 
  'users' as table, COUNT(*) as migrated_count  
FROM users
WHERE metadata->>'source' LIKE '%redis%'
UNION ALL
SELECT
  'usage_tracking' as table, COUNT(*) as migrated_count
FROM usage_tracking
WHERE metadata->>'source' LIKE '%redis%';
"

# Re-run specific failed patterns
python redis_to_postgres_migration.py --pattern "threadr:premium:email:*" --continue-on-error
```

#### 3. Performance Issues

```bash
# Check database performance
psql $DATABASE_URL -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
"

# Optimize if needed
psql $DATABASE_URL -c "
VACUUM ANALYZE subscriptions;
VACUUM ANALYZE users;  
VACUUM ANALYZE usage_tracking;
"
```

#### 4. Rollback Required

```bash
# Automatic rollback (if migration fails)
# The migration tool automatically rolls back on critical failures

# Manual rollback (if needed)
python -c "
import asyncio
import asyncpg
import os

async def manual_rollback():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Remove migrated records (identified by metadata source)
    tables = ['subscriptions', 'users', 'usage_tracking', 'analytics_timeseries', 'threads']
    
    for table in tables:
        try:
            deleted = await conn.execute(f'''
                DELETE FROM {table} 
                WHERE metadata->>'source' IN ('redis_ip_premium', 'redis_email_premium', 'redis_user_subscription', 'redis_email_subscription')
            ''')
            print(f'Rolled back {table}: {deleted}')
        except Exception as e:
            print(f'Rollback error for {table}: {e}')
    
    await conn.close()

asyncio.run(manual_rollback())
"
```

## 📊 Success Metrics

### Migration Success Indicators

1. **Data Integrity** ✅
   - All premium users can access premium features
   - Usage limits are correctly enforced
   - No data loss reported by users

2. **Performance** ✅
   - API response times remain under 500ms
   - Database queries complete within acceptable limits
   - No increase in error rates

3. **Business Continuity** ✅
   - Revenue recognition continues uninterrupted
   - New premium purchases work correctly
   - Analytics and reporting remain accurate

### Key Metrics to Monitor

```bash
# Daily monitoring queries
psql $DATABASE_URL -c "
-- Check daily active premium users
SELECT COUNT(DISTINCT user_id) as active_premium_users
FROM subscriptions 
WHERE status = 'active' AND premium_expires_at > NOW();

-- Check daily thread generation volume
SELECT DATE(first_request_at) as date, SUM(daily_count) as threads_generated
FROM usage_tracking 
WHERE first_request_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(first_request_at)
ORDER BY date DESC;

-- Check for any orphaned data
SELECT 
  'orphaned_subscriptions' as issue,
  COUNT(*) as count
FROM subscriptions s
WHERE s.user_id IS NOT NULL 
  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = s.user_id)
UNION ALL
SELECT 
  'usage_without_users' as issue,
  COUNT(*) as count
FROM usage_tracking ut
WHERE ut.user_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = ut.user_id);
"
```

## 🔒 Security Considerations

1. **Data Privacy**: All PII remains encrypted during migration
2. **Access Control**: Migration scripts run with minimal required permissions
3. **Audit Trail**: Complete log of all migration operations
4. **Rollback Security**: Rollback capability doesn't expose sensitive data

## 📅 Maintenance Schedule

### Post-Migration Tasks

**Week 1:**
- Daily validation of critical business metrics
- Monitor application performance and error rates
- Validate that new premium purchases work correctly

**Week 2:**
- Reduce Redis usage monitoring
- Performance optimization if needed
- User acceptance testing

**Week 3:**  
- Consider switching to PostgreSQL-only mode
- Clean up any temporary migration data
- Update documentation and runbooks

**Week 4:**
- Final validation of all business processes
- Archive Redis backups (keep for 30 days minimum)
- Document lessons learned

## 🆘 Emergency Contacts and Escalation

### Critical Issues (Revenue Impact)
- **Immediate**: Check rollback options
- **Contact**: Development team lead
- **SLA**: 15-minute response time for revenue-impacting issues

### Data Integrity Issues  
- **Immediate**: Stop new migrations, assess scope
- **Contact**: Database administrator
- **SLA**: 30-minute response time

### Performance Issues
- **Immediate**: Monitor resource usage, consider scaling
- **Contact**: DevOps team
- **SLA**: 1-hour response time

## 📖 Additional Resources

- `redis_audit.py` - Data audit and analysis tool
- `migration_mapping.py` - Schema mapping and transformation logic
- `redis_to_postgres_migration.py` - Main migration execution tool
- `dual_write_service.py` - Zero-downtime dual-write implementation
- `database_schema.sql` - Complete PostgreSQL schema
- Migration logs - Generated automatically in `migration_*.log`

---

**⚠️ FINAL REMINDER**: This migration affects critical business data. Always run dry-run first, validate thoroughly, and have rollback procedures ready. Test in a staging environment if possible before production migration.
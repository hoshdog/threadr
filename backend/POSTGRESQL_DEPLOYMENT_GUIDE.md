# PostgreSQL Database Deployment Guide for Threadr

## Overview

This guide covers the complete deployment of Threadr's PostgreSQL database schema, migration from Redis, and operational procedures. The system is designed for production reliability with proper backup strategies, monitoring, and disaster recovery.

## 🚨 CRITICAL: Current Status

**Current Production Reality (August 7, 2025):**
- ✅ **Live Production**: https://threadr-plum.vercel.app (Next.js frontend)
- ✅ **Backend API**: https://threadr-pw0s.onrender.com (FastAPI on Render.com)
- ⚠️ **Database**: Currently Redis-only with 30-day TTL (DATA LOSS RISK!)
- 🚨 **Immediate Need**: PostgreSQL deployment to prevent data loss

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Schema Deployment](#schema-deployment)
4. [Data Migration](#data-migration)
5. [Application Configuration](#application-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Backup Strategy](#backup-strategy)
8. [Disaster Recovery](#disaster-recovery)
9. [Operational Procedures](#operational-procedures)

## Prerequisites

### Required Software
```bash
# PostgreSQL 15 or later
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15 postgresql-client-15

# Python dependencies (add to requirements.txt)
pip install sqlalchemy[postgresql] asyncpg psycopg2-binary alembic

# Backup tools
sudo apt install postgresql-client-common
```

### System Requirements
- **Memory**: Minimum 4GB RAM, recommended 8GB+ for production
- **Storage**: Minimum 20GB, recommended 100GB+ with SSD for performance
- **CPU**: Minimum 2 cores, recommended 4+ cores
- **Network**: Reliable connection between app servers and database

## Database Setup

### 1. PostgreSQL Installation & Configuration

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Secure installation
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_secure_password';"
```

#### Production Configuration (`postgresql.conf`)
```ini
# Memory settings
shared_buffers = 256MB                # 25% of RAM for dedicated server
effective_cache_size = 1GB            # 75% of RAM
work_mem = 4MB                        # Per-connection memory
maintenance_work_mem = 64MB           # For maintenance operations

# Connection settings
max_connections = 200                 # Adjust based on app pool size
listen_addresses = '*'                # Or specific IPs
port = 5432

# Logging for monitoring
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000     # Log slow queries (1 second)

# Performance
checkpoint_timeout = 10min
checkpoint_completion_target = 0.9
wal_buffers = 16MB
random_page_cost = 1.1                # For SSD storage

# Replication (if needed)
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB
```

#### Authentication Configuration (`pg_hba.conf`)
```ini
# Database administrative login by Unix domain socket
local   all             postgres                                peer

# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             threadr                                 md5
host    all             threadr         127.0.0.1/32            md5
host    all             threadr         10.0.0.0/8              md5  # Private network
host    all             threadr         172.16.0.0/12           md5  # Docker networks

# Replication connections
host    replication     replicator      10.0.0.0/8              md5
```

### 2. Database and User Creation

```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE threadr;
CREATE USER threadr WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE threadr TO threadr;
ALTER USER threadr CREATEDB;  -- For testing databases

-- Connect to threadr database
\c threadr

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO threadr;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO threadr;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO threadr;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO threadr;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO threadr;
```

## Schema Deployment

### 1. Deploy Schema

```bash
# Navigate to backend directory
cd backend

# Run schema creation
psql -U threadr -d threadr -h localhost < database_schema.sql

# Verify tables were created
psql -U threadr -d threadr -c "\dt"
```

### 2. Verify Schema

```sql
-- Check table structure
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check indexes
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Verify constraints
SELECT conname, contype, conrelid::regclass AS table_name
FROM pg_constraint 
WHERE connamespace = 'public'::regnamespace;
```

## Data Migration

### 1. Pre-Migration Checklist

- [ ] PostgreSQL schema deployed successfully
- [ ] Redis backup created
- [ ] Application in maintenance mode (if applicable)
- [ ] Monitoring systems notified

### 2. Run Migration

```bash
# Dry run first to check data
python database_operations.py migrate --dry-run

# Review output, then run actual migration
python database_operations.py migrate

# Validate migration
python database_operations.py validate
```

### 3. Migration Script Usage

```bash
# Create backup before migration
python database_operations.py backup --type full

# Run full migration
python database_operations.py migrate

# Validate data integrity
python database_operations.py validate

# Health check
python database_operations.py health
```

## Application Configuration

### 1. Environment Variables

```bash
# Required database settings
DATABASE_URL=postgresql://threadr:password@localhost:5432/threadr
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_REQUIRE_SSL=true

# Optional performance tuning
DB_STATEMENT_TIMEOUT=30000
DB_IDLE_TIMEOUT=300000
DB_ENABLE_QUERY_LOGGING=false
DB_SLOW_QUERY_THRESHOLD=1.0

# Backup settings
BACKUP_RETENTION_DAYS=30
MAX_BACKUP_COUNT=50
```

### 2. FastAPI Integration

```python
# Update main.py
from src.database.config import get_db, check_database_connection
from src.database.models import User, Thread, Subscription
from sqlalchemy.orm import Session
from fastapi import Depends

# Add health check endpoint
@app.get("/health/database")
async def database_health():
    return {
        "database_connected": check_database_connection(),
        "database_info": get_database_info()
    }

# Update existing endpoints to use PostgreSQL
@app.get("/api/threads")
async def get_threads(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    threads = db.query(Thread).filter(
        Thread.user_id == current_user["user_id"]
    ).order_by(Thread.created_at.desc()).all()
    
    return [thread.to_dict() for thread in threads]
```

### 3. Update Requirements.txt

Add these PostgreSQL dependencies:
```txt
# PostgreSQL database support
sqlalchemy[postgresql]==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.13.0

# Database monitoring
psutil==5.9.6
```

## Monitoring Setup

### 1. Application Monitoring

```python
# Add to FastAPI startup
@app.on_event("startup")
async def startup_event():
    # Initialize database monitoring
    if not check_database_connection():
        logger.error("Database connection failed on startup")
        raise Exception("Database not available")
    
    # Log connection info
    db_info = get_database_info()
    logger.info(f"Connected to PostgreSQL: {db_info}")
```

### 2. System Monitoring Scripts

```bash
# Create monitoring cron jobs
# /etc/cron.d/threadr-monitoring

# Health check every 5 minutes
*/5 * * * * /usr/local/bin/python3 /app/database_operations.py health --output /var/log/threadr/health.json

# Daily backup at 2 AM
0 2 * * * /usr/local/bin/python3 /app/database_operations.py backup --type full

# Weekly maintenance on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/python3 /app/database_operations.py maintenance

# Monthly full report
0 4 1 * * /usr/local/bin/python3 /app/database_operations.py monitor --output /var/log/threadr/monthly-report.json
```

### 3. Alert Thresholds

```bash
# Monitoring thresholds (adjust as needed)
CONNECTION_USAGE_ALERT=80%
REPLICATION_LAG_ALERT=60s
SLOW_QUERY_ALERT=5s
DISK_USAGE_ALERT=85%
MEMORY_USAGE_ALERT=90%
```

## Backup Strategy

### 1. Automated Backup Schedule

```bash
# Daily incremental backups
0 1 * * * /usr/local/bin/python3 /app/database_operations.py backup --type data

# Weekly full backups
0 2 * * 0 /usr/local/bin/python3 /app/database_operations.py backup --type full

# Monthly schema backups
0 3 1 * * /usr/local/bin/python3 /app/database_operations.py backup --type schema
```

### 2. Backup Verification

```bash
# Test restore process (monthly)
#!/bin/bash
# /scripts/test_backup.sh

LATEST_BACKUP=$(ls -t /backups/threadr/threadr_full_*.dump | head -n1)
if [ -n "$LATEST_BACKUP" ]; then
    echo "Testing backup restore: $LATEST_BACKUP"
    # Create test database
    createdb -U postgres threadr_test
    # Restore to test database
    pg_restore -U postgres -d threadr_test "$LATEST_BACKUP"
    # Verify restore
    psql -U postgres -d threadr_test -c "SELECT COUNT(*) FROM users;"
    # Cleanup
    dropdb -U postgres threadr_test
    echo "Backup test completed successfully"
fi
```

### 3. Remote Backup Storage

```bash
# S3 backup sync (if using AWS)
#!/bin/bash
# /scripts/backup_to_s3.sh

BACKUP_DIR="/backups/threadr"
S3_BUCKET="s3://your-backup-bucket/threadr"

# Sync to S3 with encryption
aws s3 sync "$BACKUP_DIR" "$S3_BUCKET" \
    --exclude "*.tmp" \
    --storage-class STANDARD_IA \
    --server-side-encryption AES256

# Cleanup old S3 backups (keep 90 days)
aws s3 ls "$S3_BUCKET" --recursive | \
    awk '$1 < "'$(date -d '90 days ago' '+%Y-%m-%d')'" {print $4}' | \
    xargs -I {} aws s3 rm "$S3_BUCKET/{}"
```

## Disaster Recovery

### 1. Recovery Time Objectives (RTO/RPO)

- **RPO (Recovery Point Objective)**: 1 hour (maximum data loss)
- **RTO (Recovery Time Objective)**: 4 hours (maximum downtime)

### 2. Disaster Recovery Procedures

#### Complete Database Loss
```bash
# 1. Provision new database server
# 2. Install PostgreSQL and configure
# 3. Restore from latest backup

# Get latest backup
LATEST_BACKUP=$(ls -t /backups/threadr/threadr_full_*.dump | head -n1)

# Create database
createdb -U postgres threadr

# Restore data
python database_operations.py restore "$LATEST_BACKUP" --confirm

# Verify restore
python database_operations.py validate

# Update application configuration
# Restart application services
```

#### Partial Data Loss
```sql
-- If specific tables are affected, restore individual tables
pg_restore -U threadr -d threadr -t threads /path/to/backup.dump
```

### 3. Replication Setup (High Availability)

#### Primary Server Configuration
```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB
synchronous_commit = on
synchronous_standby_names = 'standby1'
```

#### Standby Server Setup
```bash
# Create replication user on primary
psql -U postgres -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replication_password';"

# Setup standby server
pg_basebackup -h primary_server -U replicator -D /var/lib/postgresql/15/main -P -W

# Configure recovery
echo "standby_mode = 'on'" >> /var/lib/postgresql/15/main/recovery.conf
echo "primary_conninfo = 'host=primary_server user=replicator password=replication_password'" >> /var/lib/postgresql/15/main/recovery.conf
```

## Operational Procedures

### 1. Daily Operations

```bash
#!/bin/bash
# /scripts/daily_operations.sh

echo "=== Daily Database Operations ==="
echo "Date: $(date)"

# Health check
echo "Running health check..."
python3 /app/database_operations.py health

# Cleanup expired data
echo "Running maintenance..."
python3 /app/database_operations.py maintenance --tasks cleanup_sessions cleanup_invites

# Check backup status
echo "Checking backup status..."
python3 /app/database_operations.py list-backups | head -5

# Check replication lag (if applicable)
echo "Checking replication status..."
psql -U threadr -d threadr -c "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;" 2>/dev/null || echo "No replication configured"

echo "=== Daily operations completed ==="
```

### 2. Weekly Operations

```bash
#!/bin/bash
# /scripts/weekly_operations.sh

echo "=== Weekly Database Operations ==="

# Full backup
echo "Creating weekly full backup..."
python3 /app/database_operations.py backup --type full

# Analyze database statistics
echo "Updating table statistics..."
python3 /app/database_operations.py maintenance --tasks analyze

# Generate monitoring report
echo "Generating weekly report..."
python3 /app/database_operations.py monitor --output "/var/log/threadr/weekly-report-$(date +%Y%m%d).json"

# Check table growth and recommend optimizations
psql -U threadr -d threadr -c "
SELECT 
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    CASE WHEN n_live_tup > 0 THEN (n_dead_tup::float / n_live_tup * 100)::int ELSE 0 END as dead_row_percent
FROM pg_stat_user_tables 
WHERE n_live_tup > 1000
ORDER BY dead_row_percent DESC;
"

echo "=== Weekly operations completed ==="
```

### 3. Emergency Procedures

#### High Connection Usage
```bash
# Check active connections
psql -U threadr -d threadr -c "
SELECT state, count(*) 
FROM pg_stat_activity 
GROUP BY state;
"

# Kill idle connections if needed
psql -U threadr -d threadr -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND now() - state_change > interval '1 hour';
"
```

#### Slow Queries
```bash
# Identify slow queries
psql -U threadr -d threadr -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Kill specific query by PID (if needed)
psql -U threadr -d threadr -c "SELECT pg_terminate_backend(12345);"
```

#### Disk Space Issues
```bash
# Check database size
psql -U threadr -d threadr -c "
SELECT pg_size_pretty(pg_database_size('threadr')) as database_size;
"

# Check table sizes
psql -U threadr -d threadr -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Emergency cleanup if needed
python3 /app/database_operations.py maintenance --tasks vacuum
```

## Production Deployment Checklist

### Pre-Deployment
- [ ] PostgreSQL server provisioned and configured
- [ ] Database user and permissions configured
- [ ] SSL certificates configured (if required)
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented and tested

### Deployment
- [ ] Schema deployed successfully
- [ ] Data migration completed and validated
- [ ] Application configuration updated
- [ ] Connection pooling configured
- [ ] Health checks passing

### Post-Deployment
- [ ] Performance baseline established
- [ ] Monitoring dashboards configured
- [ ] Backup and restore procedures tested
- [ ] Emergency procedures documented and tested
- [ ] Team trained on new procedures

## Security Considerations

### 1. Access Control
```sql
-- Create read-only user for reporting
CREATE USER threadr_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE threadr TO threadr_readonly;
GRANT USAGE ON SCHEMA public TO threadr_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO threadr_readonly;
```

### 2. Connection Security
```bash
# Force SSL connections
echo "hostssl all threadr 0.0.0.0/0 md5" >> /etc/postgresql/15/main/pg_hba.conf
echo "ssl = on" >> /etc/postgresql/15/main/postgresql.conf
```

### 3. Audit Logging
```sql
-- Enable audit logging for sensitive operations
CREATE EXTENSION IF NOT EXISTS pgaudit;
ALTER SYSTEM SET pgaudit.log = 'ddl,role,read,write';
SELECT pg_reload_conf();
```

## Performance Tuning

### 1. Query Optimization
```sql
-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Monitor slow queries
SELECT query, calls, total_time, mean_time, rows 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### 2. Index Maintenance
```sql
-- Check unused indexes
SELECT s.schemaname, s.tablename, s.indexname, s.idx_tup_read, s.idx_tup_fetch
FROM pg_stat_user_indexes s
JOIN pg_index i ON s.indexrelid = i.indexrelid
WHERE s.idx_tup_read = 0 AND s.idx_tup_fetch = 0
AND NOT i.indisunique;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

This deployment guide provides a comprehensive foundation for migrating Threadr from Redis to PostgreSQL with production-grade reliability, monitoring, and disaster recovery capabilities.
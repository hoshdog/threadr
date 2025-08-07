# 🚀 RENDER POSTGRESQL SETUP GUIDE FOR THREADR

**IMPORTANT**: This guide will walk you through setting up PostgreSQL on Render.com for your Threadr backend. Since your backend is already on Render, this keeps everything in one place with low latency.

---

## 📋 STEP 1: Create PostgreSQL Database on Render

### Via Render Dashboard:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"PostgreSQL"**
3. **Configure Database**:
   - **Name**: `threadr-db` (or your preference)
   - **Database**: `threadr_production`
   - **User**: (auto-generated, keep it)
   - **Region**: Same as your backend (likely Oregon)
   - **PostgreSQL Version**: 15 (latest stable)
   - **Plan**: 
     - Start with **Free** tier for testing
     - Upgrade to **Starter** ($7/month) for production
4. **Click "Create Database"**
5. **Wait** for database to be created (2-3 minutes)

### Database Details You'll Get:
```
Hostname: dpg-xxxxx.oregon-postgres.render.com
Port: 5432
Database: threadr_production
Username: threadr_user_xxxx
Password: [auto-generated]
Internal URL: postgresql://threadr_user:password@dpg-xxxxx/threadr_production
External URL: postgresql://threadr_user:password@dpg-xxxxx.oregon-postgres.render.com/threadr_production
```

---

## 📋 STEP 2: Update Your Backend Environment Variables

### In Render Dashboard:

1. **Go to your Backend Service** (threadr-backend)
2. **Click "Environment"** tab
3. **Add these environment variables**:

```bash
# Database Configuration
DATABASE_URL=[Internal Database URL from Step 1]
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false

# IMPORTANT: Change this to false once DB is ready
BYPASS_DATABASE=false

# Keep existing variables
REDIS_URL=[your existing Redis URL]
JWT_SECRET_KEY=[your existing JWT secret]
STRIPE_SECRET_KEY=[your existing Stripe key]
OPENAI_API_KEY=[your existing OpenAI key]
```

**CRITICAL**: Use the **Internal Database URL** (starts with `postgresql://`) not the external one for better performance!

---

## 📋 STEP 3: Update Backend Requirements

Add these packages to `backend/requirements.txt`:

```txt
# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
asyncpg==0.29.0
alembic==1.13.0
```

---

## 📋 STEP 4: Initialize Database Schema

### Option A: Via Render Shell (Recommended)

1. **In Render Dashboard**, go to your backend service
2. Click **"Shell"** tab
3. Run these commands:

```bash
# Enter Python shell
python

# Initialize database
from src.database.config import init_db
init_db()
exit()
```

### Option B: Create an Init Script

Create `backend/src/init_db.py`:

```python
"""Initialize database schema."""
import asyncio
from database.config import init_db, engine
from database.models import Base

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database initialized successfully!")
```

Then add to your deployment:
```bash
python src/init_db.py
```

---

## 📋 STEP 5: Migrate Existing Data from Redis

Create `backend/src/migrate_redis_to_postgres.py`:

```python
"""Migrate existing Redis data to PostgreSQL."""
import os
import json
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database.config import SessionLocal
from database.models import User, Thread, Subscription
from core.redis_manager import RedisManager

def migrate_users(db: Session, redis_manager: RedisManager):
    """Migrate user data from Redis."""
    # Get all premium users from Redis
    premium_keys = redis_manager.client.keys("threadr:premium:*")
    
    for key in premium_keys:
        email = key.decode().split(":")[-1]
        expires_timestamp = redis_manager.client.get(key)
        
        # Create or update user
        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                username=email.split("@")[0],
                is_premium=True,
                premium_expires_at=datetime.fromtimestamp(int(expires_timestamp))
            )
            # Set a temporary password (user will need to reset)
            user.set_password("TemporaryPassword123!")
            db.add(user)
    
    db.commit()
    print(f"Migrated {len(premium_keys)} premium users")

def migrate_threads(db: Session, redis_manager: RedisManager):
    """Migrate thread data from Redis."""
    thread_keys = redis_manager.client.keys("threadr:thread:*")
    
    for key in thread_keys:
        thread_data = redis_manager.client.get(key)
        if thread_data:
            data = json.loads(thread_data)
            
            # Find user
            user = db.query(User).filter_by(email=data.get('user_email')).first()
            if user:
                thread = Thread(
                    user_id=user.id,
                    title=data.get('title', ''),
                    source_url=data.get('source_url'),
                    tweets=data.get('tweets', []),
                    tweet_count=len(data.get('tweets', [])),
                    created_at=datetime.fromtimestamp(data.get('created_at', 0))
                )
                db.add(thread)
    
    db.commit()
    print(f"Migrated {len(thread_keys)} threads")

def main():
    """Run migration."""
    print("Starting Redis to PostgreSQL migration...")
    
    # Initialize connections
    db = SessionLocal()
    redis_manager = RedisManager()
    redis_manager.initialize()
    
    try:
        # Run migrations
        migrate_users(db, redis_manager)
        migrate_threads(db, redis_manager)
        
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

---

## 📋 STEP 6: Update Backend Code to Use PostgreSQL

### Update `backend/src/main.py`:

Add database initialization to your lifespan handler:

```python
from contextlib import asynccontextmanager
from database.config import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting up Threadr backend...")
    
    # Initialize database
    if not os.getenv("BYPASS_DATABASE", "false").lower() == "true":
        init_db()
        logger.info("Database initialized")
    
    # Initialize Redis (keep existing)
    redis_manager.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    close_db()
```

### Update Authentication to Use Database:

```python
from sqlalchemy.orm import Session
from database import get_db
from database.models import User

@router.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check if user exists
    existing_user = db.query(User).filter_by(email=request.email).first()
    if existing_user:
        raise HTTPException(400, "User already exists")
    
    # Create new user
    user = User(
        email=request.email,
        username=request.username
    )
    user.set_password(request.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate JWT token
    access_token = create_access_token(user.id)
    
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username
        },
        "access_token": access_token
    }
```

---

## 📋 STEP 7: Test Database Connection

Create `backend/test_db_connection.py`:

```python
"""Test database connection."""
from database.config import engine

try:
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {conn.execute('SELECT version()').scalar()}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

Run in Render Shell:
```bash
python test_db_connection.py
```

---

## 📋 STEP 8: Setup Automatic Backups

### In Render Dashboard:

1. Go to your PostgreSQL database
2. Click **"Backups"** tab
3. Render automatically backs up:
   - **Free tier**: No automatic backups
   - **Paid tiers**: Daily backups with 7-day retention

### Manual Backup Script:

```bash
#!/bin/bash
# backup_render_db.sh

DATABASE_URL="your-external-database-url"
BACKUP_FILE="threadr_backup_$(date +%Y%m%d_%H%M%S).sql"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_FILE

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE s3://your-backup-bucket/

echo "Backup completed: $BACKUP_FILE"
```

---

## 📋 STEP 9: Monitor Database Performance

### Add Health Check Endpoint:

```python
@app.get("/api/health/database")
async def database_health():
    """Check database health."""
    from database.config import check_database_health
    return await check_database_health()
```

### Monitor in Render:

1. Go to PostgreSQL database in Render
2. Click **"Metrics"** tab
3. Monitor:
   - Connection count
   - CPU usage
   - Memory usage
   - Storage usage

---

## 🚨 IMPORTANT DEPLOYMENT CHECKLIST

### Before Deploying:

- [ ] **Backup Redis data** (just in case)
- [ ] **Test in development** first
- [ ] **Have rollback plan** ready

### Deployment Steps:

1. [ ] Create PostgreSQL database on Render
2. [ ] Add DATABASE_URL to environment variables
3. [ ] Deploy backend with new dependencies
4. [ ] Initialize database schema
5. [ ] Run migration script
6. [ ] Test all endpoints
7. [ ] Set `BYPASS_DATABASE=false`
8. [ ] Monitor for errors

### After Deployment:

- [ ] Verify user login works
- [ ] Test thread generation saves to DB
- [ ] Check subscription management
- [ ] Monitor database metrics
- [ ] Setup backup verification

---

## 🔧 TROUBLESHOOTING

### Connection Errors:
```
could not connect to server: Connection refused
```
**Solution**: Check DATABASE_URL is correct and using internal URL

### Migration Errors:
```
relation "users" already exists
```
**Solution**: Database already initialized, skip init step

### Performance Issues:
```
FATAL: too many connections
```
**Solution**: Reduce DB_POOL_SIZE or upgrade database plan

---

## 📊 MONITORING QUERIES

### Check Database Size:
```sql
SELECT pg_database_size('threadr_production') / 1024 / 1024 as size_mb;
```

### Active Connections:
```sql
SELECT count(*) FROM pg_stat_activity;
```

### Slow Queries:
```sql
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

---

## ✅ SUCCESS INDICATORS

You'll know everything is working when:

1. `/api/health/database` returns `{"status": "healthy"}`
2. User registration creates records in PostgreSQL
3. Thread generation saves to database
4. No more Redis TTL data loss warnings
5. Database metrics show active connections

---

## 🎯 NEXT STEPS

After PostgreSQL is working:

1. **Remove Redis-only code** - Clean up technical debt
2. **Add database indexes** - Optimize query performance
3. **Implement caching** - Use Redis for caching, not storage
4. **Setup replication** - For high availability (paid plans)
5. **Add monitoring** - Sentry or DataDog integration

---

**Need Help?** 
- Render Documentation: https://render.com/docs/databases
- PostgreSQL on Render: https://render.com/docs/postgresql
- Support: https://render.com/support

This setup will give you a production-ready PostgreSQL database that solves your data persistence issues while keeping everything in the Render ecosystem for optimal performance!
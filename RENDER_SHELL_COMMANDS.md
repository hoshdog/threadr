# 🚀 RENDER SHELL COMMANDS - POSTGRESQL SETUP

**IMPORTANT**: Follow these commands EXACTLY in your Render Shell to initialize your PostgreSQL database.

---

## 📋 STEP 1: Access Render Shell

1. Go to your Render Dashboard
2. Click on your **backend service** (threadr-backend)
3. Click on the **"Shell"** tab
4. Wait for the shell to load

---

## 📋 STEP 2: Navigate to Correct Directory

In the Render Shell, run:

```bash
# Check where you are
pwd

# Navigate to backend source directory
cd /opt/render/project/src/backend/src

# Verify you're in the right place
ls -la
```

You should see files like `main.py`, `init_database.py`, etc.

---

## 📋 STEP 3: Test Database Connection First

Run this command to test your database connection:

```bash
python test_db_connection.py
```

**Expected Output:**
```
✅ Connected successfully!
📊 PostgreSQL: 15.x
🗄️ Database: threadr_production
👤 User: threadr_user_xxxx
```

### If Connection Fails:

**Error: "DATABASE_URL not found"**
- Go to Environment tab
- Add DATABASE_URL with Internal Database URL
- Click "Save Changes"
- Wait for redeploy

**Error: "BYPASS_DATABASE is true"**
- Go to Environment tab
- Set BYPASS_DATABASE=false
- Click "Save Changes"
- Wait for redeploy

---

## 📋 STEP 4: Initialize Database Tables

Once connection test passes, run:

```bash
python init_database.py
```

**Expected Output:**
```
Starting Threadr database initialization...
✅ Database connection successful!
Creating database tables...
✅ Successfully created 11 tables:
  - analytics_timeseries
  - subscriptions
  - team_activities
  - team_invites
  - team_memberships
  - teams
  - thread_analytics
  - threads
  - usage_tracking
  - user_sessions
  - users
✅ DATABASE INITIALIZATION COMPLETE!
```

---

## 📋 STEP 5: Verify Tables Were Created

Run Python interactive shell to verify:

```bash
python
```

Then in Python shell:

```python
# Import database components
from database.config import engine
from sqlalchemy import text

# Check tables
with engine.connect() as conn:
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    tables = [row[0] for row in result]
    print(f"Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

# Check users table structure
with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'"))
    print("\nUsers table columns:")
    for row in result:
        print(f"  - {row[0]}: {row[1]}")

# Exit Python
exit()
```

---

## 📋 STEP 6: Create Test User (Optional)

If you want to create a test user:

```bash
python
```

Then in Python shell:

```python
from database.config import SessionLocal
from database.models import User
from datetime import datetime, timedelta

# Create session
db = SessionLocal()

# Create test user
test_user = User(
    email="test@threadr.app",
    username="testuser",
    is_premium=True,
    premium_expires_at=datetime.utcnow() + timedelta(days=30)
)
test_user.set_password("TestPassword123!")

# Save to database
db.add(test_user)
db.commit()

print(f"Created user: {test_user.email}")
print(f"User ID: {test_user.id}")

# Verify user was created
user_count = db.query(User).count()
print(f"Total users in database: {user_count}")

db.close()
exit()
```

---

## 📋 STEP 7: Migrate Redis Data (If Needed)

If you have existing data in Redis to migrate:

```bash
python
```

Then in Python shell:

```python
import json
from datetime import datetime
from database.config import SessionLocal
from database.models import User, Thread
from core.redis_manager import RedisManager

# Initialize
db = SessionLocal()
redis_manager = RedisManager()
redis_manager.initialize()

# Check for Redis data
if redis_manager.client:
    # Get premium users
    premium_keys = redis_manager.client.keys("threadr:premium:*")
    print(f"Found {len(premium_keys)} premium users in Redis")
    
    # Migrate each user
    for key in premium_keys:
        email = key.decode().split(":")[-1]
        expires = redis_manager.client.get(key)
        
        # Check if user exists
        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                username=email.split("@")[0],
                is_premium=True,
                premium_expires_at=datetime.fromtimestamp(int(expires))
            )
            user.set_password("TempPassword123!")  # User needs to reset
            db.add(user)
            print(f"Migrated user: {email}")
    
    db.commit()
    print("Migration complete!")
else:
    print("Redis not available")

db.close()
exit()
```

---

## 📋 STEP 8: Test Full Application

After database is initialized, test the full flow:

```bash
# Check health endpoint
curl http://localhost:10000/health

# Or using Python
python -c "import requests; print(requests.get('http://localhost:10000/health').json())"
```

---

## 🔧 TROUBLESHOOTING

### Common Issues:

**1. "ModuleNotFoundError: No module named 'database'"**
```bash
# Make sure you're in the right directory
cd /opt/render/project/src/backend/src
# Check if database folder exists
ls -la database/
```

**2. "relation already exists"**
- Tables are already created, this is fine
- Skip to verification step

**3. "could not connect to server"**
- Check DATABASE_URL is set correctly
- Make sure you're using Internal URL
- Verify PostgreSQL is running in Render

**4. "FATAL: too many connections"**
- Database connection limit reached
- Restart your backend service
- Or upgrade PostgreSQL plan

---

## ✅ SUCCESS CHECKLIST

After completing all steps, verify:

- [ ] `test_db_connection.py` shows "CONNECTION TEST PASSED"
- [ ] `init_database.py` shows "DATABASE INITIALIZATION COMPLETE"
- [ ] 11 tables created in PostgreSQL
- [ ] Can create and query users
- [ ] Health endpoint returns database status

---

## 🎯 NEXT STEPS

Once database is working:

1. **Deploy Backend Changes**
   - Commit and push the database code
   - Render will auto-deploy

2. **Monitor Application**
   - Check logs for any errors
   - Test user registration
   - Test thread generation

3. **Disable Redis-Only Mode**
   - Gradually migrate from Redis to PostgreSQL
   - Keep Redis for caching only

---

## 💡 QUICK REFERENCE

### Essential Commands:
```bash
# Test connection
python test_db_connection.py

# Initialize database
python init_database.py

# Python shell
python

# Exit Python shell
exit()

# Check current directory
pwd

# List files
ls -la
```

### Python Quick Tests:
```python
# Test database connection
from database.config import engine
engine.connect().execute("SELECT 1")

# Count users
from database.config import SessionLocal
from database.models import User
db = SessionLocal()
print(f"Users: {db.query(User).count()}")
db.close()
```

---

**Need Help?** Check the logs in Render Dashboard → Logs tab for detailed error messages.
# Railway Redis Setup Guide - Complete Walkthrough

## Overview
This guide walks you through adding Redis to your existing Railway project for the Threadr backend. Redis will be used for rate limiting and email storage.

## Step 1: Access Your Railway Project

1. **Go to Railway Dashboard**
   - Navigate to [railway.app](https://railway.app)
   - Click "Login" and sign in to your account
   - You'll see your project dashboard with your existing services

2. **Select Your Project**
   - Click on your "Threadr" project (or whatever you named it)
   - You should see your current backend service deployed

## Step 2: Add Redis Service

1. **Add New Service**
   - In your project dashboard, look for a "+" button or "New Service" button
   - Click the "+" button (usually in the top-right area of the services section)

2. **Choose Database Option**
   - You'll see options like "GitHub Repo", "Docker Image", "Database", etc.
   - **Click "Database"**

3. **Select Redis**
   - A list of database options will appear:
     - PostgreSQL
     - MySQL
     - **Redis** ← Click this one
     - MongoDB
   - **Click "Add Redis"**

4. **Redis Service Creation**
   - Railway will automatically create a Redis instance
   - You'll see a new service card appear in your dashboard
   - It will show "Redis" with a red Redis logo
   - Status will change from "Building" → "Deploying" → "Active"

## Step 3: Get Redis Connection Details

1. **Click on Redis Service**
   - Click on the Redis service card in your dashboard
   - This opens the Redis service details

2. **Go to Variables Tab**
   - In the Redis service view, click the "Variables" tab
   - You'll see several automatically generated variables:
     - `REDIS_URL` (this is what you need!)
     - `REDIS_HOST`
     - `REDIS_PORT`
     - `REDIS_PASSWORD`

3. **Copy REDIS_URL**
   - Find the `REDIS_URL` variable
   - Click the "Copy" icon next to its value
   - The URL format will be: `redis://default:PASSWORD@HOST:PORT`
   - **Save this URL - you'll need it for testing**

## Step 4: Configure Your Backend Service

1. **Go to Your Backend Service**
   - Click on your backend service (the one running your FastAPI app)
   - Go to the "Variables" tab

2. **Verify REDIS_URL is Available**
   - Railway automatically makes database URLs available to all services in the project
   - You should see `REDIS_URL` listed in your backend's environment variables
   - If you don't see it, manually add it:
     - Click "New Variable"
     - Name: `REDIS_URL`
     - Value: The URL you copied from Step 3

## Step 5: Update Your Backend Code

1. **Install Redis Dependencies**
   - Add to your `backend/requirements.txt`:
   ```
   redis==5.0.1
   aioredis==2.0.1
   ```

2. **Create Redis Connection in FastAPI**
   - Add this to your `backend/main.py`:

```python
import redis
import os
from urllib.parse import urlparse

# Redis connection setup
def get_redis_client():
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("Warning: REDIS_URL not found, rate limiting disabled")
        return None
    
    try:
        # Parse the Redis URL
        url = urlparse(redis_url)
        return redis.Redis(
            host=url.hostname,
            port=url.port,
            password=url.password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    except Exception as e:
        print(f"Redis connection error: {e}")
        return None

# Initialize Redis client
redis_client = get_redis_client()

# Test Redis connection on startup
@app.on_event("startup")
async def startup_event():
    if redis_client:
        try:
            redis_client.ping()
            print("✅ Redis connection successful")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
    else:
        print("⚠️ Redis not available - rate limiting disabled")
```

## Step 6: Test Redis Connection

1. **Add a Test Endpoint**
   - Add this test endpoint to your FastAPI app:

```python
@app.get("/test-redis")
async def test_redis():
    if not redis_client:
        return {"status": "error", "message": "Redis not available"}
    
    try:
        # Test basic operations
        redis_client.set("test_key", "test_value", ex=60)
        value = redis_client.get("test_key")
        redis_client.delete("test_key")
        
        return {
            "status": "success", 
            "message": "Redis working correctly",
            "test_result": value
        }
    except Exception as e:
        return {"status": "error", "message": f"Redis error: {str(e)}"}
```

2. **Deploy and Test**
   - Push your changes to trigger a Railway deployment
   - Once deployed, visit: `https://your-app.railway.app/test-redis`
   - You should see: `{"status": "success", "message": "Redis working correctly", "test_result": "test_value"}`

## Step 7: Implement Rate Limiting

Here's a complete rate limiting implementation:

```python
from functools import wraps
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
import json

def rate_limit(max_requests: int = 10, window_minutes: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request or not redis_client:
                return await func(*args, **kwargs)
            
            # Get client IP
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"
            
            try:
                # Get current request count
                current_requests = redis_client.get(key)
                
                if current_requests is None:
                    # First request in window
                    redis_client.setex(key, window_minutes * 60, 1)
                    return await func(*args, **kwargs)
                
                if int(current_requests) >= max_requests:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Max {max_requests} requests per {window_minutes} minutes."
                    )
                
                # Increment counter
                redis_client.incr(key)
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                print(f"Rate limiting error: {e}")
                # If Redis fails, allow the request
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Use it on your endpoints
@app.post("/api/generate")
@rate_limit(max_requests=5, window_minutes=60)  # 5 requests per hour
async def generate_thread(request: Request, content: dict):
    # Your existing endpoint code
    pass
```

## Troubleshooting Common Issues

### Issue 1: "REDIS_URL not found"
**Symptoms**: Environment variable missing
**Solution**: 
1. Check if Redis service is "Active" in Railway dashboard
2. Manually add REDIS_URL to backend service variables
3. Redeploy backend service

### Issue 2: "Connection timeout"
**Symptoms**: Redis connection fails with timeout
**Solution**:
```python
# Add longer timeouts
return redis.Redis(
    host=url.hostname,
    port=url.port,
    password=url.password,
    decode_responses=True,
    socket_connect_timeout=10,  # Increased from 5
    socket_timeout=10,          # Increased from 5
    retry_on_timeout=True
)
```

### Issue 3: "Authentication failed"
**Symptoms**: Redis rejects connection
**Solution**:
1. Verify REDIS_URL format: `redis://default:PASSWORD@HOST:PORT`
2. Check if password contains special characters (URL encode if needed)
3. Try connecting without password parsing:

```python
# Alternative connection method
redis_client = redis.from_url(redis_url, decode_responses=True)
```

### Issue 4: Railway Redis Service Won't Start
**Symptoms**: Redis service stuck in "Building" or "Error" state
**Solution**:
1. Delete the Redis service
2. Wait 2-3 minutes
3. Add Redis service again
4. If still failing, try the alternative below

## Alternative: Upstash Redis (If Railway Redis Fails)

If Railway's Redis service has issues, use Upstash (free tier):

1. **Sign up at [Upstash](https://upstash.com/)**
2. **Create Redis Database**
   - Click "Create Database"
   - Choose region closest to your Railway deployment
3. **Get Connection Details**
   - Copy the "UPSTASH_REDIS_REST_URL"
   - Copy the "UPSTASH_REDIS_REST_TOKEN"
4. **Add to Railway Variables**:
   - `UPSTASH_REDIS_REST_URL`: Your REST URL
   - `UPSTASH_REDIS_REST_TOKEN`: Your token
5. **Update Code for Upstash**:

```python
import requests
import os

class UpstashRedis:
    def __init__(self):
        self.url = os.getenv('UPSTASH_REDIS_REST_URL')
        self.token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def set(self, key, value, ex=None):
        data = ['SET', key, value]
        if ex:
            data.extend(['EX', ex])
        response = requests.post(f'{self.url}', json=data, headers=self.headers)
        return response.json()
    
    def get(self, key):
        response = requests.post(f'{self.url}', json=['GET', key], headers=self.headers)
        return response.json().get('result')
    
    def incr(self, key):
        response = requests.post(f'{self.url}', json=['INCR', key], headers=self.headers)
        return response.json()
    
    def ping(self):
        response = requests.post(f'{self.url}', json=['PING'], headers=self.headers)
        return response.json().get('result') == 'PONG'

# Use Upstash if Railway Redis fails
redis_client = get_redis_client() or UpstashRedis()
```

## Verification Checklist

✅ Redis service shows "Active" in Railway dashboard  
✅ REDIS_URL appears in backend service variables  
✅ `/test-redis` endpoint returns success  
✅ Rate limiting works (test by making multiple requests)  
✅ No Redis errors in Railway logs  

## Next Steps

1. **Implement Email Storage**:
```python
@app.post("/api/capture-email")
async def capture_email(request: Request, email_data: dict):
    email = email_data.get('email')
    if redis_client:
        redis_client.sadd('user_emails', email)
    return {"status": "success"}
```

2. **Monitor Usage**:
   - Check Railway Redis metrics in dashboard
   - Monitor connection count and memory usage
   - Set up alerts if needed

3. **Scale if Needed**:
   - Railway Redis scales automatically
   - Upgrade plan if you hit memory limits

Your Redis setup is now complete and ready for production use with your Threadr backend!
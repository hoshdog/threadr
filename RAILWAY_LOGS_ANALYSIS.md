# Railway Logs Analysis Guide

This guide helps you interpret Railway deployment logs to identify and fix "service unavailable" issues.

## How to Access Railway Logs

1. **Via Railway Dashboard:**
   - Go to your Railway project
   - Click on your service
   - Navigate to "Deployments" tab
   - Click on the failing deployment
   - Check both "Build Logs" and "Deploy Logs"

2. **Via Railway CLI:**
   ```bash
   railway logs
   railway logs --deployment [deployment-id]
   ```

## Critical Log Sections to Check

### 1. Build Phase Logs
Look for these sections in order:

#### Python Environment Setup
```
✓ Detected Python app
✓ Using Python version 3.11
✓ Installing dependencies from requirements.txt
```

**RED FLAGS:**
- `ERROR: Could not find a version that satisfies the requirement`
- `pip install failed`
- `requirements.txt not found`
- `Python version not supported`

#### Dependency Installation
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

**RED FLAGS:**
- `ERROR: Failed building wheel for [package]`
- `No module named '[package]'`
- `Memory limit exceeded during pip install`
- Compilation errors for packages like `uvloop` or `cryptography`

### 2. Start Phase Logs
This is where most "service unavailable" issues occur:

#### Application Startup
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**RED FLAGS:**
- `ImportError: No module named 'main'`
- `ModuleNotFoundError`
- `Address already in use`
- `Permission denied`
- `Failed to bind to port`
- Application startup never completes
- Process exits immediately after starting

#### Health Check Failures
```
HTTP GET /health -> 200 OK
```

**RED FLAGS:**
- `HTTP GET /health -> 404 Not Found`
- `HTTP GET /health -> 500 Internal Server Error`
- `Connection refused`
- `Timeout waiting for health check`

## Common Error Patterns and Solutions

### 1. Import Errors
**Log Pattern:**
```
ImportError: No module named 'main'
ModuleNotFoundError: No module named '[package]'
```

**Causes & Solutions:**
- **Wrong working directory:** Add `workDir = "backend"` to nixpacks.toml
- **Missing dependencies:** Check requirements.txt has all needed packages
- **Python path issues:** Ensure main.py is in the correct location

### 2. Port Binding Issues
**Log Pattern:**
```
OSError: [Errno 98] Address already in use
Permission denied binding to port
Failed to bind to 0.0.0.0:$PORT
```

**Causes & Solutions:**
- **Port not set:** Railway should set $PORT automatically, but check it's being used
- **Wrong host binding:** Always use `0.0.0.0`, never `localhost` or `127.0.0.1`
- **Multiple processes:** Ensure only one process tries to bind to the port

### 3. Application Startup Failures
**Log Pattern:**
```
Application startup complete. (Never appears)
Process exited with code 1
Uvicorn never shows "running on" message
```

**Causes & Solutions:**
- **Code errors in startup:** Check for exceptions in your FastAPI app initialization
- **Missing environment variables:** App crashes if required env vars are missing
- **Database connection failures:** If app requires DB, check connection strings

### 4. Health Check Failures
**Log Pattern:**
```
Health check failed: HTTP 404
Health check failed: Connection refused
Deployment failed health checks
```

**Causes & Solutions:**
- **Missing health endpoint:** Ensure `/health` endpoint exists and returns 200
- **App not responding:** Check if uvicorn actually started listening
- **Wrong health check path:** Railway expects `/health` by default

### 5. Memory/Resource Issues
**Log Pattern:**
```
Killed (OOM - Out of Memory)
Process killed by signal 9
Memory limit exceeded
```

**Causes & Solutions:**
- **Heavy dependencies:** Remove unnecessary packages (numpy, tensorflow, etc.)
- **Memory leaks:** Check for infinite loops or memory-intensive operations
- **Too many workers:** Reduce gunicorn workers to 1 for testing

### 6. Working Directory Issues
**Log Pattern:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'main.py'
No module named 'main'
```

**Causes & Solutions:**
- **Wrong build context:** Add `workDir = "backend"` to nixpacks.toml
- **Incorrect file paths:** Ensure main.py is in the specified working directory
- **Case sensitivity:** Linux is case-sensitive, check file names exactly

## Step-by-Step Log Analysis Process

### 1. First, Check Build Success
```
✓ Build completed successfully
✓ Image built and pushed
```
If build fails, focus on dependency and environment issues.

### 2. Then, Check Process Start
```
INFO: Started server process [1]
INFO: Uvicorn running on http://0.0.0.0:$PORT
```
If this doesn't appear, you have a startup issue.

### 3. Finally, Check Health Response
```
Health check passed: HTTP 200
Deployment successful
```
If health checks fail, your app started but isn't responding correctly.

## Quick Debugging Commands

Add these to your FastAPI app for better logging:

```python
import logging
import os
import sys

# Add to your startup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")  
logger.info(f"Port from env: {os.getenv('PORT', 'not set')}")
logger.info(f"Files in current dir: {os.listdir('.')}")
```

## Most Common Fixes for "Service Unavailable"

1. **Use minimal nixpacks.toml:**
   ```toml
   [build]
   workDir = "backend"
   
   [start]
   cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
   ```

2. **Ensure health endpoint exists:**
   ```python
   @app.get("/health")
   async def health():
       return {"status": "healthy"}
   ```

3. **Use minimal requirements.txt:**
   ```
   fastapi==0.109.0
   uvicorn[standard]==0.27.0
   ```

4. **Start with uvicorn, not gunicorn:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

## When All Else Fails

1. **Use the test app:** Deploy `test_railway_app.py` instead of your main app
2. **Check Railway status:** Visit status.railway.app for platform issues
3. **Try different regions:** Switch Railway deployment region
4. **Contact Railway support:** If logs show no obvious issues

Remember: Railway expects your app to:
- Bind to `0.0.0.0:$PORT`
- Respond to health checks on `/health`
- Start within the timeout period (usually 60 seconds)
- Not exceed memory limits
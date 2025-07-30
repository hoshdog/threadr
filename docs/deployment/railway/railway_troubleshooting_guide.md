# Railway FastAPI Deployment Troubleshooting Guide

## Immediate Debugging Steps

### 1. Run Local Diagnostics
```bash
# Run the diagnostic script to test all components locally
python railway_debug.py
```

### 2. Check Railway Build Logs
```bash
# View build logs to see where deployment fails
railway logs --build

# View runtime logs 
railway logs

# Follow logs in real-time
railway logs --follow
```

### 3. Check Railway Service Status
```bash
# Get service information
railway status

# Get environment variables
railway variables

# Get domain information  
railway domain
```

## Common Railway FastAPI Issues & Solutions

### Issue 1: "Service Unavailable" - App Not Starting

**Symptoms**: Health checks fail, 503 errors, no response from app

**Likely Causes**:
1. **Import errors** - Missing dependencies or syntax errors
2. **Port binding issues** - Not using Railway's PORT variable correctly
3. **Working directory problems** - App can't find main.py 
4. **Startup crashes** - Exceptions during app initialization

**Debugging Steps**:
```bash
# Check if build succeeded
railway logs --build | grep -i error

# Check runtime logs for startup errors
railway logs | head -50

# Look for specific error patterns
railway logs | grep -i "error\|exception\|failed\|traceback"
```

### Issue 2: Build Failures

**Symptoms**: Deployment fails during build phase

**Common Causes**:
- Dependency conflicts in requirements.txt
- Python version mismatches
- Missing system dependencies

**Solutions**:
```bash
# Use minimal requirements first
cp requirements_minimal.txt requirements.txt

# Use simplified nixpacks config
cp nixpacks_simplified.toml nixpacks.toml

# Redeploy
railway up
```

### Issue 3: Configuration Conflicts

**Symptoms**: App starts but behaves unexpectedly

**Fixed Issues**:
- ✅ Removed duplicate start commands
- ✅ Simplified working directory handling
- ✅ Increased health check timeout to 120s

## Step-by-Step Deployment Recovery

### Step 1: Use Simplified Configuration
```bash
# Backup current config
cp nixpacks.toml nixpacks_backup.toml
cp requirements.txt requirements_backup.txt

# Use simplified versions
cp nixpacks_simplified.toml nixpacks.toml  
cp requirements_minimal.txt requirements.txt

# Deploy
railway up
```

### Step 2: Monitor Deployment
```bash
# Watch logs during deployment
railway logs --follow

# In another terminal, check status
railway status
```

### Step 3: Test Health Endpoint
Once deployed, test the health endpoint:
```bash
# Get your Railway URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/health

# Test debug endpoint
curl https://your-app.railway.app/debug/startup
```

## Advanced Debugging

### Check Environment Variables
```bash
# List all environment variables
railway variables

# Make sure these are set:
# - PORT (automatically set by Railway)
# - ENVIRONMENT=production
# - OPENAI_API_KEY (if using OpenAI features)
```

### Test Gunicorn Command Locally
```bash
# Simulate Railway environment
cd backend
PORT=8000 ENVIRONMENT=production gunicorn main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --log-level debug \
  --preload
```

### Validate FastAPI App
```bash
# Test app creation
cd backend
python -c "from main import app; print('App created successfully')"

# Test basic functionality
python -c "
from main import app, split_into_tweets
test = split_into_tweets('Hello world')
print(f'Basic functionality works: {test}')
"
```

## Railway-Specific Gotchas

### 1. Working Directory Issues
- Railway runs from project root, not backend/
- Solution: Use `cd backend &&` in start commands

### 2. Port Environment Variable
- Railway sets PORT automatically
- Don't hardcode port numbers
- Always use `$PORT` in bind commands

### 3. Health Check Timeout
- Default 60s may be too short for Python apps
- Increased to 120s in configuration
- Health endpoint should respond quickly

### 4. File Path Issues
- Relative paths may not work as expected
- Use absolute paths or ensure working directory is correct

## Emergency Rollback Plan

If deployment completely fails:

### Option 1: Minimal FastAPI App
Create a simple test app to verify Railway works:

```python
# Create backend/minimal_main.py
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "port": os.getenv("PORT")}

@app.get("/health")  
def health():
    return {"status": "healthy"}
```

Deploy with:
```toml
# minimal_nixpacks.toml
[start]
cmd = "cd backend && uvicorn minimal_main:app --host 0.0.0.0 --port $PORT"
```

### Option 2: Use Different Deployment Method
If nixpacks continues to fail, try:
- Railway's Docker deployment
- Manual Dockerfile
- Different Python buildpack

## Log Analysis Patterns

Look for these patterns in Railway logs:

**Successful Startup**:
```
Starting Threadr backend in production mode...
Health check passed
Server started successfully
```

**Import Errors**:
```
ModuleNotFoundError: No module named 'xyz'
ImportError: cannot import name 'xyz'
```

**Port Binding Issues**:
```
OSError: [Errno 98] Address already in use
Error binding to host
```

**Working Directory Issues**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'main.py'
ModuleNotFoundError: No module named 'main'
```

## Contact Points

If issues persist:
1. Run `python railway_debug.py` and share results
2. Share Railway build logs: `railway logs --build`
3. Share Railway runtime logs: `railway logs | head -100`
4. Share service status: `railway status`
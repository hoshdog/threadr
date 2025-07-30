# Railway Deployment Verification Process

This document provides a systematic approach to debug and fix Railway deployment issues.

## Phase 1: Pre-Deployment Verification (Local)

### Step 1: Run the Debugging Script
```bash
cd /path/to/your/project
python railway_debug.py
```

This will check:
- Python environment and dependencies
- File structure and requirements
- Local app startup capability
- Configuration files

**Fix all CRITICAL issues before proceeding.**

### Step 2: Test Minimal Configuration Locally
```bash
cd backend
python test_railway_app.py
```

The test app should start and show:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

Visit http://localhost:8000/health to verify it responds.

### Step 3: Test Your Main App Locally
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

If this fails, fix the issues before deploying to Railway.

## Phase 2: Minimal Railway Deployment

### Step 4: Deploy Test App First
1. **Replace your main configuration with minimal versions:**
   ```bash
   # Backup current files
   cp nixpacks.toml nixpacks.toml.backup
   cp backend/requirements.txt backend/requirements.txt.backup
   
   # Use minimal versions
   cp nixpacks_minimal.toml nixpacks.toml
   cp backend/requirements_minimal.txt backend/requirements.txt
   ```

2. **Temporarily use test app:**
   ```bash
   cd backend
   cp main.py main.py.backup
   cp test_railway_app.py main.py
   ```

3. **Deploy to Railway:**
   ```bash
   git add .
   git commit -m "Deploy minimal test app"
   git push
   ```

### Step 5: Verify Minimal Deployment
1. **Check Railway logs immediately:**
   - Build logs should show successful dependency installation
   - Deploy logs should show uvicorn starting
   - Health checks should pass

2. **Test the deployed endpoints:**
   ```bash
   curl https://your-app.railway.app/health
   curl https://your-app.railway.app/debug
   ```

3. **Run debugging script against deployed app:**
   ```bash
   python railway_debug.py --url https://your-app.railway.app
   ```

**If minimal deployment fails, focus on Phase 3. If it succeeds, proceed to Phase 4.**

## Phase 3: Deployment Issue Resolution

### Step 6: Analyze Failure Patterns

#### If Build Fails:
1. **Check Python version compatibility**
2. **Simplify requirements.txt further**
3. **Check for package compilation issues**
4. **Try different Python version in nixpacks.toml**

#### If App Doesn't Start:
1. **Check working directory in logs**
2. **Verify file paths and case sensitivity**
3. **Add debug logging to your app**
4. **Check environment variables**

#### If Health Checks Fail:
1. **Verify /health endpoint exists**
2. **Check port binding (must use $PORT)**
3. **Ensure host is 0.0.0.0, not localhost**
4. **Check for startup timeouts**

### Step 7: Incremental Fixes
For each issue found:

1. **Make ONE change at a time**
2. **Test locally first**
3. **Deploy and check logs**
4. **Document what worked/didn't work**

Common fixes in order of impact:
1. Fix working directory: `workDir = "backend"` in nixpacks.toml
2. Use simple start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Reduce dependencies to absolute minimum
4. Add health endpoint if missing
5. Fix import paths and file locations

## Phase 4: Gradual Feature Restoration

### Step 8: Restore Your Main App
Once minimal deployment works:

1. **Restore your main.py:**
   ```bash
   cp main.py.backup main.py
   ```

2. **Deploy and test:**
   ```bash
   git add main.py
   git commit -m "Restore main app"
   git push
   ```

3. **If this fails, bisect the problem:**
   - Comment out complex features
   - Deploy simple version first
   - Add features back one by one

### Step 9: Restore Dependencies Gradually
Add dependencies back in groups:

1. **Core FastAPI dependencies:**
   ```
   fastapi==0.109.0
   uvicorn[standard]==0.27.0
   pydantic==2.5.3
   httpx==0.26.0
   ```

2. **Application-specific dependencies:**
   ```
   beautifulsoup4==4.12.3
   openai==1.10.0
   ```

3. **Production dependencies (last):**
   ```
   gunicorn==21.2.0
   # monitoring, security packages, etc.
   ```

Test deployment after each group.

### Step 10: Optimize Configuration
Once everything works:

1. **Switch from uvicorn to gunicorn if needed:**
   ```
   cmd = "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
   ```

2. **Add production environment variables**
3. **Enable monitoring and logging**
4. **Set up proper CORS origins**

## Phase 5: Final Verification

### Step 11: Complete End-to-End Test
1. **Run full debugging script:**
   ```bash
   python railway_debug.py --url https://your-app.railway.app
   ```

2. **Test all endpoints:**
   ```bash
   curl https://your-app.railway.app/
   curl https://your-app.railway.app/health
   curl https://your-app.railway.app/api/test
   ```

3. **Test your main functionality:**
   ```bash
   curl -X POST https://your-app.railway.app/api/generate \
     -H "Content-Type: application/json" \
     -d '{"text": "Test message for thread generation"}'
   ```

### Step 12: Performance and Monitoring
1. **Check response times**
2. **Monitor memory usage in Railway dashboard**
3. **Set up log aggregation if needed**
4. **Test under load if required**

## Troubleshooting Quick Reference

### Common Error → Solution Mapping

| Error | Quick Fix |
|-------|-----------|
| `ModuleNotFoundError: No module named 'main'` | Add `workDir = "backend"` to nixpacks.toml |
| `Address already in use` | Check you're using `$PORT` environment variable |
| `Health check failed` | Add `/health` endpoint that returns 200 status |
| `Process exited with code 1` | Check app startup errors, add debug logging |
| `Memory limit exceeded` | Reduce dependencies, check for memory leaks |
| `Build failed: pip install` | Simplify requirements.txt, check package compatibility |
| `Connection refused` | Ensure binding to `0.0.0.0`, not `localhost` |
| `File not found: requirements.txt` | Check working directory, ensure file exists |

### Emergency Recovery Steps

If deployment is completely broken:
1. Deploy the test app (`test_railway_app.py`)
2. Use minimal configuration files
3. Start fresh with basic FastAPI setup
4. Build up functionality incrementally

### Files to Keep Handy
- `C:\Users\HoshitoPowell\Desktop\Threadr\backend\test_railway_app.py` - Minimal working app
- `C:\Users\HoshitoPowell\Desktop\Threadr\nixpacks_minimal.toml` - Basic configuration
- `C:\Users\HoshitoPowell\Desktop\Threadr\backend\requirements_minimal.txt` - Minimal dependencies
- `C:\Users\HoshitoPowell\Desktop\Threadr\railway_debug.py` - Debugging script

### Success Criteria
Your deployment is working when:
- ✅ Build completes without errors
- ✅ App starts and uvicorn shows "running on" message
- ✅ Health endpoint returns 200 OK
- ✅ Main functionality endpoints respond correctly
- ✅ No memory or resource limit issues
- ✅ Logs show no critical errors

Remember: Start simple, fix one issue at a time, and always test locally before deploying to Railway.
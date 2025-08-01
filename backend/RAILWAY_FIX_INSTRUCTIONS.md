# Railway Deployment Fix Instructions

## The Problem
Railway is running `simple_app.py` (test app) instead of your actual backend in `src/main.py`.

## Solution 1: Switch to Docker Build (Recommended)

1. Go to Railway Dashboard: https://railway.app/project/[your-project-id]
2. Click on your service
3. Go to Settings → Build
4. Change "Build Provider" from "Nixpacks" to "Docker"
5. Click "Save" and trigger new deployment

## Solution 2: Force Correct App with Environment Variable

If Docker doesn't work, add this environment variable in Railway:
- Key: `NIXPACKS_START_CMD`
- Value: `cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`

## Solution 3: Delete and Redeploy

1. Delete the current Railway project
2. Create new Railway project
3. Connect GitHub repo
4. Set build command: `cd backend && pip install -r requirements.txt`
5. Set start command: `cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `ENVIRONMENT=production`
   - `REDIS_URL=[your-redis-url]`
   - `OPENAI_API_KEY=[your-api-key]`
   - `STRIPE_SECRET_KEY=[your-stripe-key]`
   - `STRIPE_WEBHOOK_SECRET=[your-webhook-secret]`

## Verification

Once deployed correctly, test:
```bash
curl https://threadr-production.up.railway.app/health
```

Should return:
```json
{"status": "healthy", "timestamp": "...", "version": "1.0.0", "environment": "production"}
```

## Why This Happened

Railway auto-detected Python and found `simple_app.py` first, using it instead of following the proper project structure in `src/main.py`.
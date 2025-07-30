# Railway Deployment Guide for Threadr Backend

## Deployment Configuration Summary

The Railway deployment has been configured to properly detect and build your FastAPI application from the `backend/` directory.

### Key Configuration Files:

1. **Root `railway.json`** - Main Railway service configuration
2. **Root `nixpacks.toml`** - Build configuration specifying backend working directory
3. **Backend `requirements.txt`** - Python dependencies
4. **Backend `runtime.txt`** - Python version specification
5. **Backend `Procfile`** - Alternative start command

### Deployment Steps:

1. **Connect to Railway:**
   ```bash
   railway login
   railway init
   ```

2. **Deploy the service:**
   ```bash
   railway up
   ```

3. **Set Environment Variables in Railway Dashboard:**
   - `OPENAI_API_KEY` - Your OpenAI API key (required)
   - Other variables are pre-configured in railway.json

### Build Process:

Railway will:
1. Detect Python application in the backend directory
2. Install dependencies from `backend/requirements.txt`
3. Start the FastAPI app using uvicorn with 2 workers
4. Expose the service on the assigned port

### Health Check:

The service is configured with a health check at `/health` endpoint.

### Expected Environment Variables:

- `ENVIRONMENT=production`
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`
- `CORS_ORIGINS` - Pre-configured for your frontend domains
- `RATE_LIMIT_REQUESTS=10`
- `RATE_LIMIT_WINDOW_HOURS=1`
- `MAX_TWEET_LENGTH=280`
- `MAX_CONTENT_LENGTH=10000`

### Troubleshooting:

If deployment fails:
1. Check Railway logs for build errors
2. Verify OPENAI_API_KEY is set in Railway dashboard
3. Ensure all dependencies in requirements.txt are available
4. Check that the /health endpoint responds correctly

### Testing the Deployment:

Once deployed, test these endpoints:
- `GET /health` - Health check
- `GET /` - API root
- `POST /generate-threads` - Main functionality (requires content)
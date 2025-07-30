# Railway Deployment Guide for Threadr FastAPI Backend

This guide provides step-by-step instructions for deploying the Threadr FastAPI backend to Railway.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. Git repository with your code
3. OpenAI API key

## Railway Configuration Files

The following files have been configured for Railway deployment:

### 1. `nixpacks.toml` (Primary Method)
- Configures Nixpacks to build the Python FastAPI app from the `backend/` subdirectory
- Uses Python 3.11 with gunicorn + uvicorn workers for production
- Sets appropriate environment variables

### 2. `Dockerfile` (Alternative Method)
- Multi-stage Docker build for optimized production deployment
- Includes security best practices (non-root user)
- Health checks and proper signal handling

### 3. `railway.toml`
- Railway-specific configuration
- Health check endpoint configuration
- Restart policies and resource limits

### 4. `.railwayignore`
- Excludes unnecessary files from deployment
- Reduces build time and image size

## Deployment Methods

### Method 1: Using Nixpacks (Recommended)

1. **Connect Repository to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Initialize project
   railway init
   ```

2. **Configure Environment Variables:**
   Set these environment variables in your Railway project:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

### Method 2: Using Docker

1. **Force Docker Build:**
   If Railway doesn't detect the Nixpacks configuration, you can force Docker:
   - In Railway dashboard, go to Settings > Build
   - Set Builder to "Docker"
   - Railway will use the `Dockerfile` in the root directory

2. **Environment Variables:**
   Same as Method 1

## Environment Variables Configuration

### Required Variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ENVIRONMENT`: Set to "production"

### Optional Variables:
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `RATE_LIMIT_REQUESTS`: Number of requests per hour (default: 10)
- `RATE_LIMIT_WINDOW_HOURS`: Rate limit window in hours (default: 1)
- `MAX_TWEET_LENGTH`: Maximum tweet length (default: 280)
- `MAX_CONTENT_LENGTH`: Maximum content length (default: 10000)

## Troubleshooting

### "Could not determine how to build the app"

If you encounter this error, try these solutions:

1. **Verify File Structure:**
   ```
   project-root/
   ├── nixpacks.toml
   ├── Dockerfile
   ├── railway.toml
   ├── .railwayignore
   └── backend/
       ├── main.py
       ├── requirements.txt
       ├── runtime.txt
       ├── setup.py
       ├── pyproject.toml
       └── __init__.py
   ```

2. **Check Railway Logs:**
   ```bash
   railway logs
   ```

3. **Force Redeploy:**
   ```bash
   railway up --detach
   ```

4. **Switch to Docker:**
   - Go to Railway dashboard > Settings > Build
   - Change Builder from "Auto" to "Docker"

### Build Fails

1. **Check Python Version:**
   - Ensure `runtime.txt` specifies `python-3.11.9`
   - Verify `nixpacks.toml` has `python = "3.11"`

2. **Dependencies Issues:**
   - Check `requirements.txt` for compatibility issues
   - Ensure all dependencies are pinned to specific versions

3. **Memory Issues:**
   - Railway free tier has memory limits
   - Consider upgrading plan or optimizing dependencies

### App Starts but Returns 500 Errors

1. **Environment Variables:**
   - Verify `OPENAI_API_KEY` is set correctly
   - Check all required environment variables are present

2. **Port Configuration:**
   - Railway automatically sets `$PORT` environment variable
   - Application should bind to `0.0.0.0:$PORT`

3. **Check Application Logs:**
   ```bash
   railway logs
   ```

## Health Checks

The application includes a health check endpoint at `/health`. Railway will use this to:
- Determine when the application is ready to receive traffic
- Monitor application health
- Restart the service if health checks fail

## Performance Optimization

### Production Configuration:
- Uses gunicorn with 2 uvicorn workers
- Enables request limiting (1000 requests per worker)
- Includes proper timeout settings
- Preloads application for faster response times

### Resource Limits:
- Default: 1 replica (adjust based on traffic)
- Memory: Optimized for Railway's free tier
- CPU: Efficient async handling with FastAPI

## Monitoring

### Built-in Endpoints:
- `GET /health` - Health check
- `GET /api/rate-limit-status` - Rate limit status
- `GET /` - API information

### Logging:
- Structured logging in production
- All errors logged with timestamps
- Request/response logging enabled

## Security Features

### Docker Security:
- Non-root user in container
- Minimal base image (python:3.11-slim)
- No unnecessary packages

### Application Security:
- CORS properly configured for production
- Rate limiting implemented
- Input validation with Pydantic
- Environment-based configuration

## Next Steps

1. **Custom Domain:**
   - Configure custom domain in Railway dashboard
   - Update CORS_ORIGINS environment variable

2. **Database Integration:**
   - Add database service in Railway
   - Update application configuration

3. **Monitoring & Alerting:**
   - Consider integrating Sentry for error tracking
   - Set up uptime monitoring

4. **Scaling:**
   - Monitor usage and scale replicas as needed
   - Consider upgrading Railway plan for higher limits

## Support

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Verify environment variables in Railway dashboard
3. Test locally with same environment variables
4. Check Railway status page: https://status.railway.app/
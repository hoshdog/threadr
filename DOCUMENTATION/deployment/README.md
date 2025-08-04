# Deployment Documentation

> **🚀 PRODUCTION**: Live systems at https://threadr-plum.vercel.app and https://threadr-production.up.railway.app

## Deployment Overview

Threadr uses a dual-deployment strategy with frontend on Vercel and backend on Railway. This provides optimal performance, cost efficiency, and scalability for the current architecture.

### Current Production Deployment
- **Frontend**: Vercel (Static HTML/Alpine.js)
- **Backend**: Railway (FastAPI/Python)
- **Database**: Upstash Redis (managed Redis)
- **DNS**: Vercel domains with automatic SSL
- **Monitoring**: Railway + Vercel built-in monitoring

## Platform Selection Rationale

### Why Vercel for Frontend
- **Optimized for Static Sites**: Perfect for Alpine.js single-page app
- **Edge Network**: Global CDN for fast loading worldwide
- **Automatic Deployments**: Git integration with instant deployments
- **SSL/Domain Management**: Automatic HTTPS and custom domains
- **Cost**: Free tier sufficient for current traffic

### Why Railway for Backend
- **Python-First Platform**: Excellent FastAPI support
- **Simple Configuration**: Minimal setup with automatic detection
- **Environment Management**: Easy environment variable management
- **Scaling**: Automatic scaling based on demand
- **Cost**: Reasonable pricing with usage-based billing

### Why Upstash Redis
- **Serverless Redis**: No server management required
- **Global Distribution**: Low latency worldwide
- **Free Tier**: Sufficient for current usage patterns
- **Reliability**: Enterprise-grade uptime and backup

## Deployment Architectures

### Current Production Architecture
```
User Request → Cloudflare (Optional) → Vercel (Frontend) → Railway (Backend) → Upstash Redis
     ↓              ↓                      ↓                    ↓               ↓
  Browser      DDoS Protection       Alpine.js App         FastAPI          Rate Limiting
     ↓              ↓                      ↓                    ↓               ↓
  JavaScript   Security Headers      API Calls            Business Logic    User Data
```

### Target Architecture (Next.js)
```
User Request → Cloudflare → Vercel (Next.js) → Railway (Backend) → PostgreSQL + Redis
     ↓              ↓             ↓                    ↓               ↓
  Browser      DDoS Protection   SSR/SSG           FastAPI        Persistent Data
     ↓              ↓             ↓                    ↓               ↓
  React App    Security          Optimized Pages    Business Logic   Cache Layer
```

## Frontend Deployment (Vercel)

### Current Setup (Alpine.js)
```bash
# Automatic deployment from Git
cd frontend/public
# Edit index.html, config.js, or assets
git add .
git commit -m "Frontend update"
git push origin main
# Vercel automatically deploys in ~30 seconds
```

### Configuration Files
```json
// vercel.json
{
  "rewrites": [
    {
      "source": "/((?!api)(?!_next)(?!favicon.ico)(?!.*\\.).)*",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

### Environment Variables (Vercel)
- **NEXT_PUBLIC_API_URL**: Backend API URL
- **NEXT_PUBLIC_STRIPE_PUBLIC_KEY**: Stripe publishable key
- **NEXT_PUBLIC_ENVIRONMENT**: production

### Deployment Process
1. **Development**: Edit files in `frontend/public/`
2. **Testing**: Test locally with development server
3. **Commit**: Git commit and push to main branch
4. **Deploy**: Vercel automatically deploys
5. **Verify**: Check deployment at https://threadr-plum.vercel.app

### Common Issues and Solutions

#### Issue: Deployment Fails with Regex Error
```bash
# Problem: Complex regex in vercel.json
"source": "/((?!api)(?!_next)(?!favicon.ico)(?!.*\\.).)*"

# Solution: Simplify regex pattern
"source": "/:path([^.]*)"
```

#### Issue: API Key Exposure
```javascript
// Problem: Hardcoded keys in config.js
const config = {
  openaiApiKey: 'sk-proj-XXXX' // EXPOSED
}

// Solution: Use backend proxy
const response = await fetch('/api/generate', {
  method: 'POST',
  body: JSON.stringify({ content })
})
```

## Backend Deployment (Railway)

### Current Setup (FastAPI)
```bash
# Automatic deployment from Git
cd backend
# Edit src/ files, requirements.txt, or configuration
git add .
git commit -m "Backend update"
git push origin main
# Railway automatically deploys in ~2-3 minutes
```

### Configuration Files
```toml
# nixpacks.toml
[phases.setup]
nixPkgs = ["python311"]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn src.main:app --host 0.0.0.0 --port $PORT"

[variables]
PYTHONPATH = "/app/backend:/app/backend/src"
```

### Environment Variables (Railway)
```bash
# Required Variables
OPENAI_API_KEY=sk-proj-your-openai-key
STRIPE_SECRET_KEY=sk_live_your-stripe-secret
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
REDIS_URL=redis://default:password@host:port

# Optional Variables
CORS_ORIGINS=https://threadr-plum.vercel.app
ENVIRONMENT=production
LOG_LEVEL=info
RATE_LIMIT_DAILY=5
RATE_LIMIT_MONTHLY=20
```

### Deployment Process
1. **Development**: Edit files in `backend/src/`
2. **Testing**: Run tests locally with `pytest`
3. **Commit**: Git commit and push to main branch
4. **Deploy**: Railway automatically builds and deploys
5. **Verify**: Check health at https://threadr-production.up.railway.app/health

### Health Checks
Railway monitors the following endpoints:
- **Health**: `/health` - Overall system health
- **Readiness**: `/readiness` - Service readiness for traffic
- **Startup**: Custom startup probe for complex initialization

### Common Issues and Solutions

#### Issue: Health Check Failures
```python
# Problem: Health check endpoint not responding
@app.get("/health")
async def health_check():
    return {"status": "ok"}  # Too simple

# Solution: Comprehensive health check
@app.get("/health")
async def health_check():
    try:
        # Test database connection
        await redis_client.ping()
        # Test external APIs
        # Return detailed status
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "redis": "connected",
                "openai": "available"
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Health check failed: {str(e)}")
```

#### Issue: Import Errors
```python
# Problem: Import paths fail in production
from .utils.security import SecurityUtils

# Solution: Try/except import pattern
try:
    from .utils.security import SecurityUtils
except ImportError:
    from utils.security import SecurityUtils
```

## Database Deployment (Redis)

### Current Setup (Upstash)
- **Provider**: Upstash Redis
- **Plan**: Free tier (10,000 commands/day)
- **Region**: US-East-1 (closest to Railway)
- **Persistence**: Enabled for data durability

### Connection Configuration
```python
# Redis connection with Upstash
import redis
from urllib.parse import urlparse

redis_url = os.getenv("REDIS_URL")
url = urlparse(redis_url)

redis_client = redis.Redis(
    host=url.hostname,
    port=url.port,
    password=url.password,
    ssl=True,
    ssl_cert_reqs=None
)
```

### Future Database Migration (PostgreSQL)
```bash
# Planned PostgreSQL on Railway
# 1. Add PostgreSQL service to Railway
# 2. Update environment variables
# 3. Create migration scripts
# 4. Gradual data migration from Redis
```

## Monitoring and Alerting

### Current Monitoring
- **Railway**: Built-in metrics and logs
- **Vercel**: Deployment and performance metrics
- **Upstash**: Redis usage and performance
- **Manual**: Health check endpoints

### Health Check Endpoints
```bash
# Backend health checks
curl https://threadr-production.up.railway.app/health
curl https://threadr-production.up.railway.app/readiness

# Frontend availability
curl https://threadr-plum.vercel.app

# Redis connectivity (through backend)
curl https://threadr-production.up.railway.app/health
```

### Alerting Setup (Planned)
- **Uptime Monitoring**: UptimeRobot or similar
- **Error Tracking**: Sentry for error monitoring
- **Performance**: New Relic or DataDog
- **Cost Alerts**: Railway and Vercel spending alerts

## Security Configuration

### SSL/TLS Configuration
- **Vercel**: Automatic SSL with Let's Encrypt
- **Railway**: Automatic SSL for custom domains
- **Upstash**: SSL-enabled Redis connections
- **APIs**: All external API calls use HTTPS

### Security Headers
```javascript
// Vercel security headers
{
  "key": "Strict-Transport-Security",
  "value": "max-age=31536000; includeSubDomains"
},
{
  "key": "X-Content-Type-Options",
  "value": "nosniff"
},
{
  "key": "X-Frame-Options",
  "value": "DENY"
}
```

### Environment Security
- **API Keys**: Stored in platform environment variables
- **Secrets Rotation**: Manual rotation process (needs automation)
- **Access Control**: Platform-level access controls
- **Audit Logs**: Platform audit logs enabled

## Disaster Recovery

### Backup Strategy
- **Code**: Git repository on GitHub (primary backup)
- **Redis Data**: Upstash automatic backups
- **Environment Config**: Documented in this guide
- **Deployment Config**: Version controlled

### Recovery Procedures

#### Complete System Recovery
1. **Code Recovery**: Clone from GitHub
2. **Environment Setup**: Recreate environment variables
3. **Database Recovery**: Restore from Upstash backups
4. **Deployment**: Redeploy to Railway and Vercel
5. **Testing**: Comprehensive system testing
6. **DNS**: Update DNS if needed

#### Partial Service Recovery
- **Frontend Only**: Redeploy to Vercel
- **Backend Only**: Redeploy to Railway
- **Database Issues**: Contact Upstash support

### Recovery Time Objectives (RTO)
- **Complete System**: 2-4 hours
- **Frontend Only**: 5-10 minutes
- **Backend Only**: 15-30 minutes
- **Database Issues**: 1-2 hours (depends on Upstash)

## Cost Optimization

### Current Costs (Monthly)
- **Vercel**: $0 (free tier)
- **Railway**: $5-20 (usage-based)
- **Upstash**: $0 (free tier)
- **Total**: $5-20/month

### Cost Scaling Projections
```
100 users: $10-30/month
500 users: $50-100/month
1000 users: $100-200/month
5000 users: $300-500/month
```

### Cost Optimization Strategies
1. **Efficient Code**: Optimize API calls and database queries
2. **Caching**: Implement comprehensive caching
3. **Monitoring**: Track costs and usage patterns
4. **Scaling**: Use auto-scaling to match demand

## Deployment Automation

### Current Automation
- **Git Integration**: Automatic deployments on push
- **Health Checks**: Automatic health monitoring
- **Basic Testing**: Manual testing process

### Enhanced Automation (Planned)
```yaml
# GitHub Actions CI/CD
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest backend/tests/
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        run: railway up
      - name: Deploy to Vercel
        run: vercel --prod
```

## Migration Planning

### Next.js Migration Deployment
1. **Parallel Deployment**: Deploy Next.js to staging
2. **A/B Testing**: Route small percentage to Next.js
3. **Gradual Migration**: Increase Next.js traffic
4. **Complete Cutover**: Switch all traffic
5. **Cleanup**: Remove Alpine.js deployment

### Database Migration (Redis to PostgreSQL)
1. **Setup PostgreSQL**: Add PostgreSQL service to Railway
2. **Dual Write**: Write to both Redis and PostgreSQL
3. **Data Migration**: Migrate existing Redis data
4. **Read Cutover**: Switch reads to PostgreSQL
5. **Cleanup**: Remove Redis dependencies

---

**🚀 Production deployment is stable and scalable - ready for growth to $1K MRR**

*Comprehensive deployment strategy supporting current needs and future expansion*
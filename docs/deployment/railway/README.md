# Railway Deployment Documentation

This directory contains the consolidated Railway deployment documentation for the Threadr backend.

## Current Documentation

### 📖 [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
**The single source of truth for Railway deployment.** This comprehensive guide consolidates all previous deployment knowledge and includes:

- Quick start deployment process
- Complete configuration (nixpacks.toml)
- Environment variables setup
- Common issues and solutions
- Redis setup options
- URL scraping configuration
- Health check implementation
- Troubleshooting guide
- Best practices and emergency procedures

## Archive

The `archive/` directory contains previous versions of deployment documentation that have been consolidated into the main guide. These files are kept for historical reference but should not be used for new deployments.

### Archived Files:
- Multiple fragmented guides from different deployment attempts
- Issue-specific fixes that are now integrated
- Redundant configuration examples
- Previous troubleshooting attempts

## Key Deployment Points

### Current Working Configuration
- **Server**: Uvicorn (NOT gunicorn)
- **Python Version**: 3.11
- **Working Directory**: `backend/`
- **Start Command**: `python -m uvicorn src.main:app`
- **Workers**: 1 (for Railway stability)

### Critical Environment Variables
- `ENVIRONMENT=production`
- `OPENAI_API_KEY=your-key`
- `CORS_ORIGINS=https://your-frontend-domain` (NO trailing slash)
- `API_KEYS=comma,separated,keys`

### Success Indicators
- Health endpoint returns 200 OK
- No gunicorn references in logs
- Startup shows "Uvicorn running on http://0.0.0.0:PORT"
- CORS properly configured for frontend connection

## Usage

For any Railway deployment questions or issues:

1. **First**: Read the [main deployment guide](./RAILWAY_DEPLOYMENT_GUIDE.md)
2. **Check**: Current production status in project CLAUDE.md
3. **Debug**: Use the troubleshooting section for specific errors
4. **Update**: This documentation when new issues are discovered and solved

## Maintenance

This documentation should be updated when:
- New deployment issues are discovered and resolved
- Railway changes their platform requirements
- The application structure changes significantly
- New features require additional configuration

The goal is to maintain a single, comprehensive guide that works for 95% of Railway deployment scenarios.
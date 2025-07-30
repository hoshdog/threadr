# Threadr Documentation

Welcome to the comprehensive documentation for Threadr - a SaaS tool that converts blog articles into Twitter threads.

## 📚 Documentation Structure

### 🚀 Deployment Guides

#### Railway (Backend)
- [Complete Railway Deployment Guide](./deployment/railway/) - Comprehensive guide for deploying the FastAPI backend
- [Health Check Configuration](./deployment/railway/RAILWAY_HEALTH_CHECK_FIXES.md)
- [URL Scraping Fixes](./deployment/railway/RAILWAY_URL_SCRAPING_FIX.md)
- [Port Configuration](./deployment/railway/RAILWAY_PORT_FIX.md)
- [Redis Setup](./deployment/railway/RAILWAY_REDIS_SETUP_GUIDE.md)
- [Troubleshooting Guide](./deployment/railway/railway_troubleshooting_guide.md)

#### Vercel (Frontend)
- [Vercel Deployment Guide](./deployment/vercel/VERCEL_DEPLOYMENT.md)
- [GitHub Integration](./deployment/vercel/GITHUB_VERCEL_SETUP.md)
- [Authentication Fix](./deployment/vercel/VERCEL_AUTHENTICATION_FIX.md)
- [Deployment Summary](./deployment/vercel/DEPLOYMENT_SUMMARY.md)

#### General Deployment
- [Deployment Overview](./deployment/DEPLOYMENT.md)
- [Deployment Checklist](./deployment/DEPLOYMENT_CHECKLIST.md)
- [Cloudflare Setup](./deployment/CLOUDFLARE_SETUP.md)

### 🔌 API Documentation
- [API Documentation](./api/API_DOCUMENTATION.md) - Complete API reference
- [Quick Reference](./api/API_QUICK_REFERENCE.md) - Quick endpoint overview
- [API Keys](./api/API_KEYS.md) - Authentication setup
- [API Key Debugging](./api/API_KEY_DEBUG_SOLUTION.md)
- [Frontend API Integration](./api/FRONTEND_API_KEY_FIX.md)

### 🛠️ Development
- [Testing Guide](./development/TESTING_GUIDE.md) - How to run tests
- [Redis Implementation](./development/REDIS_IMPLEMENTATION.md) - Redis caching details
- [Production Test Report](./development/PRODUCTION_TEST_REPORT.md)
- [OpenAI Setup](./development/OPENAI_SETUP.md) - GPT integration guide

### 🔒 Security
- [Security Checklist](./security/SECURITY_CHECKLIST.md) - Security best practices
- [Security Fixes](./security/SECURITY_FIXES.md) - Implemented security measures
- [Security Overview](./security/SECURITY.md) - General security documentation

## 🎯 Quick Links

### For New Developers
1. Start with the [main README](../README.md)
2. Follow the [Development Setup](./development/getting-started.md)
3. Review the [API Documentation](./api/API_DOCUMENTATION.md)

### For Deployment
1. Backend: [Railway Deployment Guide](./deployment/railway/)
2. Frontend: [Vercel Deployment Guide](./deployment/vercel/VERCEL_DEPLOYMENT.md)
3. [Deployment Checklist](./deployment/DEPLOYMENT_CHECKLIST.md)

### For Troubleshooting
1. [Railway Troubleshooting](./deployment/railway/railway_troubleshooting_guide.md)
2. [API Key Issues](./api/API_KEY_DEBUG_SOLUTION.md)
3. [Security Fixes](./security/SECURITY_FIXES.md)

## 📖 Documentation Standards

When adding new documentation:
- Use clear, descriptive filenames
- Include a table of contents for long documents
- Add code examples where relevant
- Keep deployment-specific docs in the appropriate subfolder
- Update this index when adding new documentation

## 🔄 Recent Updates

- **2025-07-31**: Reorganized documentation structure
- **2025-07-30**: Fixed Railway health check issues
- **2025-07-30**: Enhanced web scraping error handling

## 📝 Documentation TODO

- [ ] Create comprehensive Railway deployment guide (consolidating all Railway docs)
- [ ] Add frontend development guide
- [ ] Create API client examples
- [ ] Add monitoring and logging guide
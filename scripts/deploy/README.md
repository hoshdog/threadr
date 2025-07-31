# Threadr Deployment Scripts

This directory contains scripts for deploying Threadr when network connectivity issues prevent normal GitHub push workflows.

## Quick Start

### 1. Test Everything Locally First
```bash
# Run complete verification suite
python local-verification.py

# Test monetization features specifically
python ../test/test-monetization-features.py

# Windows PowerShell
.\deploy-when-online.ps1 -TestOnly
```

### 2. Deploy When Network Returns
```bash
# Automated deployment (waits for network)
python auto-deploy-when-online.py

# Windows PowerShell
.\deploy-when-online.ps1 -WaitForNetwork

# Deploy immediately if network is available
python auto-deploy-when-online.py --immediate
```

### 3. Manual Deployment Options
```bash
# Create Railway deployment package
python manual-railway-deploy.py

# Create Vercel deployment package  
python manual-vercel-deploy.py

# Both with ZIP files for manual upload
python manual-railway-deploy.py --method zip
python manual-vercel-deploy.py --method zip
```

## Available Scripts

### `local-verification.py`
Complete local testing suite that verifies:
- Backend health endpoints
- Thread generation functionality
- Email capture
- Usage tracking and rate limiting
- Stripe webhook endpoint
- Frontend file structure
- Deployment configuration files

**Usage:**
```bash
python local-verification.py --backend-url http://localhost:8001
python local-verification.py --output verification-results.json
```

### `auto-deploy-when-online.py`
Automated deployment script that:
- Waits for network connectivity
- Pushes commits to GitHub
- Triggers Railway and Vercel deployments
- Verifies deployment completion
- Runs post-deployment tests

**Usage:**
```bash
python auto-deploy-when-online.py                    # Wait for network
python auto-deploy-when-online.py --immediate        # Deploy now if online
python auto-deploy-when-online.py --check-interval 5 # Check every 5 seconds
```

### `manual-railway-deploy.py`
Manual Railway deployment with options:
- CLI-based deployment via Railway CLI
- ZIP file creation for dashboard upload
- Package validation and preparation

**Usage:**
```bash
python manual-railway-deploy.py --method auto  # Try CLI, fallback to ZIP
python manual-railway-deploy.py --method cli   # CLI only
python manual-railway-deploy.py --method zip   # ZIP file only
```

### `manual-vercel-deploy.py`
Manual Vercel deployment with options:
- CLI-based deployment via Vercel CLI
- Drag-and-drop ZIP creation
- Production configuration updates

**Usage:**
```bash
python manual-vercel-deploy.py --method auto    # Try CLI, fallback to manual
python manual-vercel-deploy.py --method cli     # CLI only
python manual-vercel-deploy.py --method manual  # Create files for manual upload
```

### `test-monetization-features.py`
Specialized testing for monetization features:
- Email capture validation
- Usage tracking and limits
- Free tier enforcement
- Premium feature locks
- Stripe webhook availability
- CORS configuration

**Usage:**
```bash
python ../test/test-monetization-features.py --backend-url http://localhost:8001
python ../test/test-monetization-features.py --output monetization-results.json
```

### `deploy-when-online.ps1` (Windows)
PowerShell wrapper for Windows users:
- Easy command-line interface
- Network connectivity checking
- Automated test running
- Deployment orchestration

**Usage:**
```powershell
.\deploy-when-online.ps1 -TestOnly              # Run tests only
.\deploy-when-online.ps1 -WaitForNetwork        # Wait and deploy
.\deploy-when-online.ps1 -Help                  # Show help
```

## Deployment Checklist

Follow `deployment-checklist.md` for complete deployment verification.

**Critical Steps:**
1. ✅ Run local verification suite
2. ✅ Test monetization features
3. ✅ Verify all files are committed
4. ✅ Push to GitHub when network available
5. ✅ Monitor deployments complete
6. ✅ Run post-deployment tests
7. ✅ Verify production URLs working

## Production URLs

- **Backend (Railway):** https://threadr-production.up.railway.app
- **Frontend (Vercel):** https://threadr-plum.vercel.app

## Environment Requirements

### Python Dependencies
```bash
pip install aiohttp asyncio
```

### CLI Tools (Optional)
```bash
# Railway CLI
npm install -g @railway/cli

# Vercel CLI  
npm install -g vercel
```

## Troubleshooting

### Network Issues
- Use `--wait-for-network` flag to wait for connectivity
- Monitor network status with `auto-deploy-when-online.py`
- Create ZIP files for manual upload as fallback

### Deployment Failures
- Check individual service logs (Railway/Vercel dashboards)
- Use manual CLI deployment methods
- Verify environment variables are set correctly
- Run local verification first to catch issues early

### Testing Issues
- Ensure backend is running on correct port
- Check CORS configuration for frontend integration
- Verify Redis is available for rate limiting tests
- Test with different IP addresses for rate limiting

## File Structure

```
scripts/deploy/
├── README.md                     # This file
├── deployment-checklist.md       # Complete deployment checklist
├── local-verification.py         # Local testing suite
├── auto-deploy-when-online.py    # Automated deployment
├── manual-railway-deploy.py      # Manual Railway deployment
├── manual-vercel-deploy.py       # Manual Vercel deployment
└── deploy-when-online.ps1        # Windows PowerShell script

scripts/test/
└── test-monetization-features.py # Monetization testing suite
```

## Success Indicators

### Local Testing
- All verification tests pass
- Monetization features working
- No console errors
- API endpoints responding correctly

### Deployment
- GitHub push successful
- Railway deployment live and healthy
- Vercel deployment accessible
- End-to-end functionality working
- Production URLs serving correctly

---

**Need Help?** Check the deployment checklist or run scripts with `--help` flag for detailed usage information.
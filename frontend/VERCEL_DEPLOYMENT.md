# Threadr Frontend - Vercel Deployment Guide

## 🚀 Quick Start

The Threadr frontend is ready for immediate deployment to Vercel. All configuration files are in place and the frontend is configured to work with the Railway backend at `https://threadr-production.up.railway.app`.

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally with `npm install -g vercel`
3. **Railway Backend**: Ensure the backend is running at `https://threadr-production.up.railway.app`

## 📦 Deployment Options

### Option 1: Automated Script (Recommended)

**Windows (PowerShell):**
```powershell
cd frontend
.\deploy-vercel.ps1
```

**macOS/Linux (Bash):**
```bash
cd frontend
./deploy-vercel.sh
```

### Option 2: Manual Deployment

```bash
# Navigate to frontend directory
cd frontend

# Login to Vercel (if not already logged in)
vercel login

# Preview deployment
vercel

# Production deployment
vercel --prod
```

### Option 3: GitHub Integration

1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Vercel will automatically deploy on push

## 🔧 Configuration Details

### Files Structure
```
frontend/
├── index.html              # Main application file
├── config.js              # Environment configuration
├── vercel.json            # Vercel deployment config
├── package.json           # Project metadata
├── deploy-vercel.ps1      # Windows deployment script
├── deploy-vercel.sh       # Unix deployment script
└── VERCEL_DEPLOYMENT.md   # This guide
```

### Environment Variables

The application automatically detects the environment and uses the appropriate backend URL:

- **Development** (`localhost`): `http://localhost:8000`
- **Production** (Vercel): `https://threadr-production.up.railway.app`

**Optional Environment Variables:**
```bash
# Override API URL (if needed)
THREADR_API_URL=https://threadr-production.up.railway.app
```

### Vercel Configuration (`vercel.json`)

The included `vercel.json` configures:
- Static file serving
- SPA routing (all routes → `index.html`)
- Security headers (HSTS, XSS protection, etc.)
- Cache control for assets
- Environment variables

## 🌐 Custom Domain Setup

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Navigate to **Settings** → **Domains**
4. Add your custom domain
5. Follow Vercel's DNS configuration instructions

## 🧪 Testing Your Deployment

### 1. Health Check
Visit your deployed URL and verify:
- Page loads correctly
- No console errors
- UI elements render properly

### 2. Backend Connection Test
1. Try generating a thread from a URL (e.g., a news article)
2. Try generating a thread from pasted text
3. Verify error handling works (try invalid URLs)

### 3. Feature Testing
- Email capture modal (after first use)
- Copy functionality for individual tweets
- Copy all tweets functionality
- Tweet editing and character counting

## 🔍 Troubleshooting

### Common Issues

**1. Deployment Failed**
```bash
# Check Vercel CLI version
vercel --version

# Re-login if needed
vercel login

# Try deploying with verbose output
vercel --prod --debug
```

**2. Backend Connection Issues**
- Verify Railway backend is running: `https://threadr-production.up.railway.app/health`
- Check browser console for CORS errors
- Ensure Vercel environment variables are set correctly

**3. CORS Errors**
The frontend handles CORS gracefully with:
- Proper request headers
- Error fallback mechanisms
- Development mode detection

**4. Environment Variable Issues**
```bash
# List current environment variables
vercel env ls

# Add/update environment variable
vercel env add THREADR_API_URL production https://threadr-production.up.railway.app
```

### Debug Mode

Enable debug mode in the browser console:
```javascript
// Enable fallback mode for testing
localStorage.setItem('threadr_allow_fallback', 'true');

// Check current configuration
console.log('Config:', config);
```

## 📊 Monitoring and Analytics

### Vercel Dashboard
Monitor your deployment at:
- **Functions**: View serverless function logs (if any)
- **Analytics**: Traffic and performance metrics
- **Speed Insights**: Core Web Vitals data
- **Security**: Security scan results

### Application Metrics
The frontend tracks:
- Usage count (localStorage)
- Email capture status
- Error rates and types
- Feature usage patterns

## 🚀 Post-Deployment Steps

1. **Test thoroughly** on the live URL
2. **Set up custom domain** (optional)
3. **Configure analytics** (Google Analytics, etc.)
4. **Monitor error rates** via browser dev tools
5. **Set up uptime monitoring** for the full stack

## 🔄 Updates and Redeployment

### Automatic Redeployment
If connected via GitHub:
- Push changes to main branch
- Vercel automatically redeploys

### Manual Redeployment
```bash
cd frontend
vercel --prod
```

## 🆘 Support

If you encounter issues:

1. **Check Vercel Status**: [status.vercel.com](https://status.vercel.com)
2. **Railway Backend**: Verify backend is running
3. **Browser Console**: Check for JavaScript errors
4. **Network Tab**: Verify API requests are being sent correctly

## 📝 Notes

- The frontend is a static SPA (Single Page Application)
- No build step required - pure HTML/CSS/JS
- Automatically handles environment detection
- Configured for optimal performance and security
- Ready for production use with the Railway backend
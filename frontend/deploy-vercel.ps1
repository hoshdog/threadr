# Threadr Frontend - Vercel Deployment Script
# Run this script from the frontend/ directory

Write-Host "🚀 Threadr Frontend - Vercel Deployment" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "index.html")) {
    Write-Host "❌ Error: index.html not found. Please run this script from the frontend/ directory." -ForegroundColor Red
    exit 1
}

# Check if Vercel CLI is installed
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelInstalled) {
    Write-Host "⚠️  Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Vercel CLI. Please install manually: npm install -g vercel" -ForegroundColor Red
        exit 1
    }
}

# Check Vercel login status
Write-Host "🔐 Checking Vercel authentication..." -ForegroundColor Blue
vercel whoami
if ($LASTEXITCODE -ne 0) {
    Write-Host "🔐 Please login to Vercel..." -ForegroundColor Yellow
    vercel login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Vercel login failed. Please try again." -ForegroundColor Red
        exit 1
    }
}

# Display current configuration
Write-Host "`n📋 Current Configuration:" -ForegroundColor Cyan
Write-Host "- Project: threadr-frontend" -ForegroundColor White
Write-Host "- Backend API: https://threadr-production.up.railway.app" -ForegroundColor White
Write-Host "- Files: index.html, config.js, vercel.json, package.json" -ForegroundColor White

# Ask for deployment type
Write-Host "`n🎯 Select deployment type:" -ForegroundColor Cyan
Write-Host "1. Preview deployment (for testing)" -ForegroundColor White
Write-Host "2. Production deployment" -ForegroundColor White
$choice = Read-Host "Enter your choice (1 or 2)"

switch ($choice) {
    "1" {
        Write-Host "`n🔄 Deploying to preview..." -ForegroundColor Blue
        vercel
    }
    "2" {
        Write-Host "`n🚀 Deploying to production..." -ForegroundColor Blue
        vercel --prod
    }
    default {
        Write-Host "❌ Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "`n🔗 Your frontend is now live and connected to the Railway backend." -ForegroundColor Green
    Write-Host "📱 Test the application by generating a thread from a URL or text." -ForegroundColor Green
    
    Write-Host "`n📊 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test the live deployment" -ForegroundColor White
    Write-Host "2. Set up custom domain (optional)" -ForegroundColor White
    Write-Host "3. Monitor usage and performance" -ForegroundColor White
} else {
    Write-Host "`n❌ Deployment failed. Please check the error messages above." -ForegroundColor Red
    Write-Host "💡 Common issues:" -ForegroundColor Yellow
    Write-Host "- Network connectivity problems" -ForegroundColor White
    Write-Host "- Vercel account limits reached" -ForegroundColor White
    Write-Host "- Configuration errors in vercel.json" -ForegroundColor White
}

Write-Host "`n🔧 For troubleshooting, check:" -ForegroundColor Cyan
Write-Host "- Vercel dashboard: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "- Railway backend: https://threadr-production.up.railway.app/health" -ForegroundColor White
Write-Host "- Browser console for client-side errors" -ForegroundColor White
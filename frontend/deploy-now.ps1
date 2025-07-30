# Quick Deployment Script for Threadr Frontend
# This script will guide you through the deployment process step by step

Write-Host "Threadr Frontend - Quick Deployment to Vercel" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "index.html") -or !(Test-Path "vercel.json")) {
    Write-Host "ERROR: Please run this script from the frontend directory" -ForegroundColor Red
    Write-Host "Required files not found: index.html, vercel.json" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found required deployment files" -ForegroundColor Green

# Check Vercel CLI
try {
    $vercelVersion = & vercel --version 2>$null
    Write-Host "✓ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Vercel CLI not found. Please install with: npm install -g vercel" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "DEPLOYMENT STEPS:" -ForegroundColor Yellow
Write-Host "=================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. First, authenticate with Vercel (browser will open)" -ForegroundColor Cyan
Write-Host "2. Then deploy to production" -ForegroundColor Cyan
Write-Host ""

# Step 1: Authentication
Write-Host "Step 1: Authenticating with Vercel..." -ForegroundColor Yellow
Write-Host "A browser window will open. Please sign in with your account." -ForegroundColor White
Write-Host ""

try {
    & vercel login
    Write-Host "✓ Authentication successful" -ForegroundColor Green
} catch {
    Write-Host "Authentication failed. Please try again manually: vercel login" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Production deployment
Write-Host "Step 2: Deploying to Vercel production..." -ForegroundColor Yellow

$deployArgs = @("--prod", "--yes")
Write-Host "Running: vercel $($deployArgs -join ' ')" -ForegroundColor Cyan
Write-Host ""

try {
    $deployResult = & vercel @deployArgs
    
    Write-Host "✓ Deployment completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Deployment output:" -ForegroundColor White
    Write-Host $deployResult
    
    # Try to extract URL
    $url = $deployResult | Select-String "https://.*\.vercel\.app" | Select-Object -First 1
    if ($url) {
        $deploymentUrl = $url.Matches[0].Value
        Write-Host ""
        Write-Host "🎉 SUCCESS! Your app is deployed at:" -ForegroundColor Green
        Write-Host $deploymentUrl -ForegroundColor White
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Visit the URL above to test your deployment" -ForegroundColor White
        Write-Host "2. Try creating a thread to test backend integration" -ForegroundColor White
        Write-Host "3. The 404 error should now be resolved!" -ForegroundColor White
    }
    
} catch {
    Write-Host "Deployment failed. Error details:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Try: vercel --prod --debug" -ForegroundColor White
    Write-Host "2. Check your Vercel account dashboard" -ForegroundColor White
    Write-Host "3. Ensure you have proper permissions" -ForegroundColor White
}

Write-Host ""
Write-Host "Deployment script completed." -ForegroundColor Green
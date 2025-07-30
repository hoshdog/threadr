# Threadr Frontend Deployment Script for Vercel
# Run this script from the root directory of the project

Write-Host "🚀 Threadr Frontend Deployment to Vercel" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "frontend\index.html")) {
    Write-Host "❌ Error: frontend\index.html not found. Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Set-Location frontend

Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Yellow

# Check Vercel CLI installation
Write-Host "🔍 Checking Vercel CLI installation..." -ForegroundColor Yellow
try {
    $vercelVersion = vercel --version
    Write-Host "✅ Vercel CLI installed: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
    Write-Host "✅ Vercel CLI installed successfully" -ForegroundColor Green
}

# Test backend API health
Write-Host "🏥 Testing backend API health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://threadr-production.up.railway.app/health" -Method Get
    if ($response.status -eq "healthy") {
        Write-Host "✅ Backend API is healthy: $($response.message)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend API status: $($response.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend API health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "⚠️  Continuing with deployment, but API may not be available" -ForegroundColor Yellow
}

# Check authentication status
Write-Host "🔐 Checking Vercel authentication..." -ForegroundColor Yellow
try {
    $authCheck = vercel whoami 2>$null
    if ($authCheck) {
        Write-Host "✅ Already authenticated as: $authCheck" -ForegroundColor Green
        $needsAuth = $false
    } else {
        $needsAuth = $true
    }
} catch {
    $needsAuth = $true
}

if ($needsAuth) {
    Write-Host "🔑 Authentication required. Please login to Vercel..." -ForegroundColor Yellow
    Write-Host "   Choose your preferred method (GitHub recommended)" -ForegroundColor Gray
    vercel login
    
    # Verify authentication worked
    try {
        $authCheck = vercel whoami
        Write-Host "✅ Successfully authenticated as: $authCheck" -ForegroundColor Green
    } catch {
        Write-Host "❌ Authentication failed. Please try again." -ForegroundColor Red
        exit 1
    }
}

# Deploy to production
Write-Host "🚀 Deploying to Vercel production..." -ForegroundColor Yellow
Write-Host "   This may take a few moments..." -ForegroundColor Gray

try {
    $deployResult = vercel --prod --yes 2>&1
    
    # Extract the production URL from the output
    $productionUrl = $deployResult | Select-String -Pattern "https://.*\.vercel\.app" | ForEach-Object { $_.Matches[0].Value }
    
    if ($productionUrl) {
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        Write-Host "🌐 Production URL: $productionUrl" -ForegroundColor Cyan
        Write-Host "📋 URL copied to clipboard" -ForegroundColor Gray
        
        # Copy URL to clipboard (Windows)
        $productionUrl | Set-Clipboard
        
        # Test the deployed frontend
        Write-Host "🧪 Testing deployed frontend..." -ForegroundColor Yellow
        try {
            $testResponse = Invoke-WebRequest -Uri $productionUrl -Method Get -TimeoutSec 10
            if ($testResponse.StatusCode -eq 200) {
                Write-Host "✅ Frontend is accessible and responding" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Frontend returned status code: $($testResponse.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "⚠️  Deployment completed but couldn't extract URL from output" -ForegroundColor Yellow
        Write-Host "Full output:" -ForegroundColor Gray
        Write-Host $deployResult -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Full error output:" -ForegroundColor Gray
    Write-Host $deployResult -ForegroundColor Red
    exit 1
}

# Final instructions
Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host "Frontend URL: $productionUrl" -ForegroundColor Cyan
Write-Host "Backend API:  https://threadr-production.up.railway.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Visit the frontend URL to test the application" -ForegroundColor White
Write-Host "2. Try converting a blog article URL to a Twitter thread" -ForegroundColor White
Write-Host "3. Verify that the API connection works properly" -ForegroundColor White
Write-Host "4. Test the email capture modal after first use" -ForegroundColor White
Write-Host ""
Write-Host "If you encounter issues, check the browser console for errors." -ForegroundColor Gray

# Return to original directory
Set-Location ..
# Threadr Deployment Script for Windows
# This script helps deploy both frontend and backend

Write-Host "Threadr Deployment Helper" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Check if Railway CLI is installed
try {
    railway --version | Out-Null
} catch {
    Write-Host "Railway CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

# Check if Vercel CLI is installed
try {
    vercel --version | Out-Null
} catch {
    Write-Host "Vercel CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g vercel" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Yellow
Write-Host "1. Make sure you have accounts on Railway and Vercel"
Write-Host "2. Your OPENAI_API_KEY should be ready"
Write-Host "3. Update frontend/config.js with your Railway URL after deployment"
Write-Host ""

$continue = Read-Host "Continue with deployment? (y/n)"
if ($continue -ne 'y') {
    exit 0
}

Write-Host ""
Write-Host "Step 1: Deploying Backend to Railway" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Set-Location backend

Write-Host "Logging into Railway..."
railway login

Write-Host "Creating new Railway project..."
railway init

Write-Host "Adding environment variables..."
Write-Host "Please add OPENAI_API_KEY in Railway dashboard after deployment" -ForegroundColor Yellow

Write-Host "Deploying to Railway..."
railway up

Write-Host "Backend deployment initiated! Check Railway dashboard for status." -ForegroundColor Green
Write-Host ""

Set-Location ..

Write-Host "Step 2: Deploying Frontend to Vercel" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Set-Location frontend

Write-Host "Deploying to Vercel..."
vercel

Write-Host ""
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Add OPENAI_API_KEY in Railway dashboard"
Write-Host "2. Update frontend/config.js with your Railway backend URL"
Write-Host "3. Redeploy frontend with: vercel --prod"
Write-Host "4. Update CORS_ORIGINS in Railway with your Vercel URL"
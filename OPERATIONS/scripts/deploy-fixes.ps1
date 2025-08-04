# Threadr Fixes Deployment Script
# This script deploys the fixes for logo loading and template page issues

Write-Host "🔧 Deploying Threadr Fixes..." -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend\public\index.html")) {
    Write-Host "❌ Error: Please run this script from the Threadr root directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found Threadr project structure" -ForegroundColor Green

# Display what fixes are being deployed
Write-Host ""
Write-Host "📋 Fixes being deployed:" -ForegroundColor Cyan
Write-Host "1. Logo Loading Fix: Updated Vercel rewrites to exclude static assets"
Write-Host "2. Templates Page Fix: Removed debugging return statements from template functions"
Write-Host ""

# Verify fixes are in place
Write-Host "🔍 Verifying fixes..." -ForegroundColor Yellow

# Check Vercel configuration
$vercelConfig = Get-Content "frontend\vercel.json" -Raw
if ($vercelConfig -match "logos|assets") {
    Write-Host "✅ Vercel rewrite fix detected in configuration" -ForegroundColor Green
} else {
    Write-Host "❌ Vercel rewrite fix not found" -ForegroundColor Red
    exit 1
}

# Check template functions
$indexContent = Get-Content "frontend\public\index.html" -Raw
if ($indexContent -match "getPopularTemplates\(\)\s*\{\s*const filtered") {
    Write-Host "✅ Template function fix detected (no debugging returns)" -ForegroundColor Green
} else {
    Write-Host "❌ Template function fix not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 All fixes verified. Deploying to Vercel..." -ForegroundColor Yellow

# Deploy to Vercel
Set-Location "frontend"
$deployResult = & vercel --prod 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Post-deployment verification:" -ForegroundColor Cyan
    Write-Host "1. Visit your Threadr app and check that logos are loading"
    Write-Host "2. Navigate to the Templates page and verify it shows content"
    Write-Host "3. Try selecting a template to test functionality"
    Write-Host ""
    Write-Host "🔗 Test the fixes at: https://threadr-plum.vercel.app" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🧪 Use the verification page: https://threadr-plum.vercel.app/verify-fixes.html" -ForegroundColor Blue
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Error output:" -ForegroundColor Red
    Write-Host $deployResult -ForegroundColor Red
    exit 1
}

Set-Location ".."
Write-Host ""
Write-Host "✅ Fix deployment complete!" -ForegroundColor Green
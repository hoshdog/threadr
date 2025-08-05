# Threadr Next.js Deployment Script for PowerShell

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    Threadr Next.js Deployment to Vercel" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
try {
    $null = Get-Command vercel -ErrorAction Stop
    Write-Host "✓ Vercel CLI found" -ForegroundColor Green
} catch {
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

Write-Host ""
Write-Host "Starting Vercel deployment..." -ForegroundColor Yellow
Write-Host ""
Write-Host "When prompted:" -ForegroundColor Magenta
Write-Host "1. Login if needed" -ForegroundColor White
Write-Host "2. Accept default project settings" -ForegroundColor White
Write-Host "3. Note the deployment URL" -ForegroundColor White
Write-Host ""

# Deploy to production
vercel --prod

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "    🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy your Vercel URL" -ForegroundColor White
Write-Host "2. Update environment variables in Vercel dashboard:" -ForegroundColor White
Write-Host "   - NEXT_PUBLIC_API_BASE_URL = [backend URL]" -ForegroundColor Gray
Write-Host "   - NEXT_PUBLIC_APP_URL = [your Vercel URL]" -ForegroundColor Gray
Write-Host "3. Test the deployment" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
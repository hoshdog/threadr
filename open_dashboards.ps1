# Open all relevant dashboards for Threadr configuration

Write-Host "Opening Threadr Configuration Dashboards..." -ForegroundColor Green
Write-Host ""

# Open Vercel Dashboard
Write-Host "1. Opening Vercel Dashboard for API Key configuration..." -ForegroundColor Yellow
Start-Process "https://vercel.com/dashboard"
Write-Host "   - Navigate to your threadr project" -ForegroundColor Gray
Write-Host "   - Go to Settings -> Environment Variables" -ForegroundColor Gray
Write-Host "   - Add: THREADR_API_KEY = zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2

# Open Railway Dashboard
Write-Host "2. Opening Railway Dashboard for Redis setup..." -ForegroundColor Yellow
Start-Process "https://railway.app/dashboard"
Write-Host "   - Click New Service -> Database -> Redis" -ForegroundColor Gray
Write-Host "   - Or use Upstash free tier instead" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2

# Open Upstash Console (alternative)
Write-Host "3. Opening Upstash Console (free Redis alternative)..." -ForegroundColor Yellow
Start-Process "https://console.upstash.com"
Write-Host "   - Create free account if you prefer Upstash over Railway Redis" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2

# Open Production Site
Write-Host "4. Opening your production site to verify changes..." -ForegroundColor Yellow
Start-Process "https://threadr-plum.vercel.app"
Write-Host "   - Check that UX improvements are visible" -ForegroundColor Gray
Write-Host "   - Open DevTools (F12) to verify API key is hidden" -ForegroundColor Gray
Write-Host ""

# Instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configure API Key in Vercel (CRITICAL!)" -ForegroundColor Red
Write-Host "2. Set up Redis (Railway or Upstash)" -ForegroundColor Yellow
Write-Host "3. Run verification: .\run_verification_suite.bat" -ForegroundColor Green
Write-Host ""
Write-Host "All dashboards have been opened in your browser." -ForegroundColor Green
Write-Host "Complete the configuration in each dashboard." -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
@echo off
echo ========================================
echo Opening Threadr Configuration Dashboards
echo ========================================
echo.

echo 1. Opening Vercel Dashboard for API Key configuration...
start https://vercel.com/dashboard
echo    - Navigate to your threadr project
echo    - Go to Settings -^> Environment Variables
echo    - Add: THREADR_API_KEY = zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8
echo    - WARNING: Use THREADR_API_KEY (with underscores), NOT threadr-api-key!
echo.

timeout /t 2 /nobreak >nul

echo 2. Opening Railway Dashboard for Redis setup...
start https://railway.app/dashboard
echo    - Click New Service -^> Database -^> Redis
echo    - Or use Upstash free tier instead
echo.

timeout /t 2 /nobreak >nul

echo 3. Opening Upstash Console (free Redis alternative)...
start https://console.upstash.com
echo    - Create free account if you prefer Upstash over Railway Redis
echo.

timeout /t 2 /nobreak >nul

echo 4. Opening your production site to verify changes...
start https://threadr-plum.vercel.app
echo    - Check that UX improvements are visible
echo    - Open DevTools (F12) to verify API key is hidden
echo.

echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo 1. Configure API Key in Vercel (CRITICAL!)
echo 2. Set up Redis (Railway or Upstash)
echo 3. Run verification: run_verification_suite.bat
echo.
echo All dashboards have been opened in your browser.
echo Complete the configuration in each dashboard.
echo.
echo Press any key to exit...
pause >nul
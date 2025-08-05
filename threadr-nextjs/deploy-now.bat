@echo off
echo ============================================
echo     Threadr Next.js Deployment to Vercel
echo ============================================
echo.

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Vercel CLI...
    npm install -g vercel
)

echo Starting Vercel deployment...
echo.
echo When prompted:
echo 1. Login if needed
echo 2. Accept default project settings
echo 3. Note the deployment URL
echo.

REM Deploy to production
vercel --prod

echo.
echo ============================================
echo     Deployment Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Copy your Vercel URL
echo 2. Update environment variables in Vercel dashboard
echo 3. Test the deployment
echo.
pause
@echo off
echo ===============================================
echo  Threadr Next.js - Vercel Staging Deployment
echo ===============================================
echo.

echo Checking Vercel CLI...
vercel --version
if %errorlevel% neq 0 (
    echo ERROR: Vercel CLI not found. Please install with: npm i -g vercel
    pause
    exit /b 1
)

echo.
echo Checking build status...
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Build failed. Please check for errors above.
    pause
    exit /b 1
)

echo.
echo Build successful! Starting deployment...
echo.
echo IMPORTANT: When prompted, choose:
echo   - Set up and deploy: Yes
echo   - Link to existing project: No (new deployment)
echo   - Project name: threadr-nextjs-staging
echo   - Directory: Accept default (./)
echo   - Override settings: No
echo.
pause

echo Deploying to Vercel staging...
vercel --prod=false

echo.
echo ===============================================
echo Deployment completed!
echo.
echo Next steps:
echo 1. Note your deployment URL from above
echo 2. Go to Vercel Dashboard
echo 3. Add environment variables (see VERCEL_DEPLOYMENT_INSTRUCTIONS.md)
echo 4. Redeploy with: vercel --prod=false
echo ===============================================
pause
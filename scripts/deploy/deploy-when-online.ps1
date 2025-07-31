# PowerShell script for Windows users to deploy Threadr when network returns
# Threadr Deployment Script for Windows

param(
    [string]$BackendUrl = "http://localhost:8001",
    [string]$ProjectRoot = ".",
    [switch]$TestOnly,
    [switch]$WaitForNetwork,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Threadr Deployment Script for Windows

Usage:
  .\deploy-when-online.ps1 [options]

Options:
  -BackendUrl <url>     Backend URL for testing (default: http://localhost:8001)
  -ProjectRoot <path>   Project root directory (default: current directory)
  -TestOnly            Only run tests, don't deploy
  -WaitForNetwork      Wait for network connectivity before proceeding
  -Help                Show this help message

Examples:
  .\deploy-when-online.ps1 -TestOnly
  .\deploy-when-online.ps1 -WaitForNetwork
  .\deploy-when-online.ps1 -BackendUrl "https://threadr-production.up.railway.app"
"@
    exit 0
}

Write-Host "🚀 Threadr Deployment Script for Windows" -ForegroundColor Green
Write-Host "=" * 50

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
$mainPy = Join-Path $ProjectRoot "backend\src\main.py"
if (-not (Test-Path $mainPy)) {
    Write-Host "❌ Not in Threadr project directory. Please navigate to project root." -ForegroundColor Red
    exit 1
}

Write-Host "📁 Project root: $(Resolve-Path $ProjectRoot)" -ForegroundColor Cyan

if ($TestOnly) {
    Write-Host "🧪 Running local tests only..." -ForegroundColor Yellow
    
    # Run local verification
    Write-Host "📋 Running deployment verification..." -ForegroundColor Cyan
    python "scripts\deploy\local-verification.py" --backend-url $BackendUrl
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed!" -ForegroundColor Green
        
        # Run monetization tests
        Write-Host "💰 Running monetization tests..." -ForegroundColor Cyan
        python "scripts\test\test-monetization-features.py" --backend-url $BackendUrl
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "🎉 All monetization features working!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Some monetization tests failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Some tests failed" -ForegroundColor Red
    }
    exit $LASTEXITCODE
}

if ($WaitForNetwork) {
    Write-Host "🌐 Waiting for network connectivity and deploying..." -ForegroundColor Yellow
    python "scripts\deploy\auto-deploy-when-online.py" --project-root $ProjectRoot
} else {
    # Check network immediately
    Write-Host "🌐 Checking network connectivity..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "https://github.com" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Network is available, starting deployment..." -ForegroundColor Green
            python "scripts\deploy\auto-deploy-when-online.py" --project-root $ProjectRoot --immediate
        } else {
            Write-Host "❌ Network not available" -ForegroundColor Red
            Write-Host "💡 Use -WaitForNetwork to wait for connectivity" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "❌ Network not available: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Use -WaitForNetwork to wait for connectivity" -ForegroundColor Yellow
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
}

exit $LASTEXITCODE
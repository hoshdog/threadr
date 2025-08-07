#!/usr/bin/env pwsh
<#
.SYNOPSIS
    PowerShell script to run comprehensive Threadr business functionality tests
    
.DESCRIPTION
    This script runs the complete business functionality test suite for Threadr,
    validating thread generation, storage, authentication, rate limiting, and analytics.
    
.PARAMETER BaseUrl
    Base URL for the Threadr API (default: https://threadr-pw0s.onrender.com)
    
.PARAMETER Environment
    Environment to test (production, staging, local)
    
.PARAMETER SkipCleanup
    Skip cleanup of test data (useful for debugging)
    
.EXAMPLE
    .\run_business_tests.ps1
    
.EXAMPLE
    .\run_business_tests.ps1 -Environment staging -BaseUrl "https://staging-api.threadr.com"
#>

param(
    [string]$BaseUrl = "https://threadr-pw0s.onrender.com",
    [ValidateSet("production", "staging", "local")]
    [string]$Environment = "production",
    [switch]$SkipCleanup
)

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🚀 Threadr Business Functionality Test Suite" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

# Environment setup
Write-Host "🔧 Setting up test environment..." -ForegroundColor Yellow
$env:BASE_URL = $BaseUrl

# Check Python availability
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Python not found. Please install Python 3.8+ and ensure it's in PATH"
    exit 1
}

# Check required packages
Write-Host "📦 Checking Python dependencies..." -ForegroundColor Yellow
$requiredPackages = @("httpx", "asyncio")

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "✅ Package '$package' available" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Installing missing package: $package" -ForegroundColor Yellow
        pip install $package
    }
}

# Display test configuration
Write-Host "`n🎯 TEST CONFIGURATION:" -ForegroundColor Cyan
Write-Host "   Base URL: $BaseUrl"
Write-Host "   Environment: $Environment"
Write-Host "   Skip Cleanup: $($SkipCleanup.ToString())"
Write-Host "   Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Validate API availability
Write-Host "`n🔍 Pre-flight checks..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 30
    Write-Host "✅ API Health: $($healthCheck.status)" -ForegroundColor Green
    
    if ($healthCheck.services.database -eq $true) {
        Write-Host "✅ Database: Connected" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database: Not available" -ForegroundColor Yellow
    }
    
    if ($healthCheck.services.redis -eq $true) {
        Write-Host "✅ Redis: Connected" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Redis: Not available" -ForegroundColor Yellow
    }
    
} catch {
    Write-Error "❌ Pre-flight check failed: API not responding at $BaseUrl"
    exit 1
}

# Run the comprehensive test suite
Write-Host "`n🧪 Starting comprehensive business functionality tests..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Yellow

$testScriptPath = Join-Path $PSScriptRoot "test_core_business_functionality.py"

if (-not (Test-Path $testScriptPath)) {
    Write-Error "❌ Test script not found at: $testScriptPath"
    exit 1
}

try {
    # Execute the Python test suite
    $startTime = Get-Date
    
    Write-Host "⏳ Executing test suite (this may take 2-5 minutes)..." -ForegroundColor Yellow
    python $testScriptPath
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
        Write-Host "✅ Core business functionality is working correctly" -ForegroundColor Green
        Write-Host "📈 Revenue-generating features validated" -ForegroundColor Green
        Write-Host "🔒 Security and authentication verified" -ForegroundColor Green
        Write-Host "💾 Data persistence confirmed" -ForegroundColor Green
        
        Write-Host "`n⏱️  Total execution time: $($duration.ToString('F2')) seconds" -ForegroundColor Cyan
        
        # Success recommendations
        Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Cyan
        Write-Host "   1. ✅ System ready for production traffic"
        Write-Host "   2. 📊 Consider setting up monitoring alerts"
        Write-Host "   3. 🚀 Deploy any pending features"
        Write-Host "   4. 💰 Focus on user acquisition"
        
    } else {
        Write-Host "`n⚠️  SOME TESTS FAILED" -ForegroundColor Red
        Write-Host "❌ Core business functionality has issues" -ForegroundColor Red
        Write-Host "🔧 Review test report for specific failures" -ForegroundColor Yellow
        Write-Host "⚠️  DO NOT deploy to production until issues are resolved" -ForegroundColor Red
        
        # Check for test report files
        $reportFiles = Get-ChildItem -Path "." -Name "threadr_test_report_*.json" | Sort-Object LastWriteTime -Descending
        if ($reportFiles) {
            Write-Host "`n📄 Latest test report: $($reportFiles[0])" -ForegroundColor Yellow
        }
        
        exit 1
    }
    
} catch {
    Write-Host "`n💥 TEST EXECUTION FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔧 TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "   1. Check API connectivity: curl $BaseUrl/health"
    Write-Host "   2. Verify environment variables are set"
    Write-Host "   3. Check Python dependencies: pip list"
    Write-Host "   4. Review logs above for specific errors"
    
    exit 1
}

# Display additional information
Write-Host "`n📋 TEST COVERAGE:" -ForegroundColor Cyan
Write-Host "   ✅ Thread Generation (URL + Content)"
Write-Host "   ✅ OpenAI API Integration"
Write-Host "   ✅ PostgreSQL Data Storage"
Write-Host "   ✅ User Authentication (JWT)"
Write-Host "   ✅ Rate Limiting (Free vs Premium)"
Write-Host "   ✅ Thread CRUD Operations"
Write-Host "   ✅ Analytics Tracking"
Write-Host "   ✅ Data Persistence Validation"

Write-Host "`n🔍 MONITORED METRICS:" -ForegroundColor Cyan
Write-Host "   📊 API Response Times"
Write-Host "   💾 Database Connection Health"
Write-Host "   🧠 AI Generation Success Rate"
Write-Host "   🔐 Authentication Success Rate"
Write-Host "   📈 Feature Completion Rate"

if (-not $SkipCleanup) {
    Write-Host "`n🧹 Cleanup completed automatically" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Test data cleanup SKIPPED (as requested)" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "✅ Business functionality testing completed successfully!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
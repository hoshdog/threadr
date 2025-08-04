# Threadr Deployment Verification Suite - PowerShell Version
# Run this script to verify your Week 1 premium improvements deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Threadr Deployment Verification Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
Set-Location $PSScriptRoot

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ and add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting comprehensive deployment verification..." -ForegroundColor Yellow
Write-Host ""

# Create output directory for reports
$reportsDir = "verification_reports"
if (!(Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir | Out-Null
}

# Generate timestamp for report naming
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Function to run a command and check its exit code
function Invoke-VerificationTest {
    param(
        [string]$TestName,
        [string]$Command,
        [string]$Description
    )
    
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "$TestName" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "$Description" -ForegroundColor Gray
    Write-Host ""
    
    try {
        Invoke-Expression $Command
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "✅ $TestName completed successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $TestName completed with warnings (exit code: $exitCode)" -ForegroundColor Yellow
        }
        return $exitCode
    } catch {
        Write-Host "❌ $TestName failed with error: $_" -ForegroundColor Red
        return 1
    }
}

# Run verification tests
$results = @{}

Write-Host "🚀 Starting verification tests..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Production Verification
$cmd1 = "python scripts/verification/production_verification.py --verbose --json-output `"$reportsDir/production_verification_$timestamp.json`""
$results['Production'] = Invoke-VerificationTest -TestName "1/3: Production Verification" -Command $cmd1 -Description "Testing all core functionality and API endpoints..."

Write-Host ""

# Test 2: Security Monitoring
$cmd2 = "python scripts/monitoring/api_security_monitor.py --verbose --json-output `"$reportsDir/security_report_$timestamp.json`""
$results['Security'] = Invoke-VerificationTest -TestName "2/3: Security Monitoring" -Command $cmd2 -Description "Checking API security and configuration..."

Write-Host ""

# Test 3: Performance Tests
$cmd3 = "python scripts/performance/redis_performance_test.py --test-suite standard --duration 20 --workers 3 --json-output `"$reportsDir/performance_report_$timestamp.json`""
$results['Performance'] = Invoke-VerificationTest -TestName "3/3: Performance Tests" -Command $cmd3 -Description "Testing Redis and API performance..."

Write-Host ""

# Generate summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification Suite Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Count results
$passed = ($results.Values | Where-Object { $_ -eq 0 }).Count
$total = $results.Count
$warnings = ($results.Values | Where-Object { $_ -ne 0 }).Count

Write-Host "📊 Test Results Summary:" -ForegroundColor White
Write-Host "✅ Passed: $passed/$total" -ForegroundColor Green
if ($warnings -gt 0) {
    Write-Host "⚠️ Warnings: $warnings/$total" -ForegroundColor Yellow
}

# Show individual results
foreach ($test in $results.Keys) {
    $status = if ($results[$test] -eq 0) { "✅ PASSED" } else { "⚠️ WARNING" }
    $color = if ($results[$test] -eq 0) { "Green" } else { "Yellow" }
    Write-Host "   $test: $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "📁 Reports saved to: $reportsDir/" -ForegroundColor White
Write-Host "   - production_verification_$timestamp.json" -ForegroundColor Gray
Write-Host "   - security_report_$timestamp.json" -ForegroundColor Gray
Write-Host "   - performance_report_$timestamp.json" -ForegroundColor Gray

Write-Host ""
Write-Host "🌐 To view the monitoring dashboard:" -ForegroundColor Yellow
Write-Host "   1. Open a new PowerShell window" -ForegroundColor Gray
Write-Host "   2. Run: python -m http.server 8080" -ForegroundColor Gray
Write-Host "   3. Open: http://localhost:8080/monitoring_dashboard.html" -ForegroundColor Gray

Write-Host ""

# Overall status
if ($passed -eq $total) {
    Write-Host "🎉 All tests passed! Your deployment is ready for production." -ForegroundColor Green
} elseif ($warnings -gt 0 -and $passed -gt 0) {
    Write-Host "⚠️ Some tests have warnings. Review the reports for details." -ForegroundColor Yellow
} else {
    Write-Host "❌ Critical issues found. Please address them before going to production." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
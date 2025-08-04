@echo off
echo ========================================
echo Threadr Deployment Verification Suite
echo ========================================
echo.

:: Set the working directory
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

echo Starting comprehensive deployment verification...
echo.

:: Create output directory for reports
if not exist "verification_reports" mkdir verification_reports

:: Get timestamp for report naming
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

echo ========================================
echo 1/3: Running Production Verification
echo ========================================
echo This tests all core functionality...
echo.

python scripts/verification/production_verification.py --verbose --json-output "verification_reports/production_verification_%timestamp%.json"

echo.
echo ========================================
echo 2/3: Running Security Monitoring
echo ========================================
echo This checks API security and configuration...
echo.

python scripts/monitoring/api_security_monitor.py --verbose --json-output "verification_reports/security_report_%timestamp%.json"

echo.
echo ========================================
echo 3/3: Running Performance Tests
echo ========================================
echo This tests Redis and API performance...
echo.

python scripts/performance/redis_performance_test.py --test-suite standard --duration 20 --workers 3 --json-output "verification_reports/performance_report_%timestamp%.json"

echo.
echo ========================================
echo Verification Suite Complete!
echo ========================================
echo.
echo Reports saved to: verification_reports/
echo - production_verification_%timestamp%.json
echo - security_report_%timestamp%.json  
echo - performance_report_%timestamp%.json
echo.
echo To view the monitoring dashboard:
echo 1. Open a new command prompt
echo 2. Run: python -m http.server 8080
echo 3. Open: http://localhost:8080/monitoring_dashboard.html
echo.
echo Press any key to exit...
pause >nul
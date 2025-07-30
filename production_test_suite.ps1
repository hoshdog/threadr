# Threadr Production API Test Suite (PowerShell)
# Tests all features of the deployed API at https://threadr-production.up.railway.app

$BaseUrl = "https://threadr-production.up.railway.app"
$ApiKey1 = "zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8"
$ApiKey2 = "FFAvIrarUm32RGDntib20DzSU21-B_zJ4w8mzaSz1So"
$InvalidKey = "invalid-key-for-testing"

# Test counters
$TestsPassed = 0
$TestsFailed = 0

# Helper functions
function Log-Test($message) {
    Write-Host "[TEST] $message" -ForegroundColor Blue
}

function Log-Success($message) {
    Write-Host "[PASS] $message" -ForegroundColor Green
    $script:TestsPassed++
}

function Log-Failure($message) {
    Write-Host "[FAIL] $message" -ForegroundColor Red
    $script:TestsFailed++
}

function Log-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Yellow
}

# Test wrapper function
function Run-Test($testName, $testFunction) {
    Log-Test $testName
    try {
        $result = & $testFunction
        if ($result) {
            Log-Success $testName
        } else {
            Log-Failure $testName
        }
    } catch {
        Log-Failure "$testName - Exception: $($_.Exception.Message)"
    }
    Write-Host ""
}

# HTTP request helper
function Invoke-APIRequest($method, $endpoint, $headers = @{}, $body = $null) {
    try {
        $uri = "$BaseUrl$endpoint"
        $params = @{
            Uri = $uri
            Method = $method
            Headers = $headers
            TimeoutSec = 30
        }
        
        if ($body) {
            $params.Body = $body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params -ErrorAction SilentlyContinue
        return @{
            StatusCode = $response.StatusCode
            Content = $response.Content
            Headers = $response.Headers
        }
    } catch {
        $statusCode = 0
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        return @{
            StatusCode = $statusCode
            Content = $_.Exception.Message
            Headers = @{}
        }
    }
}

# Test functions
function Test-HealthEndpoint {
    $response = Invoke-APIRequest -method "GET" -endpoint "/health"
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return $json.status -eq "healthy"
        } catch {
            return $false
        }
    }
    return $false
}

function Test-ReadinessEndpoint {
    $response = Invoke-APIRequest -method "GET" -endpoint "/readiness"
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return $json.status -eq "ready"
        } catch {
            return $false
        }
    }
    return $false
}

function Test-MonitorHealth {
    $response = Invoke-APIRequest -method "GET" -endpoint "/api/monitor/health"
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return ($json.status -eq "healthy") -and ($null -ne $json.services)
        } catch {
            return $false
        }
    }
    return $false
}

function Test-TestEndpoint {
    $response = Invoke-APIRequest -method "GET" -endpoint "/api/test"
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return $json.status -eq "working"
        } catch {
            return $false
        }
    }
    return $false
}

function Test-AuthNoKey {
    $body = '{"text": "Test authentication without API key"}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -body $body
    return $response.StatusCode -eq 401
}

function Test-AuthInvalidKey {
    $headers = @{ "X-API-Key" = $InvalidKey }
    $body = '{"text": "Test authentication with invalid API key"}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    return $response.StatusCode -eq 401
}

function Test-AuthValidKey {
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $body = '{"text": "Test authentication with valid API key"}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return ($json.success -eq $true) -and ($null -ne $json.thread)
        } catch {
            return $false
        }
    }
    return $false
}

function Test-GenerateThreadFromText {
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $testText = "This is a comprehensive test of the thread generation functionality. It should be split into multiple tweets based on the 280 character limit. The system should handle this gracefully and create a properly numbered thread with appropriate content distribution."
    $body = @{ text = $testText } | ConvertTo-Json
    
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return ($json.success -eq $true) -and ($json.thread.Count -gt 1) -and ($json.source_type -eq "text")
        } catch {
            return $false
        }
    }
    return $false
}

function Test-GenerateThreadFromUrl {
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $testUrl = "https://medium.com/@test/sample-article"
    $body = @{ url = $testUrl } | ConvertTo-Json
    
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    
    # URL may fail to fetch (expected), but should return proper error structure
    try {
        $json = $response.Content | ConvertFrom-Json
        return $null -ne $json.PSObject.Properties["success"]
    } catch {
        return $false
    }
}

function Test-RateLimitStatus {
    $response = Invoke-APIRequest -method "GET" -endpoint "/api/rate-limit-status"
    
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return ($null -ne $json.PSObject.Properties["requests_used"]) -and 
                   ($null -ne $json.PSObject.Properties["requests_remaining"]) -and 
                   ($null -ne $json.PSObject.Properties["total_limit"])
        } catch {
            return $false
        }
    }
    return $false
}

function Test-CacheStats {
    $response = Invoke-APIRequest -method "GET" -endpoint "/api/cache/stats"
    
    if ($response.StatusCode -eq 200) {
        try {
            $json = $response.Content | ConvertFrom-Json
            return $null -ne $json.PSObject.Properties["available"]
        } catch {
            return $false
        }
    }
    return $false
}

function Test-SecurityHeaders {
    $response = Invoke-APIRequest -method "GET" -endpoint "/health"
    $headers = $response.Headers
    
    return ($headers.ContainsKey("X-Content-Type-Options")) -and
           ($headers.ContainsKey("X-Frame-Options")) -and
           ($headers.ContainsKey("X-XSS-Protection")) -and
           ($headers.ContainsKey("Content-Security-Policy"))
}

function Test-CorsHeaders {
    $headers = @{ "Origin" = "https://example.com" }
    $response = Invoke-APIRequest -method "GET" -endpoint "/health" -headers $headers
    
    $responseHeaders = $response.Headers
    foreach ($key in $responseHeaders.Keys) {
        if ($key -like "*Access-Control-Allow*") {
            return $true
        }
    }
    return $false
}

function Test-InvalidRequestFormat {
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $body = '{"invalid": "request"}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    return $response.StatusCode -eq 422
}

function Test-EmptyText {
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $body = '{"text": ""}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    return $response.StatusCode -eq 422
}

function Test-BothUrlAndText {
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $body = '{"text": "Test", "url": "https://example.com"}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    return $response.StatusCode -eq 422
}

function Test-PerformanceSimpleText {
    $startTime = Get-Date
    
    $headers = @{ "X-API-Key" = $ApiKey1 }
    $body = '{"text": "Quick performance test of the API"}'
    $response = Invoke-APIRequest -method "POST" -endpoint "/api/generate" -headers $headers -body $body
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalMilliseconds
    
    Log-Info "API response time: $([math]::Round($duration, 2))ms"
    
    return ($response.StatusCode -eq 200) -and ($duration -lt 5000) # Should respond within 5 seconds
}

# MAIN TEST EXECUTION
Write-Host "==================================="
Write-Host "Threadr Production API Test Suite"
Write-Host "Testing: $BaseUrl"
Write-Host "==================================="
Write-Host ""

# Basic Health Tests
Write-Host "--- HEALTH & MONITORING TESTS ---"
Run-Test "Health endpoint responds correctly" { Test-HealthEndpoint }
Run-Test "Readiness endpoint responds correctly" { Test-ReadinessEndpoint }
Run-Test "Monitor health endpoint provides detailed status" { Test-MonitorHealth }
Run-Test "Test endpoint confirms API functionality" { Test-TestEndpoint }

# Authentication Tests
Write-Host "--- AUTHENTICATION TESTS ---"
Run-Test "Reject requests without API key" { Test-AuthNoKey }
Run-Test "Reject requests with invalid API key" { Test-AuthInvalidKey }
Run-Test "Accept requests with valid API key" { Test-AuthValidKey }

# Core Functionality Tests
Write-Host "--- THREAD GENERATION TESTS ---"
Run-Test "Generate thread from text content" { Test-GenerateThreadFromText }
Run-Test "Handle URL input (may fail gracefully)" { Test-GenerateThreadFromUrl }

# Rate Limiting & Caching Tests
Write-Host "--- RATE LIMITING & CACHING TESTS ---"
Run-Test "Rate limit status endpoint works" { Test-RateLimitStatus }
Run-Test "Cache stats endpoint responds" { Test-CacheStats }

# Security Tests
Write-Host "--- SECURITY TESTS ---"
Run-Test "Security headers are present" { Test-SecurityHeaders }
Run-Test "CORS headers are configured" { Test-CorsHeaders }

# Error Handling Tests
Write-Host "--- ERROR HANDLING TESTS ---"
Run-Test "Reject invalid request format" { Test-InvalidRequestFormat }
Run-Test "Reject empty text input" { Test-EmptyText }
Run-Test "Reject both URL and text in same request" { Test-BothUrlAndText }

# Performance Tests
Write-Host "--- PERFORMANCE TESTS ---"
Run-Test "API responds within acceptable time" { Test-PerformanceSimpleText }

# FINAL RESULTS
Write-Host "==================================="
Write-Host "TEST RESULTS SUMMARY"
Write-Host "==================================="
Write-Host "Tests Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $TestsFailed" -ForegroundColor Red
Write-Host "Total Tests: $($TestsPassed + $TestsFailed)"

if ($TestsFailed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! The API is production ready." -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed. Please review the failures above." -ForegroundColor Red
}
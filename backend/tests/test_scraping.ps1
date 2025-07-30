# PowerShell script to test Threadr web scraping functionality
# Run this script to test all endpoints

$BaseUrl = "http://localhost:8001"
$Results = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    BaseUrl = $BaseUrl
    Tests = @()
    Summary = @{
        Total = 0
        Success = 0
        Failed = 0
    }
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method = "GET",
        [string]$Endpoint,
        [hashtable]$Body = @{},
        [hashtable]$Query = @{}
    )
    
    Write-Host "`n[$Name]" -ForegroundColor Cyan
    
    $Uri = "$BaseUrl$Endpoint"
    
    # Add query parameters
    if ($Query.Count -gt 0) {
        $QueryString = ($Query.GetEnumerator() | ForEach-Object { "$($_.Key)=$([System.Web.HttpUtility]::UrlEncode($_.Value))" }) -join "&"
        $Uri = "$Uri?$QueryString"
    }
    
    Write-Host "URL: $Uri" -ForegroundColor Gray
    
    $TestResult = @{
        Name = $Name
        Endpoint = $Endpoint
        Method = $Method
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Success = $false
        Response = $null
        Error = $null
    }
    
    try {
        if ($Method -eq "GET") {
            $Response = Invoke-RestMethod -Uri $Uri -Method Get -TimeoutSec 30
        }
        elseif ($Method -eq "POST") {
            $JsonBody = $Body | ConvertTo-Json
            Write-Host "Body: $JsonBody" -ForegroundColor Gray
            $Response = Invoke-RestMethod -Uri $Uri -Method Post -Body $JsonBody -ContentType "application/json" -TimeoutSec 30
        }
        
        $TestResult.Success = $true
        $TestResult.Response = $Response
        $Results.Summary.Success++
        
        Write-Host "✅ Success" -ForegroundColor Green
        
        # Display key information based on endpoint
        if ($Response) {
            if ($Response.status) {
                Write-Host "  Status: $($Response.status)" -ForegroundColor Gray
            }
            if ($Response.success -ne $null) {
                Write-Host "  Success: $($Response.success)" -ForegroundColor Gray
            }
            if ($Response.title) {
                Write-Host "  Title: $($Response.title)" -ForegroundColor Gray
            }
            if ($Response.thread) {
                Write-Host "  Tweets: $($Response.thread.Count)" -ForegroundColor Gray
            }
            if ($Response.error) {
                Write-Host "  Error: $($Response.error)" -ForegroundColor Yellow
            }
        }
    }
    catch {
        $TestResult.Success = $false
        $TestResult.Error = $_.Exception.Message
        $Results.Summary.Failed++
        
        Write-Host "❌ Failed" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            try {
                $Reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $ErrorBody = $Reader.ReadToEnd()
                Write-Host "  Response: $ErrorBody" -ForegroundColor Red
            } catch {}
        }
    }
    
    $Results.Summary.Total++
    $Results.Tests += $TestResult
    
    return $TestResult
}

function Test-HealthEndpoints {
    Write-Host "`n" -NoNewline
    Write-Host "==== TESTING HEALTH ENDPOINTS ====" -ForegroundColor Yellow
    
    Test-Endpoint -Name "Basic Health" -Endpoint "/health"
    Test-Endpoint -Name "Root Health" -Endpoint "/"
    Test-Endpoint -Name "Readiness" -Endpoint "/readiness"
    Test-Endpoint -Name "API Test" -Endpoint "/api/test"
    Test-Endpoint -Name "Monitor Health" -Endpoint "/api/monitor/health"
}

function Test-DebugEndpoints {
    Write-Host "`n" -NoNewline
    Write-Host "==== TESTING DEBUG ENDPOINTS ====" -ForegroundColor Yellow
    
    $TestUrls = @(
        @{Name="Medium"; Url="https://medium.com/@example/test-article"},
        @{Name="Dev.to"; Url="https://dev.to/test/article"},
        @{Name="HTTPBin"; Url="https://httpbin.org/html"},
        @{Name="Example"; Url="https://example.com"}
    )
    
    Write-Host "`n--- Simple Scrape ---" -ForegroundColor Magenta
    foreach ($Test in $TestUrls) {
        Test-Endpoint -Name "Simple Scrape - $($Test.Name)" `
                     -Endpoint "/api/debug/simple-scrape" `
                     -Query @{url=$Test.Url}
    }
    
    Write-Host "`n--- Scrape Test ---" -ForegroundColor Magenta
    Test-Endpoint -Name "Scrape Comparison" -Endpoint "/api/debug/scrape-test"
    
    Write-Host "`n--- Minimal Scrape ---" -ForegroundColor Magenta
    foreach ($Test in $TestUrls[0..1]) {
        Test-Endpoint -Name "Minimal Scrape - $($Test.Name)" `
                     -Endpoint "/api/debug/minimal-scrape" `
                     -Query @{url=$Test.Url}
    }
}

function Test-GenerateEndpoint {
    Write-Host "`n" -NoNewline
    Write-Host "==== TESTING MAIN GENERATE ENDPOINT ====" -ForegroundColor Yellow
    
    $TestCases = @(
        @{
            Name = "URL - Medium"
            Body = @{url = "https://medium.com/@test/sample-article"}
        },
        @{
            Name = "URL - Dev.to"
            Body = @{url = "https://dev.to/test/sample-post"}
        },
        @{
            Name = "Direct Text"
            Body = @{text = "This is a test article about web scraping. Web scraping is the process of extracting data from websites. It involves making HTTP requests to web pages and parsing the HTML content. Python libraries like BeautifulSoup make this easier. Always respect robots.txt and rate limits."}
        },
        @{
            Name = "URL - HTTPBin"
            Body = @{url = "https://httpbin.org/html"}
        }
    )
    
    foreach ($Test in $TestCases) {
        Test-Endpoint -Name $Test.Name `
                     -Method "POST" `
                     -Endpoint "/api/generate" `
                     -Body $Test.Body
    }
}

function Test-NetworkDiagnostics {
    Write-Host "`n" -NoNewline
    Write-Host "==== TESTING NETWORK DIAGNOSTICS ====" -ForegroundColor Yellow
    
    Test-Endpoint -Name "Railway Network Test" -Endpoint "/api/test/railway-network"
    
    Test-Endpoint -Name "HTTP Config Test" `
                 -Endpoint "/debug/http-config-test" `
                 -Query @{url="https://httpbin.org/get"}
}

function Test-SSLHandling {
    Write-Host "`n" -NoNewline
    Write-Host "==== TESTING SSL/TLS HANDLING ====" -ForegroundColor Yellow
    
    $SSLTests = @(
        @{Name="Standard HTTPS"; Url="https://httpbin.org/get"},
        @{Name="Self-signed"; Url="https://self-signed.badssl.com/"},
        @{Name="Expired"; Url="https://expired.badssl.com/"},
        @{Name="Wrong Host"; Url="https://wrong.host.badssl.com/"}
    )
    
    foreach ($Test in $SSLTests) {
        Test-Endpoint -Name "SSL - $($Test.Name)" `
                     -Endpoint "/api/debug/minimal-scrape" `
                     -Query @{url=$Test.Url}
    }
}

function Show-Summary {
    Write-Host "`n" -NoNewline
    Write-Host "==== TESTING SUMMARY ====" -ForegroundColor Yellow
    
    $Total = $Results.Summary.Total
    $Success = $Results.Summary.Success
    $Failed = $Results.Summary.Failed
    $SuccessRate = if ($Total -gt 0) { [math]::Round(($Success / $Total) * 100, 1) } else { 0 }
    
    Write-Host "`nTotal Tests: $Total"
    Write-Host "Successful: $Success ($SuccessRate%)" -ForegroundColor Green
    Write-Host "Failed: $Failed" -ForegroundColor Red
    
    if ($Failed -gt 0) {
        Write-Host "`nFailed Tests:" -ForegroundColor Red
        $Results.Tests | Where-Object { -not $_.Success } | ForEach-Object {
            Write-Host "  - $($_.Name): $($_.Error)" -ForegroundColor Red
        }
    }
    
    # Save results to JSON
    $ResultsFile = "scraping_test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $Results | ConvertTo-Json -Depth 10 | Out-File $ResultsFile
    Write-Host "`nDetailed results saved to: $ResultsFile" -ForegroundColor Cyan
}

# Main execution
Write-Host "🚀 Starting Threadr Scraping Tests" -ForegroundColor Green
Write-Host "Target: $BaseUrl" -ForegroundColor Gray
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Check if backend is running
Write-Host "`nChecking backend availability..." -NoNewline
try {
    $HealthCheck = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
    Write-Host " ✅ Backend is running" -ForegroundColor Green
}
catch {
    Write-Host " ❌ Backend is not accessible!" -ForegroundColor Red
    Write-Host "Please ensure the backend is running on $BaseUrl" -ForegroundColor Red
    exit 1
}

# Run all tests
Test-HealthEndpoints
Test-DebugEndpoints
Test-GenerateEndpoint
Test-NetworkDiagnostics
Test-SSLHandling

# Show summary
Show-Summary

Write-Host "`n✨ Testing Complete!" -ForegroundColor Green
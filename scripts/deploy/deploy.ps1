# Threadr Frontend Deployment Script - PowerShell
# Deploys the Threadr frontend to Vercel with proper configuration
# Author: Claude Code Deployment Engineer

param(
    [Parameter(Mandatory=$false)]
    [switch]$Production = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$Token = ""
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Green = @{ForegroundColor = "Green"}
$Red = @{ForegroundColor = "Red"}
$Yellow = @{ForegroundColor = "Yellow"}
$Blue = @{ForegroundColor = "Blue"}
$Cyan = @{ForegroundColor = "Cyan"}

function Write-Header {
    param([string]$Text)
    Write-Host "`n" @Blue
    Write-Host "=" * 60 @Blue
    Write-Host " $Text" @Blue
    Write-Host "=" * 60 @Blue
    Write-Host ""
}

function Write-Step {
    param([string]$Text)
    Write-Host "[STEP] $Text" @Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "[SUCCESS] $Text" @Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "[ERROR] $Text" @Red
}

function Write-Warning {
    param([string]$Text)
    Write-Host "[WARNING] $Text" @Yellow
}

# Main deployment function
function Deploy-Frontend {
    try {
        Write-Header "Threadr Frontend Deployment Script"
        
        # Check if we're in the correct directory
        if (!(Test-Path "index.html") -or !(Test-Path "config.js") -or !(Test-Path "vercel.json")) {
            Write-Error "Missing required files. Please run this script from the frontend directory."
            Write-Host "Required files: index.html, config.js, vercel.json"
            exit 1
        }
        
        Write-Success "Found all required files"
        
        # Check Vercel CLI installation
        Write-Step "Checking Vercel CLI installation..."
        try {
            $vercelVersion = vercel --version 2>$null
            Write-Success "Vercel CLI installed: $vercelVersion"
        }
        catch {
            Write-Error "Vercel CLI not found. Please install it with: npm install -g vercel"
            exit 1
        }
        
        # Check authentication status
        Write-Step "Checking Vercel authentication..."
        try {
            if ($Token) {
                Write-Step "Using provided token for authentication..."
                $env:VERCEL_TOKEN = $Token
            }
            
            # Try to list projects to test authentication
            $null = vercel ls 2>$null
            Write-Success "Vercel authentication verified"
        }
        catch {
            Write-Warning "Not authenticated with Vercel. Starting login process..."
            Write-Host ""
            Write-Host "Please follow these steps:" @Yellow
            Write-Host "1. A browser window will open" @Yellow
            Write-Host "2. Sign in with your Vercel account" @Yellow
            Write-Host "3. Return to this terminal once authenticated" @Yellow
            Write-Host ""
            
            # Attempt login
            try {
                vercel login
                Write-Success "Successfully authenticated with Vercel"
            }
            catch {
                Write-Error "Failed to authenticate with Vercel. Please try manually: vercel login"
                exit 1
            }
        }
        
        # Pre-deployment checks
        Write-Step "Running pre-deployment checks..."
        
        # Validate vercel.json structure
        if (Test-Path "vercel.json") {
            try {
                $vercelConfig = Get-Content "vercel.json" | ConvertFrom-Json
                if (!$vercelConfig.builds -or !$vercelConfig.routes) {
                    Write-Warning "vercel.json may be incomplete"
                }
                Write-Success "vercel.json validation passed"
            }
            catch {
                Write-Error "Invalid vercel.json format"
                exit 1
            }
        }
        
        # Validate config.js
        if (Test-Path "config.js") {
            $configContent = Get-Content "config.js" -Raw
            if ($configContent -match "threadr-production\.up\.railway\.app") {
                Write-Success "Backend API URL configured correctly"
            } else {
                Write-Warning "Backend API URL may not be configured correctly"
            }
        }
        
        # Deploy to Vercel
        Write-Step "Starting Vercel deployment..."
        
        $deployArgs = @()
        
        if ($Production) {
            Write-Step "Deploying to PRODUCTION..."
            $deployArgs += "--prod"
        } else {
            Write-Step "Deploying to PREVIEW..."
        }
        
        if ($Force) {
            $deployArgs += "--force"
        }
        
        # Add yes flag to skip confirmations
        $deployArgs += "--yes"
        
        Write-Host "Deployment command: vercel $($deployArgs -join ' ')" @Blue
        Write-Host ""
        
        # Execute deployment
        $deployOutput = vercel @deployArgs 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Deployment completed successfully!"
            Write-Host ""
            
            # Extract deployment URL from output
            $deploymentUrl = ""
            foreach ($line in $deployOutput) {
                if ($line -match "https://.*\.vercel\.app") {
                    $deploymentUrl = $matches[0]
                    break
                }
            }
            
            if ($deploymentUrl) {
                Write-Host "Deployment URL: $deploymentUrl" @Green
                
                # Test the deployment
                Write-Step "Testing deployment..."
                try {
                    $response = Invoke-WebRequest -Uri $deploymentUrl -Method GET -TimeoutSec 30
                    if ($response.StatusCode -eq 200) {
                        Write-Success "Deployment is accessible and returning HTTP 200"
                        
                        # Check if it contains expected content
                        if ($response.Content -match "Threadr") {
                            Write-Success "Deployment contains expected Threadr content"
                        } else {
                            Write-Warning "Deployment accessible but may not contain expected content"
                        }
                    } else {
                        Write-Warning "Deployment returned HTTP $($response.StatusCode)"
                    }
                }
                catch {
                    Write-Warning "Could not test deployment: $($_.Exception.Message)"
                }
                
                Write-Host ""
                Write-Host "Next Steps:" @Yellow
                Write-Host "1. Visit: $deploymentUrl" @Yellow
                Write-Host "2. Test the thread generation functionality" @Yellow
                Write-Host "3. Configure custom domain if needed: vercel domains add your-domain.com" @Yellow
                
                if (!$Production) {
                    Write-Host "4. Deploy to production when ready: .\deploy.ps1 -Production" @Yellow
                }
            } else {
                Write-Warning "Could not extract deployment URL from output"
                Write-Host "Full deployment output:" @Blue
                $deployOutput | ForEach-Object { Write-Host $_ }
            }
        } else {
            Write-Error "Deployment failed!"
            Write-Host "Error output:" @Red
            $deployOutput | ForEach-Object { Write-Host $_ @Red }
            exit 1
        }
        
    }
    catch {
        Write-Error "Unexpected error during deployment: $($_.Exception.Message)"
        Write-Host "Stack trace:" @Red
        Write-Host $_.ScriptStackTrace @Red
        exit 1
    }
}

# Script execution
Write-Host "Threadr Frontend Deployment Script" @Blue
Write-Host "Current directory: $(Get-Location)" @Blue
Write-Host "Production deployment: $Production" @Blue
Write-Host "Force deployment: $Force" @Blue

if ($Token) {
    Write-Host "Using provided authentication token" @Blue
}

Write-Host ""

Deploy-Frontend

Write-Host ""
Write-Success "Deployment script completed successfully!"
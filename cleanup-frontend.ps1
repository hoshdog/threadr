# Threadr Frontend Cleanup Script
# Removes duplicate src/ directory that's causing confusion

Write-Host "🧹 Threadr Frontend Cleanup Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$frontendPath = "C:\Users\HoshitoPowell\Desktop\Threadr\frontend"
$srcPath = "$frontendPath\src"
$publicPath = "$frontendPath\public"

# Check if directories exist
Write-Host "`n📁 Checking directory structure..." -ForegroundColor Yellow

if (Test-Path $srcPath) {
    Write-Host "❌ FOUND: $srcPath (unused directory)" -ForegroundColor Red
    $srcExists = $true
} else {
    Write-Host "✅ NOT FOUND: $srcPath (good)" -ForegroundColor Green
    $srcExists = $false
}

if (Test-Path $publicPath) {
    Write-Host "✅ FOUND: $publicPath (active directory)" -ForegroundColor Green
    $publicExists = $true
} else {
    Write-Host "❌ NOT FOUND: $publicPath (CRITICAL ERROR)" -ForegroundColor Red
    $publicExists = $false
}

if (-not $publicExists) {
    Write-Host "`n🚨 CRITICAL ERROR: Public directory missing!" -ForegroundColor Red
    Write-Host "Cannot proceed without active frontend directory." -ForegroundColor Red
    exit 1
}

if (-not $srcExists) {
    Write-Host "`n✅ No cleanup needed - src directory already removed" -ForegroundColor Green
    exit 0
}

# Show what's in src directory
Write-Host "`n📋 Contents of src directory:" -ForegroundColor Yellow
Get-ChildItem $srcPath -Recurse | ForEach-Object {
    Write-Host "   - $($_.FullName.Replace($srcPath, 'src'))" -ForegroundColor Gray
}

# Confirm removal
Write-Host "`n⚠️  CONFIRMATION REQUIRED" -ForegroundColor Yellow
Write-Host "This script will permanently delete the src/ directory." -ForegroundColor Yellow
Write-Host "The src/ directory is NOT used by Vercel (only public/ is used)." -ForegroundColor Yellow
$confirm = Read-Host "`nType 'DELETE' to confirm removal"

if ($confirm -ne "DELETE") {
    Write-Host "`n❌ Cleanup cancelled by user" -ForegroundColor Red
    exit 0
}

# Attempt to remove src directory
Write-Host "`n🗑️  Removing src directory..." -ForegroundColor Yellow

try {
    # First try to remove read-only attributes
    Get-ChildItem $srcPath -Recurse | ForEach-Object {
        $_.Attributes = $_.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly)
    }
    
    # Remove the directory
    Remove-Item $srcPath -Recurse -Force
    
    Write-Host "✅ Successfully removed src directory!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to remove src directory: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔧 Manual removal steps:" -ForegroundColor Yellow
    Write-Host "1. Close all editors/IDEs that might have files open" -ForegroundColor Gray
    Write-Host "2. Open Windows Explorer" -ForegroundColor Gray
    Write-Host "3. Navigate to: $frontendPath" -ForegroundColor Gray
    Write-Host "4. Delete the 'src' folder manually" -ForegroundColor Gray
    exit 1
}

# Verify removal
Write-Host "`n🔍 Verifying cleanup..." -ForegroundColor Yellow

if (Test-Path $srcPath) {
    Write-Host "❌ src directory still exists - manual removal required" -ForegroundColor Red
} else {
    Write-Host "✅ src directory successfully removed" -ForegroundColor Green
}

if (Test-Path $publicPath) {
    Write-Host "✅ public directory intact" -ForegroundColor Green
} else {
    Write-Host "🚨 CRITICAL: public directory missing!" -ForegroundColor Red
}

Write-Host "`n🎉 Cleanup Complete!" -ForegroundColor Cyan
Write-Host "Frontend structure now clean:" -ForegroundColor Cyan
Write-Host "  ✅ frontend/public/ (active - served by Vercel)" -ForegroundColor Green
Write-Host "  ❌ frontend/src/ (removed - was causing confusion)" -ForegroundColor Red

Write-Host "`n🔗 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test the live site: https://threadr-plum.vercel.app" -ForegroundColor Gray
Write-Host "2. Use debug page: https://threadr-plum.vercel.app/debug-test.html" -ForegroundColor Gray
Write-Host "3. Edit files only in frontend/public/ directory" -ForegroundColor Gray
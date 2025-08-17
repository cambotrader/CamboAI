# CAMBOAI TRADERSTATION - Quick Path Check
Write-Host "Checking D: drive paths..." -ForegroundColor Green

$baseDir = "d:\CamboAI"
Write-Host "Base Directory: $baseDir" -ForegroundColor White

if (Test-Path $baseDir) {
    Write-Host "SUCCESS: CamboAI folder exists on D: drive" -ForegroundColor Green
    
    # Key directories
    $dirs = @(
        "frontend",
        "web", 
        "web-advanced",
        "backend",
        "mobile",
        "dashboard"
    )
    
    foreach ($dirName in $dirs) {
        $fullPath = Join-Path $baseDir $dirName
        if (Test-Path $fullPath) {
            Write-Host "  OK: $dirName exists" -ForegroundColor Green
        } else {
            Write-Host "  MISSING: $dirName" -ForegroundColor Yellow
        }
    }
    
    # Check the fixed web page
    $webPage = "d:\CamboAI\web\app\page.tsx"
    if (Test-Path $webPage) {
        $content = Get-Content $webPage -Raw
        if ($content.Length -gt 100) {
            Write-Host "  OK: Web page.tsx restored successfully" -ForegroundColor Green
        } else {
            Write-Host "  ISSUE: Web page.tsx content too short" -ForegroundColor Red
            Write-Host "    Content preview: $($content.Substring(0, [Math]::Min(50, $content.Length)))" -ForegroundColor Gray
        }
    } else {
        Write-Host "  MISSING: Web page.tsx" -ForegroundColor Red
    }
    
} else {
    Write-Host "ERROR: CamboAI folder NOT FOUND on D: drive!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Path verification complete!" -ForegroundColor Green
Write-Host "All files should be on D:\CamboAI (NOT C: drive)" -ForegroundColor Cyan
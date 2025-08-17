# Simple path verification for CamboAI TraderStation
Write-Host "🔍 CHECKING D: DRIVE PATHS..." -ForegroundColor Green

$baseDir = "d:\CamboAI"
Write-Host "Base Directory: $baseDir" -ForegroundColor White

if (Test-Path $baseDir) {
    Write-Host "✅ CamboAI folder exists on D: drive" -ForegroundColor Green
    
    # Key directories
    $dirs = @(
        "d:\CamboAI\frontend",
        "d:\CamboAI\web", 
        "d:\CamboAI\web-advanced",
        "d:\CamboAI\backend"
    )
    
    foreach ($dir in $dirs) {
        $dirName = Split-Path $dir -Leaf
        if (Test-Path $dir) {
            Write-Host "✅ $dirName exists" -ForegroundColor Green
        } else {
            Write-Host "❌ $dirName missing" -ForegroundColor Red
        }
    }
    
    # Check web page file
    $webPage = "d:\CamboAI\web\app\page.tsx"
    if (Test-Path $webPage) {
        $content = Get-Content $webPage -Raw
        if ($content.Length -gt 100) {
            Write-Host "✅ Web page.tsx is properly restored" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Web page.tsx content is too short" -ForegroundColor Yellow
        }
    }
    
} else {
    Write-Host "❌ CamboAI folder NOT FOUND on D: drive!" -ForegroundColor Red
}

Write-Host "`n🎉 Path verification complete!" -ForegroundColor Green
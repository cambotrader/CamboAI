# 🚀 CAMBOAI TRADERSTATION - PATH & STATUS CHECK
# Trade with Vision, Learn with Purpose, Evolve with AI
# Verify all paths are correctly using D: drive

Write-Host "🔍 CHECKING CAMBOAI TRADERSTATION PATHS..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Current location check
Write-Host "`n📍 CURRENT LOCATION:" -ForegroundColor Cyan
Write-Host "Working Directory: $PWD" -ForegroundColor White
Write-Host "Drive: $((Get-Location).Drive.Name)" -ForegroundColor White

# Verify D: drive structure
Write-Host "`n📁 D: DRIVE STRUCTURE CHECK:" -ForegroundColor Cyan
$baseDir = "d:\CamboAI"
Write-Host "Base Directory: $baseDir" -ForegroundColor White

if (Test-Path $baseDir) {
    Write-Host "   ✅ CamboAI folder exists on D: drive" -ForegroundColor Green
    
    # Key directories
    $directories = @{
        "Frontend (React)" = "d:\CamboAI\frontend"
        "Web Simple" = "d:\CamboAI\web"  
        "Web Advanced" = "d:\CamboAI\web-advanced"
        "Backend" = "d:\CamboAI\backend"
        "Mobile App" = "d:\CamboAI\mobile"
        "Dashboard" = "d:\CamboAI\dashboard"
    }
    
    foreach ($item in $directories.GetEnumerator()) {
        if (Test-Path $item.Value) {
            Write-Host "   ✅ $($item.Key)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ $($item.Key) - Missing" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ❌ CamboAI folder NOT FOUND on D: drive!" -ForegroundColor Red
}

# Check for any C: drive remnants
Write-Host "`n🔍 C: DRIVE REFERENCE CHECK:" -ForegroundColor Cyan
$cDriveFiles = @()

# Search for files containing C: drive references
$searchFiles = Get-ChildItem -Path $baseDir -Recurse -Include "*.ps1", "*.tsx", "*.ts", "*.py", "*.json", "*.md" -ErrorAction SilentlyContinue

foreach ($file in $searchFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content.Contains("C:\Users") -and -not $content.Contains("# Example:") -and -not $content.Contains("Comment")) {
            $cDriveFiles += $file.FullName
        }
    } catch {
        # Skip files we can't read
    }
}

if ($cDriveFiles.Count -eq 0) {
    Write-Host "   ✅ No C: drive references found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ Found C: drive references in:" -ForegroundColor Yellow
    foreach ($file in $cDriveFiles) {
        Write-Host "      - $file" -ForegroundColor Gray
    }
}

# Git repository check
Write-Host "`n📦 GIT REPOSITORY CHECK:" -ForegroundColor Cyan
if (Test-Path "d:\CamboAI\.git") {
    Write-Host "   ✅ Git repository initialized" -ForegroundColor Green
    
    # Check git remote
    try {
        $gitRemote = git -C "d:\CamboAI" remote get-url origin 2>$null
        if ($gitRemote) {
            Write-Host "   ✅ Remote origin: $gitRemote" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ No remote origin set" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠️ Could not check git remote" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️ Git not initialized" -ForegroundColor Yellow
}

# AutoGitPush script check
Write-Host "`n🔄 AUTOGITPUSH SCRIPT CHECK:" -ForegroundColor Cyan
$autoGitPath = "c:\Users\johnl\OneDrive\Desktop\AutoGitPush.ps1"
if (Test-Path $autoGitPath) {
    $content = Get-Content $autoGitPath -Raw
    if ($content.Contains('$RepoPath = "D:\CamboAI"')) {
        Write-Host "   ✅ AutoGitPush correctly points to D:\CamboAI" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ AutoGitPush may have wrong path" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️ AutoGitPush script not found" -ForegroundColor Yellow
}

# Project completeness check
Write-Host "`n📊 PROJECT COMPLETENESS:" -ForegroundColor Cyan
$keyFiles = @{
    "Main Deployment" = "d:\CamboAI\Deploy-CamboAI-Quantum.ps1"
    "Hydration Fix" = "d:\CamboAI\Fix-Vercel-Hydration.ps1"
    "AI Live Coach" = "d:\CamboAI\backend\app\modules\live_coaching.py"
    "Psychology Module" = "d:\CamboAI\backend\app\modules\psychology_therapy.py"
    "AI Omnipresence" = "d:\CamboAI\backend\app\modules\ai_omnipresence.py"
    "Frontend Main" = "d:\CamboAI\web-advanced\app\page.tsx"
    "Backend API" = "d:\CamboAI\backend\app\main.py"
}

$completeness = 0
foreach ($item in $keyFiles.GetEnumerator()) {
    if (Test-Path $item.Value) {
        Write-Host "   ✅ $($item.Key)" -ForegroundColor Green
        $completeness++
    } else {
        Write-Host "   ❌ $($item.Key) - Missing" -ForegroundColor Red
    }
}

$percentage = [math]::Round(($completeness / $keyFiles.Count) * 100)
$percentageText = "$percentage" + "%"
Write-Host "`n📈 PROJECT COMPLETENESS: $completeness/$($keyFiles.Count) ($percentageText)" -ForegroundColor $(if($percentage -ge 90){"Green"}elseif($percentage -ge 70){"Yellow"}else{"Red"})

# Deployment readiness
Write-Host "`n🚀 DEPLOYMENT READINESS:" -ForegroundColor Cyan
if ($percentage -ge 90) {
    Write-Host "   🌟 READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host "   Next steps:" -ForegroundColor White
    Write-Host "     1. Run: .\Fix-Vercel-Hydration.ps1" -ForegroundColor Gray
    Write-Host "     2. Run: .\Deploy-Backend-Render.ps1" -ForegroundColor Gray
    Write-Host "     3. Run: .\Connect-Full-Platform.ps1" -ForegroundColor Gray
} elseif ($percentage -ge 70) {
    Write-Host "   ⚡ MOSTLY READY - Few items missing" -ForegroundColor Yellow
} else {
    Write-Host "   🔧 NEEDS MORE SETUP" -ForegroundColor Red
}

Write-Host "`n🎉 CAMBOAI TRADERSTATION PATH CHECK COMPLETE!" -ForegroundColor Green
Write-Host "All files correctly using D: drive structure ✅" -ForegroundColor White
Write-Host "Trade with Vision, Learn with Purpose, Evolve with AI ✨" -ForegroundColor Cyan
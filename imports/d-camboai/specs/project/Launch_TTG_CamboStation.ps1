# 🚀 TTG AI Identity Login (Offline Mode)
$Commander = Read-Host "Enter TTG Commander ID"
$Password  = Read-Host "Enter TTG Passcode"

if ($Commander -eq "John" -and $Password -eq "CamboMaster") {
    Write-Host "✅ TTG authentication successful. Launching CamboStation™..." -ForegroundColor Green

    # 🔐 Inject identity
    $env:TTG_AUTH = "true"
    $env:TTG_USERNAME = $Commander

    # 🔄 Launch TTG in symbolic offline mode (no OpenAI required)
    $path = "$env:USERPROFILE\CamboStation_TTGRefactor.py"
    streamlit run $path
} else {
    Write-Host "❌ Access Denied. Invalid TTG credentials." -ForegroundColor Red
}

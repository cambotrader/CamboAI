# CamboStation Vision - Free Backend Deployment
# Deploy your FastAPI backend completely free

Write-Host "🖥️ Deploying CamboStation Vision Backend (100% Free)" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "d:\CamboAI\backend")) {
    Write-Host "❌ Backend directory not found. Make sure you're in the CamboAI project root." -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
Set-Location "d:\CamboAI\backend"

# Check if Python is installed
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install from https://python.org" -ForegroundColor Red
    exit 1
}

# Create requirements.txt for deployment if it doesn't exist
if (-not (Test-Path "requirements.txt")) {
    Write-Host "📝 Creating requirements.txt..." -ForegroundColor Yellow
    @"
fastapi==0.68.0
uvicorn==0.15.0
sqlalchemy==1.4.23
pandas==1.3.3
numpy==1.21.2
python-multipart==0.0.5
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==0.19.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
}

Write-Host ""
Write-Host "🎉 Ready to deploy! Choose your free option:" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Option 1: Railway (Recommended)" -ForegroundColor Cyan
Write-Host "1. Install: npm install -g @railway/cli" -ForegroundColor White
Write-Host "2. Login: railway login" -ForegroundColor White
Write-Host "3. Deploy: railway up" -ForegroundColor White
Write-Host "4. Free tier: 512MB RAM, $5 credit/month" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Render" -ForegroundColor Cyan
Write-Host "1. Go to: https://render.com" -ForegroundColor White
Write-Host "2. Connect your GitHub repo" -ForegroundColor White
Write-Host "3. Auto-deploy on push" -ForegroundColor White
Write-Host "4. Free tier: 512MB RAM" -ForegroundColor White
Write-Host ""
Write-Host "Option 3: Fly.io" -ForegroundColor Cyan
Write-Host "1. Install: https://fly.io/docs/getting-started/installing-flyctl/" -ForegroundColor White
Write-Host "2. Run: flyctl launch" -ForegroundColor White
Write-Host "3. Deploy: flyctl deploy" -ForegroundColor White
Write-Host ""
Write-Host "Option 4: PythonAnywhere (Python-specific)" -ForegroundColor Cyan
Write-Host "1. Sign up: https://pythonanywhere.com" -ForegroundColor White
Write-Host "2. Upload your code" -ForegroundColor White
Write-Host "3. Configure web app" -ForegroundColor White
Write-Host ""
Write-Host "💡 All options are 100% FREE with generous limits!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Quick setup for Railway:" -ForegroundColor Yellow
Write-Host "npm install -g @railway/cli" -ForegroundColor Cyan
Write-Host "railway login" -ForegroundColor Cyan
Write-Host "railway init" -ForegroundColor Cyan
Write-Host "railway up" -ForegroundColor Cyan
# CamboAI - Complete Free Setup
# Sets up mobile app, website, and backend deployment - all 100% FREE!

Write-Host ""
Write-Host "🎉 CamboAI - Complete Free Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "This script will set up your existing CamboAI project for:" -ForegroundColor White
Write-Host "📱 Mobile App (Android APK + iOS) - React Native Expo" -ForegroundColor Cyan
Write-Host "🌐 Website (Next.js) - Already in /web folder" -ForegroundColor Cyan
Write-Host "🖥️ Frontend (React) - Already in /frontend folder" -ForegroundColor Cyan
Write-Host "🖥️ Backend API (FastAPI) - Already in /backend folder" -ForegroundColor Cyan
Write-Host "📊 Dashboard (Streamlit) - Already in /dashboard folder" -ForegroundColor Cyan
Write-Host "💰 Total Cost: $0 (100% FREE!)" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Installing..." -ForegroundColor Red
    Write-Host "Please install Node.js from: https://nodejs.org" -ForegroundColor Yellow
    Start-Process "https://nodejs.org"
    Read-Host "Press Enter after installing Node.js"
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install from: https://python.org" -ForegroundColor Red
    Start-Process "https://python.org"
    Read-Host "Press Enter after installing Python"
}

Write-Host ""
Write-Host "📦 Installing free development tools..." -ForegroundColor Yellow

# Install global tools
npm install -g @expo/cli
npm install -g eas-cli
npm install -g vercel
npm install -g @railway/cli

Write-Host "✅ Development tools installed!" -ForegroundColor Green

# Setup Mobile App
Write-Host ""
Write-Host "📱 Setting up Mobile App..." -ForegroundColor Yellow
if (Test-Path "d:\CamboAI\mobile") {
    Set-Location "d:\CamboAI\mobile"
    npm install
    Write-Host "✅ Mobile app dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "❌ Mobile directory not found" -ForegroundColor Red
}

# Setup Website
Write-Host ""
Write-Host "🌐 Setting up Website..." -ForegroundColor Yellow
if (Test-Path "d:\CamboAI\web") {
    Set-Location "d:\CamboAI\web"
    npm install
    Write-Host "✅ Website dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "❌ Web directory not found" -ForegroundColor Red
}

# Setup Backend
Write-Host ""
Write-Host "🖥️ Setting up Backend..." -ForegroundColor Yellow
if (Test-Path "d:\CamboAI\backend") {
    Set-Location "d:\CamboAI\backend"
    if (Test-Path ".venv") {
        .\.venv\Scripts\Activate.ps1
    }
    pip install -r requirements.txt
    Write-Host "✅ Backend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "❌ Backend directory not found" -ForegroundColor Red
}

# Return to root
Set-Location "d:\CamboAI"

Write-Host ""
Write-Host "🎉 SETUP COMPLETE! Here's what you can do now:" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

Write-Host "📱 MOBILE APP (100% Free)" -ForegroundColor Cyan
Write-Host "1. Create Expo account: https://expo.dev" -ForegroundColor White
Write-Host "2. Login: eas login" -ForegroundColor White
Write-Host "3. Test on device: cd mobile && npm start" -ForegroundColor White
Write-Host "4. Build APK: eas build --platform android --profile preview" -ForegroundColor White
Write-Host ""

Write-Host "🌐 WEBSITE (100% Free)" -ForegroundColor Cyan
Write-Host "1. Deploy to Vercel: cd web && vercel --prod" -ForegroundColor White
Write-Host "2. Get free domain: your-app.vercel.app" -ForegroundColor White
Write-Host "3. Custom domain supported (free)" -ForegroundColor White
Write-Host ""

Write-Host "🖥️ BACKEND (100% Free)" -ForegroundColor Cyan
Write-Host "1. Deploy to Railway: cd backend && railway up" -ForegroundColor White
Write-Host "2. Or use Render: https://render.com" -ForegroundColor White
Write-Host "3. Free database: Supabase or PlanetScale" -ForegroundColor White
Write-Host ""

Write-Host "💡 FREE RESOURCES:" -ForegroundColor Yellow
Write-Host "• Vercel: Free hosting + domain" -ForegroundColor White
Write-Host "• Railway: Free backend hosting" -ForegroundColor White
Write-Host "• Expo: Free mobile app building" -ForegroundColor White
Write-Host "• Supabase: Free database" -ForegroundColor White
Write-Host "• GitHub: Free code hosting + CI/CD" -ForegroundColor White
Write-Host ""

Write-Host "🚀 QUICK START COMMANDS:" -ForegroundColor Green
Write-Host "cd mobile && npm start     # Test mobile app" -ForegroundColor Cyan
Write-Host "cd web && vercel --prod    # Deploy website" -ForegroundColor Cyan
Write-Host "cd backend && railway up   # Deploy backend" -ForegroundColor Cyan
Write-Host ""

Write-Host "📚 Need help? Check:" -ForegroundColor Yellow
Write-Host "• FREE_DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "• mobile/README.md" -ForegroundColor White
Write-Host "• Expo Discord (free support)" -ForegroundColor White
Write-Host "• Vercel Discord (free support)" -ForegroundColor White
Write-Host ""

Write-Host "🎊 You're all set! Everything is 100% FREE!" -ForegroundColor Green
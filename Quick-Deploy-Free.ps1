# CamboAI - Quick Free Deployment
# Deploy your entire CamboAI platform for FREE in minutes!

Write-Host ""
Write-Host "🚀 CamboAI - Quick Free Deployment" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "D:\CamboAI\backend") -or -not (Test-Path "D:\CamboAI\frontend") -or -not (Test-Path "D:\CamboAI\web")) {
    Write-Host "❌ Please run this script from the CamboAI root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Your CamboAI Project Components:" -ForegroundColor Yellow
Write-Host "✅ Backend (FastAPI) - /backend" -ForegroundColor Green
Write-Host "✅ Frontend (React) - /frontend" -ForegroundColor Green
Write-Host "✅ Web App (Next.js) - /web" -ForegroundColor Green
Write-Host "✅ Dashboard (Streamlit) - /dashboard" -ForegroundColor Green
Write-Host "✅ Mobile App (React Native) - /mobile" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 Choose what to deploy (all FREE):" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 📱 Mobile App (Android APK)" -ForegroundColor White
Write-Host "   - Build with Expo (free)" -ForegroundColor Gray
Write-Host "   - Direct APK distribution" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 🌐 Next.js Web App" -ForegroundColor White
Write-Host "   - Deploy to Vercel (free)" -ForegroundColor Gray
Write-Host "   - Custom domain supported" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 🖥️ React Frontend" -ForegroundColor White
Write-Host "   - Deploy to Netlify (free)" -ForegroundColor Gray
Write-Host "   - Or GitHub Pages" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 🖥️ FastAPI Backend" -ForegroundColor White
Write-Host "   - Deploy to Railway (free)" -ForegroundColor Gray
Write-Host "   - Or Render (free)" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 📊 Streamlit Dashboard" -ForegroundColor White
Write-Host "   - Deploy to Streamlit Cloud (free)" -ForegroundColor Gray
Write-Host ""
Write-Host "6. 🎉 Deploy Everything!" -ForegroundColor White
Write-Host "   - All components at once" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "📱 Setting up Mobile App..." -ForegroundColor Yellow
        Set-Location "D:\CamboAI\mobile"
        
        Write-Host "Installing dependencies..." -ForegroundColor Gray
        npm install
        
        Write-Host ""
        Write-Host "🎉 Mobile app ready!" -ForegroundColor Green
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Create free Expo account: https://expo.dev" -ForegroundColor White
        Write-Host "2. Login: eas login" -ForegroundColor White
        Write-Host "3. Test: npm start (scan QR with Expo Go app)" -ForegroundColor White
        Write-Host "4. Build APK: eas build --platform android --profile preview" -ForegroundColor White
    }
    
    "2" {
        Write-Host ""
        Write-Host "🌐 Setting up Next.js Web App..." -ForegroundColor Yellow
        Set-Location "D:\CamboAI\web"
        
        Write-Host "Installing dependencies..." -ForegroundColor Gray
        npm install
        
        Write-Host "Building project..." -ForegroundColor Gray
        npm run build
        
        Write-Host ""
        Write-Host "🎉 Web app ready!" -ForegroundColor Green
        Write-Host "Deploy to Vercel:" -ForegroundColor Cyan
        Write-Host "1. Install: npm install -g vercel" -ForegroundColor White
        Write-Host "2. Deploy: vercel --prod" -ForegroundColor White
        Write-Host "3. Get free domain: your-app.vercel.app" -ForegroundColor White
    }
    
    "3" {
        Write-Host ""
        Write-Host "🖥️ Setting up React Frontend..." -ForegroundColor Yellow
        Set-Location "D:\CamboAI\frontend"
        
        Write-Host "Installing dependencies..." -ForegroundColor Gray
        npm install
        
        Write-Host "Building project..." -ForegroundColor Gray
        npm run build
        
        Write-Host ""
        Write-Host "🎉 Frontend ready!" -ForegroundColor Green
        Write-Host "Deploy options:" -ForegroundColor Cyan
        Write-Host "Netlify: netlify deploy --prod --dir=build" -ForegroundColor White
        Write-Host "GitHub Pages: npm run deploy" -ForegroundColor White
    }
    
    "4" {
        Write-Host ""
        Write-Host "🖥️ Setting up FastAPI Backend..." -ForegroundColor Yellow
        Set-Location "D:\CamboAI\backend"
        
        Write-Host "Installing dependencies..." -ForegroundColor Gray
        if (Test-Path ".venv") {
            .\.venv\Scripts\Activate.ps1
        }
        pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "🎉 Backend ready!" -ForegroundColor Green
        Write-Host "Deploy options:" -ForegroundColor Cyan
        Write-Host "Railway: railway up" -ForegroundColor White
        Write-Host "Render: Connect GitHub repo at render.com" -ForegroundColor White
    }
    
    "5" {
        Write-Host ""
        Write-Host "📊 Setting up Streamlit Dashboard..." -ForegroundColor Yellow
        Set-Location "D:\CamboAI\dashboard"
        
        Write-Host "Installing dependencies..." -ForegroundColor Gray
        pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "🎉 Dashboard ready!" -ForegroundColor Green
        Write-Host "Deploy to Streamlit Cloud:" -ForegroundColor Cyan
        Write-Host "1. Push to GitHub" -ForegroundColor White
        Write-Host "2. Go to share.streamlit.io" -ForegroundColor White
        Write-Host "3. Connect your repo" -ForegroundColor White
    }
    
    "6" {
        Write-Host ""
        Write-Host "🎉 Setting up EVERYTHING..." -ForegroundColor Yellow
        
        # Mobile App
        Write-Host "📱 Mobile App..." -ForegroundColor Cyan
        Set-Location "D:\CamboAI\mobile"
        npm install
        
        # Web App
        Write-Host "🌐 Web App..." -ForegroundColor Cyan
        Set-Location "D:\CamboAI\web"
        npm install
        npm run build
        
        # Frontend
        Write-Host "🖥️ Frontend..." -ForegroundColor Cyan
        Set-Location "D:\CamboAI\frontend"
        npm install
        npm run build
        
        # Backend
        Write-Host "🖥️ Backend..." -ForegroundColor Cyan
        Set-Location "D:\CamboAI\backend"
        if (Test-Path ".venv") {
            .\.venv\Scripts\Activate.ps1
        }
        pip install -r requirements.txt
        
        # Dashboard
        Write-Host "📊 Dashboard..." -ForegroundColor Cyan
        Set-Location "D:\CamboAI\dashboard"
        pip install -r requirements.txt
        
        Set-Location "D:\CamboAI"
        
        Write-Host ""
        Write-Host "🎊 EVERYTHING IS READY!" -ForegroundColor Green
        Write-Host "========================" -ForegroundColor Green
        Write-Host ""
        Write-Host "📱 Mobile: cd mobile && npm start" -ForegroundColor Cyan
        Write-Host "🌐 Web: cd web && vercel --prod" -ForegroundColor Cyan
        Write-Host "🖥️ Frontend: cd frontend && netlify deploy --prod --dir=build" -ForegroundColor Cyan
        Write-Host "🖥️ Backend: cd backend && railway up" -ForegroundColor Cyan
        Write-Host "📊 Dashboard: Push to GitHub, deploy on share.streamlit.io" -ForegroundColor Cyan
    }
    
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📚 Need help? Check:" -ForegroundColor Yellow
Write-Host "• FREE_DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "• mobile/README.md" -ForegroundColor White
Write-Host ""
Write-Host "💡 Everything is 100% FREE!" -ForegroundColor Green
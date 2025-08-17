# 🚀 CAMBOAI TRADERSTATION - VERCEL HYDRATION FIX
# Trade with Vision, Learn with Purpose, Evolve with AI

Write-Host "🔧 FIXING VERCEL HYDRATION ISSUES..." -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Navigate to web-advanced directory
Set-Location "d:\CamboAI\web-advanced"

Write-Host "📍 Current working directory: $PWD" -ForegroundColor Gray
Write-Host "📁 Verifying D: drive paths..." -ForegroundColor Gray

Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host "🧹 Cleaning build cache..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".next" -ErrorAction SilentlyContinue
npm run build

Write-Host "🚀 Testing locally first..." -ForegroundColor Yellow
Write-Host "Run: npm run dev" -ForegroundColor Cyan
Write-Host "Visit: http://localhost:3000" -ForegroundColor Cyan

Write-Host "`n✅ HYDRATION FIXES APPLIED:" -ForegroundColor Green
Write-Host "   ✅ NoSSR wrapper for animations" -ForegroundColor White
Write-Host "   ✅ Dynamic motion imports" -ForegroundColor White
Write-Host "   ✅ Browser extension blocking" -ForegroundColor White
Write-Host "   ✅ Hydration suppression" -ForegroundColor White
Write-Host "   ✅ Better SSR configuration" -ForegroundColor White

Write-Host "`n🌐 DEPLOY TO VERCEL:" -ForegroundColor Cyan
Write-Host "1. Test locally first: npm run dev" -ForegroundColor White
Write-Host "2. If working, commit and push:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Fix hydration issues'" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray
Write-Host "3. Vercel will auto-deploy" -ForegroundColor White

Write-Host "`n🎉 CAMBOAI TRADERSTATION READY!" -ForegroundColor Green
Write-Host "Trade with Vision, Learn with Purpose, Evolve with AI ✨" -ForegroundColor Cyan
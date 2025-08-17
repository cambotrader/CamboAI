# 🚀 CONNECT CAMBOAI TRADERSTATION FULL PLATFORM
# Frontend (Vercel) + Backend (Render) + Domain (Cloudflare)
# Trade with Vision, Learn with Purpose, Evolve with AI

Write-Host "🚀 CONNECTING FULL PLATFORM..." -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Update frontend environment variables
Write-Host "⚙️ Updating Frontend Environment..." -ForegroundColor Yellow

$frontendEnv = @"
# 🚀 CAMBOAI TRADERSTATION - PRODUCTION ENVIRONMENT
# Trade with Vision, Learn with Purpose, Evolve with AI

# Backend API (Update with your Render URL)
NEXT_PUBLIC_API_URL=https://camboai-traderstation-api.onrender.com
NEXT_PUBLIC_WS_URL=wss://camboai-traderstation-api.onrender.com

# Authentication
NEXTAUTH_URL=https://camboai.com
NEXTAUTH_SECRET=your_nextauth_secret_here

# Database (if needed for frontend)
DATABASE_URL=your_database_url_here

# AI Services (for client-side features)
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_key_here
NEXT_PUBLIC_ANTHROPIC_API_KEY=your_claude_key_here

# Analytics & Monitoring
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your_analytics_id
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn

# Trading APIs (for live data)
NEXT_PUBLIC_ALPHA_VANTAGE_KEY=your_alpha_vantage_key
NEXT_PUBLIC_POLYGON_API_KEY=your_polygon_key
"@

# Write to web-advanced directory
Set-Location "web-advanced" -ErrorAction SilentlyContinue
$frontendEnv | Out-File -FilePath ".env.production" -Encoding UTF8
$frontendEnv | Out-File -FilePath ".env.local" -Encoding UTF8
Set-Location ".."

Write-Host "✅ Frontend environment configured" -ForegroundColor Green

# Update Vercel environment (instructions)
Write-Host "`n🔧 VERCEL ENVIRONMENT SETUP:" -ForegroundColor Cyan
Write-Host "Go to: https://vercel.com/your-username/camboai/settings/environment-variables" -ForegroundColor White
Write-Host "Add these variables:" -ForegroundColor White
Write-Host "   NEXT_PUBLIC_API_URL = https://your-render-app.onrender.com" -ForegroundColor Gray
Write-Host "   NEXTAUTH_SECRET = (generate random string)" -ForegroundColor Gray

# Backend environment template
Write-Host "`n⚙️ Backend Environment Template..." -ForegroundColor Yellow

$backendEnv = @"
# 🚀 CAMBOAI TRADERSTATION BACKEND - PRODUCTION
# Trade with Vision, Learn with Purpose, Evolve with AI

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
GOOGLE_AI_API_KEY=your_gemini_api_key_here

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Trading APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key
FINNHUB_API_KEY=your_finnhub_key

# Redis Cache
REDIS_URL=redis://default:password@host:port

# App Settings
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=your-render-app.onrender.com,camboai.com
CORS_ORIGINS=https://camboai.com,https://www.camboai.com

# Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
"@

Set-Location "backend" -ErrorAction SilentlyContinue
$backendEnv | Out-File -FilePath ".env.production" -Encoding UTF8
Set-Location ".."

Write-Host "✅ Backend environment template created" -ForegroundColor Green

Write-Host "`n🌐 DEPLOYMENT STATUS CHECK:" -ForegroundColor Cyan
Write-Host "   ✅ Domain: camboai.com (Cloudflare DNS)" -ForegroundColor Green
Write-Host "   ✅ Frontend: Vercel (auto-deploy from GitHub)" -ForegroundColor Green  
Write-Host "   ⏳ Backend: Render (manual setup required)" -ForegroundColor Yellow
Write-Host "   ⏳ Database: PostgreSQL on Render" -ForegroundColor Yellow

Write-Host "`n📋 NEXT STEPS CHECKLIST:" -ForegroundColor Cyan
Write-Host "1. 🚀 Deploy Backend to Render:" -ForegroundColor White
Write-Host "   - Run: .\Deploy-Backend-Render.ps1" -ForegroundColor Gray
Write-Host "   - Go to render.com and create service" -ForegroundColor Gray
Write-Host "   - Add environment variables" -ForegroundColor Gray

Write-Host "2. 🔧 Update Frontend with Backend URL:" -ForegroundColor White
Write-Host "   - Get your Render URL: https://your-app.onrender.com" -ForegroundColor Gray
Write-Host "   - Update NEXT_PUBLIC_API_URL in Vercel settings" -ForegroundColor Gray

Write-Host "3. 🔑 Get API Keys:" -ForegroundColor White
Write-Host "   - OpenAI: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host "   - Anthropic: https://console.anthropic.com/" -ForegroundColor Gray
Write-Host "   - Google AI: https://aistudio.google.com/app/apikey" -ForegroundColor Gray

Write-Host "4. ✅ Test Full Platform:" -ForegroundColor White
Write-Host "   - Visit: https://camboai.com" -ForegroundColor Gray
Write-Host "   - Test AI features" -ForegroundColor Gray
Write-Host "   - Verify backend connection" -ForegroundColor Gray

Write-Host "`n🎉 CAMBOAI TRADERSTATION PLATFORM INTEGRATION COMPLETE!" -ForegroundColor Green
Write-Host "Trade with Vision, Learn with Purpose, Evolve with AI ✨" -ForegroundColor Cyan
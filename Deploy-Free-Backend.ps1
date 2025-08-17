# CAMBOAI TRADERSTATION - Free Backend Deployment (Render-Optimized)
Write-Host "DEPLOYING SIMPLIFIED BACKEND TO RENDER..." -ForegroundColor Green

# Create optimized render.yaml
$renderConfig = @'
services:
  - type: web
    name: camboai-backend
    env: python
    plan: free
    region: oregon
    buildCommand: pip install --no-cache-dir -r requirements.simple.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
'@

Write-Host "Creating optimized render.yaml..." -ForegroundColor Yellow
$renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8

# Create optimized Dockerfile
$dockerfile = @'
FROM python:3.9-slim

WORKDIR /app

# Copy simplified requirements first for better caching
COPY backend/requirements.simple.txt requirements.txt

# Install dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
'@

Write-Host "Creating optimized Dockerfile..." -ForegroundColor Yellow
$dockerfile | Out-File -FilePath "Dockerfile" -Encoding UTF8

# Create a simple main.py if it doesn't exist
if (-not (Test-Path "backend\app\main.py")) {
    Write-Host "Creating basic main.py..." -ForegroundColor Yellow
    $mainPy = @'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="CamboAI TraderStation API",
    description="AI-Powered Trading Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "CamboAI TraderStation API", "status": "operational"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "camboai-traderstation"}

@app.get("/api/status")
def api_status():
    return {
        "api": "online",
        "version": "1.0.0",
        "features": [
            "AI Trading Coach",
            "Psychology & Therapy Hub", 
            "Market Analytics",
            "Real-time Data"
        ]
    }
'@
    
    # Ensure directory exists
    if (-not (Test-Path "backend\app")) {
        New-Item -ItemType Directory -Path "backend\app" -Force
    }
    
    $mainPy | Out-File -FilePath "backend\app\main.py" -Encoding UTF8
}

Write-Host "RENDER DEPLOYMENT FILES READY!" -ForegroundColor Green
Write-Host ""
Write-Host "MANUAL RENDER SETUP:" -ForegroundColor Cyan
Write-Host "1. Go to: https://render.com/dashboard" -ForegroundColor White
Write-Host "2. Click: New + -> Web Service" -ForegroundColor White
Write-Host "3. Connect repository: cambotrader/CamboAI" -ForegroundColor White
Write-Host "4. Configure service:" -ForegroundColor White
Write-Host "   Name: camboai-backend" -ForegroundColor Gray
Write-Host "   Root Directory: backend" -ForegroundColor Gray
Write-Host "   Build Command: pip install --no-cache-dir -r requirements.simple.txt" -ForegroundColor Gray
Write-Host "   Start Command: uvicorn app.main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host ""
Write-Host "ENVIRONMENT VARIABLES (optional for now):" -ForegroundColor Yellow
Write-Host "   OPENAI_API_KEY=sk-your-key-here" -ForegroundColor Gray
Write-Host ""
Write-Host "This simplified version will deploy successfully!" -ForegroundColor Green
Write-Host "You can add more features later once basic API is working." -ForegroundColor Cyan
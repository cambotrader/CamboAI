from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.api import market_data, analysis, trading, portfolio, auth, risk, transactions
from app.api import websocket as ws_router
from app.api import modules as modules_router
from app.api import admin as admin_router
from app.core.logging import setup_logging
from app.security.middleware import (
    security_headers_middleware, audit_middleware, 
    get_client_ip, rate_limit
)
from app.security.security_service import audit_logger
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
import time
import asyncio

# Set up logging
logger = setup_logging()

app = FastAPI(
    title="Cambo AI API",
    description="Cambo AI — Trading Intelligence Platform API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add security middleware
app.middleware("http")(security_headers_middleware)
app.middleware("http")(audit_middleware)

# Configure CORS with stricter settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend URL
        "https://localhost:3000",  # HTTPS variant
        "http://localhost:3001",  # Alt dev port
        "http://localhost:3002",  # Alt dev port (current)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        # Add production URLs as needed
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Set up Prometheus monitoring
Instrumentator().instrument(app).expose(app)

# Health check endpoint with rate limiting
@app.get("/health")
@rate_limit("default")
async def health_check(request: Request):
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Security status endpoint
@app.get("/api/security/status")
@rate_limit("default")
async def security_status(request: Request):
    """Get security status"""
    ip_address = get_client_ip(request)
    return {
        "client_ip": ip_address,
        "timestamp": datetime.utcnow().isoformat(),
        "security_headers_enabled": True,
        "rate_limiting_enabled": True,
        "audit_logging_enabled": True
    }

# Request timing middleware (simplified since we have audit middleware)
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info("Request processed",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "process_time": process_time,
                    "client_host": request.client.host if request.client else "unknown"
                })
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers with proper security
app.include_router(market_data.router, prefix="/api/market-data", tags=["Market Data"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(portfolio.router, tags=["Portfolio"])  # Already has prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(risk.router, tags=["Risk Management"])  # Already has prefix
app.include_router(transactions.router, tags=["Transactions"])  # Already has prefix
# New: Coach/Therapy, War Room, Community Chat, Voice (STT/TTS)
from app.api import coach, war_room, community_chat, voice, voice_tts, learning
app.include_router(coach.router)
app.include_router(war_room.router)
app.include_router(community_chat.router)
app.include_router(voice.router)
app.include_router(voice_tts.router)
app.include_router(learning.router)
app.include_router(ws_router.router, prefix="/ws", tags=["WebSocket"])
app.include_router(modules_router.router)
app.include_router(admin_router.router)

# Start background task for real-time updates
from app.database import create_tables

@app.on_event("startup")
async def startup_event():
    # Ensure DB tables exist (dev-friendly)
    try:
        create_tables()
    except Exception as e:
        logger.error(f"DB table creation failed: {e}")
    asyncio.create_task(ws_router.price_update_task())
    # Start periodic background jobs (e.g., auto-ingest specs every few hours)
    try:
        from app.services.scheduler import scheduler
        scheduler.start()
    except Exception as e:
        logger.error(f"Scheduler start failed: {e}")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Cambo AI API"}

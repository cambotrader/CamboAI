from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Cambo AI Trader Station API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Cambo AI Trader Station API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/portfolio")
async def get_portfolio():
    return {
        "total_value": 100000.00,
        "cash": 50000.00,
        "positions": []
    }

@app.get("/api/v1/market-data/{symbol}")
async def get_market_data(symbol: str):
    return {
        "symbol": symbol,
        "price": 150.00,
        "change": 2.50,
        "change_percent": 1.69
    }

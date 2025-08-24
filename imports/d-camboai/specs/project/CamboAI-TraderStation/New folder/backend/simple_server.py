from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import importlib.util

spec = importlib.util.find_spec("app.api.auth")
if spec is not None:
    from app.api import auth as auth_router_module  # type: ignore
    AUTH_ROUTER_AVAILABLE = True
else:
    AUTH_ROUTER_AVAILABLE = False

app = FastAPI()

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount lightweight auth endpoints if available
if AUTH_ROUTER_AVAILABLE:
    app.include_router(auth_router_module.router, prefix="/api/auth", tags=["Authentication"])  # type: ignore
else:
    # Minimal fallback auth for development
    from pydantic import BaseModel
    from datetime import datetime, timedelta
    
    class Token(BaseModel):
        access_token: str
        token_type: str
        expires_in: int

    class User(BaseModel):
        id: int
        email: str
        is_active: bool
        created_at: str

    class UserLogin(BaseModel):
        email: str
        password: str

    DEMO_EMAIL = "demo@cambostation.com"
    DEMO_PASSWORD = "password"

    @app.post("/api/auth/login", response_model=Token)
    async def dev_login(user_credentials: UserLogin):
        if user_credentials.email != DEMO_EMAIL or user_credentials.password != DEMO_PASSWORD:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        return Token(access_token="demo-token", token_type="bearer", expires_in=30*60)

    @app.get("/api/auth/me", response_model=User)
    async def dev_me(authorization: str = Header(default="")):
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        # In dev, accept demo-token
        token = authorization.split(" ", 1)[1]
        if token != "demo-token":
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(id=1, email=DEMO_EMAIL, is_active=True, created_at=datetime.utcnow().isoformat())

# ----- Lightweight portfolio endpoints for dashboard -----
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import random
from math import sqrt


class Position(BaseModel):
    id: int
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    market_value: float
    entry_date: str


class PerformancePoint(BaseModel):
    date: str
    value: float
    daily_return: float
    cumulative_return: float


class PortfolioSummary(BaseModel):
    total_value: float
    total_pnl: float
    total_return_percentage: float
    positions_count: int
    current_day_value: float
    current_day_return: float


@app.get("/api/portfolio/positions", response_model=List[Position])
def get_positions() -> List[Position]:
    symbols = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
    positions: List[Position] = []
    for i, sym in enumerate(symbols, start=1):
        qty = random.choice([25, 50, 100])
        entry = round(random.uniform(100, 250), 2)
        cur = round(entry * random.uniform(0.95, 1.15), 2)
        pnl = round((cur - entry) * qty, 2)
        pnl_pct = round(((cur - entry) / entry) * 100, 2)
        mv = round(cur * qty, 2)
        positions.append(
            Position(
                id=i,
                symbol=sym,
                quantity=qty,
                entry_price=entry,
                current_price=cur,
                pnl=pnl,
                pnl_percentage=pnl_pct,
                market_value=mv,
                entry_date=(datetime.utcnow() - timedelta(days=random.randint(10, 60))).isoformat(),
            )
        )
    return positions


@app.get("/api/portfolio/performance", response_model=List[PerformancePoint])
def get_performance(days: int = 30) -> List[PerformancePoint]:
    base_value = 100000.0
    points: List[PerformancePoint] = []
    cumulative_return = 0.0
    current = base_value
    start_date = datetime.utcnow() - timedelta(days=days)
    for d in range(days):
        # simulate small daily return between -1% and +1%
        daily_ret = random.uniform(-0.01, 0.01)
        current = current * (1 + daily_ret)
        cumulative_return = (current / base_value) - 1
        points.append(
            PerformancePoint(
                date=(start_date + timedelta(days=d + 1)).date().isoformat(),
                value=round(current, 2),
                daily_return=round(daily_ret * 100, 3),
                cumulative_return=round(cumulative_return * 100, 3),
            )
        )
    return points


@app.get("/api/portfolio/summary", response_model=PortfolioSummary)
def get_summary() -> PortfolioSummary:
    # derive from positions for consistency
    pos = get_positions()
    total_value = round(sum(p.market_value for p in pos), 2)
    total_pnl = round(sum(p.pnl for p in pos), 2)
    total_return_pct = round((total_pnl / (total_value - total_pnl)) * 100, 2) if total_value - total_pnl != 0 else 0.0
    # current day random move
    day_ret_pct = random.uniform(-0.5, 0.5)  # +/- 0.5%
    current_day_value = round(total_value * (1 + day_ret_pct / 100), 2)
    return PortfolioSummary(
        total_value=total_value,
        total_pnl=total_pnl,
        total_return_percentage=total_return_pct,
        positions_count=len(pos),
        current_day_value=current_day_value,
        current_day_return=round(day_ret_pct, 3),
    )


# ----- Technical analysis (no external talib) -----
class TechnicalInput(BaseModel):
    close: List[float]


@app.post("/api/analysis/technical")
def technical_analysis(inp: TechnicalInput):
    closes = inp.close
    n = len(closes)
    def sma(period: int):
        out = [None] * n
        if period <= 0:
            return out
        s = 0.0
        for i, v in enumerate(closes):
            s += v
            if i >= period:
                s -= closes[i - period]
            if i >= period - 1:
                out[i] = s / period
        return out

    def rsi(period: int = 14):
        out = [None] * n
        if n == 0 or period <= 0:
            return out
        gains = [0.0] * n
        losses = [0.0] * n
        for i in range(1, n):
            change = closes[i] - closes[i - 1]
            gains[i] = max(change, 0.0)
            losses[i] = -min(change, 0.0)
        avg_gain = sum(gains[1:period + 1]) / period if n > period else 0.0
        avg_loss = sum(losses[1:period + 1]) / period if n > period else 0.0
        if n > period:
            rs = (avg_gain / avg_loss) if avg_loss != 0 else float('inf')
            out[period] = 100 - (100 / (1 + rs))
        for i in range(period + 1, n):
            avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
            avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
            rs = (avg_gain / avg_loss) if avg_loss != 0 else float('inf')
            out[i] = 100 - (100 / (1 + rs))
        return out

    def bbands(period: int = 20, k: float = 2.0):
        upper = [None] * n
        middle = [None] * n
        lower = [None] * n
        for i in range(n):
            if i >= period - 1:
                window = closes[i - period + 1:i + 1]
                m = sum(window) / period
                var = sum((x - m) ** 2 for x in window) / period
                sd = sqrt(var)
                middle[i] = m
                upper[i] = m + k * sd
                lower[i] = m - k * sd
        return upper, middle, lower

    sma20 = sma(20)
    rsi14 = rsi(14)
    upper, mid, lower = bbands(20, 2.0)

    # Convert None to null via pydantic by returning directly
    return {
        "sma": sma20,
        "rsi": rsi14,
        "bollinger_bands": {
            "upper": upper,
            "middle": mid,
            "lower": lower,
        },
    }

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ----- Optional: Journal CRUD (in-memory) -----
class JournalNote(BaseModel):
    id: int
    title: str
    body: str
    tags: List[str]
    date: str  # ISO string

_journal_store_by_user: Dict[str, List[JournalNote]] = {}

def _get_user_key(authorization: str) -> str:
    # Dev-friendly: use bearer token as a user key; fallback to 'public'
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return "public"

@app.get("/api/journal", response_model=List[JournalNote])
def list_journal(query: Optional[str] = None, tag: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, authorization: str = Header(default="")):
    def to_date_only(iso: str):
        try:
            d = datetime.fromisoformat(iso)
            return datetime(d.year, d.month, d.day)
        except (ValueError, TypeError):
            return None
    q = (query or "").lower().strip()
    frm = datetime.fromisoformat(date_from) if date_from else None
    to = datetime.fromisoformat(date_to) if date_to else None
    out: List[JournalNote] = []
    user_key = _get_user_key(authorization)
    store = _journal_store_by_user.get(user_key, [])
    for n in store:
        txt = f"{n.title} {n.body}".lower()
        if q and q not in txt:
            continue
        if tag and tag not in n.tags:
            continue
        if frm or to:
            nd = to_date_only(n.date)
            if not nd:
                continue
            if frm and nd < frm:
                continue
            if to:
                end = datetime(to.year, to.month, to.day, 23, 59, 59, 999000)
                if nd > end:
                    continue
        out.append(n)
    # newest first
    out.sort(key=lambda x: x.date, reverse=True)
    return out

class JournalCreate(BaseModel):
    title: str = ""
    body: str = ""
    tags: List[str] = []

@app.post("/api/journal", response_model=JournalNote)
def create_journal(payload: JournalCreate, authorization: str = Header(default="")):
    nid = int(datetime.utcnow().timestamp() * 1000)
    note = JournalNote(id=nid, title=payload.title.strip(), body=payload.body.strip(), tags=list(dict.fromkeys(payload.tags)), date=datetime.utcnow().isoformat())
    user_key = _get_user_key(authorization)
    if user_key not in _journal_store_by_user:
        _journal_store_by_user[user_key] = []
    _journal_store_by_user[user_key].insert(0, note)
    return note

class JournalUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None

@app.put("/api/journal/{note_id}", response_model=JournalNote)
def update_journal(note_id: int, payload: JournalUpdate, authorization: str = Header(default="")):
    user_key = _get_user_key(authorization)
    store = _journal_store_by_user.get(user_key, [])
    for i, n in enumerate(store):
        if n.id == note_id:
            updated = n.copy(update={
                "title": payload.title if payload.title is not None else n.title,
                "body": payload.body if payload.body is not None else n.body,
                "tags": list(dict.fromkeys(payload.tags)) if payload.tags is not None else n.tags,
            })
            store[i] = updated
            _journal_store_by_user[user_key] = store
            return updated
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/api/journal/{note_id}")
def delete_journal(note_id: int, authorization: str = Header(default="")):
    user_key = _get_user_key(authorization)
    store = _journal_store_by_user.get(user_key, [])
    for i, n in enumerate(store):
        if n.id == note_id:
            store.pop(i)
            _journal_store_by_user[user_key] = store
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Note not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

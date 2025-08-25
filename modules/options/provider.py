import time, requests, sqlite3, json, math
from pathlib import Path
import pandas as pd

DB_PATH = Path("data") / "pattern_detections.db"
DDL = """
CREATE TABLE IF NOT EXISTS options_cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol TEXT,
  source TEXT,
  expiry TEXT,
  fetched_ts INTEGER,
  payload TEXT
);
CREATE INDEX IF NOT EXISTS ix_options_symbol ON options_cache(symbol, source);
"""
IV_HIST_DDL = """
CREATE TABLE IF NOT EXISTS iv_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol TEXT,
  ts INTEGER,
  avg_iv REAL
);
CREATE INDEX IF NOT EXISTS ix_iv_symbol ON iv_history(symbol);
"""

TRADIER_ENDPOINT = "https://api.tradier.com/v1"

def _init():
    with sqlite3.connect(DB_PATH) as c:
        c.executescript(DDL)
        c.executescript(IV_HIST_DDL)

def fetch_tradier_chain(symbol: str, token: str, expiry: str | None = None):
    if token:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        params = {"symbol": symbol, "greeks": "true"}
        if expiry: params["expiration"] = expiry
        try:
            r = requests.get(f"{TRADIER_ENDPOINT}/markets/options/chains", headers=headers, params=params, timeout=12)
            if r.status_code == 200:
                js = r.json()
                contracts = js.get("options",{}).get("option",[])
                rows = []
                for c in contracts:
                    rows.append({
                        "type": c.get("option_type"),
                        "strike": c.get("strike"),
                        "bid": c.get("bid"),
                        "ask": c.get("ask"),
                        "iv": c.get("greeks",{}).get("iv"),
                        "delta": c.get("greeks",{}).get("delta"),
                        "theta": c.get("greeks",{}).get("theta"),
                        "gamma": c.get("greeks",{}).get("gamma"),
                        "rho": c.get("greeks",{}).get("rho"),
                        "vega": c.get("greeks",{}).get("vega"),
                        "expiry": c.get("expiration_date"),
                        "symbol": c.get("symbol")
                    })
                return pd.DataFrame(rows)
        except Exception:
            pass
    # synthetic fallback
    rows = []
    base = 100.0
    for k in range(-5,6):
        strike = base + k*2
        rows.append({"type":"call","strike":strike,"bid":1.2,"ask":1.5,"iv":0.35,"delta":0.55,"expiry": expiry or "2024-12-20"})
        rows.append({"type":"put","strike":strike,"bid":1.1,"ask":1.4,"iv":0.37,"delta":-0.48,"expiry": expiry or "2024-12-20"})
    return pd.DataFrame(rows)

def get_chain(symbol: str, source: str = "tradier", expiry: str | None = None,
              token: str | None = None, cache_ttl: int = 300):
    _init()
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT payload,fetched_ts FROM options_cache WHERE symbol=? AND source=? ORDER BY fetched_ts DESC LIMIT 1",
                        (symbol,source)).fetchone()
    if row and (now - row[1] < cache_ttl):
        return pd.read_json(row[0], orient="records")
    if source == "tradier":
        df = fetch_tradier_chain(symbol, token or "", expiry)
    else:
        df = fetch_tradier_chain(symbol, token or "", expiry)
    with sqlite3.connect(DB_PATH) as c:
        c.execute("INSERT INTO options_cache(symbol,source,expiry,fetched_ts,payload) VALUES (?,?,?,?,?)",
                  (symbol,source,expiry,now,df.to_json(orient="records")))
    _record_iv(symbol, df)
    return df

def _record_iv(symbol: str, df: pd.DataFrame):
    if df.empty or "iv" not in df.columns: return
    avg_iv = float(df['iv'].dropna().mean()) if not df['iv'].dropna().empty else None
    if avg_iv is None: return
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as c:
        c.execute("INSERT INTO iv_history(symbol,ts,avg_iv) VALUES (?,?,?)",(symbol,now,avg_iv))

def get_iv_rank(symbol: str, lookback_days: int = 180):
    cutoff = int(time.time()) - lookback_days*86400
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT avg_iv FROM iv_history WHERE symbol=? AND ts>=? ORDER BY ts", (symbol, cutoff)).fetchall()
    ivs = [r[0] for r in rows if r[0] is not None]
    if len(ivs) < 5:
        return None
    current = ivs[-1]
    rank = sum(iv <= current for iv in ivs)/len(ivs)
    return {"current_iv": current, "rank": rank, "samples": len(ivs)}

def compute_greeks_black_scholes(df, underlying: float, r: float = 0.01, dte: int = 30, iv_col: str = "iv"):
    import numpy as np, math
    T = max(dte/365.0, 1e-6)
    out = []
    for _, row in df.iterrows():
        sigma = row.get(iv_col)
        if sigma is None or not sigma or sigma <= 0:
            out.append(row)
            continue
        S = underlying
        K = row['strike']
        d1 = (math.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        from math import exp
        from math import erf, sqrt
        N = lambda x: 0.5*(1+erf(x/sqrt(2)))
        nd1 = (1/math.sqrt(2*math.pi))*math.exp(-0.5*d1*d1)
        delta = N(d1) if row['type']=="call" else N(d1)-1
        gamma = nd1/(S*sigma*math.sqrt(T))
        vega = S*nd1*math.sqrt(T)/100
        theta = -(S*nd1*sigma/(2*math.sqrt(T)))/365
        r2 = row.copy()
        r2["delta_calc"]=delta; r2["gamma_calc"]=gamma; r2["vega_calc"]=vega; r2["theta_calc"]=theta
        out.append(r2)
    return pd.DataFrame(out)

def list_tradier_expirations(symbol: str, token: str):
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        r = requests.get(f"{TRADIER_ENDPOINT}/markets/options/expirations",
                         params={"symbol":symbol,"includeAll":"true"}, headers=headers, timeout=10)
        if r.status_code == 200:
            js = r.json()
            return js.get("expirations",{}).get("date",[])
    except Exception:
        pass
    return []
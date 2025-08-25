import json, sqlite3
from datetime import datetime
from modules.patterns.persist_base import get_conn, DDL  # assuming existing base
DDL_HARMONIC = """
CREATE TABLE IF NOT EXISTS harmonic_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    timeframe TEXT,
    pattern TEXT,
    index_pos INTEGER,
    confidence REAL,
    ratios TEXT,
    legs TEXT,
    ts TEXT
);
CREATE INDEX IF NOT EXISTS ix_harmonic_symbol_time ON harmonic_detections(symbol,timeframe,pattern);
"""

def init_db():
    with get_conn() as c:
        c.executescript(DDL)
        c.executescript(DDL_HARMONIC)

def save_harmonics(detections, symbol: str, timeframe: str):
    detections = [d for d in detections if d.get("family") == "Harmonic"]
    if not detections:
        return 0
    init_db()
    now = datetime.utcnow().isoformat()
    rows = []
    for d in detections:
        rows.append((
            symbol, timeframe, d.get("pattern"), d.get("index"),
            d.get("confidence"), json.dumps(d.get("ratios")),
            json.dumps(d.get("legs")), now
        ))
    with get_conn() as c:
        c.executemany("""
        INSERT INTO harmonic_detections(symbol,timeframe,pattern,index_pos,confidence,ratios,legs,ts)
        VALUES (?,?,?,?,?,?,?,?)""", rows)
    return len(rows)
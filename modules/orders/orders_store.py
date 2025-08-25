import sqlite3, time, json
from pathlib import Path

DB_PATH = Path("data") / "pattern_detections.db"

DDL = """
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  broker TEXT,
  symbol TEXT,
  side TEXT,
  qty REAL,
  type TEXT,
  status TEXT,
  raw TEXT,
  created_ts INTEGER,
  updated_ts INTEGER
);
"""

def _init():
    with sqlite3.connect(DB_PATH) as c:
        c.executescript(DDL)

def save_order(order_id: str, broker: str, symbol: str, side: str,
               qty: float, otype: str, status: str, raw):
    _init()
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""INSERT OR REPLACE INTO orders
            (id,broker,symbol,side,qty,type,status,raw,created_ts,updated_ts)
            VALUES (?,?,?,?,?,?,?,?,COALESCE((SELECT created_ts FROM orders WHERE id=?),?),?)""",
            (order_id,broker,symbol,side,qty,otype,status,json.dumps(raw),now,order_id,now,now))

def list_orders(limit: int = 50):
    _init()
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("PRAGMA table_info(orders)")
        cols = [r[1] for r in cur.fetchall()]
        rows = c.execute("SELECT * FROM orders ORDER BY created_ts DESC LIMIT ?", (limit,)).fetchall()
    return [dict(zip(cols,row)) for row in rows]

def update_order_status(order_id: str, status: str, raw):
    _init()
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as c:
        c.execute("UPDATE orders SET status=?, raw=?, updated_ts=? WHERE id=?",
                  (status, json.dumps(raw), now, order_id))

def open_order_ids():
    _init()
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT id, broker FROM orders WHERE status NOT IN ('filled','canceled','rejected')").fetchall()
    return rows
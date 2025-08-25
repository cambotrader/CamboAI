import pandas as pd, time, sqlite3

from pathlib import Path
DB_PATH = Path("data") / "pattern_detections.db"

def iv_history(symbol: str, lookback_days: int = 180):
    cutoff = int(time.time()) - lookback_days*86400
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT ts, avg_iv FROM iv_history WHERE symbol=? AND ts>=? ORDER BY ts",
                         (symbol, cutoff)).fetchall()
    if not rows: return pd.DataFrame()
    return pd.DataFrame(rows, columns=["ts","avg_iv"]).assign(ts=lambda d: pd.to_datetime(d.ts, unit="s"))

def skew_snapshot(chain_df: pd.DataFrame):
    if chain_df.empty: return {}
    atm = chain_df.iloc[(chain_df['strike'] - chain_df['strike'].median()).abs().argmin()]['strike']
    calls = chain_df[(chain_df.type=="call") & (chain_df.strike>=atm)].head(5)
    puts  = chain_df[(chain_df.type=="put") & (chain_df.strike<=atm)].tail(5)
    call_iv = calls.iv.mean() if not calls.empty else None
    put_iv  = puts.iv.mean() if not puts.empty else None
    return {
        "atm_strike": atm,
        "call_iv": call_iv,
        "put_iv": put_iv,
        "skew": (call_iv - put_iv) if (call_iv and put_iv) else None
    }

def greeks_distribution(chain_df: pd.DataFrame):
    cols = [c for c in chain_df.columns if c.endswith("_calc")]
    if not cols: return {}
    return chain_df[cols].describe().to_dict()
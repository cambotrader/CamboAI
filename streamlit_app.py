import os, json, threading, time, io, base64
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import streamlit as st

HEAD
# External libs for visuals / clustering (guarded)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib = None
    plt = None
# External libs for visuals / clustering
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
main

try:
    from sklearn.cluster import KMeans
except ImportError:
    KMeans = None

# WebSocket client (for market data / orders)
try:
    import websocket
except ImportError:
    websocket = None

# Ensure harmonic patterns & engine register
from modules.patterns.harmonic import *  # noqa
from modules.patterns.registry import registry as pattern_registry

APP_BUILD_TAG = "post-SECRETS_ENFORCED_V1-2025-08-24"

# ---------------- Session Init ----------------
def _init_session():
    if "nav_choice" not in st.session_state:
        st.session_state.nav_choice = "Dashboard"
    if "latest_tick" not in st.session_state:
        st.session_state.latest_tick = None
    if "ws_thread_started" not in st.session_state:
        st.session_state.ws_thread_started = False

_init_session()

# ---------------- Utility ----------------
def fetch_live_ohlc(symbol: str, provider: str = "yfinance", interval: str = "1d", period: str = "1mo"):
    try:
        params = {"source": provider, "symbol": symbol, "interval": interval, "period": period}
        r = requests.get("http://127.0.0.1:8000/marketdata/ohlc", params=params, timeout=15)
        js = r.json()
        if "ohlc" not in js:
            return None
        o = js["ohlc"]
        df = pd.DataFrame({
            "open": o["open"],
            "high": o["high"],
            "low": o["low"],
            "close": o["close"]
        }, index=pd.to_datetime(o["index"]))
        return df
    except Exception:
        return None

def synthetic_price_df(rows: int = 500):
    idx = pd.date_range(end=pd.Timestamp.utcnow(), periods=rows, freq="H")
    base = 100 + np.cumsum(np.random.randn(rows))
    high = base + np.random.rand(rows)*1.2
    low = base - np.random.rand(rows)*1.2
    close = low + (high - low)*np.random.rand(rows)
    return pd.DataFrame({"open":base, "high":high, "low":low, "close":close}, index=idx)

# ---------------- WebSocket Live Ticker ----------------
def start_ws_listener(symbol: str, external: bool = False):
    if websocket is None:
        return
    url = f"ws://127.0.0.1:8000/ws/marketdata?symbol={symbol}&interval=15"
    if external:
        url += "&external=true"
    def on_message(_, message):
        try:
            js = json.loads(message)
            if js.get("type") in ("tick","ext_tick"):
                st.session_state.latest_tick = js["data"]
        except Exception:
            pass
    def run():
        try:
            ws = websocket.WebSocketApp(url, on_message=on_message)
            ws.run_forever()
        except Exception:
            pass
    if not st.session_state.ws_thread_started:
        t = threading.Thread(target=run, daemon=True)
        t.start()
        st.session_state.ws_thread_started = True

# ---------------- Orders WebSocket (optional) ----------------
def start_orders_ws():
    if websocket is None:
        return
    if st.session_state.get("orders_ws_started"):
        return
    url = "ws://127.0.0.1:8000/ws/orders?interval=6"
    def on_message(_, message):
        try:
            js = json.loads(message)
            if js.get("type") == "orders":
                st.session_state.orders_live = js["orders"]
        except Exception:
            pass
    def run():
        try:
            ws = websocket.WebSocketApp(url, on_message=on_message)
            ws.run_forever()
        except Exception:
            pass
    st.session_state.orders_live = []
    threading.Thread(target=run, daemon=True).start()
    st.session_state.orders_ws_started = True

# ---------------- Pattern Scans ----------------
def render_pattern_markers(price_df: pd.DataFrame):
    import pandas as pd
    st.markdown("### Pattern Markers")
    scan = st.button("Scan Patterns")
    if scan:
        from modules.patterns.calibration import add_candle_metrics, calibrate_confidence
        from modules.chart_patterns import detect_all_patterns
        metrics_df = add_candle_metrics(price_df)
        detections = detect_all_patterns(price_df)
        detections = calibrate_confidence(detections, metrics_df)
        if detections:
            latest = sorted(detections, key=lambda d: d.get("index",0), reverse=True)[:15]
            badge_html = ""
            for d in latest:
                typ = d.get("type","")
                color = "#35d58b" if typ in ("bullish","bull") else "#ff5f56" if typ in ("bearish","bear") else "#8899aa"
                badge_html += f'<span style="background:{color}22;border:1px solid {color}55;color:{color};padding:2px 6px;margin:2px 4px;border-radius:5px;font-size:11px;display:inline-block;">{d.get("pattern")}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(detections))
        else:
            st.info("No patterns detected.")

def render_harmonic_outline(df: pd.DataFrame):
    st.markdown("### Harmonic Engine")
    harm_names = [p.name for p in pattern_registry.all() if p.family == "Harmonic"]
    if st.button("Scan Harmonics"):
        from modules.chart_patterns import detect_all_patterns
        det = detect_all_patterns(df, include=harm_names)
        if det:
            st.success(f"{len(det)} harmonic matches")
            st.dataframe(pd.DataFrame(det))
        else:
            st.info("No harmonic matches with current thresholds.")

# ---------------- Ratio Heatmap (Refined) ----------------
def render_ratio_heatmap():
HEAD
    import sqlite3, json, pandas as pd, numpy as np, io
    st.subheader("Harmonic Ratio Heatmap (Refined)")
    if plt is None:
        st.error("matplotlib not installed. Run: pip install matplotlib")
        return
    if KMeans is None:
        st.error("scikit-learn not installed. Run: pip install scikit-learn")
        return
    st.subheader("Harmonic Ratio Heatmap (Refined)")
    import sqlite3, json
main
    ratio_keys_all = ["B_XA","D_XA","D_XA_ext","AB_CD_equality","AD_BC_ratio"]
    dbp = st.text_input("DB Path", "data/pattern_detections.db", key="db_heatmap")
    ratio_keys = st.multiselect("Ratios", ratio_keys_all, default=ratio_keys_all[:3])
    norm_mode = st.selectbox("Normalization", ["zscore","minmax","none"], index=0)
    k = st.slider("Clusters (k)", 2, 10, 4)
    conf_min = st.slider("Min Confidence", 0.0, 1.0, 0.6, 0.01)
    if not ratio_keys:
        st.info("Select ratios.")
        return
    try:
        with sqlite3.connect(dbp) as c:
            rows = c.execute("SELECT pattern, ratios, confidence FROM harmonic_detections").fetchall()
    except Exception as e:
        st.error(f"DB error: {e}")
        return
    data=[]
    for pattern, rj, conf in rows:
        if conf < conf_min: continue
        try:
            rdict=json.loads(rj)
            row={"pattern":pattern,"confidence":conf}
            for rk in ratio_keys:
                if rk in rdict: row[rk]=rdict[rk]
            if len(row)>2: data.append(row)
        except:
            pass
    if not data:
        st.warning("No data after filters.")
        return
    df = pd.DataFrame(data).dropna(subset=ratio_keys)
    if df.empty:
        st.info("No rows after NaN drop.")
        return
HEAD
=======
    if KMeans is None:
        st.error("scikit-learn not installed.")
        return
main
    X = df[ratio_keys].values
    km = KMeans(n_clusters=k, n_init="auto", random_state=42)
    df["cluster"] = km.fit_predict(X)
    piv = df.groupby("pattern")[ratio_keys].mean()
    if norm_mode == "zscore":
        M = (piv - piv.mean())/(piv.std(ddof=0)+1e-9)
    elif norm_mode == "minmax":
        M = (piv - piv.min())/(piv.max()-piv.min()+1e-9)
    else:
        M = piv.copy()
    fig,ax=plt.subplots(figsize=(1+0.9*len(ratio_keys), 0.5+0.4*len(M)))
    mat=M.values
    im=ax.imshow(mat,cmap="coolwarm",aspect="auto")
    ax.set_yticks(range(len(M.index))); ax.set_yticklabels(M.index,fontsize=7)
    ax.set_xticks(range(len(ratio_keys))); ax.set_xticklabels(ratio_keys,rotation=35,ha="right",fontsize=7)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val=mat[i,j]
            ax.text(j,i,f"{val:.2f}",ha="center",va="center",fontsize=6,color="black" if abs(val)<0.9 else "white")
    plt.colorbar(im,ax=ax,fraction=0.025,pad=0.02)
    buf=io.BytesIO(); plt.tight_layout(); fig.savefig(buf,format="png",dpi=130)
    st.image(buf.getvalue())
    st.dataframe(df[["pattern","cluster","confidence"]+ratio_keys].head(100))
    c1,c2,c3 = st.columns(3)
    if c1.button("Export CSV"):
        st.download_button("Download CSV", df.to_csv(index=False), file_name="ratios_refined.csv")
    if c2.button("Export JSON"):
        st.download_button("Download JSON", df.to_json(orient="records"), file_name="ratios_refined.json", mime="application/json")
    if c3.button("Export Pivot"):
        st.download_button("Download Pivot CSV", piv.to_csv(), file_name="ratios_pivot.csv")

HEAD
# ---------------- Education ----------------
def render_education_tab():
    st.header("Education")
    st.write("Quick lessons and references for patterns, risk, and strategies.")

    # Progress tracking (per user session)
    if "edu_progress" not in st.session_state:
        st.session_state.edu_progress = {}

    # Search docs
    query = st.text_input("Search modules", "")

    # Module catalog
    modules = [
        ("curriculum", "Curriculum", "d:/CamboAI/docs/education/curriculum.md"),
        ("technical-analysis", "Technical Analysis", "d:/CamboAI/docs/education/modules/technical-analysis.md"),
        ("risk-management", "Risk Management", "d:/CamboAI/docs/education/modules/risk-management.md"),
        ("asset-classes", "Asset Classes", "d:/CamboAI/docs/education/modules/asset-classes.md"),
        ("scalping", "Scalping Playbook", "d:/CamboAI/docs/education/modules/scalping.md"),
        ("scalping-advanced", "Scalping Advanced", "d:/CamboAI/docs/education/modules/scalping-advanced.md"),
        ("trend-swing", "Trend/Swing Playbook", "d:/CamboAI/docs/education/modules/trend-swing-playbook.md"),
        ("vwap", "VWAP Strategies", "d:/CamboAI/docs/education/modules/vwap-strategies.md"),
        ("options-basics", "Options Basics", "d:/CamboAI/docs/education/modules/options-basics.md"),
        ("options-advanced", "Options Advanced", "d:/CamboAI/docs/education/modules/options-advanced.md"),
        ("fx-futures", "FX/Futures Nuances", "d:/CamboAI/docs/education/modules/fx-futures-nuances.md"),
        ("backtest-journal", "Backtesting & Journaling", "d:/CamboAI/docs/education/modules/backtesting-journaling.md"),
    ]

    # Filter by search
    filtered = modules
    if query:
        q = query.lower()
        filtered = [m for m in modules if q in m[1].lower() or q in m[2].lower()]

    # Module list with progress
    sel = st.selectbox("Modules", [m[1] for m in filtered])

    # Render selected module
    chosen = next((m for m in filtered if m[1] == sel), None)
    content = None
    if chosen:
        try:
            with open(chosen[2], "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            st.error(f"Failed to load module: {e}")
    if content:
        st.markdown(content)
        k = f"done:{chosen[0]}"
        done = st.checkbox("Mark completed", value=bool(st.session_state.edu_progress.get(k)), key=k)
        st.session_state.edu_progress[k] = done

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Candlestick Basics")
        st.markdown("- Bullish/Bearish candles\n- Doji, Hammer, Engulfing\n- Support/Resistance")
        if st.button("Show Examples"):
            df = synthetic_price_df(200)
            st.line_chart(df["close"])    
    with col2:
        st.subheader("Risk Management")
        st.markdown("- Position sizing\n- Stop loss / Take profit\n- Risk/Reward ratio")
        risk = st.slider("Risk per trade (%)", 0.1, 5.0, 1.0, 0.1)
        st.info(f"Recommended: Keep risk per trade under {risk:.1f}% based on your plan.")

    st.markdown("---")
    st.subheader("Pattern Library")
    try:
        names = [p.name for p in pattern_registry.all()][:50]
        st.write(names)
    except Exception:
        st.write("Pattern registry not available.")

# ---------------- Screener ----------------
def render_screener_tab():
    st.header("Screener")
    st.write("Scan a watchlist and flag technical conditions.")
    symbols = st.text_area("Symbols (comma-separated)", "AAPL,MSFT,TSLA,NVDA,SPY").replace(" ","")
    provider = st.selectbox("Provider", ["yfinance","alpha_vantage"], index=0)
    interval = st.selectbox("Interval", ["1d","1h","15m"], index=0)
    period = st.selectbox("Period", ["1mo","3mo","6mo","1y"], index=0)
    # Filters
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        rsi_min = st.number_input("RSI min", value=30)
        rsi_max = st.number_input("RSI max", value=70)
    with colf2:
        macd_cross = st.selectbox("MACD", ["any","bullish_cross","bearish_cross"], index=0)
    with colf3:
        sort_by = st.selectbox("Sort by", ["symbol","close","rsi","macd_hist","pct_from_ma20","atr_pct"], index=0)
    # Extra filters
    colx1, colx2, colx3 = st.columns(3)
    with colx1:
        ma_cross = st.selectbox("MA Cross", ["any","price>ma20","price<ma20"], index=0)
    with colx2:
        pct_from_ma_thr = st.number_input("% from MA20 (abs <=)", value=5.0)
    with colx3:
        atr_pct_thr = st.number_input("ATR % of price (<=)", value=3.0)
    export_holder = st.empty()
    if st.button("Run Screener"):
        rows = []
        for sym in symbols.split(','):
            df = fetch_live_ohlc(sym, provider=provider, interval=interval, period=period)
            if df is None or df.empty:
                rows.append({"symbol":sym, "status":"no data"})
                continue
            close = df["close"].iloc[-1]
            # Indicators
            delta = df["close"].diff()
            gain = (delta.clip(lower=0)).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / (loss + 1e-9)
            rsi = 100 - (100 / (1 + rs))
            rsi_val = float(rsi.iloc[-1]) if not rsi.empty else None
            ema12 = df["close"].ewm(span=12, adjust=False).mean()
            ema26 = df["close"].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            hist = macd - signal
            macd_hist = float(hist.iloc[-1]) if not hist.empty else None
            macd_cross_sig = None
            if len(hist) >= 2:
                prev = hist.iloc[-2]
                cur = hist.iloc[-1]
                if prev <= 0 and cur > 0: macd_cross_sig = "bullish_cross"
                elif prev >= 0 and cur < 0: macd_cross_sig = "bearish_cross"
                else: macd_cross_sig = "any"
            ma20 = df["close"].rolling(20).mean().iloc[-1]
            atr = (df["high"]-df["low"]).rolling(14).mean().iloc[-1]
            trend = "up" if close > ma20 else "down"
            pct_from_ma20 = float((close - ma20) / ma20 * 100) if ma20 else None
            atr_pct = float(atr / close * 100) if close else None
            row = {"symbol":sym, "close":float(close), "rsi":rsi_val, "macd_hist":macd_hist, "macd_cross":macd_cross_sig, "ma20":float(ma20), "atr":float(atr), "trend":trend, "pct_from_ma20":pct_from_ma20, "atr_pct":atr_pct}
            # Apply filters
            ok = True
            if rsi_val is not None and not (rsi_min <= rsi_val <= rsi_max):
                ok = False
            if macd_cross != "any" and macd_cross_sig is not None and macd_cross_sig != macd_cross:
                ok = False
            if ma_cross == "price>ma20" and not (close > ma20):
                ok = False
            if ma_cross == "price<ma20" and not (close < ma20):
                ok = False
            if pct_from_ma20 is not None and abs(pct_from_ma20) > pct_from_ma_thr:
                ok = False
            if atr_pct is not None and atr_pct > atr_pct_thr:
                ok = False
            if ok:
                rows.append(row)
        if rows:
            df_out = pd.DataFrame(rows)
            if sort_by in df_out.columns:
                df_out = df_out.sort_values(sort_by, ascending=True if sort_by in ("symbol","trend") else False)
            st.dataframe(df_out)
            csv_bytes = df_out.to_csv(index=False).encode()
            export_holder.download_button("Download CSV", csv_bytes, file_name="screener.csv")

# ---------------- Debate Room ----------------
def render_debate_room_tab():
    st.header("Debate Room")
    st.write("Collaborative idea board. Share tickers and trade theses.")
    if "debate_msgs" not in st.session_state:
        st.session_state.debate_msgs = []

    # Room selector and pagination
    room = st.selectbox("Room", ["debate","stocks","crypto","options","forex","futures","lounge"], index=0)
    page = st.number_input("Page", min_value=1, value=1, step=1)
    page_size = st.selectbox("Page size", [25, 50, 100, 200], index=1)

    if st.button("Refresh Board"):
        try:
            r = requests.get(f"http://127.0.0.1:8000/api/community/history/{room}", timeout=10)
            msgs = r.json()
            # Simple client-side pagination
            start = (page-1) * page_size
            end = start + page_size
            msgs = msgs[start:end]
            st.session_state.debate_msgs = [
                {"user":m.get("user_id","anon"), "ticker":"", "side":"", "text":m.get("text",""), "ts":m.get("timestamp","")}
                for m in msgs
            ]
        except Exception as e:
            st.warning(f"Refresh failed: {e}")

    with st.form("debate_form"):
        user = st.text_input("Name", "Trader")
        ticker = st.text_input("Ticker", "AAPL")
        thesis = st.text_area("Thesis", "Breakout above resistance with volume.")
        side = st.selectbox("Bias", ["Bullish","Bearish","Neutral"], index=0)
        # Attachment placeholder (future: upload to backend)
        st.file_uploader("Attachment (optional)", type=["png","jpg","pdf"], accept_multiple_files=False, key="debate_attach")
        submitted = st.form_submit_button("Post")
        if submitted:
            try:
                payload = {"room":room,"user_id":user,"text":f"[{ticker.upper()}][{side}] {thesis}"}
                r = requests.post("http://127.0.0.1:8000/api/community/post", json=payload, timeout=10)
                if r.ok:
                    flags = r.json().get("redactions", {})
                    if any(flags.values()):
                        st.warning("Message was sanitized for PII or sensitive content.")
                    else:
                        st.success("Posted!")
                else:
                    st.error(f"Post failed: {r.status_code}")
            except Exception as e:
                st.error(f"Post failed: {e}")
            st.session_state.debate_msgs.append({"user":user, "ticker":ticker.upper(), "side":side, "text":thesis, "ts":datetime.utcnow().isoformat()})

    if st.session_state.debate_msgs:
        st.subheader("Board")
        st.dataframe(pd.DataFrame(st.session_state.debate_msgs))

main
# ---------------- Options Tab ----------------
def render_options_tab():
    import requests
    st.header("Options")
    symbol = st.text_input("Symbol", "AAPL", key="opt_symbol")
    token = st.text_input("Tradier Token (optional)", type="password")
    colA,colB,colC = st.columns(3)
    expiry = st.text_input("Expiry (YYYY-MM-DD optional)")
    if colA.button("Expirations"):
        r=requests.get("http://127.0.0.1:8000/options/expirations", params={"symbol":symbol}, headers={"token":token})
        st.write(r.json())
    if colB.button("Chain"):
        r = requests.get("http://127.0.0.1:8000/options/chain", params={"symbol":symbol,"expiry":expiry})
        js = r.json()
        st.write(f"Rows: {js.get('rows')}")
        if js.get("chain"):
            df = pd.DataFrame(js["chain"])
            st.dataframe(df.head(50))
    if colC.button("Chain + Greeks"):
        r = requests.get("http://127.0.0.1:8000/options/chain/with_greeks", params={"symbol":symbol,"underlying":100,"expiry":expiry})
        js=r.json()
        df=pd.DataFrame(js.get("chain",[]))
        st.dataframe(df.head(50))
    st.markdown("---")
    if st.button("Analytics"):
        r = requests.get("http://127.0.0.1:8000/options/analytics", params={"symbol":symbol,"expiry":expiry})
        js = r.json()
        st.subheader("Skew")
        st.json(js.get("skew"))
        iv_hist = js.get("iv_history") or []
        if iv_hist:
            iv_df = pd.DataFrame(iv_hist)
            iv_df['ts'] = pd.to_datetime(iv_df['ts'])
            st.line_chart(iv_df.set_index("ts")["avg_iv"])
        st.subheader("Greeks Stats")
        st.json(js.get("greeks_stats"))

# ---------------- Order Ticket ----------------
def render_order_ticket():
    from modules.brokers.base import registry as broker_registry
    st.subheader("Order Ticket")
    broker = st.selectbox("Broker", broker_registry.names())
    symbol = st.text_input("Order Symbol", "AAPL")
    side = st.selectbox("Side", ["buy","sell"])
    qty = st.number_input("Qty", value=1.0)
    col1,col2,col3 = st.columns(3)
    if col1.button("Place"):
        payload = {"broker":broker,"symbol":symbol,"side":side,"qty":qty}
        r = requests.post("http://127.0.0.1:8000/orders/place", json=payload)
        st.json(r.json())
    if col2.button("List"):
        r = requests.get("http://127.0.0.1:8000/orders/list")
        st.json(r.json())
    if col3.button("Start Orders WS"):
        start_orders_ws()
    # Live orders table
    orders_live = st.session_state.get("orders_live") or []
    if orders_live:
        st.markdown("Live Orders (WS)")
        st.dataframe(pd.DataFrame(orders_live))

# ---------------- Secrets / 2FA UI ----------------
def render_secrets_section():
    st.subheader("Broker Secrets / 2FA")
    code = st.text_input("2FA Code (admin)", type="password")
    with st.expander("Enable 2FA"):
        if st.button("Generate 2FA Secret"):
            r = requests.post("http://127.0.0.1:8000/brokers/secrets/2fa/enable")
            st.json(r.json())
    with st.expander("Verify 2FA"):
        if st.button("Verify Code"):
            r = requests.get("http://127.0.0.1:8000/brokers/secrets/2fa/verify", params={"code":code})
            st.json(r.json())
    with st.expander("Rotate Master Key (requires 2FA)"):
        if st.button("Rotate Key"):
            r = requests.post("http://127.0.0.1:8000/brokers/secrets/rotate_master", params={"code":code})
            st.json(r.json())
    with st.expander("Export Audit (JSON)"):
        if st.button("Export Audit"):
            r = requests.get("http://127.0.0.1:8000/brokers/secrets/audit/export", params={"format":"json","code":code})
            st.json(r.json())

# ---------------- Settings / Brokerage ----------------
def render_settings_tab():
    from modules.brokers.base import registry as broker_registry
    st.header("Settings / Brokerage / Admin")
    st.write("Build:", APP_BUILD_TAG)
    st.subheader("Broker Configure")
    brokers = broker_registry.names()
    if not brokers:
        st.info("No brokers registered.")
        return
    broker = st.selectbox("Broker", brokers, key="broker_select")
    c1,c2,c3,c4 = st.columns(4)
    key = c1.text_input("API Key", type="password")
    secret = c2.text_input("Secret", type="password")
    token = c3.text_input("Token", type="password")
    paper = c4.checkbox("Paper (Alpaca)", value=True)
    host = st.text_input("Host", value="127.0.0.1")
    port = st.number_input("Port", value=4001)
    twofa = st.text_input("2FA Code (for secrets)", type="password", key="2fa_conf")
    if st.button("Configure Broker"):
        payload = {"broker":broker,"key":key,"secret":secret,"token":token,"host":host,"port":port,"paper":paper}
        r = requests.post("http://127.0.0.1:8000/brokers/configure", json=payload, timeout=10)
        st.json(r.json())
    if st.button("Account Info"):
        r = requests.get(f"http://127.0.0.1:8000/brokers/account/{broker}", timeout=10)
        st.json(r.json())
    with st.expander("Store Secret (2FA required)"):
        b_key_id = st.text_input("Secret Key ID", "API_KEY")
        b_val = st.text_input("Secret Value", type="password")
        if st.button("Store Secret"):
            r = requests.post("http://127.0.0.1:8000/brokers/secrets/set",
                              params={"broker":broker,"key_id":b_key_id,"value":b_val,"code":twofa})
            st.json(r.json())
    render_secrets_section()
    st.markdown("---")
    render_order_ticket()
    st.markdown("---")
    render_options_tab()

# ---------------- Chart / Dashboard ----------------
def render_main_chart_section(price_df):
    st.subheader("Charts")
    if "chart_symbol" not in st.session_state:
        st.session_state.chart_symbol = "NASDAQ:AAPL"
    symbol_in = st.text_input("Symbol (TradingView style)", st.session_state.chart_symbol)
    st.session_state.chart_symbol = symbol_in
    c1,c2,c3,c4,c5 = st.columns([1.2,1,1,1,1])
    with c1:
        provider = st.selectbox("Data Provider", ["yfinance","ccxt","alpha_vantage"], index=0)
    with c2:
        interval = st.selectbox("Interval", ["1d","60","240","1h","4h"], index=0)
    with c3:
        multi = st.toggle("Multi View", True)
    with c4:
        theme_dark = st.toggle("Dark", True)
    with c5:
        ext_ws = st.toggle("External WS", False)
    base_symbol = symbol_in.split(":")[-1]
    live_df = fetch_live_ohlc(base_symbol, provider=provider,
                              interval="1d" if interval == "1d" else ("60" if interval in ("60","1h") else "1d"))
    data_df = live_df if live_df is not None and not live_df.empty else price_df
    # TradingView placeholders (assume implemented elsewhere)
    try:
        if multi:
            from modules.chart_providers.tradingview import tradingview_multi
            tradingview_multi(symbol=symbol_in, intervals=["60","240","D"], theme="dark" if theme_dark else "light")
        else:
            from modules.chart_providers.tradingview import tradingview_widget
            tradingview_widget(symbol=symbol_in, interval="60", theme="dark" if theme_dark else "light")
    except Exception:
        st.warning("TradingView widget module not found or errored.")
    # Live ticker
    if st.toggle("Live Ticker", value=False, key="live_ticker_toggle"):
        start_ws_listener(base_symbol, external=ext_ws)
        tick = st.session_state.get("latest_tick")
        if tick:
            st.metric(label=f"{tick['symbol']} Live Close", value=f"{tick.get('close',tick.get('price',0)):.2f}")
        else:
            st.write("Waiting for tick...")
    render_pattern_markers(data_df)
    render_harmonic_outline(data_df)

# ---------------- Analytics Tab ----------------
def render_analytics_tab():
    st.header("Analytics")
    render_ratio_heatmap()

# ---------------- Navigation ----------------
def sidebar_nav():
    st.sidebar.title("CamboAI")
    st.sidebar.caption(f"Build: {APP_BUILD_TAG}")
HEAD
    nav = st.sidebar.radio("Navigation", ["Dashboard","Analytics","Education","Screener","Debate Room","Settings"])
    nav = st.sidebar.radio("Navigation", ["Dashboard","Analytics","Settings"])
main
    st.session_state.nav_choice = nav
    return nav

nav_choice = sidebar_nav()

# Root synthetic data (fallback)
base_df = synthetic_price_df()

if nav_choice == "Dashboard":
    render_main_chart_section(base_df)
elif nav_choice == "Analytics":
    render_analytics_tab()
HEAD
elif nav_choice == "Education":
    render_education_tab()
elif nav_choice == "Screener":
    render_screener_tab()
elif nav_choice == "Debate Room":
    render_debate_room_tab()
main
elif nav_choice == "Settings":
    render_settings_tab()
else:
    st.write("Unknown section.")

# Footer
st.sidebar.markdown("---")
HEAD
st.sidebar.write("© 2025 CamboAI (Dev Build)")

st.sidebar.write("© 2025 CamboAI (Dev Build)")
main

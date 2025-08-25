import os, json, threading, time, io, base64
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import streamlit as st

# External libs for visuals / clustering
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    st.subheader("Harmonic Ratio Heatmap (Refined)")
    import sqlite3, json
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
    if KMeans is None:
        st.error("scikit-learn not installed.")
        return
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
    nav = st.sidebar.radio("Navigation", ["Dashboard","Analytics","Settings"])
    st.session_state.nav_choice = nav
    return nav

nav_choice = sidebar_nav()

# Root synthetic data (fallback)
base_df = synthetic_price_df()

if nav_choice == "Dashboard":
    render_main_chart_section(base_df)
elif nav_choice == "Analytics":
    render_analytics_tab()
elif nav_choice == "Settings":
    render_settings_tab()
else:
    st.write("Unknown section.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("© 2025 CamboAI (Dev Build)")

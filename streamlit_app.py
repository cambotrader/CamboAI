import streamlit as st
import requests
import pandas as pd

# CamboAI TraderStation (temporary Streamlit cockpit)
st.set_page_config(page_title='CamboAI TraderStation', layout='wide', initial_sidebar_state='expanded')
st.title('📊 CamboAI TraderStation — Streamlit Cockpit (Standalone)')

# Check if running in standalone mode (no backend)
def is_backend_available(url="http://localhost:8000"):
    try:
        response = requests.get(f"{url}/health", timeout=1)
        return response.status_code == 200
    except:
        return False

# Display mode indicator
if is_backend_available():
    st.success("🔗 Connected to CamboAI Backend API")
else:
    st.info("🚀 **Standalone Mode** - Charts & sentiment analysis working independently (Backend API not required)")

st.sidebar.header('Control Panel')
# Basic inputs
symbol = st.sidebar.text_input('Ticker', value='AAPL').upper()
interval = st.sidebar.selectbox('Interval', ['1d', '1h', '15m', '5m'], index=0)
period = st.sidebar.selectbox('History', ['1y', '6mo', '3mo', '1mo'], index=0)
api_key = st.sidebar.text_input('X-API-Key (optional, for backend calls)', value='', type='password')

show_bands = st.sidebar.checkbox('Show Bollinger Bands', value=True)
show_rsi = st.sidebar.checkbox('Compute RSI (tooltip only)', value=False)
show_sentiment = st.sidebar.checkbox('Show Sentiment Panel', value=True)

status_exp = st.sidebar.expander('Backend Status (Optional)', expanded=False)
with status_exp:
    st.caption("⚡ App works independently - Backend connection is optional for enhanced features")
    backend_url = st.text_input('Backend URL', value='http://localhost:8000')
    if st.button('Test Backend Connection', key='check_backend'):
        headers = {'X-API-Key': api_key} if api_key else {}
        try:
            h = requests.get(f"{backend_url}/health", headers=headers, timeout=3)
            r = requests.get(f"{backend_url}/ready", headers=headers, timeout=3)
            st.write('Health:', h.status_code, h.json() if str(h.headers.get('content-type','')).startswith('application/json') else h.text)
            st.write('Ready:', r.status_code, r.json() if str(r.headers.get('content-type','')).startswith('application/json') else r.text)
            if h.ok and r.ok:
                st.success('✅ Backend API connected successfully!')
            else:
                st.warning('⚠️ Backend returned non-OK status codes')
        except Exception as e:
            st.info(f'ℹ️ Backend not available: {e}\n\n**No worries!** The app works perfectly in standalone mode.')

st.divider()

# Tabs
chart_tab, sentiment_tab = st.tabs(["📈 Chart", "📰 Sentiment"])

with chart_tab:
    st.subheader('Price & Volume')
    import yfinance as yf
    from modules.chart_module import render_chart
    with st.spinner('Loading price data...'):
        try:
            df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
            # Fix multi-level columns issue
            if hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
                df.columns = df.columns.droplevel(1)
            # Ensure columns are properly named and 1D
            if not df.empty:
                expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in expected_cols:
                    if col in df.columns:
                        # Flatten any multi-dimensional columns
                        df[col] = df[col].squeeze()
        except Exception as e:
            df = pd.DataFrame()
            st.warning(f'Unable to fetch data: {e}')
    if df is None or df.empty:
        # Provide a small fallback synthetic dataset
        st.info('No data received. Showing a small sample dataset.')
        try:
            dates = pd.date_range(end=pd.Timestamp.utcnow(), periods=60, freq='D')
            base = 150.0
            close = pd.Series(base + pd.Series(range(60)).rolling(5, min_periods=1).mean().fillna(0).values).clip(lower=1)
            df = pd.DataFrame({
                'Open': close + 0.5,
                'High': close + 1.0,
                'Low': close - 1.0,
                'Close': close,
                'Volume': 1_000_000,
            }, index=dates)
        except Exception:
            df = pd.DataFrame()
    if df is None or df.empty:
        st.warning('Still no data. Try another symbol or period.')
    else:
        try:
            fig = render_chart(df, title=f"{symbol} Tactical Chart", show_bands=show_bands, show_rsi=show_rsi)
            st.plotly_chart(fig, use_container_width=True)
            st.caption('Overlays: MA50, MA200, optional Bollinger Bands. RSI computed if enabled.')
        except Exception as e:
            st.error(f'Chart error: {e}')

with sentiment_tab:
    if show_sentiment:
        st.subheader('News & Sentiment (FinBERT fallback to heuristics)')
        from modules.news_sentiment import get_headlines, score_headlines, build_sentiment_zones
        with st.spinner('Fetching headlines...'):
            try:
                items = get_headlines(symbol)
                scored = score_headlines(items)
            except Exception as e:
                scored = []
                st.error(f'Sentiment error: {e}')
        if not scored:
            st.info('No headlines available right now.')
        else:
            st.dataframe(pd.DataFrame([
                {"time": i.get("time"), "publisher": i.get("publisher"), "tone": f"{i.get('emoji')} {i.get('tone')}", "title": i.get("title"), "link": i.get("link")}
                for i in scored
            ]))
    else:
        st.info('Enable Sentiment Panel from the sidebar.')

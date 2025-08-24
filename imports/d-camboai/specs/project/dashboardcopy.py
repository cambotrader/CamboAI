import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ─── FinBERT Setup ──────────────────────────────────────────────────────────
@st.cache_resource
def load_finbert():
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    return tokenizer, model

tokenizer, model = load_finbert()
labels = ["negative", "neutral", "positive"]

def finbert_sentiment_score(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
    return labels[scores.argmax()]

def get_recent_headlines(ticker):
    return [
        {"date": datetime.now() - timedelta(days=3), "headline": f"{ticker.upper()} Q2 earnings exceed expectations"},
        {"date": datetime.now() - timedelta(days=6), "headline": f"{ticker.upper()} faces regulatory probe"},
        {"date": datetime.now() - timedelta(days=10), "headline": f"{ticker.upper()} announces AI partnership"}
    ]

def get_sentiment_zones(headlines):
    zones = []
    color_map = {
        "positive": "rgba(0,200,0,0.2)",
        "neutral": "rgba(180,180,0,0.2)",
        "negative": "rgba(200,0,0,0.2)"
    }
    for item in headlines:
        tone = finbert_sentiment_score(item["headline"])
        zones.append({
            "start": item["date"] - timedelta(days=1),
            "end": item["date"] + timedelta(days=1),
            "color": color_map[tone],
            "label": tone
        })
    return zones

# ─── Chart ───────────────────────────────────────────────────────────────────
def plot_chart(df, ticker, zones=None):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price'
    )])

    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='blue'), name='MA50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], line=dict(color='red'), name='MA200'))

    if zones:
        for zone in zones:
            fig.add_vrect(
                x0=zone['start'], x1=zone['end'],
                fillcolor=zone['color'], opacity=0.2, line_width=0
            )

    fig.update_layout(title=f"{ticker} Tactical Chart", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ─── App ─────────────────────────────────────────────────────────────────────
st.title("📊 CamboStation Tactical Dashboard")

ticker = st.text_input("Enter a stock symbol", "AAPL").upper()
if not ticker:
    st.stop()

df = yf.download(ticker, period="1y", auto_adjust=True)
if df.empty or 'Close' not in df.columns or len(df) < 200:
    st.error("Not enough data to generate signals.")
    st.stop()

df['MA50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
df['MA200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()

# ─── Sentiment Zones ─────────────────────────────────────────────────────────
if st.checkbox("🧠 Overlay FinBERT Sentiment Zones"):
    headlines = get_recent_headlines(ticker)
    zones = get_sentiment_zones(headlines)
else:
    zones = None

plot_chart(df, ticker, zones)

# ─── TradingView Widget ──────────────────────────────────────────────────────
if st.checkbox("💹 Show TradingView Chart"):
    embed = f"""
    <iframe src="https://s.tradingview.com/widgetembed/?symbol={ticker}&interval=D&theme=dark"
        width="100%" height="520" frameborder="0"></iframe>
    """
    components.html(embed, height=540)

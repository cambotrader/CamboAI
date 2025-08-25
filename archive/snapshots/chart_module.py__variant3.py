import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

def plot_price_chart(ticker, show_ma50=True, show_ma200=True, signals=None, sentiment=None):
    df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
    if df.empty or "Close" not in df.columns:
        st.error(f"No data for {ticker}")
        return

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="limegreen",
        decreasing_line_color="crimson",
        showlegend=False
    ))

    if show_ma50:
        df["MA50"] = df["Close"].rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MA50"],
            mode="lines", name="MA50",
            line=dict(color="blue", width=2)
        ))

    if show_ma200:
        df["MA200"] = df["Close"].rolling(200).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MA200"],
            mode="lines", name="MA200",
            line=dict(color="orange", width=2)
        ))

    if sentiment:
        for zone in sentiment:
            fig.add_vrect(
                x0=zone["start"], x1=zone["end"],
                fillcolor=zone["color"], opacity=0.15,
                line_width=0
            )

    if signals:
        for sig in signals:
            fig.add_trace(go.Scatter(
                x=[sig["index"]],
                y=[sig["price"]],
                mode="markers+text",
                name=sig["label"],
                marker=dict(size=12, color="gold", symbol="star"),
                text=[sig["label"]],
                textposition="top center",
                showlegend=False
            ))

    fig.update_layout(
        title=f"{ticker.upper()} – 1Y Candlestick Chart",
        xaxis_title="Date", yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        legend=dict(orientation="h", x=0, y=1.1)
    )

    st.plotly_chart(fig, use_container_width=True)

# chart_module.py - CamboAI upgraded charting module
# Provides Plotly-based candlestick charts with MA50/MA200 overlays,
# optional Bollinger Bands/RSI, and basic pattern annotations placeholder.

from __future__ import annotations
from typing import Optional, List, Dict

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# NOTE: This file is the active runtime chart module. A different spec variant was marked
# canonical during consolidation. Reconciled differences:
# - This runtime version includes multi-level column handling absent in archived variants.
# - Retained existing indicator logic; future merge of any missing annotations to happen here.

try:
    from ta.trend import SMAIndicator
    from ta.volatility import BollingerBands
    from ta.momentum import RSIIndicator
except ImportError:  # narrow exception
    SMAIndicator = None
    BollingerBands = None
    RSIIndicator = None


def _safe_indicator_series(series: pd.Series) -> pd.Series:
    if isinstance(series, pd.Series):
        return series
    return pd.Series(dtype=float)


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds MA50, MA200, optional BB bands and RSI if ta is available.
    """
    df = df.copy()
    
    # Handle multi-level columns from yfinance
    if hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
        df.columns = df.columns.droplevel(1)
    
    # Ensure Close column is 1D for indicators
    if "Close" in df.columns:
        close_series = _safe_indicator_series(df["Close"])
        
        if SMAIndicator:
            df["MA50"] = SMAIndicator(close=close_series, window=50).sma_indicator()
            df["MA200"] = SMAIndicator(close=close_series, window=200).sma_indicator()
        else:
            df["MA50"] = close_series.rolling(50).mean()
            df["MA200"] = close_series.rolling(200).mean()

        if BollingerBands:
            bb = BollingerBands(close=close_series, window=20)
            df["BB_upper"] = bb.bollinger_hband()
            df["BB_lower"] = bb.bollinger_lband()
        if RSIIndicator:
            df["RSI"] = RSIIndicator(close=close_series, window=14).rsi()
    return df


def render_chart(
    df: pd.DataFrame,
    title: str = "CamboAI Tactical Chart",
    show_bands: bool = True,
    show_rsi: bool = False,
    annotations: Optional[List[Dict]] = None,
):
    """
    Render a two-row chart: price with overlays + volume. Optional RSI as tooltip metric.
    annotations: list of {x: index, y: float, text: str}
    """
    if df is None or df.empty:
        raise ValueError("Dataframe is empty. Provide OHLCV df with columns: Open,High,Low,Close,Volume")

    # Ensure all OHLCV columns are 1D
    df = df.copy()
    ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in ohlcv_cols:
        if col in df.columns:
            df[col] = _safe_indicator_series(df[col])

    df = compute_indicators(df)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.72, 0.28],
        vertical_spacing=0.03,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
    )

    # Candles
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1, col=1,
    )

    # Overlays
    if "MA50" in df:
        fig.add_trace(go.Scatter(x=df.index, y=_safe_indicator_series(df["MA50"]),
                                 mode="lines", name="MA50", line=dict(color="#42a5f5")),
                      row=1, col=1)
    if "MA200" in df:
        fig.add_trace(go.Scatter(x=df.index, y=_safe_indicator_series(df["MA200"]),
                                 mode="lines", name="MA200", line=dict(color="#ab47bc")),
                      row=1, col=1)

    if show_bands and "BB_upper" in df and "BB_lower" in df:
        fig.add_trace(go.Scatter(x=df.index, y=_safe_indicator_series(df["BB_upper"]),
                                 mode="lines", name="BB Upper", line=dict(color="rgba(255,193,7,0.6)")),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=_safe_indicator_series(df["BB_lower"]),
                                 mode="lines", name="BB Lower", line=dict(color="rgba(255,193,7,0.6)")),
                      row=1, col=1)

    # Volume
    fig.add_trace(
        go.Bar(x=df.index, y=df.get("Volume", pd.Series(0, index=df.index)), name="Volume", marker_color="#90caf9"),
        row=2, col=1,
    )

    # Annotations (pattern markers etc.)
    if annotations:
        for ann in annotations:
            try:
                fig.add_annotation(
                    x=ann.get("x"), y=ann.get("y", df["High"].max()), text=ann.get("text", ""),
                    showarrow=True, arrowhead=2, bgcolor="rgba(33,33,33,0.6)", font=dict(color="white"),
                    row=1, col=1,
                )
            except (KeyError, ValueError, TypeError):
                # Skip invalid annotation without failing chart
                continue

    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig
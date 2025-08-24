import talib
import pandas as pd
import plotly.graph_objects as go

def plot_price_chart(df):

    df['MA50'] = talib.SMA(df['close'], timeperiod=50)
    df['MA200'] = talib.SMA(df['close'], timeperiod=200)

    fig = go.Figure(data=[go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    )])

    fig.add_trace(go.Scatter(x=df['date'], y=df['MA50'], line=dict(color='blue'), name='MA50'))
    fig.add_trace(go.Scatter(x=df['date'], y=df['MA200'], line=dict(color='red'), name='MA200'))

    fig.update_layout(title='CamboStation Tactical Chart', xaxis_rangeslider_visible=False)
    return fig

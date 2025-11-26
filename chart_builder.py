# chart_builder.py
import plotly.graph_objs as go
import pandas as pd
from indicator import macd, rsi, supertrend, keltner_channel, zigzag, swing_high_low, stockstick

# ============================================================
#                 CHART BUILDER
# ============================================================

def build_chart(df, indicators=None, volume=True):
    """
    Build Plotly chart with multiple indicators.
    df: DataFrame with OHLCV columns
    indicators: list of indicator names to apply (str)
    volume: bool, add volume bars
    """
    indicators = indicators or []

    # Apply stockstick color
    df = stockstick(df)

    fig = go.Figure()

    # Candlestick trace
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price",
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    # Volume trace
    if volume and 'Volume' in df.columns:
        vol_scale = (df['Close'].max() - df['Close'].min()) / df['Volume'].max()
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume']*vol_scale + df['Close'].min(),
            marker_color='lightblue',
            name='Volume',
            yaxis='y2',
            customdata=df['Volume'],
            hovertemplate="Volume: %{customdata}<extra></extra>"
        ))

    # Indicators
    for ind in indicators:
        if ind.lower() == 'macd':
            df = macd(df)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='MACD Signal', line=dict(color='blue', dash='dot')))
        elif ind.lower() == 'rsi':
            df = rsi(df)
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')))
        elif ind.lower() == 'supertrend':
            df = supertrend(df)
            # color by trend
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                line=dict(color='green'),
                name='SuperTrend Up',
                visible='legendonly'
            ))
        elif ind.lower() == 'keltner':
            df = keltner_channel(df)
            fig.add_trace(go.Scatter(x=df.index, y=df['KC_Upper'], line=dict(color='red', dash='dot'), name='KC Upper'))
            fig.add_trace(go.Scatter(x=df.index, y=df['KC_Lower'], line=dict(color='green', dash='dot'), name='KC Lower'))
        elif ind.lower() == 'zigzag':
            df = zigzag(df)
            fig.add_trace(go.Scatter(x=df.index, y=df['ZigZag'], line=dict(color='black'), name='ZigZag'))
        elif ind.lower() == 'swing':
            df = swing_high_low(df)
            fig.add_trace(go.Scatter(x=df.index, y=df['Swing_High'], mode='markers', marker=dict(color='red', symbol='triangle-up'), name='Swing High'))
            fig.add_trace(go.Scatter(x=df.index, y=df['Swing_Low'], mode='markers', marker=dict(color='green', symbol='triangle-down'), name='Swing Low'))

    # Layout adjustments
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=600,
        yaxis=dict(title='Price'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, range=[df['Close'].min(), df['Close'].max()]),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Return HTML div
    return fig.to_html(full_html=False)

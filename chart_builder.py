# chart_builder.py
import plotly.graph_objs as go
import pandas as pd

def build_chart(df, indicators=None):
    """
    Build OHLC chart with volume and optional indicators.
    
    df : DataFrame with 'Open','High','Low','Close','Volume'
    indicators : dict {name: Series or DataFrame} from indicater.py
    """
    if indicators is None:
        indicators = {}

    fig = go.Figure()

    # --- Main OHLC Candlestick chart ---
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))

    # --- Overlay indicators on main chart (SMA, EMA) ---
    overlay_indicators = ['SMA5','SMA20','SMA50','SMA200','EMA5','EMA20','EMA50','EMA200']
    for ind in overlay_indicators:
        if ind in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=indicators[ind],
                mode='lines',
                name=ind,
                visible='legendonly'  # default off, toggle via legend
            ))

    # --- Volume subplot ---
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color='lightblue',
        yaxis='y2'
    ))

    # --- Subplot indicators (MACD, RSI, SuperTrend, etc.) ---
    subplots = ['MACD','MACD_signal','MACD_hist','RSI','STOCH','ADX','CCI','OBV','SuperTrend']
    for ind in subplots:
        if ind in indicators:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=indicators[ind],
                mode='lines',
                name=ind,
                visible='legendonly',
                yaxis='y3'
            ))

    # --- Layout ---
    fig.update_layout(
        xaxis=dict(domain=[0,1]),
        yaxis=dict(title='Price'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, position=0.15),
        yaxis3=dict(title='Indicators', anchor='free', overlaying='y', side='right', position=0.85),
        legend=dict(orientation='h', y=-0.2),
        margin=dict(l=50, r=50, t=50, b=100),
        height=700,
        template='plotly_white'
    )

    # --- Add HTML + JS for toggle (legend already allows visibility control) ---
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Add optional instructions
    instructions = """
    <div style="margin:10px 0;color:#555;">
        <b>Instructions:</b> Click legend items to enable/disable indicators and overlays.
    </div>
    """

    return instructions + chart_html

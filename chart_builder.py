# chart_builder.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_chart(df, indicators):
    """
    df: OHLCV DataFrame with ['Open','High','Low','Close','Volume']
    indicators: dict from indicater.py
    Returns: HTML string of Plotly chart with JS toggles
    """
    # --- Create subplots ---
    fig = make_subplots(
        rows=2 + sum(1 for k in indicators if k not in ['SMA_5','SMA_10','SMA_20','SMA_50','EMA_5','EMA_10','EMA_20','EMA_50','Volume']),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.2] + [0.2]*sum(1 for k in indicators if k not in ['SMA_5','SMA_10','SMA_20','SMA_50','EMA_5','EMA_10','EMA_20','EMA_50','Volume'])
    )

    # --- Main Candle Chart ---
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price'
    ), row=1, col=1)

    # --- Add MA/EMA overlays on main chart ---
    for key in ['SMA_5','SMA_10','SMA_20','SMA_50','EMA_5','EMA_10','EMA_20','EMA_50']:
        if key in indicators:
            fig.add_trace(go.Scatter(
                x=df.index, y=indicators[key],
                mode='lines', name=key, visible=False  # initially hidden
            ), row=1, col=1)

    # --- Volume subplot ---
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], name='Volume'
    ), row=2, col=1)

    # --- Other indicators in separate subplots ---
    row_counter = 3
    for key, series in indicators.items():
        if key in ['SMA_5','SMA_10','SMA_20','SMA_50','EMA_5','EMA_10','EMA_20','EMA_50','Volume']:
            continue
        fig.add_trace(go.Scatter(
            x=df.index, y=series,
            mode='lines', name=key, visible=False
        ), row=row_counter, col=1)
        row_counter += 1

    fig.update_layout(
        height=600 + 200*(row_counter-3),
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_rangeslider_visible=False
    )

    # --- Inject JS buttons to toggle visibility ---
    buttons = []
    for i, trace in enumerate(fig.data):
        buttons.append(dict(
            label=trace.name,
            method='restyle',
            args=['visible', [j==i for j in range(len(fig.data))]],
        ))

    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            buttons=buttons,
            showactive=True,
            x=1.02,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )]
    )

    return fig.to_html(full_html=False)

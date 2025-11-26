# chart_builder.py
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def build_chart(df, indicators=None):
    """
    df: OHLCV dataframe
    indicators: dict of indicator_name -> DataFrame
    Returns HTML string of chart
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.03,
        subplot_titles=("Price & Indicators", "Volume / Subplots")
    )

    # Main OHLC
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"
    ), row=1, col=1)

    # Default volume subplot
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], name="Volume", marker_color='lightblue'
    ), row=2, col=1)

    # Overlay indicators
    if indicators:
        for name, ind_df in indicators.items():
            if ind_df is None:
                continue
            if name.lower() in ['sma20','sma50','ema20','ema50','bb_upper','bb_middle','bb_lower','supertrend']:
                # Overlay on main chart
                for col in ind_df.columns:
                    fig.add_trace(go.Scatter(
                        x=ind_df.index, y=ind_df[col], mode='lines', name=col,
                        visible='legendonly'  # hidden by default
                    ), row=1, col=1)
            else:
                # Other indicators like MACD/RSI as subplots
                for col in ind_df.columns:
                    fig.add_trace(go.Scatter(
                        x=ind_df.index, y=ind_df[col], mode='lines', name=col,
                        visible='legendonly'
                    ), row=2, col=1)

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,
        template='plotly_dark',
        legend=dict(orientation='h', y=1.02)
    )

    # Inject JS for toggling indicators (all by legend click)
    html_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html_chart

# chart_builder.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_chart(df, indicators=None, symbol="STOCK"):
    """
    df: DataFrame with ['Open','High','Low','Close','Volume']
    indicators: dict returned from calculate_indicators
    Returns Plotly HTML div
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.02,
        subplot_titles=[f"{symbol} Price Chart", "Volume"]
    )

    # -------------------------------
    # CANDLESTICK ON MAIN CHART
    # -------------------------------
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        ),
        row=1, col=1
    )

    # -------------------------------
    # ADD MOVING AVERAGES ON MAIN CHART
    # -------------------------------
    if indicators:
        for name in ['SMA20','SMA50','EMA20','EMA50']:
            if name in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=indicators[name],
                        mode='lines',
                        name=name
                    ),
                    row=1, col=1
                )

    # -------------------------------
    # VOLUME BAR
    # -------------------------------
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Volume",
            marker_color='lightblue'
        ),
        row=2, col=1
    )

    # -------------------------------
    # ADD SUBPLOTS FOR INDICATORS
    # -------------------------------
    if indicators:
        # MACD
        if 'MACD' in indicators:
            macd = indicators['MACD']
            fig.add_trace(
                go.Scatter(x=macd.index, y=macd['MACD'], name="MACD", line=dict(color='blue')),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=macd.index, y=macd['Signal'], name="MACD Signal", line=dict(color='orange')),
                row=2, col=1
            )

        # SuperTrend as overlay
        if 'SuperTrend' in indicators:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=indicators['SuperTrend'],
                    name="SuperTrend",
                    line=dict(color='green')
                ),
                row=1, col=1
            )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig.to_html(include_plotlyjs='cdn')

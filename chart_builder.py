# chart_builder.py
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

def build_chart(data, indicators):
    """
    data: pd.DataFrame with OHLCV
    indicators: dict of series (MACD, RSI, SMA20, etc.)
    """
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.5, 0.2, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.02,
        specs=[[{"type":"candlestick"}],
               [{"type":"bar"}],
               [{"type":"scatter"}]]  # indicator plot
    )

    # --- Main candlestick ---
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        name='Candlestick'
    ), row=1, col=1)

    # --- Add MA overlays on main chart ---
    for ma_name in ['SMA20','SMA50','EMA20','EMA50']:
        if ma_name in indicators:
            fig.add_trace(go.Scatter(
                x=data.index, y=indicators[ma_name],
                mode='lines', name=ma_name,
                visible='legendonly'  # initially hidden, toggle via legend or script
            ), row=1, col=1)

    # --- Volume subplot ---
    fig.add_trace(go.Bar(
        x=data.index, y=data['Volume'],
        name='Volume', marker_color='blue'
    ), row=2, col=1)

    # --- Single indicator subplot (default empty, user selects via checkbox) ---
    for ind_name in ['MACD', 'RSI', 'Stochastic']:
        if ind_name in indicators:
            fig.add_trace(go.Scatter(
                x=data.index, y=indicators[ind_name],
                mode='lines', name=ind_name,
                visible=False  # initially hidden, toggle via script
            ), row=3, col=1)

    fig.update_layout(height=900, showlegend=True, margin=dict(l=20,r=20,t=40,b=20))

    # --- Inject script for checkbox toggle ---
    script = """
    <script>
    function applyIndicators() {
        var checkboxes = document.querySelectorAll('input.indicator-toggle');
        var update = {visible: []};
        var traces = document.querySelectorAll('g.cartesianlayer .main-svg > g');
        checkboxes.forEach(function(cb, i){
            var idx = parseInt(cb.dataset.trace);
            update.visible[idx] = cb.checked;
        });
        Plotly.restyle('chart', update);
    }
    </script>
    """
    
    # Return full HTML
    chart_html = fig.to_html(full_html=False, include_plotlyjs=True, div_id="chart")
    return chart_html + script

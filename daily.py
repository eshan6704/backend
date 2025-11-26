# daily.py
import yfinance as yf
import pandas as pd
from common import wrap_plotly_html, make_table
from indicater import calculate_indicators
from chart_builder import build_chart

def fetch_daily(symbol):
    """
    Fetch daily OHLC + volume data for the past 1 year and render as HTML chart + table
    with selectable indicators (via script in chart_builder).
    """
    yfsymbol = f"{symbol}.NS"
    try:
        # Download daily data
        df = yf.download(yfsymbol, period="1y", interval="1d").round(2)

        if df.empty:
            return f"<h1>No daily data for {symbol}</h1>"

        # Handle multilevel columns (take 0th level)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Format table HTML for last 30 rows
        table_html = make_table(df.tail(30))

        # Calculate indicators
        indicators = calculate_indicators(df)

        # Build Plotly chart with main + volume subplot + subplots for indicators
        chart_html = build_chart(df, indicators, symbol)

        # Wrap chart + table together
        full_html = wrap_plotly_html(chart_html, table_html)

        return full_html

    except Exception as e:
        return f"<h1>Error fetching daily data</h1><p>{str(e)}</p>"

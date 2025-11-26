# daily.py
import pandas as pd
import yfinance as yf
from common import format_number, format_large_number, html_card, make_table, wrap_html, clean_df
from indicater import calculate_indicators
from chart_builder import build_chart

def fetch_daily(symbol):
    """
    Fetch real daily stock data from Yahoo Finance, calculate indicators,
    build chart and table, and return full HTML.
    """
    try:
        # 1. Fetch daily OHLCV data
        yf_symbol = f"{symbol}.NS"  # NSE stocks; adjust for your exchange
        df = yf.download(yf_symbol, period="1y", interval="1d", progress=False)
        if df.empty:
            return f"<h3>No daily data found for {symbol}</h3>"

        # 2. Handle multi-level columns (take 0th level)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = clean_df(df)

        # 3. Calculate indicators
        indicators = calculate_indicators(df)

        # 4. Build Plotly chart with indicators
        chart_html = build_chart(df, indicators, symbol=symbol)

        # 5. Format table
        table_html = make_table(df)

        # 6. Wrap chart + table in card layout
        content_html = html_card(f"{symbol} Daily Data", chart_html + table_html)

        # 7. Return full HTML
        return wrap_html(content_html, title=f"{symbol} Daily Data")

    except Exception as e:
        return f"<h3>Error fetching daily data for {symbol}:</h3><pre>{e}</pre>"

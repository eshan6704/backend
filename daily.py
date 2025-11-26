# daily.py
import yfinance as yf
import pandas as pd
from indicater import calculate_indicators
from chart_builder import build_chart
from common import html_card, wrap_html

def fetch_daily(symbol):
    """
    Fetch daily stock data, compute indicators, return full HTML
    """
    try:
        df = yf.download(symbol, period='6mo', interval='1d', auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)  # flatten multi-level headers

        df.reset_index(inplace=True)
        df.rename(columns={'Date':'Datetime'}, inplace=True)
        df.set_index('Datetime', inplace=True)
        if 'Volume' not in df.columns:
            df['Volume'] = 1

        # Calculate indicators
        indicators = calculate_indicators(df)

        # Build chart
        html_chart = build_chart(df, indicators=indicators)

        return wrap_html(html_card(f"{symbol} Daily Chart", html_chart))
    except Exception as e:
        import traceback
        return wrap_html(html_card("Error", f"{e}<br><pre>{traceback.format_exc()}</pre>"))

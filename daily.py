# daily.py
import yfinance as yf
import pandas as pd
from indicater import calculate_indicators
from chart_builder import build_chart
from common import html_card, make_table, wrap_html

def fetch_daily(symbol):
    try:
        # --- Fetch historical data ---
        df = yf.download(symbol + ".NS", period="6mo", interval="1d")
        if df.empty:
            return html_card("Error", f"No daily data found for {symbol}")
        df.reset_index(inplace=True)

        # --- Calculate indicators ---
        indicators = calculate_indicators(df)

        # --- Build chart with injected checkbox script ---
        chart_html = build_chart(df, indicators)

        # --- Format table ---
        table_html = make_table(df)

        # --- Combine everything in HTML ---
        content = f"""
        <h2>{symbol} - Daily Data</h2>

        <div>
            <b>Select Indicators to Display:</b><br>
            <input type="checkbox" class="indicator-toggle" data-trace="1" checked> SMA20
            <input type="checkbox" class="indicator-toggle" data-trace="2" checked> SMA50
            <input type="checkbox" class="indicator-toggle" data-trace="3"> EMA20
            <input type="checkbox" class="indicator-toggle" data-trace="4"> EMA50
            <input type="checkbox" class="indicator-toggle" data-trace="5"> MACD
            <input type="checkbox" class="indicator-toggle" data-trace="6"> RSI
            <input type="checkbox" class="indicator-toggle" data-trace="7"> Stochastic
            <button onclick="applyIndicators()">Apply</button>
        </div>
        <br>

        {chart_html}
        <br>
        {html_card("Data Table", table_html)}
        """

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return html_card("Error", str(e))

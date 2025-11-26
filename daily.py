# daily.py
import yfinance as yf
import pandas as pd
from chart_builder import build_chart

def fetch_daily(symbol):
    yfs = f"{symbol}.NS"
    df = yf.download(yfs, period="1y", interval="1d").round(2)

    if df.empty:
        return {
            "html": f"<h1>No daily data for {symbol}</h1>",
            "data": {}
        }

    chart_html = build_chart(df)

    table_html = df.tail(30).to_html(
        classes="styled-table",
        border=0
    )

    final = f"""
    <div class="group">
        <h2>Daily Chart — {symbol}</h2>
        {chart_html}
        <h3>Last 30 Days Data</h3>
        {table_html}
    </div>
    """

    return {
        "html": final,
        "data": df.tail(30).to_dict()
    }

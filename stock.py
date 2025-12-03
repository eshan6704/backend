
import yfinance as yf
import pandas as pd

def yfinfo(symbol):

        tk = yf.Ticker(symbol + ".NS")
        return tk.info

def qresult(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.quarterly_financials
    return df
    
def result(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.financials
    return df
    
def balance(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.balance_sheet
    return df
    
def cashflow(symbol):

    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.cashflow
    return df
    
def dividend(symbol):        
    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.dividends.to_frame('Dividend')
    return df
    
def split(symbol): 
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.splits.to_frame('Split')
        return df
    
def intraday(symbol): 

        df = ticker.download(symbol + ".NS",period="1d",interval="5min").round(2)
        return df
    
def daily(symbol): 

        df = ticker.download(symbol + ".NS",period="1y",interval="1d").round(2)
        return df

# ============================
# info.py — Company Info Page
# EXACT SAME LOOK AS BEFORE
# ============================

import yfinance as yf
import pandas as pd
import traceback

from yf import yfinfo

from common import (format_number,format_large_number,make_table,html_card,html_section,html_error,clean_df,safe_get)


def fetch_info(symbol: str):
    """
    Fetch full company info and return the SAME layout you used earlier.
    Only internal code updated to use common.py helpers.
    """
    try:
        
        info = yfinfo(symbol)

        if not info:
            return html_error(f"No information found for {symbol}")

        # ===== BASIC DETAILS =====
        basic = {
            "Symbol": symbol,
            "Name": safe_get(info, "longName"),
            "Sector": safe_get(info, "sector"),
            "Industry": safe_get(info, "industry"),
            "Website": safe_get(info, "website"),
            "Employee Count": format_large_number(safe_get(info, "fullTimeEmployees")),
        }
        df_basic = pd.DataFrame(basic.items(), columns=["Field", "Value"])
        basic_html = make_table(df_basic)

        # ===== PRICE DETAILS =====
        price_info = {
            "Current Price": format_number(safe_get(info, "currentPrice")),
            "Previous Close": format_number(safe_get(info, "previousClose")),
            "Open": format_number(safe_get(info, "open")),
            "Day High": format_number(safe_get(info, "dayHigh")),
            "Day Low": format_number(safe_get(info, "dayLow")),
            "52W High": format_number(safe_get(info, "fiftyTwoWeekHigh")),
            "52W Low": format_number(safe_get(info, "fiftyTwoWeekLow")),
            "Volume": format_large_number(safe_get(info, "volume")),
            "Avg Volume": format_large_number(safe_get(info, "averageVolume")),
        }
        df_price = pd.DataFrame(price_info.items(), columns=["Field", "Value"])
        price_html = make_table(df_price)

        # ===== VALUATION METRICS =====
        valuation = {
            "Market Cap": format_large_number(safe_get(info, "marketCap")),
            "PE Ratio": format_number(safe_get(info, "trailingPE")),
            "EPS": format_number(safe_get(info, "trailingEps")),
            "PB Ratio": format_number(safe_get(info, "priceToBook")),
            "Dividend Yield": format_number(safe_get(info, "dividendYield")),
            "ROE": format_number(safe_get(info, "returnOnEquity")),
            "ROA": format_number(safe_get(info, "returnOnAssets")),
        }
        df_val = pd.DataFrame(valuation.items(), columns=["Field", "Value"])
        val_html = make_table(df_val)

        # ===== COMPANY EXTRA DETAILS =====
        extra = {
            "Beta": format_number(safe_get(info, "beta")),
            "Revenue": format_large_number(safe_get(info, "totalRevenue")),
            "Gross Margins": format_number(safe_get(info, "grossMargins")),
            "Operating Margins": format_number(safe_get(info, "operatingMargins")),
            "Profit Margins": format_number(safe_get(info, "profitMargins")),
            "Book Value": format_number(safe_get(info, "bookValue")),
        }
        df_extra = pd.DataFrame(extra.items(), columns=["Field", "Value"])
        extra_html = make_table(df_extra)

        # ========================
        # Final HTML (Same Layout)
        # ========================
        final_html = (
            html_card("Basic Information", basic_html)
            + html_card("Price Details", price_html)
            + html_card("Valuation Metrics", val_html)
            + html_card("Additional Company Data", extra_html)
        )

        return final_html

    except Exception as e:
        return html_error(f"INFO MODULE ERROR: {e}<br><pre>{traceback.format_exc()}</pre>")
# intraday.py
import yfinance as yf
import pandas as pd
from common import format_large_number, wrap_html, make_table
from chart_builder import build_chart
from yf import intraday
# ============================================================
#               INTRADAY DATA PROCESSING
# ============================================================

def fetch_intraday(symbol, indicators=None):

    try:
        # Fetch 1-day intraday 5-min interval
        df = intraday(symbol)
        if df.empty:
            return wrap_html(f"<h1>No intraday data available for {symbol}</h1>")

        # Reset MultiIndex if exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Build chart with indicators
        chart_html = build_chart(df, indicators=indicators, volume=True)

        # Format last 50 rows for table
        table_html = make_table(df.tail(50))

        # Wrap in full HTML
        full_html = wrap_html(f"{chart_html}<h2>Recent Intraday Data (last 50 rows)</h2>{table_html}",
                              title=f"Intraday Data for {symbol}")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetching intraday data for {symbol}</h1><p>{str(e)}</p>")

import yfinance as yf
import pandas as pd
import io
import requests
from  nse import daily
from datetime import datetime, timedelta
from ta_indi_pat import talib_df  # use the combined talib_df function
from common import html_card, wrap_html
def fetch_daily(symbol, source,max_rows=200):
    """
    Fetch daily OHLCV data, calculate TA-Lib indicators + patterns,
    return a single scrollable HTML table.
    """
    try:
        # --- Fetch daily data ---
        df=daily(symbol,source)

        # --- Limit rows for display ---
        df_display = df.head(max_rows)

        # --- Generate combined TA-Lib DataFrame ---
        combined_df = talib_df(df_display)

        # --- Convert to HTML table ---
        table_html = combined_df.to_html(
            classes="table table-striped table-bordered",
            index=False
        )

        # --- Wrap in scrollable div ---
        scrollable_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:600px; border:1px solid #ccc; padding:5px;">
            {table_html}
        </div>
        """

        # --- Wrap in card and full HTML ---
        content = f"""
        <h2>{symbol} - Daily Data (OHLCV + Indicators + Patterns)</h2>
        {html_card("TA-Lib Data", scrollable_html)}
        """

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
# qresult.py
import yfinance as yf
import pandas as pd
from common import make_table, wrap_html, format_large_number, html_error
from yf import qresult
def fetch_qresult(symbol):
    """
    Fetch quarterly financials for a stock symbol and return HTML
    """

    try:
 
        df = qresult(symbol)

        if df.empty:
            return wrap_html(f"<h1>No quarterly results available for {symbol}</h1>")

        # Format numeric columns
        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        # Format index (dates)
        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]

        # Convert to pretty HTML table
        table_html = make_table(df_formatted)

        # Wrap into full HTML page
        return wrap_html(table_html, title=f"{symbol} - Quarterly Results")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch quarterly results: {e}"))
# result.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error
from yf import result
def fetch_result(symbol):
    
    try:
        
        df = result(symbol)

        if df.empty:
            return wrap_html(f"<h1>No annual results available for {symbol}</h1>")

        # Format numeric columns
        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Annual Results")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch annual results: {e}"))

# balance.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error
from yf import balance
def fetch_balance(symbol):
    
    try:
        df = balance(symbol)

        if df.empty:
            return wrap_html(f"<h1>No balance sheet available for {symbol}</h1>")

        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Balance Sheet")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch balance sheet: {e}"))
# cashflow.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error
from yf import cashflow
def fetch_cashflow(symbol):
    
    try:
      
        df = cashflow(symbol)

        if df.empty:
            return wrap_html(f"<h1>No cash flow data available for {symbol}</h1>")

        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Cash Flow")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch cash flow data: {e}"))

# dividend.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error
from yf import dividend
def fetch_dividend(symbol):

    try:

        df = dividend(symbol)

        if df.empty:
            return wrap_html(f"<h1>No dividend history available for {symbol}</h1>")

        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Dividend History")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch dividend history: {e}"))
# split.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error
from yf import split
def fetch_split(symbol):
    
    try:
        
        df = split(symbol)

        if df.empty:
            return wrap_html(f"<h1>No split history available for {symbol}</h1>")

        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Split History")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch split history: {e}"))
# other.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error

def fetch_other(symbol):
    yfsymbol = symbol + ".NS"
    try:
        ticker = yf.Ticker(yfsymbol)
        df = ticker.earnings

        if df.empty:
            return wrap_html(f"<h1>No earnings data available for {symbol}</h1>")

        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Earnings")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch earnings data: {e}"))

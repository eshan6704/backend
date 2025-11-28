'''import io
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from common import html_card, wrap_html
from ta_indi_pat import talib_df
import datetime
from nse import nse_index_df


def fetch_index(max_rows=200):
    """
    Fetch NIFTY 50 (^NSEI) 1-year OHLCV data from Yahoo Finance,
    add TA-Lib indicators + candlestick patterns,
    return HTML table inside a scrollable container.
    """

    try:
        # ----------------------------------
        # Fetch NIFTY 50 data
        # ----------------------------------
        df = nse_index_df(index_name="NIFTY 50")
        
        print(df)
        if df.empty:
            return html_card("Error", "No data found for NIFTY 50 (^NSEI).")


        # ----------------------------------
        # Convert to HTML
        # ----------------------------------
        table_html = df.to_html(
            classes="table table-striped table-bordered",
            index=False
        )

        scrollable_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:650px; border:1px solid #ccc; padding:8px;">
            {table_html}
        </div>
        """

        content = f"""
        <h2>NIFTY 50 </h2>
        {html_card("Technical Analysis Table", scrollable_html)}
        """

        return wrap_html(content, title="NIFTY 50 Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
'''
import io
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from common import html_card, wrap_html
from ta_indi_pat import talib_df
import datetime
from nse import nse_index_df


def fetch_index(max_rows=200):
    """
    Fetch NIFTY 50 data using nse_index_df(),
    format each returned DataFrame into its own HTML table.
    """

    try:
        # ------------------------------------------------
        # Fetch NIFTY 50 → 4 dataframes
        # ------------------------------------------------
        df_market, df_adv, df_meta, df_data = nse_index_df(index_name="NIFTY 50")

        # Debug print
        print("MARKET DF:", df_market.shape)
        print("ADVANCE DECLINE DF:", df_adv.shape)
        print("META DF:", df_meta.shape)
        print("DATA DF:", df_data.shape)

        # ------------------------------------------------
        # Helper for HTML conversion
        # ------------------------------------------------
        def make_table(df):
            return f"""
            <div style="overflow-x:auto; overflow-y:auto; max-height:450px; border:1px solid #ccc; padding:8px; margin-bottom:18px;">
                {df.to_html(classes='table table-striped table-bordered', index=False)}
            </div>
            """

        # Convert all tables
        html_market = make_table(df_market)
        html_adv    = make_table(df_adv)
        html_meta   = make_table(df_meta)
        html_data   = make_table(df_data)

        # ------------------------------------------------
        # Final HTML layout
        # ------------------------------------------------
        content = f"""
        <h2>NIFTY 50 - Index Report</h2>

        {html_card("Market Overview", html_market)}
        {html_card("Advance / Decline", html_adv)}
        {html_card("Index Meta Information", html_meta)}
        {html_card("Daily OHLCV + Calculated Indicators", html_data)}
        """

        return wrap_html(content, title="NIFTY 50 Index Data")

    except Exception as e:
        return html_card("Error", str(e))

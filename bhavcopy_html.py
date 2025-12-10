import datetime
from nsepython import *
import pandas as pd

def safe_rename(df, mapping):
    """Rename only existing columns, ignore missing ones."""
    available = {k: v for k, v in mapping.items() if k in df.columns}
    return df.rename(columns=available)

def build_bhavcopy_html(date_str):

    # Validate date
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return "<h3>Invalid date format. Use DD-MM-YYYY.</h3>"

    try:
        df = nse_bhavcopy(date_str)
    except Exception as e:
        return f"<h3>Error fetching bhavcopy: {e}</h3>"

    try:
        print("DEBUG: Columns received ->", list(df.columns))

        # Safe rename (won’t crash if a column is missing)
        df = safe_rename(df, {
            "SYMBOL": "symbol",
            "SERIES": "series",
            "DATE1": "date",
            "PREV_CLOSE": "preclose",
            "OPEN_PRICE": "open",
            "HIGH_PRICE": "high",
            "LOW_PRICE": "low",
            "LAST_PRICE": "last",
            "CLOSE_PRICE": "close",
            "AVG_PRICE": "avgprice",
            "TTL_TRD_QNTY": "volume",
            "TURNOVER_LACS": "turnover",
            "NO_OF_TRADES": "order",
            "DELIV_QTY": "del",
            "DELIV_PER": "perdel"
        })

        # Ensure missing columns do not break calculations
        for col in ["preclose", "open", "close"]:
            if col not in df.columns:
                df[col] = 0

        # Calculations
        df["change"] = df["close"] - df["preclose"]
        df["perchange"] = (df["change"] / df["preclose"]).replace([float('inf'), -float('inf')], 0) * 100
        df["pergap"] = ((df["open"] - df["preclose"]) / df["preclose"]).replace([float('inf'), -float('inf')], 0) * 100

        # Minimal table to verify working
        return df.head().to_html(index=False)

    except Exception as e:
        return f"<h3>INTERNAL ERROR: {e}</h3>"

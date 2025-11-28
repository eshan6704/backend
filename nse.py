# ================================
# NSE Fetch Module (DF Only)
# ================================

import datetime
import pandas as pd
import time
import requests
import nsepython # Moved import here
#import nse
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)

# ---------------------------------------------------
# Helper: JSON Fetch
# ---------------------------------------------------
def fetch_data(url):
    try:
        response = session.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return None

# ---------------------------------------------------
# Clean DF
# ---------------------------------------------------
def clean_dataframe(df):
    df.columns = df.columns.str.strip()
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
    df.fillna(0.01, inplace=True)
    return df

# ---------------------------------------------------
# Bhavcopy Fetch → DataFrame
# ---------------------------------------------------
def fetch_bhavcopy_df(date):
    """Returns Cleaned Bhavcopy DF for EQ / BE / SM"""
    date_str = date.strftime("%d-%m-%Y")
    print(f"Attempting to fetch bhavcopy for date: {date_str}")

    try:
        df = nsepython.get_bhavcopy(date_str) # Direct call
        if df is None or df.empty:
            print(f"No bhavcopy data or empty DataFrame returned for {date_str}")
            return None, None

        actual_bhavcopy_date = datetime.datetime.strptime(
            df.iloc[2, 2].strip(), "%d-%b-%Y"
        ).date()

        df = clean_dataframe(df)
        df_filtered = df[df.iloc[:, 1].isin(["EQ", "BE", "SM"])]

        return df_filtered, actual_bhavcopy_date

    except Exception as e:
        print(f"An error occurred while fetching bhavcopy for {date_str}: {e}")
        return None, None

# ---------------------------------------------------
# Stock Deliverable DF (security-wise archive)
# ---------------------------------------------------
def fetch_stock_df(nse_module, stock, start, end, series="ALL"):
    """Return DF for security-wise archive (deliverable + all columns)"""

    df = nse_module.security_wise_archive(start, end, stock, series)
    if df is not None and not df.empty:
        return df
    return None

# ---------------------------------------------------
# All NSE Indices → DataFrames
# ---------------------------------------------------
def nse_indices_df():
    url = "https://www.nseindia.com/api/allIndices"
    data = fetch_data(url)
    if data is None:
        return None, None, None

    df_dates = pd.DataFrame([data["dates"]])
    df_meta = pd.DataFrame([{k: v for k, v in data.items() if k not in ["data", "dates"]}])
    df_data = pd.DataFrame(data["data"])

    return df_dates, df_meta, df_data

# ---------------------------------------------------
# Specific Index → DataFrames
# ---------------------------------------------------
def nse_index_df(index_name="NIFTY 50"):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
    data = fetch_data(url)
    if data is None:
        return None, None, None, None

    df_market = pd.DataFrame([data["marketStatus"]])
    df_adv = pd.DataFrame([data["advance"]])
    df_meta = pd.DataFrame([data["metadata"]])
    df_data = pd.DataFrame(data["data"])

    return df_market, df_adv, df_meta, df_data

# ---------------------------------------------------
# Option Chain DF (Raw CE/PE)
# ---------------------------------------------------
def fetch_option_chain_df(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    data = fetch_data(url)

    if data and "filtered" in data:
        ce_df = pd.DataFrame([r["CE"] for r in data["filtered"]["data"] if "CE" in r])
        pe_df = pd.DataFrame([r["PE"] for r in data["filtered"]["data"] if "PE" in r])
        return ce_df, pe_df

    return None, None

# ---------------------------------------------------
# Pre-open market → DataFrame
# ---------------------------------------------------
def nse_preopen_df(key="NIFTY"):
    url = f"https://www.nseindia.com/api/market-data-pre-open?key={key}"
    data = fetch_data(url)
    if data:
        return pd.DataFrame(data.get("data", []))
    return None

# ---------------------------------------------------
# FNO Quote → DataFrames
# ---------------------------------------------------
def nse_fno_df(symbol):
    payload = nsepython.nse_quote(symbol) # Direct call
    if not payload:
        return None

    # info + timestamps + volatility info
    info_keys = list(payload["info"].keys()) + [
        "fut_timestamp",
        "opt_timestamp",
        "maxVolatility",
        "minVolatility",
        "avgVolatility",
    ]

    info_values = list(payload["info"].values()) + [
        payload["fut_timestamp"],
        payload["opt_timestamp"],
        payload["underlyingInfo"]["volatility"][0]['maxVolatility'],
        payload["underlyingInfo"]["volatility"][0]['minVolatility'],
        payload["underlyingInfo"]["volatility"][0]['avgVolatility'],
    ]

    df_info = pd.DataFrame([info_values], columns=info_keys)

    df_mcap = pd.DataFrame(payload["underlyingInfo"].get("marketCap", {}))
    df_fno_list = pd.DataFrame(payload.get("allSymbol", []), columns=["FNO_Symbol"])

    # Core stock depth
    df_stock = process_stocks_df(payload["stocks"])

    return {
        "info": df_info,
        "mcap": df_mcap,
        "fno": df_fno_list,
        "stock": df_stock
    }

# ---------------------------------------------------
# Handle nested stock → DF
# ---------------------------------------------------
def process_stocks_df(data):
    """Return final merged stock DF only"""
    trade_info_list, other_info_list = [], []
    bid_ask_list = []
    stock_values = []
    trade_keys = other_keys = bidask_keys = stock_keys = None

    for i, stock in enumerate(data):
        meta = stock.pop("metadata")
        depth = stock.pop("marketDeptOrderBook")
        parent = stock

        trade_info = depth.pop("tradeInfo", {})
        other_info = depth.pop("otherInfo", {})

        trade_info_list.append(trade_info)
        other_info_list.append(other_info)

        # bid / ask
        bid_ask_row = {}
        for side in ["bid", "ask"]:
            for j, entry in enumerate(depth.get(side, []), start=1):
                bid_ask_row[f"{side}_price_{j}"] = entry.get("price")
                bid_ask_row[f"{side}_qty_{j}"] = entry.get("quantity")

        bid_ask_list.append(bid_ask_row)

        if i == 0:
            trade_keys = list(trade_info.keys())
            other_keys = list(other_info.keys())
            bidask_keys = list(bid_ask_row.keys())
            stock_keys = list(meta.keys()) + list(depth.keys()) + list(parent.keys())

        stock_values.append(
            list(meta.values()) + list(depth.values()) + list(parent.values())
        )

    df_trade = pd.DataFrame(trade_info_list, columns=trade_keys)
    df_other = pd.DataFrame(other_info_list, columns=other_keys)
    df_bidask = pd.DataFrame(bid_ask_list, columns=bidask_keys)
    df_stock = pd.DataFrame(stock_values, columns=stock_keys)

    df_stock = df_stock.drop(columns=['bid', 'ask', 'carryOfCost'], errors="ignore")

    return pd.concat([df_stock, df_trade, df_other, df_bidask], axis=1)




date = datetime.date(2025, 11, 27) # Trying a past date where data is likely available

df = nse_preopen_df("NIFTY")
df_bhav, act_date = fetch_bhavcopy_df(date)
df_ce, df_pe = fetch_option_chain_df("NIFTY")
df_m, df_a, df_meta, df_data = nse_index_df("NIFTY 50")

fno = nse_fno_df("RELIANCE")
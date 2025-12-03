import requests
import pandas as pd
from datetime import datetime

# ================================
# NSE Base Settings
# ================================
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Persistent session
session = requests.Session()
session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=5)


# ================================
# Helper: Convert DataFrame to HTML
# ================================
def _to_html(title, df):
    if df is None or df.empty:
        return f"<h3>{title}</h3><p>No data available</p>"
    return f"<h3>{title}</h3>" + df.to_html(index=False, border=1)


# ================================
# Helper: Perform GET request
# ================================
def _get_json(url):
    try:
        r = session.get(url, headers=NSE_HEADERS, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ================================
# 1. Stock Quote
# ================================
def nse_stock(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching stock: {data['error']}</p>"

    info = pd.json_normalize(data.get("info", {}))
    price = pd.json_normalize(data.get("priceInfo", {}))
    meta = pd.json_normalize(data.get("metadata", {}))

    html = ""
    html += _to_html("Stock Info", info)
    html += _to_html("Price Info", price)
    html += _to_html("Metadata", meta)
    return html


# ================================
# 2. F&O / Option Chain
# ================================
def nse_fno(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching FNO: {data['error']}</p>"

    records = data.get("records", {})
    all_data = pd.DataFrame(records.get("data", []))

    ce_list = [x["CE"] for x in records.get("data", []) if "CE" in x]
    pe_list = [x["PE"] for x in records.get("data", []) if "PE" in x]

    df_ce = pd.DataFrame(ce_list)
    df_pe = pd.DataFrame(pe_list)

    html = ""
    html += _to_html("F&O Combined", all_data)
    html += _to_html("CALL Options (CE)", df_ce)
    html += _to_html("PUT Options (PE)", df_pe)
    return html


# ================================
# 3. Futures Data
# ================================
def nse_future(symbol):
    url = f"https://www.nseindia.com/api/quote-derivative?symbol={symbol.upper()}"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching futures: {data['error']}</p>"

    futures = pd.DataFrame(data.get("stocks", []))
    meta = pd.json_normalize(data.get("info", {}))

    html = ""
    html += _to_html("Futures Data", futures)
    html += _to_html("Metadata", meta)
    return html


# ================================
# 4. 52-Week High / Low
# ================================
def nse_high_low():
    url = "https://www.nseindia.com/api/market-data-52Week"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching high-low: {data['error']}</p>"

    high = pd.DataFrame(data.get("FiftyTwoWeekHigh", []))
    low = pd.DataFrame(data.get("FiftyTwoWeekLow", []))

    html = ""
    html += _to_html("52 Week High", high)
    html += _to_html("52 Week Low", low)
    return html


# ================================
# 5. Bhavcopy (date format flexible)
# ================================
def nse_bhav(date_str):
    """
    date_str: DD-MM-YYYY, DD/MM/YYYY, or DDMMYYYY
    """
    try:
        if "-" in date_str:
            dt = datetime.strptime(date_str, "%d-%m-%Y")
        elif "/" in date_str:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
        elif len(date_str) == 8:
            dt = datetime.strptime(date_str, "%d%m%Y")
        else:
            return f"<p>Invalid date format: {date_str}</p>"
    except Exception as e:
        return f"<p>Error parsing date: {e}</p>"

    date_api = dt.strftime("%d-%m-%Y")
    url = f"https://www.nseindia.com/api/reports?archives=true&date={date_api}&type=equities&mode=single"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching bhavcopy: {data['error']}</p>"

    df = pd.DataFrame(data.get("data", []))
    return _to_html(f"Bhavcopy {date_api}", df)


# ================================
# 6. All NSE Indices
# ================================
def nse_indices():
    url = "https://www.nseindia.com/api/allIndices"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching indices: {data['error']}</p>"

    df = pd.DataFrame(data.get("data", []))
    return _to_html("All NSE Indices", df)


# ================================
# 7. NSE Open Market Data
# ================================
def nse_open(index_name="NIFTY 50"):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching open data: {data['error']}</p>"

    meta = pd.json_normalize(data.get("metadata", {}))
    df = pd.DataFrame(data.get("data", []))

    html = ""
    html += _to_html("Index Metadata", meta)
    html += _to_html("Index Open Data", df)
    return html


# ================================
# 8. NSE Pre-Open Market Data
# ================================
def nse_preopen(index_name="NIFTY 50"):
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"
    data = _get_json(url)

    if "error" in data:
        return f"<p>Error fetching preopen: {data['error']}</p>"

    df = pd.DataFrame(data.get("data", []))
    meta = pd.json_normalize(data.get("metadata", {}))

    html = ""
    html += _to_html("Pre-Open Metadata", meta)
    html += _to_html("Pre-Open Market Data", df)
    return html

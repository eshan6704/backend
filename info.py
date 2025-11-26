# info.py
import yfinance as yf
from common import format_large_number, format_timestamp_to_date

def fetch_info(symbol):
    STYLE_BLOCK = """
    <style>
    .styled-table {
      border-collapse: collapse;
      margin: 10px 0;
      font-size: 0.9em;
      font-family: sans-serif;
      width: 100%;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .styled-table th, .styled-table td {
      padding: 8px 10px;
      border: 1px solid #ddd;
    }
    .styled-table tbody tr:nth-child(even) {
      background-color: #f9f9f9;
    }
    .card {
      display: block;
      width: 95%;
      margin: 10px auto;
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      background: #fafafa;
    }
    .card-category-title {
      font-size: 1.1em;
      color: #222;
      margin: 0 0 8px;
      border-bottom: 1px solid #eee;
      padding-bottom: 5px;
    }
    .card-content-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
    }
    .key-value-pair {
      flex: 1 1 calc(20% - 15px);
      box-sizing: border-box;
      min-width: 150px;
      background: #fff;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .key-value-pair h3 {
      font-size: 0.95em;
      color: #444;
      margin: 0 0 5px 0;
      border-bottom: none;
      padding-bottom: 0;
    }
    .key-value-pair p {
      font-size: 0.9em;
      color: #555;
      margin: 0;
      font-weight: bold;
    }
    .big-box {
      width:95%;
      margin:20px auto;
      padding:20px;
      border:1px solid #ccc;
      border-radius:8px;
      background:#fff;
      box-shadow:0 2px 8px rgba(0,0,0,0.1);
      font-size:0.95em;
      line-height:1.4em;
      max-height:400px;
      overflow-y:auto;
    }
    </style>
    """

    yfsymbol = symbol + ".NS"
    content_html = "<h1>No info available</h1>"

    try:
        ticker = yf.Ticker(yfsymbol)
        info = ticker.info

        if info:
            long_summary = info.pop("longBusinessSummary", None)
            officers = info.pop("companyOfficers", None)

            info_categories = {
                "Company Overview": [
                    "longName", "symbol", "exchange", "quoteType", "sector", "industry",
                    "fullTimeEmployees", "website", "address1", "city", "state", "zip", "country", "phone"
                ],
                "Valuation Metrics": [
                    "marketCap", "enterpriseValue", "trailingPE", "forwardPE", "pegRatio",
                    "priceToSalesTrailing12Months", "enterpriseToRevenue", "enterpriseToEbitda"
                ],
                "Key Financials": [
                    "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage", "twoHundredDayAverage",
                    "trailingAnnualDividendRate", "trailingAnnualDividendYield", "dividendRate", "dividendYield",
                    "exDividendDate", "lastSplitFactor", "lastSplitDate", "lastDividendValue", "payoutRatio",
                    "beta", "sharesOutstanding", "impliedSharesOutstanding"
                ],
                "Operational Details": [
                    "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk", "overallRisk",
                    "governanceEpochDate", "compensationAsOfEpochDate"
                ],
                "Trading Information": [
                    "open", "previousClose", "dayLow", "dayHigh", "volume", "averageVolume", "averageVolume10days",
                    "fiftyTwoWeekChange", "SandP52WeekChange", "currency", "regularMarketDayLow",
                    "regularMarketDayHigh", "regularMarketOpen", "regularMarketPreviousClose",
                    "regularMarketPrice", "regularMarketVolume", "regularMarketChange", "regularMarketChangePercent"
                ],
                "Analyst & Target": [
                    "targetMeanPrice", "numberOfAnalystOpinions", "recommendationKey", "recommendationMean"
                ]
            }

            categorized_html = ""
            for category_name, keys in info_categories.items():
                category_html = ""
                for key in keys:
                    if key in info and info[key] not in [None, []]:
                        value = info[key]
                        if key in ["exDividendDate","lastSplitDate","governanceEpochDate","compensationAsOfEpochDate"]:
                            value = format_timestamp_to_date(value)
                        elif key in ["marketCap","enterpriseValue","fullTimeEmployees","volume","averageVolume","averageVolume10days","sharesOutstanding","impliedSharesOutstanding","regularMarketVolume"]:
                            value = format_large_number(value)
                        elif isinstance(value,(int,float)):
                            if 'percent' in key.lower() or 'ratio' in key.lower() or 'yield' in key.lower() or 'beta' in key.lower() or 'payoutratio' in key.lower():
                                value = f"{value:.2%}"
                            elif 'price' in key.lower() or 'dividend' in key.lower() or 'average' in key.lower():
                                value = f"{value:.2f}"
                            else:
                                value = f"{value:,.0f}"
                        category_html += f"<div class='key-value-pair'><h3>{key.replace('_',' ').title()}</h3><p>{value}</p></div>"

                if category_html:
                    categorized_html += f"<h2 class='card-category-title'>{category_name}</h2><div class='card'><div class='card-content-grid'>{category_html}</div></div>"

            extra_sections = ""
            if long_summary:
                extra_sections += f"<div class='big-box'><h2>Business Summary</h2><p>{long_summary}</p></div>"

            if officers:
                officer_rows = "".join(
                    f"<tr><td>{o.get('name','')}</td><td>{o.get('title','')}</td><td>{o.get('age','')}</td></tr>"
                    for o in officers
                )
                officer_table = f"<table class='styled-table'><tr><th>Name</th><th>Title</th><th>Age</th></tr>{officer_rows}</table>"
                extra_sections += f"<div class='big-box'><h2>Company Officers</h2>{officer_table}</div>"

            content_html = f"{categorized_html}{extra_sections}"

    except Exception as e:
        content_html = f"<h1>Error</h1><p>{e}</p>"

    return f"<!DOCTYPE html><html><head>{STYLE_BLOCK}</head><body>{content_html}</body></html>"

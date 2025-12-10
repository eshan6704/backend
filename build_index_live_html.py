from nsepython import *
import pandas as pd

def build_index_live_html(name=""):
    # fetch live index data
    p = nse_index_live(name)

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    # split main / constituents
    if full_df.empty:
        main_df = pd.DataFrame()
        const_df = pd.DataFrame()
    else:
        main_df = full_df.iloc[[0]]
        const_df = full_df.iloc[1:]
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]    # remove first column

    # HTML tables (main sections)
    rem_html   = rem_df.to_html(index=False, escape=False)
    main_html  = main_df.to_html(index=False, escape=False)
    cons_html  = const_df.to_html(index=False, escape=False)

    # Compact metric list
    metric_cols = [
        "change", "totalTradedValue", "nearWKH", "nearWKL",
        "perChange365d", "perChange30d", "listingDate"
    ]

    metric_tables = ""

    # Build a table for each metric (symbol + metric)
    for col in metric_cols:
        if col not in full_df.columns:
            continue

        small_df = full_df[["symbol", col]].copy()
        table_html = small_df.to_html(index=False)

        metric_tables += f"""
        <div class="small-table">
            <h4>symbol vs {col}</h4>
            {table_html}
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
body {{
    font-family: Arial;
    margin: 15px;
    background: #f5f5f5;
}}

h2, h3 {{
    font-weight: 600;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
}}

th, td {{
    border: 1px solid #bbb;
    padding: 6px 8px;
    text-align: left;
}}

th {{
    background: #333;
    color: white;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 20px;
}}

.small-table table {{
    width: 100%;
}}

.small-table h4 {{
    margin: 5px 0;
    font-size: 16px;
}}
</style>
</head>

<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<h3>Index Info (rem)</h3>
{rem_html}

<h3>Main Data (first row)</h3>
{main_html}

<h3>Constituents</h3>
{cons_html}

<h3>Compact Metric Tables (symbol vs metric)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""
    return html

from nsepython import *
import pandas as pd

def build_index_live_html(name=""):
    # Fetch live data
    p = nse_index_live(name)

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    # Split main + constituents
    if full_df.empty:
        main_df = pd.DataFrame()
        const_df = pd.DataFrame()
    else:
        main_df = full_df.iloc[[0]]                     # first row
        const_df = full_df.iloc[1:]                    # remaining rows
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]            # remove first column

    # Convert to HTML tables
    rem_html   = rem_df.to_html(index=False, escape=False)
    main_html  = main_df.to_html(index=False, escape=False)
    const_html = const_df.to_html(index=False, escape=False)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ 
    font-family: Arial; 
    margin:15px; 
    background:#f5f5f5; 
}}

h2, h3 {{
    font-weight: 600;
}}

.table-container {{
    width: 100%;
    overflow-x: auto;      /* Horizontal scroll for wide tables */
    border: 1px solid #ccc;
    background: white;
    padding: 10px;
    margin-bottom: 25px;
}}

table {{
    border-collapse: collapse;
    width: max-content;    /* Prevent squeezing */
}}

th, td {{
    border:1px solid #bbb;
    padding:6px 8px;
    text-align:left;
    white-space: nowrap;   /* Prevent wrapping */
}}

th {{
    background:#333; 
    color:white; 
}}
</style>
</head>

<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<h3>Index Info (rem)</h3>
<div class="table-container">
{rem_html}
</div>

<h3>Main Data (first row)</h3>
<div class="table-container">
{main_html}
</div>

<h3>Constituents (remaining rows)</h3>
<div class="table-container">
{const_html}
</div>

</body>
</html>
"""
    return html

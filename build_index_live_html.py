'''
from nsepython import *
import pandas as pd

def build_index_live_html(name=""):
    p = nse_index_live(name)

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    if full_df.empty:
        main_df = pd.DataFrame()
        const_df = pd.DataFrame()
    else:
        main_df = full_df.iloc[[0]]
        const_df = full_df.iloc[1:]           # Constituents
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]   # Remove first column

    rem_html  = rem_df.to_html(index=False, escape=False)
    main_html = main_df.to_html(index=False, escape=False)
    cons_html = const_df.to_html(index=False, escape=False)

    # ==========================================================
    # METRICS WITH TOP 20 UPSIDE + TOP 20 DOWNSIDE
    # ==========================================================

    metric_cols = [
        "pChange", "totalTradedValue", "nearWKH", "nearWKL",
        "perChange365d", "perChange30d", "listingDate"
    ]

    metric_tables = ""

    for col in metric_cols:
        if col not in const_df.columns:
            continue

        df_const = const_df.copy()
        df_const[col] = pd.to_numeric(df_const[col], errors="ignore")

        # Top 20 Upside
        df_up = df_const[["symbol", col]].dropna().sort_values(col, ascending=False).head(20)
        tbl_up = df_up.to_html(index=False)

        # Top 20 Downside
        df_down = df_const[["symbol", col]].dropna().sort_values(col, ascending=True).head(20)
        tbl_down = df_down.to_html(index=False)

        metric_tables += f"""
        <div class="small-table">

            <div class="st-title">{col}</div>

            <div class="sub-title up">Top 20 Upside</div>
            <div class="st-body">{tbl_up}</div>

            <div class="sub-title down">Top 20 Downside</div>
            <div class="st-body">{tbl_down}</div>

        </div>
        """

    # ==========================================================
    # FINAL HTML
    # ==========================================================

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

h2, h3 {{
    font-weight: 600;
}}

/* GRID LAYOUT */
.grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin-top: 20px;
}}

.small-table {{
    background: white;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
    border: 1px solid #ddd;
}}

.st-title {{
    font-size: 15px;
    text-align: center;
    margin-bottom: 10px;
    font-weight: bold;
    background: #222;
    color: white;
    padding: 6px 0;
    border-radius: 4px;
}}

.sub-title {{
    margin-top: 10px;
    font-weight: bold;
    text-align: center;
    padding: 5px;
    border-radius: 4px;
    font-size: 13px;
    color: white;
}}

.sub-title.up {{
    background: #0a4;   /* Green */
}}

.sub-title.down {{
    background: #c22;   /* Red */
}}

.small-table table {{
    width: 100%;
    font-size: 12px;
    border: none;
}}

.small-table th {{
    background: #444;
    color: white;
    padding: 4px;
    font-size: 12px;
}}

.small-table td {{
    padding: 4px;
    border: 1px solid #ccc;
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

<h3>Metric Tables (Top 20 Upside / Downside)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""

    return html
'''
from nsepython import *
import pandas as pd

def build_index_live_html(name=""):
    p = nse_index_live(name)

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    if full_df.empty:
        main_df = pd.DataFrame()
        const_df = pd.DataFrame()
    else:
        main_df = full_df.iloc[[0]]
        const_df = full_df.iloc[1:]  # Constituents
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]  # Remove first column
            # Default sort constituents by pChange descending if exists
            if 'pChange' in const_df.columns:
                const_df['pChange'] = pd.to_numeric(const_df['pChange'], errors='coerce')
                const_df = const_df.sort_values('pChange', ascending=False)

    # ================= HELPER FUNCTION: COLOR-CODE NUMERIC =================
    def df_to_html_color(df):
        df_html = df.copy()
        for col in df_html.columns:
            if pd.api.types.is_numeric_dtype(df_html[col]):
                df_html[col] = df_html[col].apply(
                    lambda x: f'<span class="numeric-positive">{x}</span>' if x > 0 else
                              f'<span class="numeric-negative">{x}</span>' if x < 0 else str(x)
                )
        return df_html.to_html(index=False, escape=False, classes="compact-table")

    rem_html  = df_to_html_color(rem_df)
    main_html = df_to_html_color(main_df)
    cons_html = df_to_html_color(const_df)

    # ================= METRIC TABLES =================
    metric_cols = [
        "pChange", "totalTradedValue", "nearWKH", "nearWKL",
        "perChange365d", "perChange30d", "listingDate"
    ]

    metric_tables = ""
    for col in metric_cols:
        if col not in const_df.columns:
            continue

        df_const = const_df.copy()
        df_const[col] = pd.to_numeric(df_const[col], errors="ignore")

        # Top 20 Upside
        df_up = df_const[["symbol", col]].dropna().sort_values(col, ascending=False).head(20)
        df_up_html = df_to_html_color(df_up)

        # Top 20 Downside
        df_down = df_const[["symbol", col]].dropna().sort_values(col, ascending=True).head(20)
        df_down_html = df_to_html_color(df_down)

        metric_tables += f"""
        <div class="small-table">
            <div class="st-title">{col}</div>
            <div class="sub-title up">Top 20 Upside</div>
            <div class="st-body">{df_up_html}</div>
            <div class="sub-title down">Top 20 Downside</div>
            <div class="st-body">{df_down_html}</div>
        </div>
        """

    # ================= FINAL HTML =================
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
body {{
    font-family: Arial;
    margin: 8px;
    background: #f5f5f5;
    color: #222;
}}

h2, h3 {{
    margin: 8px 0 4px 0;
    font-weight: 600;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th, td {{
    border: 1px solid #bbb;
    padding: 3px 5px;
    text-align: left;
    font-size: 11px;
}}

th {{
    background: #333;
    color: white;
    font-weight: 600;
}}

.compact-table td.numeric-positive {{
    color: green;
    font-weight: bold;
}}
.compact-table td.numeric-negative {{
    color: red;
    font-weight: bold;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 12px;
}}

.small-table {{
    background: white;
    border-radius: 6px;
    padding: 6px;
    box-shadow: 0px 1px 4px rgba(0,0,0,0.15);
    border: 1px solid #ddd;
    overflow: auto;
}}

.st-title {{
    font-size: 13px;
    text-align: center;
    margin-bottom: 4px;
    font-weight: bold;
    background: #222;
    color: white;
    padding: 3px 0;
    border-radius: 4px;
}}

.sub-title {{
    margin-top: 4px;
    font-weight: bold;
    text-align: center;
    padding: 2px;
    border-radius: 4px;
    font-size: 11px;
    color: white;
}}

.sub-title.up {{
    background: #0a4;
}}

.sub-title.down {{
    background: #c22;
}}

.st-body {{
    max-height: 200px;
    overflow: auto;
}}

.compact-container {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}}

.compact-section {{
    background: white;
    padding: 5px;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    border: 1px solid #ddd;
    flex: 1;
    min-width: 220px;
    max-width: 48%;
    margin-bottom: 8px;
    overflow-x: auto;
}}
</style>
</head>
<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<div class="compact-container">
    <div class="compact-section">
        <h3>Index Info</h3>
        {rem_html}
    </div>
    <div class="compact-section">
        <h3>Main Data</h3>
        {main_html}
    </div>
    <div class="compact-section" style="flex-basis:100%;">
        <h3>Constituents</h3>
        {cons_html}
    </div>
</div>

<h3>Metric Tables (Top 20 Upside / Downside)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""
    return html

from nsepython import *
import pandas as pd
import json

def build_index_live_html(name):
    # Make sure to pass the name
    p = nse_index_live(name)

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    if full_df.empty:
        main_df = pd.DataFrame()
        cons_df = pd.DataFrame()
    else:
        main_df = full_df.iloc[[0]]
        cons_df = full_df.iloc[1:] if len(full_df) > 1 else pd.DataFrame()

    rem_json  = json.dumps(rem_df.to_dict(orient="records"), ensure_ascii=False)
    main_json = json.dumps(main_df.to_dict(orient="records"), ensure_ascii=False)
    cons_json = json.dumps(cons_df.to_dict(orient="records"), ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
/* ... your CSS here ... */
</style>
</head>
<body>
<h2>{name} — Live Index Data</h2>
<!-- REM, MAIN, CONS TABLES -->
<div class="section">
    <h3>Index Info</h3>
    <button onclick="toggle('remTable')">Show / Hide</button>
    <table id="remTable"></table>
</div>
<div class="section">
    <h3>Main Index Data</h3>
    <button onclick="toggle('mainTable')">Show / Hide</button>
    <table id="mainTable"></table>
</div>
<div class="section">
    <h3>Constituent Stocks</h3>
    <div class="filter-box">
        <label>Filter by Column:</label>
        <select id="filterCol"></select>
        <label>Value:</label>
        <select id="filterVal"></select>
        <button onclick="applyFilter()">Apply</button>
        <button onclick="resetFilter()">Reset</button>
    </div>
    <button onclick="toggle('consTable')">Show / Hide</button>
    <table id="consTable"></table>
</div>
<script>
const remData  = {rem_json};
const mainData = {main_json};
const consData = {cons_json};
let consFiltered = [...consData];

function toggle(id) {{
    const t = document.getElementById(id);
    t.style.display = t.style.display === "none" ? "table" : "none";
}}

function fillTable(id, rows) {{
    const table = document.getElementById(id);
    if (!rows.length) {{
        table.innerHTML = "<tr><td>No data</td></tr>";
        return;
    }}
    let keys = Object.keys(rows[0]);
    let thead = "<tr>";
    keys.forEach(k => thead += `<th>${{k}}</th>`);
    thead += "</tr>";
    let tbody = "";
    rows.forEach(r => {{
        tbody += "<tr>";
        keys.forEach(k => tbody += `<td>${{r[k]}}</td>`);
        tbody += "</tr>";
    }});
    table.innerHTML = thead + tbody;
}}

fillTable("remTable", remData);
fillTable("mainTable", mainData);
fillTable("consTable", consFiltered);

// Filter dropdown logic
const filterCol = document.getElementById("filterCol");
const filterVal = document.getElementById("filterVal");

function loadFilterOptions() {{
    if (!consData.length) return;
    let keys = Object.keys(consData[0]);
    filterCol.innerHTML = "";
    keys.forEach(k => filterCol.innerHTML += `<option>${{k}}</option>`);
    updateValues();
}}
function updateValues() {{
    let col = filterCol.value;
    let setVals = [...new Set(consData.map(r => r[col]))];
    filterVal.innerHTML = "";
    setVals.forEach(v => filterVal.innerHTML += `<option>${{v}}</option>`);
}}
filterCol.onchange = updateValues;
loadFilterOptions();

function applyFilter() {{
    let col = filterCol.value;
    let val = filterVal.value;
    consFiltered = consData.filter(r => String(r[col]) === String(val));
    fillTable("consTable", consFiltered);
}}
function resetFilter() {{
    consFiltered = [...consData];
    fillTable("consTable", consFiltered);
}}
</script>
</body>
</html>"""
    return html

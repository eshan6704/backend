import json
import pandas as pd
from nsepython import *
def build_indices_html():

    p=indices()

    data_df = p["data"]
    dates_df = p["dates"]

    # Convert to JSON for JS
    data_json = json.dumps(data_df.to_dict(orient="records"), ensure_ascii=False)
    dates_json = json.dumps(dates_df.to_dict(orient="records"), ensure_ascii=False)

    DEFAULT_KEY = "INDICES ELIGIBLE IN DERIVATIVES"
    DEFAULT_SYMBOL = "NIFTY 50"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NSE Indices Dashboard</title>

<style>
body {{
    font-family: Arial, sans-serif;
    padding: 20px;
}}
.scroll-table {{
    width: 100%;
    overflow: auto;
    border: 1px solid #ccc;
    max-height: 450px;
    margin-bottom: 20px;
}}
table {{
    border-collapse: collapse;
    width: max-content;
    min-width: 100%;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    white-space: nowrap;
}}
th {{
    background-color: #007bff;
    color: white;
    position: sticky;
    top: 0;
    z-index: 5;
}}
#datesTable {{
    margin-bottom: 25px;
    width: max-content;
    border: 1px solid #ccc;
}}

.chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 200px 200px;
    gap: 20px;
    width: 100%;
}}

.chart-box {{
    width: 100%;
    height: 100%;
    border: 1px solid #ccc;
}}

#chart365 {{
    grid-column: 1 / 3;
}}

select {{
    padding: 6px;
    margin: 8px 0;
}}
</style>

</head>
<body>

<h2>NSE Indices Dashboard</h2>

<!-- DATES TABLE -->
<h3>Reference Dates</h3>
<table id="datesTable"></table>

<hr>

<!-- Dropdown for Key -->
<label><b>Select Index Category:</b></label>
<select id="keyDropdown"></select>

<div id="altTableSection" class="scroll-table">
    <table id="altTable"></table>
</div>

<hr>

<!-- Dropdown for Charts -->
<label><b>Select Index for Charts:</b></label>
<select id="chartDropdown"></select>

<div class="chart-grid">
    <iframe id="chartToday" class="chart-box"></iframe>
    <iframe id="chart30" class="chart-box"></iframe>
    <iframe id="chart365" class="chart-box"></iframe>
</div>

<script>
const records = {data_json};
const dates = {dates_json};
const DEFAULT_KEY = "{DEFAULT_KEY}";
const DEFAULT_SYMBOL = "{DEFAULT_SYMBOL}";

const keyDropdown = document.getElementById("keyDropdown");
const chartDropdown = document.getElementById("chartDropdown");

// ------------------- Build Dates Table -------------------
function buildDatesTable() {{
    const table = document.getElementById("datesTable");
    const row = dates[0];
    let header = "<tr>";
    Object.keys(row).forEach(k => header += `<th>${{k}}</th>`);
    header += "</tr>";
    let body = "<tr>";
    Object.values(row).forEach(v => body += `<td>${{v}}</td>`);
    body += "</tr>";
    table.innerHTML = header + body;
}}
buildDatesTable();

// ------------------- Populate Key Dropdown -------------------
const keyList = [...new Set(records.map(r => r.key))];
keyList.forEach(k => {{
    const opt = document.createElement("option");
    opt.value = k;
    opt.textContent = k;
    if (k === DEFAULT_KEY) opt.selected = true;
    keyDropdown.appendChild(opt);
}});

// ------------------- Populate Chart Dropdown -------------------
function populateChartDropdown(keyVal) {{
    chartDropdown.innerHTML = "";
    records.filter(r => r.key === keyVal).forEach(r => {{
        const opt = document.createElement("option");
        opt.value = r.indexSymbol;
        opt.textContent = r.index;
        if (r.index === DEFAULT_SYMBOL) opt.selected = true;
        chartDropdown.appendChild(opt);
    }});
}}

// ------------------- Build Filtered Table -------------------
function buildAltTable(keyName) {{
    const table = document.getElementById("altTable");
    const div = document.getElementById("altTableSection");

    const filtered = records.filter(r => r.key === keyName);
    if (!filtered.length) {{
        table.innerHTML = "<tr><td>No Data</td></tr>";
        div.style.display = "none";
        return;
    }}

    const hiddenCols = [
        "key", "chartTodayPath", "chart30dPath", "chart365dPath",
        "date365dAgo","date30dAgo","previousDay","oneWeekAgo","oneMonthAgoVal",
        "oneWeekAgoVal","oneYearAgoVal","index","indicativeClose"
    ];

    const columns = Object.keys(filtered[0]).filter(c => !hiddenCols.includes(c));

    let header = "<tr>";
    columns.forEach(c => header += `<th>${{c}}</th>`);
    header += "</tr>";

    let rows = "";
    filtered.forEach(obj => {{
        rows += "<tr>";
        columns.forEach(c => rows += `<td>${{obj[c]}}</td>`);
        rows += "</tr>";
    }});

    table.innerHTML = header + rows;
    div.style.display = "block";
}}

// ------------------- Load Charts -------------------
function loadCharts(symbol) {{
    const row = records.find(r => r.indexSymbol === symbol);
    if (!row) return;
    document.getElementById("chartToday").src = row.chartTodayPath;
    document.getElementById("chart30").src = row.chart30dPath;
    document.getElementById("chart365").src = row.chart365dPath;
}}

// Event listeners
keyDropdown.addEventListener("change", () => {{
    const keyVal = keyDropdown.value;
    buildAltTable(keyVal);
    populateChartDropdown(keyVal);
    loadCharts(chartDropdown.value);
}});

chartDropdown.addEventListener("change", () => {{
    loadCharts(chartDropdown.value);
}});

// ------------------- Initial Load -------------------
buildAltTable(DEFAULT_KEY);
populateChartDropdown(DEFAULT_KEY);
loadCharts(records.find(r => r.index === DEFAULT_SYMBOL).indexSymbol);

</script>

</body>
</html>
"""
    return html
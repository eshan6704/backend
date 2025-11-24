import gradio as gr
import yfinance as yf

def fetch_data(symbol, req_type):
    try:
        ticker = yf.Ticker(symbol)

        if req_type.lower() == "info":
            info = ticker.info
            # Build HTML table from info dict
            rows = "".join(
                f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
                for key, value in info.items()
            )
            html_response = f"""
            <html>
              <head><title>Stock Data for {symbol}</title></head>
              <body>
                <h1>Ticker Info for {symbol}</h1>
                <table border="1" cellpadding="5" cellspacing="0">
                  {rows}
                </table>
              </body>
            </html>
            """
        else:
            # Default static response
            html_response = f"""
            <html>
              <head><title>Stock Data for {symbol}</title></head>
              <body>
                <h1>Data Request</h1>
                <p>Symbol: {symbol}</p>
                <p>Request Type: {req_type}</p>
                <p>No special handler for this request type.</p>
              </body>
            </html>
            """
    except Exception as e:
        html_response = f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"

    return html_response


iface = gr.Interface(
    fn=fetch_data,
    inputs=[
        gr.Textbox(label="Stock Symbol", value="PNB"),
        gr.Textbox(label="Request Type", value="info")
    ],
    outputs=gr.HTML(label="Collected Stock Data"),
    title="Stock Data API (Full)",
    description="Fetch data from NSE and yfinance",
    api_name="fetch_data"
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)

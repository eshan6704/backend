import datetime

def fetch_bhavcopy_html(date_str):
    """
    Use existing nse_bhavcopy function to fetch Bhavcopy and return HTML.
    """
    # Validate date format
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return "<h3>Invalid date format. Please use DD-MM-YYYY.</h3>"

    # Fetch data using your existing function
    try:
        df = nse_bhavcopy(date_str)
        # Convert to HTML and wrap scrollable
        return wrap(df)
    except Exception:
        return f"<h3>No Bhavcopy found for {date_str}. Please check the date.</h3>"

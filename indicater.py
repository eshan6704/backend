# indicater.py
import pandas as pd
import numpy as np
import talib as ta

# -------------------------------
# CUSTOM INDICATOR FUNCTIONS
# -------------------------------

def supertrend(df, period=10, multiplier=3):
    """
    Simple SuperTrend calculation.
    Returns a Series aligned with df.index
    """
    atr = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=period)
    hl2 = (df['High'] + df['Low']) / 2
    final_upperband = hl2 + multiplier * atr
    final_lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index, dtype=float)
    trend = True
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > final_upperband.iloc[i-1]:
            trend = True
        elif df['Close'].iloc[i] < final_lowerband.iloc[i-1]:
            trend = False
        st.iloc[i] = final_lowerband.iloc[i] if trend else final_upperband.iloc[i]
    return st

# -------------------------------
# MAIN INDICATOR FUNCTION
# -------------------------------

def calculate_indicators(df):
    """
    df: DataFrame with columns ['Open','High','Low','Close','Volume']
    Returns dict of indicator DataFrames or Series
    """
    indicators = {}

    if 'Close' in df.columns:
        # Moving averages on main chart
        indicators['SMA20'] = ta.SMA(df['Close'], timeperiod=20)
        indicators['SMA50'] = ta.SMA(df['Close'], timeperiod=50)
        indicators['EMA20'] = ta.EMA(df['Close'], timeperiod=20)
        indicators['EMA50'] = ta.EMA(df['Close'], timeperiod=50)

        # MACD as sub-plot
        macd, macdsignal, macdhist = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        indicators['MACD'] = pd.DataFrame({'MACD': macd, 'Signal': macdsignal, 'Hist': macdhist}, index=df.index)

        # Bollinger Bands
        upper, middle, lower = ta.BBANDS(df['Close'], timeperiod=20)
        indicators['Bollinger'] = pd.DataFrame({'Upper': upper, 'Middle': middle, 'Lower': lower}, index=df.index)

    # SuperTrend requires High, Low, Close
    if all(x in df.columns for x in ['High', 'Low', 'Close']):
        indicators['SuperTrend'] = supertrend(df)

    return indicators

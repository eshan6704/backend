# indicater.py
import pandas as pd
import numpy as np
import talib

def calculate_indicators(df):
    """
    Calculate various indicators.
    df: OHLCV dataframe with columns: Open, High, Low, Close, Volume
    Returns dict of indicator name -> DataFrame
    """
    indicators = {}

    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume'] if 'Volume' in df else pd.Series([1]*len(df), index=df.index)

    # --- TA-Lib indicators ---
    try:
        # Moving averages
        indicators['SMA20'] = pd.DataFrame({'SMA20': talib.SMA(close, timeperiod=20)}, index=df.index)
        indicators['SMA50'] = pd.DataFrame({'SMA50': talib.SMA(close, timeperiod=50)}, index=df.index)
        indicators['EMA20'] = pd.DataFrame({'EMA20': talib.EMA(close, timeperiod=20)}, index=df.index)
        indicators['EMA50'] = pd.DataFrame({'EMA50': talib.EMA(close, timeperiod=50)}, index=df.index)

        # MACD
        macd, macdsignal, macdhist = talib.MACD(close)
        indicators['MACD'] = pd.DataFrame({'MACD': macd, 'Signal': macdsignal, 'Hist': macdhist}, index=df.index)

        # RSI
        indicators['RSI14'] = pd.DataFrame({'RSI14': talib.RSI(close, timeperiod=14)}, index=df.index)

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close)
        indicators['BB_upper'] = pd.DataFrame({'BB_upper': upper}, index=df.index)
        indicators['BB_middle'] = pd.DataFrame({'BB_middle': middle}, index=df.index)
        indicators['BB_lower'] = pd.DataFrame({'BB_lower': lower}, index=df.index)

        # ADX
        indicators['ADX14'] = pd.DataFrame({'ADX14': talib.ADX(high, low, close, timeperiod=14)}, index=df.index)
    except Exception as e:
        print("TA-Lib indicators error:", e)

    # --- Custom indicators if not in TA-Lib ---
    # SuperTrend
    indicators['SuperTrend'] = calculate_supertrend(df)

    return indicators

def calculate_supertrend(df, period=10, multiplier=3):
    """
    Basic SuperTrend calculation
    """
    hl2 = (df['High'] + df['Low']) / 2
    atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=period)
    st_upper = hl2 + multiplier * atr
    st_lower = hl2 - multiplier * atr
    supertrend = pd.Series(index=df.index, dtype=float)
    trend = True  # True = up, False = down

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = st_upper.iloc[i]
        else:
            if df['Close'].iloc[i] > supertrend.iloc[i-1]:
                trend = True
                supertrend.iloc[i] = st_lower.iloc[i]
            else:
                trend = False
                supertrend.iloc[i] = st_upper.iloc[i]
    return pd.DataFrame({'SuperTrend': supertrend}, index=df.index)

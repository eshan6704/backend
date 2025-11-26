# indicator.py
import pandas as pd
import talib
import numpy as np

def macd(df):
    """Return MACD line and signal line"""
    if 'Close' in df.columns:
        macd_line, signal, hist = talib.MACD(df['Close'])
        return pd.DataFrame({'MACD': macd_line, 'Signal': signal})
    return pd.DataFrame()

def supertrend(df, period=10, multiplier=3):
    """Custom Supertrend indicator if not in TA-Lib"""
    hl2 = (df['High'] + df['Low']) / 2
    atr = df['High'].rolling(period).max() - df['Low'].rolling(period).min()  # simplified ATR
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr
    trend = [True]  # True = uptrend
    for i in range(1, len(df)):
        if df['Close'][i] > upperband[i-1]:
            trend.append(True)
        elif df['Close'][i] < lowerband[i-1]:
            trend.append(False)
        else:
            trend.append(trend[-1])
    return pd.Series(trend, name='Supertrend')

def keltner_channel(df, period=20):
    """Return Keltner Channels"""
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    ma = typical.rolling(period).mean()
    atr = df['High'].rolling(period).max() - df['Low'].rolling(period).min()
    upper = ma + 2 * atr
    lower = ma - 2 * atr
    return pd.DataFrame({'KC_upper': upper, 'KC_lower': lower})

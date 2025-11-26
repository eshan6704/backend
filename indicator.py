# indicator.py
import pandas as pd
import numpy as np
import talib

# ============================================================
#                 TRENDING INDICATOR HELPERS
# ============================================================

def macd(df, fast=12, slow=26, signal=9):
    """Compute MACD and signal line."""
    try:
        macd_line, signal_line, hist = talib.MACD(df['Close'], fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['MACD'] = macd_line
        df['MACD_Signal'] = signal_line
    except Exception:
        # fallback
        df['MACD'] = df['Close'].ewm(span=fast).mean() - df['Close'].ewm(span=slow).mean()
        df['MACD_Signal'] = df['MACD'].ewm(span=signal).mean()
    return df

def rsi(df, period=14):
    try:
        df['RSI'] = talib.RSI(df['Close'], timeperiod=period)
    except Exception:
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
    return df

def supertrend(df, period=10, multiplier=3):
    """Compute SuperTrend indicator"""
    # ATR calculation
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    # Basic Upper and Lower Bands
    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    # SuperTrend calculation
    supertrend = [True]  # True = uptrend, False = downtrend
    final_upper = upperband.copy()
    final_lower = lowerband.copy()
    for i in range(1, len(df)):
        if df['Close'][i] > final_upper[i-1]:
            supertrend.append(True)
        elif df['Close'][i] < final_lower[i-1]:
            supertrend.append(False)
        else:
            supertrend.append(supertrend[i-1])
            if supertrend[i-1]:
                final_upper[i] = min(upperband[i], final_upper[i-1])
            else:
                final_lower[i] = max(lowerband[i], final_lower[i-1])
    df['SuperTrend'] = supertrend
    return df

def keltner_channel(df, period=20, atr_mult=2):
    """Compute Keltner Channels"""
    try:
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        ma = df['Close'].rolling(period).mean()
        df['KC_Upper'] = ma + atr_mult * atr
        df['KC_Lower'] = ma - atr_mult * atr
    except Exception:
        pass
    return df

def zigzag(df, change_pct=5):
    """Simple ZigZag based on % change"""
    zz = [df['Close'].iloc[0]]
    last_dir = 0
    for i in range(1, len(df)):
        change = (df['Close'].iloc[i] - zz[-1]) / zz[-1] * 100
        if change > change_pct:
            zz.append(df['Close'].iloc[i])
            last_dir = 1
        elif change < -change_pct:
            zz.append(df['Close'].iloc[i])
            last_dir = -1
        else:
            zz.append(np.nan)
    df['ZigZag'] = zz
    return df

def swing_high_low(df, period=5):
    """Mark swing highs and lows"""
    df['Swing_High'] = df['High'][(df['High'].rolling(period*2+1, center=True).max() == df['High'])]
    df['Swing_Low'] = df['Low'][(df['Low'].rolling(period*2+1, center=True).min() == df['Low'])]
    return df

def stockstick(df):
    """Simple stick colors for up/down"""
    df['StickColor'] = np.where(df['Close'] >= df['Open'], 'green', 'red')
    return df

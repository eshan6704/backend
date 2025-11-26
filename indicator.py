# indicator.py
import pandas as pd
import numpy as np
try:
    import talib
except ImportError:
    talib = None

# --------------------------
# MACD
# --------------------------
def macd(df):
    """Return MACD line and Signal line"""
    if 'Close' in df.columns:
        if talib:
            macd_line, signal, hist = talib.MACD(df['Close'])
            return pd.DataFrame({'MACD': macd_line, 'Signal': signal})
        else:
            # simple manual MACD
            ema12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal = macd_line.ewm(span=9, adjust=False).mean()
            return pd.DataFrame({'MACD': macd_line, 'Signal': signal})
    return pd.DataFrame()

# --------------------------
# Supertrend
# --------------------------
def supertrend(df, period=10, multiplier=3):
    """Return Supertrend as True/False series (uptrend=True)"""
    hl2 = (df['High'] + df['Low']) / 2
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    upperband = hl2 + multiplier*atr
    lowerband = hl2 - multiplier*atr

    trend = [True]  # initial trend
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i-1]:
            trend.append(True)
        elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
            trend.append(False)
        else:
            trend.append(trend[-1])
    return pd.Series(trend, name='Supertrend')

# --------------------------
# Keltner Channel
# --------------------------
def keltner_channel(df, period=20, multiplier=2):
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    ma = typical.rolling(period).mean()
    atr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1).rolling(period).mean()
    upper = ma + multiplier*atr
    lower = ma - multiplier*atr
    return pd.DataFrame({'KC_upper': upper, 'KC_lower': lower})

# --------------------------
# ZigZag
# --------------------------
def zigzag(df, pct=5):
    """Return zigzag high and low points"""
    zz_high, zz_low = [df['Close'].iloc[0]], [df['Close'].iloc[0]]
    direction = None
    for i in range(1, len(df)):
        change = (df['Close'].iloc[i] - df['Close'].iloc[i-1])/df['Close'].iloc[i-1]*100
        if direction is None:
            direction = 'up' if change > 0 else 'down'
        if direction == 'up' and change <= -pct:
            direction = 'down'
            zz_high.append(df['Close'].iloc[i-1])
        elif direction == 'down' and change >= pct:
            direction = 'up'
            zz_low.append(df['Close'].iloc[i-1])
    return pd.Series(zz_high + zz_low, name='ZigZag')

# --------------------------
# Swing High / Low
# --------------------------
def swing_high_low(df, left=2, right=2):
    highs = df['High']
    lows = df['Low']
    swing_high = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
    swing_low = lows[(lows.shift(1) > lows) & (lows.shift(-1) > lows)]
    return swing_high, swing_low

# --------------------------
# Stockstick
# --------------------------
def stockstick(df, n=5):
    """Simple stick indicator based on n-period SMA difference"""
    sma = df['Close'].rolling(n).mean()
    stick = df['Close'] - sma
    return pd.Series(stick, name='Stockstick')

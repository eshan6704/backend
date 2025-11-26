import pandas as pd
import numpy as np
import talib

def calculate_indicators(df):
    """
    Calculates all indicators and returns a dict of arrays.
    df: DataFrame with ['Open', 'High', 'Low', 'Close', 'Volume']
    """
    indicators = {}
    
    # 1. Moving averages (plotted on main chart)
    indicators['MA10'] = talib.SMA(df['Close'], timeperiod=10)
    indicators['MA50'] = talib.SMA(df['Close'], timeperiod=50)
    indicators['MA200'] = talib.SMA(df['Close'], timeperiod=200)

    # 2. MACD (subplot)
    macd, macdsignal, macdhist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    indicators['MACD'] = {'macd': macd, 'signal': macdsignal, 'hist': macdhist}

    # 3. RSI (subplot)
    indicators['RSI'] = talib.RSI(df['Close'], timeperiod=14)

    # 4. Bollinger Bands (subplot)
    upper, middle, lower = talib.BBANDS(df['Close'], timeperiod=20)
    indicators['BBANDS'] = {'upper': upper, 'middle': middle, 'lower': lower}

    # 5. SuperTrend (custom)
    indicators['SUPERTREND'] = supertrend(df, period=10, multiplier=3)

    # 6. ZigZag (custom)
    indicators['ZIGZAG'] = zigzag(df, pct=5)

    # 7. Swing High/Low (custom)
    indicators['SWING'] = swing_high_low(df, window=5)

    return indicators

# ---------------------- Custom Indicators ----------------------
def supertrend(df, period=10, multiplier=3):
    """
    Returns SuperTrend series
    """
    hl2 = (df['High'] + df['Low'])/2
    atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=period)
    final_upperband = hl2 + multiplier*atr
    final_lowerband = hl2 - multiplier*atr
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = final_upperband.iloc[i]
            direction.iloc[i] = 1
        else:
            if df['Close'].iloc[i] > supertrend.iloc[i-1]:
                direction.iloc[i] = 1
            else:
                direction.iloc[i] = -1
            supertrend.iloc[i] = final_lowerband.iloc[i] if direction.iloc[i]==1 else final_upperband.iloc[i]
    return supertrend

def zigzag(df, pct=5):
    """
    Returns ZigZag points, pct: threshold for reversal
    """
    zig = pd.Series(index=df.index, dtype=float)
    last_pivot = df['Close'].iloc[0]
    trend = 0
    for i in range(1, len(df)):
        change_pct = (df['Close'].iloc[i]-last_pivot)/last_pivot*100
        if trend>=0 and change_pct <= -pct:
            trend = -1
            last_pivot = df['Close'].iloc[i]
        elif trend<=0 and change_pct >= pct:
            trend = 1
            last_pivot = df['Close'].iloc[i]
        zig.iloc[i] = last_pivot
    return zig

def swing_high_low(df, window=5):
    """
    Returns swing high/low points
    """
    swing = pd.Series(index=df.index, dtype=float)
    for i in range(window, len(df)-window):
        if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
            swing.iloc[i] = df['High'].iloc[i]
        elif df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window+1].min():
            swing.iloc[i] = df['Low'].iloc[i]
    return swing

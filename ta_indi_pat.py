import pandas as pd
import talib
import numpy as np

def patterns(df):
    """
    Return a DataFrame of all CDL patterns with 0/1,
    preserving the original DataFrame index.
    """
    df = df.copy()
    required_cols = ['Open','High','Low','Close']

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    original_index = df.index  # preserve original index
    pattern_df = pd.DataFrame(index=original_index)

    pattern_list = [f for f in dir(talib) if f.startswith("CDL")]

    for pattern in pattern_list:
        func = getattr(talib, pattern)
        result = func(
            df['Open'].values.astype(float),
            df['High'].values.astype(float),
            df['Low'].values.astype(float),
            df['Close'].values.astype(float)
        )
        pattern_df[pattern] = (result != 0).astype(int)

    return pattern_df


def indicators(df):
    """
    Return a DataFrame of numeric TA-Lib indicators,
    preserving the original DataFrame index.
    """
    df_std = df.copy()
    df_std.columns = [c.lower() for c in df_std.columns]

    ohlcv = {
        'open': df_std.get('open'),
        'high': df_std.get('high'),
        'low': df_std.get('low'),
        'close': df_std.get('close'),
        'volume': df_std.get('volume')
    }

    indicator_list = [
        f for f in dir(talib)
        if not f.startswith("CDL") and not f.startswith("_") and f not in ["wraps", "wrapped_func"]
    ]

    df_list = []
    original_index = df.index  # preserve original index

    for name in indicator_list:
        func = getattr(talib, name)
        try:
            if ohlcv['close'] is not None:
                result = func(ohlcv['close'].values.astype(float))
            else:
                continue

            if isinstance(result, tuple):
                for i, arr in enumerate(result):
                    col_name = f"{name}_{i}"
                    temp_df = pd.DataFrame(arr, index=original_index, columns=[col_name])
                    df_list.append(temp_df)
            else:
                temp_df = pd.DataFrame(result, index=original_index, columns=[name])
                df_list.append(temp_df)
        except:
            continue

    if df_list:
        indicator_df = pd.concat(df_list, axis=1)
    else:
        indicator_df = pd.DataFrame(index=original_index)

    return indicator_df

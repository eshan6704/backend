# chart_builder.py
import plotly.graph_objs as go
from indicator import macd, supertrend, keltner_channel

def build_chart(df, indicators=None, volume=True):
    fig = go.Figure()
    # Price candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='Price'
    ))
    # Volume
    if volume:
        vol_scale = (df['Close'].max() - df['Close'].min()) / df['Volume'].max()
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume']*vol_scale + df['Close'].min(),
            name='Volume', marker_color='lightblue'
        ))

    # Indicators
    if indicators:
        for ind in indicators:
            if ind.lower() == 'macd':
                macd_df = macd(df)
                fig.add_trace(go.Scatter(x=df.index, y=macd_df['MACD'], name='MACD'))
                fig.add_trace(go.Scatter(x=df.index, y=macd_df['Signal'], name='MACD Signal'))
            elif ind.lower() == 'supertrend':
                st = supertrend(df)
                fig.add_trace(go.Scatter(x=df.index, y=st.astype(int)*df['Close'], name='Supertrend'))
            elif ind.lower() == 'keltner':
                kc = keltner_channel(df)
                fig.add_trace(go.Scatter(x=df.index, y=kc['KC_upper'], name='Keltner Upper'))
                fig.add_trace(go.Scatter(x=df.index, y=kc['KC_lower'], name='Keltner Lower'))

    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    return fig.to_html(full_html=False)

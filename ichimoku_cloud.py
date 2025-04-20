import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def ichimoku_cloud(df):
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Tenkan_sen'] = (high_9 + low_9) / 2

    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Kijun_sen'] = (high_26 + low_26) / 2

    df['Senkou_Span_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(26)

    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Senkou_Span_B'] = ((high_52 + low_52) / 2).shift(26)

    df['Chikou_Span'] = df['Close'].shift(-26)

    return df

# === Example with real data ===
ticker = 'AAPL'
data = yf.download(ticker, period='6mo', interval='1d')
df = ichimoku_cloud(data)

# === Plotting ===
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Close'], label='Close', color='black', linewidth=1)
plt.plot(df.index, df['Tenkan_sen'], label='Tenkan-sen', color='blue', linestyle='--')
plt.plot(df.index, df['Kijun_sen'], label='Kijun-sen', color='red', linestyle='--')
plt.plot(df.index, df['Chikou_Span'], label='Chikou Span', color='green')

# Cloud
plt.fill_between(df.index, df['Senkou_Span_A'], df['Senkou_Span_B'],
                 where=df['Senkou_Span_A'] >= df['Senkou_Span_B'],
                 color='lightgreen', alpha=0.5)

plt.fill_between(df.index, df['Senkou_Span_A'], df['Senkou_Span_B'],
                 where=df['Senkou_Span_A'] < df['Senkou_Span_B'],
                 color='lightcoral', alpha=0.5)

plt.title(f'Ichimoku Cloud for {ticker}')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
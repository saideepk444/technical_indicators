from ta.momentum import StochasticOscillator
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ----------------------------------------------------------
# Utility: Download Data
# ----------------------------------------------------------


def get_data(ticker, start_date, end_date):
    # Ensure that the dates are in a proper string format
    start_date = pd.to_datetime(start_date).strftime("%Y-%m-%d")
    end_date = pd.to_datetime(end_date).strftime("%Y-%m-%d")
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# ----------------------------------------------------------
# Bollinger Bands Function (Adapted from bollinger_bands_final.py :contentReference[oaicite:0]{index=0})
# ----------------------------------------------------------


def plot_bollinger_bands(df, window=20, num_sd=2):
    df = df.copy()
    df['SMA'] = df['Close'].rolling(window=window).mean()
    df['STD'] = df['Close'].rolling(window=window).std()
    df['Upper'] = df['SMA'] + num_sd * df['STD']
    df['Lower'] = df['SMA'] - num_sd * df['STD']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA'], mode='lines', name=f'{window}-day SMA'))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Upper'], mode='lines', name='Upper Band'))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Lower'], mode='lines', name='Lower Band'))
    fig.update_layout(title='Bollinger Bands',
                      xaxis_title='Date', yaxis_title='Price')
    return fig

# ----------------------------------------------------------
# Ichimoku Cloud Function (Adapted from ichimoku_cloud.py :contentReference[oaicite:1]{index=1})
# ----------------------------------------------------------


def plot_ichimoku_cloud(df):
    df = df.copy()
    df['Tenkan_sen'] = (df['High'].rolling(window=9).max() +
                        df['Low'].rolling(window=9).min()) / 2
    df['Kijun_sen'] = (df['High'].rolling(window=26).max() +
                       df['Low'].rolling(window=26).min()) / 2
    df['Senkou_Span_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(26)
    df['Senkou_Span_B'] = ((df['High'].rolling(window=52).max(
    ) + df['Low'].rolling(window=52).min()) / 2).shift(26)
    df['Chikou_Span'] = df['Close'].shift(-26)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['Close'], label='Close', color='black', linewidth=1)
    ax.plot(df.index, df['Tenkan_sen'],
            label='Tenkan-sen', color='blue', linestyle='--')
    ax.plot(df.index, df['Kijun_sen'], label='Kijun-sen',
            color='red', linestyle='--')
    ax.plot(df.index, df['Chikou_Span'], label='Chikou Span', color='green')

    # Use .fillna(False) on the boolean conditions to avoid ambiguity if there are NaNs
    ax.fill_between(
        df.index,
        df['Senkou_Span_A'],
        df['Senkou_Span_B'],
        where=(df['Senkou_Span_A'] >= df['Senkou_Span_B']).fillna(False),
        color='lightgreen',
        alpha=0.5
    )
    ax.fill_between(
        df.index,
        df['Senkou_Span_A'],
        df['Senkou_Span_B'],
        where=(df['Senkou_Span_A'] < df['Senkou_Span_B']).fillna(False),
        color='lightcoral',
        alpha=0.5
    )

    ax.set_title("Ichimoku Cloud")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig

# ----------------------------------------------------------
# MACD Function (Adapted from MACD.py :contentReference[oaicite:2]{index=2})
# ----------------------------------------------------------


def plot_macd(df):
    df = df.copy()
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['MACD'], label='MACD', color='blue')
    ax.plot(df.index, df['Signal'], label='Signal Line', color='red')
    ax.set_title("MACD")
    ax.set_xlabel("Date")
    ax.set_ylabel("MACD")
    ax.legend(loc="upper left")

    # Overlay stock price on a secondary y-axis
    ax2 = ax.twinx()
    ax2.plot(df.index, df['Close'], label='Close Price',
             color='green', alpha=0.5)
    ax2.set_ylabel("Price")
    ax2.legend(loc="upper right")
    fig.tight_layout()
    return fig

# ----------------------------------------------------------
# Stochastic Oscillator Function (Adapted from stochastic_oscillator.py :contentReference[oaicite:3]{index=3})
# ----------------------------------------------------------


def plot_stochastic_oscillator(df, window=14, smooth_k=3, smooth_d=3):
    df = df.copy()
    low_min = df["Low"].rolling(window=window).min()
    high_max = df["High"].rolling(window=window).max()
    df["stoch_k"] = 100 * (df["Close"] - low_min) / (high_max - low_min)
    df["stoch_k"] = df["stoch_k"].rolling(window=smooth_k).mean()
    df["stoch_d"] = df["stoch_k"].rolling(window=smooth_d).mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df["stoch_k"], label="%K")
    ax.plot(df.index, df["stoch_d"], label="%D", linestyle="--")
    ax.axhline(80, linestyle=":", label="Overbought (80)")
    ax.axhline(20, linestyle=":", label="Oversold (20)")
    ax.set_title("Stochastic Oscillator")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------
# RSI Function (Adapted from stock_rsi_app.py :contentReference[oaicite:4]{index=4})
# ----------------------------------------------------------


def plot_rsi(df, period=14, rsi_buy=30, rsi_sell=70):
    df = df.copy()
    # 1) price change
    delta = df['Close'].diff()

    # 2) separate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # 3) Wilder’s smoothing (EMA of gains/losses)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    # 4) relative strength, then RSI
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 5) build RSI chart
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI'))
    fig_rsi.add_hline(y=rsi_buy, line_dash='dash',
                      annotation_text='Buy', annotation_position='bottom right')
    fig_rsi.add_hline(y=rsi_sell, line_dash='dash',
                      annotation_text='Sell', annotation_position='top right')
    fig_rsi.update_layout(
        title=f'RSI ({period}-period)',
        xaxis_title='Date',
        yaxis_title='RSI'
    )

    # 6) price + signals
    df['Signal'] = 0
    df.loc[df['RSI'] < rsi_buy, 'Signal'] = 1
    df.loc[df['RSI'] > rsi_sell, 'Signal'] = -1

    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
    fig_price.add_trace(go.Scatter(
        x=df[df['Signal'] == 1].index, y=df[df['Signal'] == 1]['Close'],
        mode='markers', name='Buy', marker_symbol='triangle-up', marker_size=10
    ))
    fig_price.add_trace(go.Scatter(
        x=df[df['Signal'] == -1].index, y=df[df['Signal'] == -1]['Close'],
        mode='markers', name='Sell', marker_symbol='triangle-down', marker_size=10
    ))
    fig_price.update_layout(
        title='Price with RSI Signals',
        xaxis_title='Date',
        yaxis_title='Price'
    )

    return fig_rsi, fig_price


# ----------------------------------------------------------
# Streamlit App Layout and Tabs
# ----------------------------------------------------------
st.set_page_config(page_title="Technical Indicators Dashboard", layout="wide")
st.title("Technical Indicators Dashboard")

# Sidebar: User inputs
st.sidebar.header("User Inputs")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL")
start_date = st.sidebar.date_input(
    "Start Date", value=pd.to_datetime("2023-01-01"))
# The end date is fixed to December 31, 2023
end_date = pd.to_datetime("2023-12-31")
st.sidebar.write("End Date: December 31, 2023")

# Download data using yfinance
if ticker:
    data = get_data(ticker, start_date, end_date)
    if data.empty:
        st.error("No data found for the given ticker and date range.")
    else:
        st.write(
            f"Showing data for {ticker} from {start_date} to {end_date.date()}")

        # Create tabs for each indicator
        tabs = st.tabs(["Bollinger Bands", "Ichimoku Cloud",
                       "MACD", "Stochastic Oscillator", "RSI"])

        with tabs[0]:
            st.header("Bollinger Bands")
            fig_bb = plot_bollinger_bands(data)
            st.plotly_chart(fig_bb, use_container_width=True)

        with tabs[1]:
            st.header("Ichimoku Cloud")
            fig_ichimoku = plot_ichimoku_cloud(data)
            st.pyplot(fig_ichimoku)

        with tabs[2]:
            st.header("MACD")
            fig_macd = plot_macd(data)
            st.pyplot(fig_macd)

        with tabs[3]:
            st.header("Stochastic Oscillator")
            fig_stoch = plot_stochastic_oscillator(data)
            st.pyplot(fig_stoch, use_container_width=True)

        with tabs[4]:
            st.header("RSI")
            fig_rsi, fig_rsi_price = plot_rsi(data)
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.plotly_chart(fig_rsi_price, use_container_width=True)

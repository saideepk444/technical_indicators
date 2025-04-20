import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt

# Step 1: Fetch Apple (AAPL) Stock Data
def fetch_stock_data(ticker="AAPL", period="6mo", interval="1d"):
    """
    Fetch historical stock data from Yahoo Finance.

    :param ticker: Stock ticker symbol (e.g., "AAPL").
    :param period: Data range (e.g., "6mo" for 6 months).
    :param interval: Data interval (e.g., "1d" for daily).
    :return: DataFrame with stock price history.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# Step 2: Calculate Stochastic Oscillator
def calculate_stochastic_oscillator(data, window=14, smooth_k=3, smooth_d=3):
    """
    Compute Stochastic Oscillator for stock data.

    :param data: DataFrame with 'High', 'Low', and 'Close' prices.
    :param window: Lookback period for %K.
    :param smooth_k: Smoothing period for %K.
    :param smooth_d: Smoothing period for %D.
    :return: DataFrame with %K and %D values.
    """
    data["stoch_k"] = ta.momentum.stoch(
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        window=window,
        smooth_window=smooth_k
    )

    # %D (smoothed version of %K)
    data["stoch_d"] = data["stoch_k"].rolling(smooth_d).mean()

    return data

# Step 3: Plot the Stochastic Oscillator
def plot_stochastic_oscillator(data, ticker="AAPL"):
    """
    Plots the Stochastic Oscillator (%K and %D) for a stock.

    :param data: DataFrame with 'stoch_k' and 'stoch_d'.
    :param ticker: Stock ticker symbol.
    """
    plt.figure(figsize=(12, 6))
    
    # Plot %K line
    plt.plot(data.index, data["stoch_k"], label="%K Line", color="blue")
    
    # Plot %D line
    plt.plot(data.index, data["stoch_d"], label="%D Line", color="orange", linestyle="dashed")
    
    # Add Overbought (80) and Oversold (20) levels
    plt.axhline(80, color="red", linestyle="dotted", label="Overbought (80)")
    plt.axhline(20, color="green", linestyle="dotted", label="Oversold (20)")
    
    plt.title(f"Stochastic Oscillator for {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Stochastic Value")
    plt.legend()
    plt.grid()
    plt.show()

# Step 4: Run Everything
if __name__ == "__main__":
    # Fetch Apple stock data
    df = fetch_stock_data("AAPL")

    # Calculate the Stochastic Oscillator
    df = calculate_stochastic_oscillator(df)

    # Plot the Stochastic Oscillator
    plot_stochastic_oscillator(df)
    
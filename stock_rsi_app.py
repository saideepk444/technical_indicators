import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta

# --- Function to calculate RSI ---
def calculate_rsi(data, period=14):
    # Ensure 'Close' is a 1-dimensional Series
    close = data['Close'].squeeze()
    rsi_indicator = ta.momentum.RSIIndicator(close=close, window=period)
    data['RSI'] = rsi_indicator.rsi()
    return data

# --- Function to identify buy/sell signals based on RSI ---
def identify_signals(data, rsi_buy, rsi_sell):
    data['Signal'] = 0
    data.loc[data['RSI'] < rsi_buy, 'Signal'] = 1  # Buy
    data.loc[data['RSI'] > rsi_sell, 'Signal'] = -1  # Sell
    return data

# --- Streamlit UI ---
st.set_page_config(page_title="📈 Advanced RSI Dashboard", layout="wide")

st.title("📈 Advanced RSI Dashboard")
st.markdown("Visualize Relative Strength Index (RSI) with buy/sell signals.")

# --- Sidebar Inputs ---
ticker = st.sidebar.selectbox("Select Stock Ticker", ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA", "META"])
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2023-12-31"))

rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
rsi_buy = st.sidebar.slider("RSI Buy Threshold", 10, 50, 30)
rsi_sell = st.sidebar.slider("RSI Sell Threshold", 50, 90, 70)

# --- Data Fetch & Processing ---
if start_date >= end_date:
    st.warning("⚠️ Start date must be before end date.")
else:
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        st.warning("⚠️ No data found. Try a different date range or ticker.")
    else:
        data = calculate_rsi(data, rsi_period)
        data = identify_signals(data, rsi_buy, rsi_sell)

        # --- RSI Chart ---
        st.subheader("📊 RSI Indicator")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='orange')))
        fig_rsi.add_hline(y=rsi_buy, line=dict(color='green', dash='dash'), annotation_text="Buy Threshold", annotation_position="top left")
        fig_rsi.add_hline(y=rsi_sell, line=dict(color='red', dash='dash'), annotation_text="Sell Threshold", annotation_position="top left")

        fig_rsi.update_layout(title=f"{ticker} RSI ({rsi_period}-period)", xaxis_title="Date", yaxis_title="RSI", template="plotly_white")
        st.plotly_chart(fig_rsi, use_container_width=True)

        # --- Price Chart with Signals ---
        st.subheader("💹 Price Chart with RSI Signals")
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price", line=dict(color='black')))
        fig_price.add_trace(go.Scatter(
            x=data[data['Signal'] == 1].index,
            y=data[data['Signal'] == 1]['Close'],
            name='Buy Signal',
            mode='markers',
            marker=dict(color='green', size=10, symbol='triangle-up')
        ))
        fig_price.add_trace(go.Scatter(
            x=data[data['Signal'] == -1].index,
            y=data[data['Signal'] == -1]['Close'],
            name='Sell Signal',
            mode='markers',
            marker=dict(color='red', size=10, symbol='triangle-down')
        ))

        fig_price.update_layout(title=f"{ticker} Close Price with RSI Signals", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
        st.plotly_chart(fig_price, use_container_width=True)

        # --- Optional Data Table ---
        with st.expander("📄 Show Raw Data"):
            st.dataframe(data.tail(100))

        # --- Summary Stats ---
        st.markdown("### 📌 Signal Summary")
        st.write(f"Total Buy Signals: **{(data['Signal'] == 1).sum()}**")
        st.write(f"Total Sell Signals: **{(data['Signal'] == -1).sum()}**")

        # --- Download Option ---
        csv = data.to_csv().encode('utf-8')
        st.download_button("⬇️ Download Data as CSV", data=csv, file_name=f"{ticker}_RSI_data.csv", mime='text/csv')

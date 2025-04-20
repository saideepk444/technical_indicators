import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to calculate MACD


def calculate_macd(data):
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()  # 12-day EMA
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()   # 26-day EMA
    macd_line = short_ema - long_ema
    # 9-day EMA (Signal Line)
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

# Function to fetch stock data and update plot


def get_stock_data():
    global ax  # Declare ax as global to use it across function calls
    symbol = stock_entry.get().upper()
    start_date = start_entry.get()
    end_date = end_entry.get()

    # Create a subplot if it doesn't exist
    if 'ax' not in globals():
        fig, ax = plt.subplots(figsize=(10, 6))
        global canvas
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack()

    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            messagebox.showerror(
                "Error", "Invalid stock symbol or no data available for the selected dates.")
            return

        # Calculate MACD
        df['MACD'], df['Signal'] = calculate_macd(df)

        # Clear previous plot
        ax.clear()
        ax.plot(df.index, df['MACD'], label="MACD Line", color="blue")
        ax.plot(df.index, df['Signal'], label="Signal Line", color="red")
        ax.set_title(f"MACD for {symbol}")
        ax.set_xlabel("Date")
        ax.set_ylabel("MACD Value")
        ax.legend(loc="lower right")

        # Overlay the stock price on the MACD plot
        ax2 = ax.twinx()  # Create a secondary y-axis
        ax2.plot(df.index, df['Close'],
                 label="Stock Price", color="green", alpha=0.5)
        ax2.set_ylabel("Stock Price")
        ax2.legend(loc="upper left")

        # Update plot on UI
        canvas.draw()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Initialize main Tkinter window
root = tk.Tk()
root.title("Stock MACD Analyzer")
root.geometry("800x600")

# Frame for user inputs
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Stock Symbol:").grid(row=0, column=0, padx=5)
stock_entry = tk.Entry(frame)
stock_entry.grid(row=0, column=1, padx=5)

tk.Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
start_entry = tk.Entry(frame)
start_entry.insert(0, "2024-01-01")  # Default start date
start_entry.grid(row=0, column=3, padx=5)

tk.Label(frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=4, padx=5)
end_entry = tk.Entry(frame)
end_entry.insert(0, "2025-01-01")  # Default end date
end_entry.grid(row=0, column=5, padx=5)

tk.Button(frame, text="Get MACD", command=get_stock_data).grid(
    row=0, column=6, padx=10)

# Run the application
root.mainloop()

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

dates = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
closing_prices = [100, 102, 105, 110, 108, 109, 106, 107, 115, 110]

# Inputs to function must be separate lists of dates and their corresponding closing prices, 
# and the length of the period you wish to use for calculating SMA.
def bollinger_bands(dates, closing_prices, SMA_len, num_sd):

    SMA = []
    sd = []
    
    for i in range(len(closing_prices)):
        period = []
        period_sum = 0
        
        # fill list "period" with closing prices within the given period, and compute each
        # SMA and sd, then append to corresponding lists
        if (i - SMA_len) < 0:
            for j in range (0, i + 1):
                period.append(closing_prices[j])
                period_sum += closing_prices[j]
        else:
            for j in range (i - SMA_len, i + 1):
                period.append(closing_prices[j])
                period_sum += closing_prices[j]
        
        # calculate SMA for i and put it into SMA
        SMA.append(period_sum / len(period))

        # calculate std for i and put it into sd
        sd.append(np.std(period))

    upper_band = []
    lower_band = []

    for i in range(0, len(sd)):
        upper_band.append(SMA[i] + (num_sd * sd[i]))
        lower_band.append(SMA[i] - (num_sd * sd[i]))

    line_graph = go.Figure()

    line_graph.add_trace(go.Scatter(
        x = dates,                          # x-axis values (dates)
        y = SMA,                        # MIDDLE BAND
        mode = 'lines+markers',         # Display lines and markers
        name = 'Simple Moving Average'  # Label for the line
    ))
    line_graph.add_trace(go.Scatter(
        x = dates,                          # x-axis values (dates)
        y = upper_band,             # UPPER BAND
        mode = 'lines+markers',         # Display lines and markers
        name = 'Upper Band'             # Label for the line
    ))
    line_graph.add_trace(go.Scatter(
        x = dates,                          # x-axis values (dates)
        y = lower_band,             # LOWER BAND
        mode = 'lines+markers',         # Display lines and markers
        name = 'Lower Band'             # Label for the line
    ))

    
    # Customize layout
    line_graph.update_layout(
        title='Stock Price Over Time, with Bollinger Bands',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark'  # Optional: You can change the theme
    )

    line_graph.show()

bollinger_bands(dates, closing_prices, 2, 1)
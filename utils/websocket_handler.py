from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import sys
import os
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from indicators.bollinger_bands import BollingerBands
from indicators.rsi import RSI
from indicators.sup_res import SupportResistance
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_SECRET_KEY')

# Initialize indicators
bbands = BollingerBands(window=20, num_of_std=2)
rsi_indicator = RSI(period=14)
sup_res = SupportResistance(window=14)

# Global DataFrame to accumulate data
data_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'RSI', 'UpperBB', 'MiddleBB', 'LowerBB', 'Support', 'Resistance'])

def handle_socket_message(msg):
    global data_df # Referencing global DataFrame

    print("Message received")  # Debugging print
    sys.stdout.flush()  # Flush output buffer
    
    # Extract the candlestick data from the message
    candlestick = msg['k']
    rsi_value = None
    
    # Extracting relevant information from the candlestick data
    open_price = float(candlestick['o'])
    high_price = float(candlestick['h'])
    low_price = float(candlestick['l'])
    close_price = float(candlestick['c'])
    volume = float(candlestick['v'])
    close_time = pd.to_datetime(candlestick['T'], unit='ms')
    
    # Update indicators
    if hasattr(bbands, 'prices') and len(bbands.prices) > 0:
        previous_close = bbands.prices[-1]
        rsi_value = rsi_indicator.update(close_price, previous_close)

    upper_band, middle_band, lower_band = bbands.update(close_price)
    support, resistance = sup_res.update(high_price, low_price)

    new_data = {
        'Time': close_time,
        'Open': open_price,
        'High': high_price,
        'Low': low_price,
        'Close': close_price,
        'RSI': rsi_value if rsi_value is not None else np.nan,
        'UpperBB': upper_band,
        'MiddleBB': middle_band,
        'LowerBB': lower_band,
        'Support': support,
        'Resistance': resistance
    }

    # Efficiently append new data to DataFrame
    data_df_length = len(data_df)
    data_df.loc[data_df_length] = new_data

    # Limit DataFrame size
    max_rows = 1000
    if data_df_length > max_rows:
        data_df.drop(data_df.index[0], inplace=True)

    # Dynamic console output
    output = (
        f"Candlestick Data: Open: {new_data['Open']}, High: {new_data['High']}, Low: {new_data['Low']}, Close: {new_data['Close']}\n"
        f"RSI: {new_data['RSI']}\n"
        f"BB Data: Upper: {new_data['UpperBB']}, Middle: {new_data['MiddleBB']}, Lower: {new_data['LowerBB']}\n"
        f"Support: {new_data['Support']}, Resistance: {new_data['Resistance']}\n"
    )

    # Clear the console and print the output
    sys.stdout.write("\033[H\033[J")  # Clear screen and move to home position
    sys.stdout.write(output)
    sys.stdout.flush()  # Ensure the print is flushed to the console

# Initialize the WebSocket manager using the client
twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, tld='us')
twm.start()

# Start a WebSocket for a specific symbol and interval
stream_name = twm.start_kline_socket(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, callback=handle_socket_message)

# To keep the script running and listening for messages
try:
    while True:
        time.sleep(1)  # A less CPU-intensive loop
except KeyboardInterrupt:
    twm.stop_socket(stream_name)
    twm.join()
# Import the necessary module
# ...


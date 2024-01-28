from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time
from indicators.bollinger_bands import BollingerBands
from indicators.rsi import RSI
from indicators.sup_res import SupportResistance
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_SECRET_KEY')


# Initialize indicators
bbands = BollingerBands(window=20, num_of_std=2)
rsi_indicator = RSI(period=14)
sup_res = SupportResistance(window=14)

#client = Client(api_key, api_secret, tld='us')
# Function to handle incoming WebSocket messages for K-line data
def handle_socket_message(msg):
    print("Message received")  # Debugging print
    sys.stdout.flush()  # Flush output buffer
    
    # Extract the candlestick data from the message
    candlestick = msg['k']
    
    # Extracting relevant information from the candlestick data
    open_price = float(candlestick['o'])
    high_price = float(candlestick['h'])
    low_price = float(candlestick['l'])
    close_price = float(candlestick['c'])
    volume = float(candlestick['v'])
    close_time = pd.to_datetime(candlestick['T'], unit='ms')
    
    # Update rolling window data structures with new price data
    if hasattr(bbands, 'prices') and len(bbands.prices) > 0:
        previous_close = bbands.prices[-1]
        rsi_value = rsi_indicator.update(close_price, previous_close)
        print(f"Updated RSI: {rsi_value}")
    
    upper_band, middle_band, lower_band = bbands.update(close_price)
    support, resistance = sup_res.update(high_price, low_price)
    
    # Print updated information
    print(f"Candlestick for {close_time}: Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}")
    print(f"Updated Bollinger Bands: Upper: {upper_band}, Middle: {middle_band}, Lower: {lower_band}")
    print(f"Updated Support/Resistance: Support: {support}, Resistance: {resistance}")

    sys.stdout.flush()  # Flush output buffer

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


"""
ok so we have a websocket connection to stream data buuuut the variable names are all screwed up and the melatonin is kicking in so i'm gonna call it a night... or day in my case lol
"""
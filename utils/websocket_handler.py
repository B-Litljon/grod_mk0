from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import os

# Your Binance API key and secret (optional for market data streams)
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Initialize the Binance client (optional if only accessing public data)
client = Client(api_key, api_secret)

# Function to handle incoming WebSocket messages for K-line data
def handle_socket_message(msg):
    """
    Handle incoming messages, parse K-line data, and print the information.
    msg: The message received, containing K-line data.
    """
    # Extract the candlestick data from the message
    candlestick = msg['k']
    
    # Extracting relevant information from the candlestick data
    open_price = candlestick['o']
    high_price = candlestick['h']
    low_price = candlestick['l']
    close_price = candlestick['c']
    volume = candlestick['v']
    close_time = pd.to_datetime(candlestick['T'], unit='ms')
    
    print(f"Candlestick for {close_time}: Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}")

# Initialize the WebSocket manager using the client
twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
twm.start()

# Start a WebSocket for a specific symbol and interval
stream_name = twm.start_kline_socket(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, callback=handle_socket_message)

# To keep the script running and listening for messages
try:
    while True:
        pass  # You can replace this with time.sleep(1) for a less CPU-intensive loop
except KeyboardInterrupt:
    twm.stop_socket(stream_name)
    twm.join()

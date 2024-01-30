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
from plotly.offline import plot, iplot


load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_SECRET_KEY')


# Initialize indicators
bbands = BollingerBands(window=20, num_of_std=2)
rsi_indicator = RSI(period=14)
sup_res = SupportResistance(window=14)


# Global DataFrame to accumulate data
data_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'RSI', 'UpperBB', 'MiddleBB', 'LowerBB', 'Support', 'Resistance'])

# Initialize Plotly figure
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, subplot_titles=('Candlesticks with Bollinger Bands', 'RSI'))
fig.add_trace(go.Candlestick(x=[], open=[], high=[], low=[], close=[], name='Candlesticks'), row=1, col=1)
fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Upper Band'), row=1, col=1)
fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Middle Band'), row=1, col=1)
fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Lower Band'), row=1, col=1)
fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='RSI'), row=2, col=1)
fig.update_layout(xaxis_rangeslider_visible=False, height=800)

def update_plot():
    fig.data[0].x = data_df['Time']
    fig.data[0].open = data_df['Open']
    fig.data[0].high = data_df['High']
    fig.data[0].low = data_df['Low']
    fig.data[0].close = data_df['Close']

    fig.data[1].x = data_df['Time']
    fig.data[1].y = data_df['UpperBB']

    fig.data[2].x = data_df['Time']
    fig.data[2].y = data_df['MiddleBB']

    fig.data[3].x = data_df['Time']
    fig.data[3].y = data_df['LowerBB']

    fig.data[4].x = data_df['Time']
    fig.data[4].y = data_df['RSI']

    fig.show()


#client = Client(api_key, api_secret, tld='us')
# Function to handle incoming WebSocket messages for K-line data
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
    
    new_data_df = pd.DataFrame(new_data, index=[0])
    # Using concat instead of append
    data_df = pd.concat([data_df, new_data_df], ignore_index=True)    
    # Limit DataFrame size
    max_rows = 1000  # Maximum number of rows before deleting old data
    if len(data_df) > max_rows:
        data_df.drop(data_df.index[0], inplace=True)

    # Update plot
    update_plot()


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
# Import the necessary module
# ...


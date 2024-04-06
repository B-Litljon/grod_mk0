from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import time
import os
# import asyncio
from dotenv import load_dotenv
from utils.indicators.bollinger_bands import BollingerBands
from utils.indicators.rsi import RSI
from utils.signals.trigger import Triggers as trigger
from utils.safety.order_calculation import OrderCalculator, TradeConfig

class BinanceWebsocketStream:
    """
A class for streaming real-time candlestick data from Binance and performing technical analysis using Bollinger Bands and RSI.

Instantiate the class by creating an instance of BinanceWebsocketStream:
    stream = BinanceWebsocketStream(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, api_key='your_api_key', api_secret='your_api_secret')

Args:
    symbol (str): The trading pair symbol to stream data for (e.g., 'BTCUSDT').
    interval (str): The interval of the candlestick data (e.g., Client.KLINE_INTERVAL_1MINUTE).
    api_key (str): Your Binance API key.
    api_secret (str): Your Binance API secret.

The `BinanceWebsocketStream` class sets up a connection to the Binance WebSocket API and streams real-time candlestick data
for the specified trading pair and interval. It performs technical analysis using Bollinger Bands and RSI indicators and
stores the data in a pandas DataFrame.

Attributes:
    bbands (BollingerBands): An instance of the BollingerBands class for calculating Bollinger Bands.
    rsi (RSI): An instance of the RSI class for calculating the Relative Strength Index.
    dataframe (pandas.DataFrame): A DataFrame to store the candlestick data and technical indicators.
    twm (ThreadedWebsocketManager): An instance of the Binance ThreadedWebsocketManager for managing the WebSocket connection.
    tc (OrderCalculator): An instance of the OrderCalculator class for calculating trade sizes and managing orders.
    client (Client): An instance of the Binance Client for making API requests.

Methods:
    - `fetch_historical_data()`: Fetches historical candlestick data and initializes the DataFrame.
    - `handle_socket_message(msg)`: Handles incoming WebSocket messages, updates the DataFrame, and checks for trading signals.
    - `check_signal()`: Checks for trading signals based on the RSI and Bollinger Band expansion strategy.
    - `start()`: Starts the WebSocket stream and keeps the program running until interrupted.

Example usage:
    # Create an instance of BinanceWebsocketStream
    stream = BinanceWebsocketStream(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, api_key='your_api_key', api_secret='your_api_secret')
    
    # Start the WebSocket stream
    stream.start()

Note:
    - The `fetch_historical_data()` method should be called before starting the WebSocket stream to initialize the DataFrame
      with historical data.
    - The `check_signal()` method uses the `rsi_and_bb_expansion_strategy()` method from the `Triggers` class to check for
      trading signals based on RSI and Bollinger Band expansion.
    - The DataFrame size is limited to a maximum of 101 rows, and older data is written to a CSV file before being removed
      from the DataFrame to manage memory usage.
"""
    def __init__(self, symbol, interval, api_key , api_secret):
        self.symbol = symbol
        self.interval = interval
        self.api_key = api_key
        self.api_secret = api_secret
        self.bbands = BollingerBands(window= 20, num_of_std=2)
        self.rsi = RSI(period=14)
        self.dataframe = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'rsi', 'UpperBB', 'MiddleBB', 'LowerBB'])
        self.twm = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret, tld='us')
        self.tc = OrderCalculator(TradeConfig()) # 'tc' is an instance of OrderCalculator class renamed in this case to 'OrderCalculator'
        self.client = Client(api_key=self.api_key, api_secret=self.api_secret, tld='us')

    def fetch_historical_data(self):
        print('Fetching historical data...')
        klines = self.client.get_historical_klines(self.symbol, self.interval, limit=100)
        for kline in klines:
            open_time = pd.to_datetime(kline[0], unit='ms')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            close_time = pd.to_datetime(kline[6], unit='ms')

            if len(self.dataframe) > 0:
                previous_close = self.dataframe['close'].iloc[-1]
                rsi_value = self.rsi.update(close_price, previous_close)
            else:
                rsi_value = None

            upper_band, middle_band, lower_band = self.bbands.update(close_price)

            new_data = {
                'Time': close_time, 
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'RSI': rsi_value if rsi_value is not None else np.nan,
                'UpperBB': upper_band,
                'MiddleBB': middle_band,
                'LowerBB': lower_band
            }

            data_df_length = len(self.dataframe)
            self.dataframe.loc[data_df_length] = new_data

        print('Historical data loaded.')

    def handle_socket_message(self, msg):
        print('message received')
        candle = msg['k']
        rsi_value = None
        open_price = float(candle['o'])
        high_price = float(candle['h'])
        low_price = float(candle['l'])
        close_price = float(candle['c'])
        close_time = pd.to_datetime(candle['T'], unit='ms')

        if len(self.dataframe) > 0:
            previous_close = self.dataframe['close'].iloc[-1]
            rsi_value = self.rsi.update(close_price, previous_close)
        else:
            rsi_value = None

        upper_band, middle_band, lower_band = self.bbands.update(close_price)

        new_data = {
            'Time': close_time,
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price,
            'RSI': rsi_value if rsi_value is not None else np.nan,
            'UpperBB': upper_band,
            'MiddleBB': middle_band,
            'LowerBB': lower_band
        }
        
        # append new data to DataFrame
        data_df_length = len(self.dataframe)
        self.dataframe.loc[data_df_length] = new_data

        self.check_signal() 

        # Limit DataFrame size
        max_rows = 101
        if data_df_length > max_rows:
            # Extract the first row of the DataFrame
            row_to_append = self.dataframe.iloc[0]

            # Write the row to the CSV file in append mode if the file exists, otherwise write the header
            row_to_append.to_csv('kline_data.csv', mode='a', header=not os.path.exists('kline_data.csv'), index=False)

            # Delete the first row from the DataFrame
            self.dataframe.drop(self.dataframe.index[0], inplace=True)

    def check_signal(self):
        if trigger.rsi_and_bb_expansion_strategy(self.bbands, self.rsi, self.dataframe):
            print('Signal detected')
            self.tc.buy_order(
                symbol=self.symbol,
                order_type='market',
                quantity=self.tc.calculate_order_size(entry_price=self.dataframe['Close'].iloc[-1]), # calculate order size needs to also calculate stop loss and take profit 
                newClientOrderId='test_order').manage_orders(closing_price=self.dataframe['Close'].iloc[-1])
            

    def start(self):
        self.twm.start()
        stream_name = self.twm.start_kline_socket(
            symbol=self.symbol, 
            interval=self.interval, 
            callback=self.handle_socket_message
        ) # need to call fetch historical data here to fill the dataframe b4 the ws stream starts
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.twm.stop_socket(stream_name)
            self.twm.join()
 


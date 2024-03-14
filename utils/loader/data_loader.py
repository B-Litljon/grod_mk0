# Description: This file contains the function to start a WebSocket stream to listen for candlestick data from Binance.
# The function will also calculate the Bollinger Bands, RSI, and Support/Resistance levels for the candlestick data.
# The function will then print the data to the console and update the DataFrame with the new data.
# The function will also include the trade logic to make trade decisions based on the calculated indicators and risk management parameters.

from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import time
# import asyncio
from dotenv import load_dotenv
from ..indicators.bollinger_bands import BollingerBands
from ..indicators.rsi import RSI
from ..safety.order_calculation import TradeCalculator, TradeConfig

class BinanceWebsocketStream:
    def __init__(self, symbol, interval, api_key, api_secret):
        self.symbol = symbol
        self.interval = interval
        self.api_key = api_key
        self.api_secret = api_secret
        self.bbands = BollingerBands(window= 20, num_of_std=2)
        self.rsi = RSI(period=14)
        self.dataframe = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'rsi', 'UpperBB', 'MiddleBB', 'LowerBB'])
        self.twm = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret, tld='us')
        self.tc = TradeCalculator(TradeConfig())
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

            rsi_value = None
            if len(self.rsi.prices) > 0:
                previous_close = self.rsi.prices[-1]
                rsi_value = self.rsi.update(close_price, previous_close)

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

        if hasattr(self.bbands, 'prices') and len (self.bbands.prices) > 0:
            previous_close = self.bbands.prices[-1]
            rsi_value = self.rsi.update(close_price, previous_close)

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
        max_rows = 1000
        if data_df_length > max_rows:
            self.dataframe.drop(self.dataframe.index[0], inplace=True)


    def check_signal(self):
        if len(self.dataframe) < 20:
            return
        
        latest_rsi = self.dataframe['RSI'].iloc[-1]
        latest_close = self.dataframe['Close'].iloc[-1]
        rsi_normal = latest_rsi > 30 and latest_rsi <= 60 

        latest_upper_bb = self.dataframe['UpperBB'].iloc[-1]
        latest_lower_bb = self.dataframe['LowerBB'].iloc[-1]
        latest_moving_avg = self.dataframe['MiddleBB'].iloc[-1] # moving average added to determine if the bollinger bands are expanding or contracting bullish or bearish in relation to the current price
        previous_upper_bb = self.dataframe['UpperBB'].iloc[-2] 
        previous_lower_bb = self.dataframe['LowerBB'].iloc[-2]
        previous_moving_avg = self.dataframe['MiddleBB'].iloc[-2]
        
        # check if the bollinger bands are expanding or contracting
        previous_bandwidth = previous_upper_bb - previous_lower_bb
        latest_bandwidth = latest_upper_bb - latest_lower_bb
        bb_expanded = (latest_bandwidth - previous_bandwidth) / previous_bandwidth >= 0.15

        # I wrote a method to calculate the rolling average of the bandwidth as well as rate of change 
        # we need to do some minor tweaks and then incorporate that into this wss class 
        # also we need to include logic into this function to request enough data
        # so that the rsi and the bbands can start off with a calculation.
        # ideally we should request enough data to fill 100 rows of the df, 
        # then we can run the calculation and start the ws stream right after  #


        if rsi_normal and bb_expanded:
            print('Buy Signal')
            latest_data = self.dataframe.iloc[-1].to_dict()
            self.tc.place_order(latest_data)# place order
            # calculate order size      
            # place order
            # update trade history
            # updat usdt balance

        

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



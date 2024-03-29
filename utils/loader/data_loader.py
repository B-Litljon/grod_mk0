from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import time
import os
# import asyncio
from dotenv import load_dotenv
from ..indicators.bollinger_bands import BollingerBands
from ..indicators.rsi import RSI
from ..indicators.trigger import Trigger as trgr
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
        self.tc = TradeCalculator(TradeConfig()) # 'tc' is an instance of OrderCalculator class renamed in this case to 'TradeCalculator'
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
            # Extract the first row of the DataFrame
            row_to_append = self.dataframe.iloc[0]

            # Write the row to the CSV file in append mode if the file exists, otherwise write the header
            row_to_append.to_csv('kline_data.csv', mode='a', header=not os.path.exists('kline_data.csv'), index=False)

            # Delete the first row from the DataFrame
            self.dataframe.drop(self.dataframe.index[0], inplace=True)

    def check_signal(self):
        if trgr.rsi_and_bb_expansion_strategy(self.bbands, self.rsi, self.dataframe):
            print('Signal detected')
            # self.tc.calculate_order_size()
            # self.tc.calculate_stop_loss()
            # self.tc.calculate_take_profit()
            # self.tc.calculate_risk_reward_ratio

        

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



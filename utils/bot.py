from binance import Client, ThreadedWebsocketManager
import logging
import pandas as pd
import numpy as np
import time
import os
# import asyncio
from dotenv import load_dotenv
from utils.indicators.bollinger_bands import BollingerBands
from utils.indicators.rsi import RSI
from utils.signals.trigger import Triggers 
from utils.safety.order_calculation import OrderCalculator, TradeConfig

class Bot:
    def __init__(self, symbol, interval, api_key , api_secret):
        self.symbol = symbol
        self.interval = interval
        self.api_key = api_key
        self.api_secret = api_secret
        self.bbands = BollingerBands(window= 20, num_of_std=2)
        self.rsi = RSI(period=14)
        self.kline_data = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'rsi', 'UpperBB', 'MiddleBB', 'LowerBB'])
        self.twm = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret, tld='us')
        self.order_calculator = OrderCalculator(TradeConfig()) # 'tc' is an instance of OrderCalculator class renamed in this case to 'OrderCalculator'
        self.client = Client(api_key=self.api_key, api_secret=self.api_secret, tld='us')
        self.trigger = Triggers(bollinger_bands=self.bbands, rsi_values=self.rsi, price_data=self.kline_data)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def fetch_historical_data(self):
        self.logger.info('fetching historical data')
        klines = self.client.get_historical_klines(symbol=self.symbol, interval=self.interval, limit= 100)
        for kline in klines:
            self.append_data_to_df(kline)

    def append_data_to_df(self, kline):
        open_time, open_price, high_price, low_price, close_price, volume, close_time = self.process_kline(kline)
        # Calculate indicators
        rsi_value = self.rsi.update(close_price)
        upper_band, middle_band, lower_band = self.bbands.update(close_price)
        # Append new data to the DataFrame
        new_data = {'time': close_time, 'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price, 'volume': volume, 'rsi': rsi_value, 'upperbb': upper_band, 'middlebb': middle_band, 'lowerbb': lower_band}
        self.kline_data = self.kline_data.append(new_data, ignore_index=True)
       
    def process_kline(self, kline):
        open_time = pd.to_datetime(kline[0], unit='ms')
        open_price = float(kline[1])
        high_price = float(kline[2])
        low_price = float(kline[3])
        close_price = float(kline[4])
        volume = float(kline[5])
        close_time = pd.to_datetime(kline[6], unit='ms')
        return open_time, open_price, high_price, low_price, close_price, volume, close_time

    def handle_socket_message(self, msg):
        self.logger.info('message received')
        candle = msg['k']
        open_price = float(candle['o'])
        high_price = float(candle['h'])
        low_price = float(candle['l'])
        close_price = float(candle['c'])
        close_time = pd.to_datetime(candle['T'], unit='ms')
        if len(self.kline_data) > 0:
            previous_close = self.kline_data['close'].iloc[-1]
            rsi_value = self.rsi.update(close_price, previous_close)
        else:
            rsi_value = None
        upper_band, middle_band, lower_band = self.bbands.update(close_price)
        new_data = {
            'time': close_time,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'rsi': rsi_value if rsi_value is not None else np.nan,
            'upperbb': upper_band,
            'middlebb': middle_band,
            'lowerbb': lower_band
        }
        self.logger.info(f"latest data: {new_data}") # logging new data without concatenating it to the dataframe will give you the same value for high, low, open, close, and rsi
        data_df_length = len(self.kline_data)
        self.kline_data.loc[data_df_length] = new_data
        self.check_signal()
        max_rows = 101
        if len(self.kline_data) > max_rows:
            row_to_append = self.kline_data.iloc[0]
            row_to_append.to_csv('kline_data.csv', mode='a', header=not os.path.exists('kline_data.csv'), index=False)
            self.kline_data.drop(self.kline_data.index[0], inplace=True)

    def check_signal(self):
        if self.trigger.rsi_and_bb_expansion_strategy(self.bbands, self.rsi, dataframe=self.kline_data):
            print('Signal detected')
            self.order_calculator.buy_order(
                symbol=self.symbol,
                order_type='market',
                quantity=self.order_calculator.calculate_order_size(entry_price=self.kline_data['close'].iloc[-1]), # calculate order size needs to also calculate stop loss and take profit 
                newClientOrderId='test_order').manage_orders(closing_price=self.kline_data['close'].iloc[-1])
            
    def start(self):
        self.fetch_historical_data()
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
 


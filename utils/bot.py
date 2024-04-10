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
    def __init__(self, symbol, interval, api_key, api_secret):
        self.symbol = symbol
        self.interval = interval
        self.api_key = api_key
        self.api_secret = api_secret
        self.bbands = BollingerBands(window=20, num_of_std=2)
        self.rsi = RSI(period=14)
        self.kline_data = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'rsi', 'UpperBB', 'MiddleBB', 'LowerBB'])
        self.twm = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret, tld='us')
        self.order_calculator = OrderCalculator(TradeConfig())  # 'tc' is an instance of OrderCalculator class renamed in this case to 'OrderCalculator'
        self.client = Client(api_key=self.api_key, api_secret=self.api_secret, tld='us')
        self.trigger = Triggers() #rsi_value exists as an attribute in both the trigger class and rsi class

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def fetch_historical_data(self):
        self.logger.info('Fetching historical data')
        klines = self.client.get_historical_klines(symbol=self.symbol, interval=self.interval, limit=100)
        for kline in klines:
            historic_kline_data = {
                'time': pd.to_datetime(kline[0], unit='ms'),
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[5]),
                'close_time': pd.to_datetime(kline[6], unit='ms')
            }
            # self.logger.debug(kline_data)
            self.append_data_to_df(historic_kline_data)

        self.logger.info("last 5 historic data:\n%s", self.kline_data.tail(5).to_string(index=False))

    def append_data_to_df(self, kline):
        # Calculate indicators
        previous_price = self.kline_data['close'].iloc[-1] if len(self.kline_data) > 0 else 0
        rsi_value = self.rsi.update(kline['close'], previous_price)
        upper_band, middle_band, lower_band = self.bbands.update(kline['close'])
        # Append new data to the DataFrame using loc
        new_data = {
            'time': kline['time'],
            'open': kline['open'],
            'high': kline['high'],
            'low': kline['low'],
            'close': kline['close'],
            'volume': kline['volume'],
            'rsi': rsi_value,
            'upperbb': upper_band,
            'middlebb': middle_band,
            'lowerbb': lower_band
        }
        self.kline_data.loc[len(self.kline_data)] = new_data
        #self.logger.info(f"New data appended to DataFrame: {new_data}")
        #self.logger.info('data appended to DataFrame')

    def handle_socket_message(self, msg):
        self.logger.info('Message received')
        self.logger.debug(msg)
        
        kline = msg['k']
        live_kline_data = {
            'time': pd.to_datetime(kline['t'], unit='ms'),
            'open': float(kline['o']),
            'high': float(kline['h']),
            'low': float(kline['l']),
            'close': float(kline['c']),
            'volume': float(kline['v']),
            'close_time': pd.to_datetime(kline['T'], unit='ms')
        }
        self.append_data_to_df(live_kline_data)
        self.logger.info("live data:\n%s", self.kline_data.tail(5).to_string(index=False))
        self.logger.debug(self.kline_data)
        self.check_signal()
        max_rows = 60
        if len(self.kline_data) > max_rows:
            try:
                row_to_append = self.kline_data.iloc[0]
                row_to_append.to_csv('kline_data.csv', mode='a', header=not os.path.exists('kline_data.csv'), index=False)
                self.kline_data.drop(self.kline_data.index[0], inplace=True)
            except Exception as e:
                self.logger.warning(f"Error occurred while writing to CSV: {e}")

    def check_signal(self):
        lower_band = self.bbands.lower_band[-1]
        rsi_value = self.rsi.values[-1]
        bandwidth_roc = self.bbands.calculate_bandwidth_roc()
        if self.trigger.rsi_and_bb_expansion_strategy(price_data=self.kline_data, lower_band=lower_band, rsi_value=rsi_value, bandwidth_roc=bandwidth_roc):
            print('Signal detected')
            self.order_calculator.buy_order(
                symbol=self.symbol,
                order_type='market',
                quantity=self.order_calculator.calculate_order_size(entry_price=self.kline_data['close'].iloc[-1]),
                newClientOrderId='test_order').manage_orders(closing_price=self.kline_data['close'].iloc[-1])

    def start(self):
        self.fetch_historical_data()
        self.twm.start()
        stream_name = self.twm.start_kline_socket(
            symbol=self.symbol,
            interval=self.interval,
            callback=self.handle_socket_message
        )  # need to call fetch historical data here to fill the dataframe b4 the ws stream starts
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.twm.stop_socket(stream_name)
            self.twm.join()
 


# Description: This file contains the function to start a WebSocket stream to listen for candlestick data from Binance.
# The function will also calculate the Bollinger Bands, RSI, and Support/Resistance levels for the candlestick data.
# The function will then print the data to the console and update the DataFrame with the new data.
# The function will also include the trade logic to make trade decisions based on the calculated indicators and risk management parameters.

from binance import Client, ThreadedWebsocketManager
import pandas as pd
import numpy as np
import sys
import os
import time
import asyncio
from dotenv import load_dotenv
from .indicators.bollinger_bands import BollingerBands
from .indicators.rsi import RSI
from .indicators.sup_res import SupportResistance
from .trade_logic import TradeCalculator, TradeConfig

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

    async def handle_socket_message(self, msg):
        print('message received')
        sys.stdout.flush()
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
        
        # Efficiently append new data to DataFrame
        data_df_length = len(self.dataframe)
        self.dataframe.loc[data_df_length] = new_data


        trade_decision, quantity = await self.tc.make_trade_decision(
            symbol=self.symbol,
            rsi_value=rsi_value,
            close_price=close_price,
            lower_band=lower_band,
            middle_band=middle_band,
            upper_band=upper_band,
            moving_average=None,  # You'll need to calculate or pass the moving average
            action='BUY' if rsi_value < self.tc.config.rsi_oversold else 'SELL'
        )

        # If a trade decision is made, place the order
        if trade_decision in ['BUY', 'SELL']:
            asyncio.run(self.tc.place_order(
                client=self.client,  # You'll need to have a client instance for API calls
                symbol=self.symbol,
                quantity=quantity,
                price=close_price,  # Or another price depending on your strategy
                order_type=trade_decision.lower()
            ))

        # Limit DataFrame size
        max_rows = 1000
        if data_df_length > max_rows:
            self.dataframe.drop(self.dataframe.index[0], inplace=True)

        # Dynamic console output
        # output = (
        #     f"Candlestick Data: Open: {new_data['Open']}, High: {new_data['High']}, Low: {new_data['Low']}, Close: {new_data['Close']}\n"
        #     f"RSI: {new_data['RSI']}\n"
        #     f"BB Data: Upper: {new_data['UpperBB']}, Middle: {new_data['MiddleBB']}, Lower: {new_data['LowerBB']}\n"
        #     f"Support: {new_data['Support']}, Resistance: {new_data['Resistance']}\n"
        # )

        # # Clear the console and print the output
        # sys.stdout.write("\033[H\033[J")  # Clear screen and move to home position
        # sys.stdout.write(output)
        sys.stdout.flush()  # Ensure the print is flushed to the console


        

    def start(self):
        self.twm.start()
        stream_name = self.twm.start_kline_socket(
            symbol=self.symbol, 
            interval=self.interval, 
            callback=lambda msg: asyncio.create_task(self.handle_socket_message(msg))
        )
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.twm.stop_socket(stream_name)
            self.twm.join()



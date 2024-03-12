# import necessary libraries and modules
from dotenv import load_dotenv
import os
from utils.feeder.data_loader import BinanceWebsocketStream
from utils.indicators.bollinger_bands import BollingerBands
from utils.indicators.rsi import RSI

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_SECRET_KEY')
    symbol = input("Enter the symbol you want to trade: ").lower() + 'USDT'
    interval = '1M'#input("Enter the interval you want to trade: ").lower()
    
    # Create an instance of BinanceWebsocketStream without using curly braces
    stream = BinanceWebsocketStream(symbol, interval, api_key, api_secret)
    stream.start()  # Start the websocket stream
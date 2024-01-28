
import pandas as pd

# Fetch API keys from environment variables for better security
# api_key = os.getenv('BINANCE_API_KEY')
# api_secret = os.getenv('BINANCE_API_SECRET')

# def fetch_historical_data(symbol, interval, lookback):
#     client = Client(api_key, api_secret)
#     candles = client.get_klines(symbol=symbol, interval=interval, limit=lookback)
    
#     df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
#     df = df.apply(pd.to_numeric, errors='ignore')
#     df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
#     df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    
#     return df['close']



class BollingerBands:
    def __init__(self, window=20, num_of_std=2):
        self.window = window
        self.num_of_std = num_of_std
        self.prices = []
        self.mean = 0
        self.std_dev = 0

    def update(self, new_price):
        self.prices.append(new_price)
        if len(self.prices) > self.window:
            self.prices.pop(0)
        
        prices_series = pd.Series(self.prices)
        self.mean = prices_series.mean()
        self.std_dev = prices_series.std()
        
        upper_band = self.mean + (self.std_dev * self.num_of_std)
        lower_band = self.mean - (self.std_dev * self.num_of_std)
        
        return upper_band, self.mean, lower_band
    





# highlight block and ctrl + / to uncomment
# def calculate_bollinger_bands(symbol, interval, lookback, window=20, num_of_std=2):
#     prices = fetch_historical_data(symbol, interval, lookback)
    
#     middle_band = prices.rolling(window=window).mean()
#     std_dev = prices.rolling(window=window).std()
#     upper_band = middle_band + (std_dev * num_of_std)
#     lower_band = middle_band - (std_dev * num_of_std)
    
#     return pd.DataFrame({'upper_band': upper_band, 'middle_band': middle_band, 'lower_band': lower_band})



# Example usage:
# symbol = 'BTCUSDT'
# interval = Client.KLINE_INTERVAL_1MINUTE
# lookback = 100  # Ensure this is sufficient for your Bollinger Band calculations
# bollinger_bands = calculate_bollinger_bands(symbol, interval, lookback)
# print(bollinger_bands.tail())

from .loader import BinanceWebsocketStream

class Bot:
    def __init__(self, symbol, interval, api_key, api_secret):
        self.stream = BinanceWebsocketStream(symbol, interval, api_key, api_secret)
    
    def run(self):
        print('booting up...')
        self.fetch_historical_data()
        print('fetching historical data...')
        print('starting websocket stream...')
        self.stream.start()
    
    def exit(self):
        print('Shutting down')
        self.stream.twm.stop()
        self.stream.twm.join()
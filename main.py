# import necessary libraries and modules
from dotenv import load_dotenv
import os
from utils.websocket_handler import start_websocket_stream



if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_SECRET_KEY')
    start_websocket_stream(api_key, api_secret)
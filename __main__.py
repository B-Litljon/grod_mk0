from dotenv import load_dotenv
import os
from utils.bot import Bot 

# import necessary libraries and modules


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_SECRET_KEY')
    symbol = input("Enter the symbol you want to trade: ").lower() + 'USDT'
    interval = '1M'  # input("Enter the interval you want to trade: ").lower()

    Bot.run(api_key, api_secret, symbol, interval)

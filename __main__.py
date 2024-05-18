from dotenv import load_dotenv
import os
from utils.bot import Bot

# import necessary libraries and modules

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_SECRET_KEY')
    symbol = input("Enter the symbol you want to trade: ").upper() + 'USDT'
    interval = '1m'
    bot = Bot(symbol, interval, api_key, api_secret )
    #bot.fetch_historical_data()  # Fetch historical data before starting the WebSocket stream
    bot.start()

    # # Wait for the bot to finish or handle any other necessary cleanup
    # # You can add any additional code or logic here

    # bot.twm.stop()  # Stop the WebSocket stream
    # bot.twm.join()  # Wait for the WebSocket thread to terminate
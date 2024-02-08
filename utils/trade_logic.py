from binance.client import Client
from dotenv import load_dotenv
import os
import asyncio
# Load environment variables
load_dotenv()
api_key = os.getenv ('BINANCE_API_KEY')
api_secret = os.getenv ('BINANCE_API_SECRET')

client = Client(api_key, api_secret, tld='us')

class TradeConfig:
    """A class to hold configuration for trading strategy."""
    def __init__(self, rsi_oversold=25, rsi_overbought=75, max_risk_per_trade=0.02, total_capital=1000):
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.max_risk_per_trade = max_risk_per_trade
        self.total_capital = total_capital

class TradeCalculator:
    """A class to calculate trade sizes and make trade decisions."""
    def __init__(self, config):
        self.config = config
        self.owned_assets = {}
        self.rsi_crossed_oversold = False

    def calculate_trade_size(self, entry_price, stop_loss_price, action):
        risk_per_share = entry_price - stop_loss_price if action == 'BUY' else stop_loss_price - entry_price
        num_of_shares_to_buy = (self.config.total_capital * self.config.max_risk_per_trade) / risk_per_share
        return num_of_shares_to_buy
    
    def update_owned_assets(self, symbol, quantity, action):
        if action == 'BUY':
            if symbol in self.owned_assets:
                self.owned_assets[symbol] += quantity
            else:
                self.owned_assets[symbol] = quantity
        elif action == 'SELL':
            if symbol in self.owned_assets:
                self.owned_assets[symbol] -= quantity
                # Ensure the quantity doesn't go negative; adjust as needed based on your strategy
                self.owned_assets[symbol] = max(self.owned_assets[symbol], 0)

    def make_trade_decision(self, symbol, rsi_value, close_price, lower_band, middle_band, upper_band, moving_average, action):
        band_width = upper_band - lower_band
        stop_loss_long = lower_band * 0.98
        stop_loss_short = upper_band * 1.02
        take_profit_long = middle_band * 0.99
        take_profit_short = middle_band * 1.01

        if band_width > moving_average:
            stop_loss_long *= 1.02
            take_profit_long *= 1.02
        elif band_width < moving_average:
            stop_loss_short *= 0.98
            take_profit_short *= 0.98

        if rsi_value < self.config.rsi_oversold and close_price <= lower_band:
            print("Buy signal triggered: RSI oversold and price near lower Bollinger Band.")
            num_of_shares_to_buy = self.calculate_trade_size(close_price, stop_loss_long, 'long')
            # Place buy order logic here
            # Example: client.create_test_order(symbol='BTCUSDT', side='BUY', type='LIMIT', quantity=num_of_shares_to_buy, price=close_price)
            return 'BUY', num_of_shares_to_buy

        elif rsi_value > self.config.rsi_overbought and close_price >= upper_band:
            print("Sell signal triggered: RSI overbought and price near upper Bollinger Band.")
            shares_to_sell = self.calculate_trade_size(close_price, stop_loss_short, 'short')
            # Place sell order logic here
            # Example: client.create_test_order(symbol='BTCUSDT', side='SELL', type='LIMIT', quantity=shares_to_sell, price=close_price)
            return 'SELL', shares_to_sell

        return 'HOLD', 0  # No action condition
from binance.client import Client
from dotenv import load_dotenv
import os
import pandas as pd
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

class OrderCalculator:
    """
    A class to calculate order size and manage trades.

    args: 

    initial_usdt_balance: float - Initial USDT balance
    risk_per_trade: float - Maximum risk per trade as a percentage of total capital
    """
    def __init__(self, initial_usdt_balance, risk_per_trade=0.01):
        self.usdt_balance = initial_usdt_balance # needs to get the actual usdt balance from the account since the algo will only use usdt to place orders
        self.risk_per_trade = risk_per_trade
    # Calculate the size of the order to place for added safety
    def calculate_order_size(self, entry_price, stop_loss_price):
        risk_per_trade_amt = self.usdt_balance * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share <= 0:
            return 0
        num_of_shares_to_buy = risk_per_trade_amt / risk_per_share
        return round(num_of_shares_to_buy, 2)  # Assuming the exchange allows for fractional quantities
    # keep track of the assets that have been purchased in a dict
    def purchased_asset(self, symbol, entry_price, quantity):
        asset = {
            'Symbol': symbol,
            'EntryPrice': entry_price,
            'Quantity': quantity
        }
        

    
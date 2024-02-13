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
        self.usdt_balance = initial_usdt_balance # needs to get the actual balance from the account
        self.risk_per_trade = risk_per_trade
        # Initialize DataFrame to track trades
        self.trades_df = pd.DataFrame(columns=['Symbol', 'EntryPrice', 'Quantity', 'StopLoss', 'TakeProfit', 'Status'])

    def calculate_order_size(self, entry_price, stop_loss_price):
        risk_per_trade_amt = self.usdt_balance * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share <= 0:
            return 0
        num_of_shares_to_buy = risk_per_trade_amt / risk_per_share
        return round(num_of_shares_to_buy, 2)  # Assuming the exchange allows for fractional quantities

    def add_trade(self, symbol, entry_price, quantity, stop_loss, take_profit):
        new_trade = {
            'Symbol': symbol,
            'EntryPrice': entry_price,
            'Quantity': quantity,
            'StopLoss': stop_loss,
            'TakeProfit': take_profit,
            'Status': 'Open'
        }
        self.trades_df = self.trades_df.append(new_trade, ignore_index=True)

    def update_trade_status(self, symbol, current_price):
        # Example method to update trade status - implement based on your strategy
        pass
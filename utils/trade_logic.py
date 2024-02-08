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

    async def make_trade_decision(self, client, symbol, rsi_value, close_price, lower_band, middle_band, upper_band, moving_average):
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
            # Call place_order to place a buy order
            order_result = await self.place_order(client, symbol, num_of_shares_to_buy, close_price, 'buy')
            return order_result

        elif rsi_value > self.config.rsi_overbought and close_price >= upper_band:
            print("Sell signal triggered: RSI overbought and price near upper Bollinger Band.")
            shares_to_sell = self.calculate_trade_size(close_price, stop_loss_short, 'short')
            # Call place_order to place a sell order
            order_result = await self.place_order(client, symbol, shares_to_sell, close_price, 'sell')
            return order_result

        return 'HOLD', 0  # No action condition
    
    async def place_order(self, client, symbol, quantity, price, order_type):
        """
        Asynchronously places a limit buy or sell order.

        :param client: The API client instance.
        :param symbol: The symbol to trade.
        :param quantity: The quantity to trade.
        :param price: The price at which to execute the order.
        :param order_type: 'buy' or 'sell' to determine the type of order.
        :return: The result of the order.
        """
        if order_type == 'buy':
            order = await client.order_limit_buy(
                symbol=symbol,
                quantity=quantity,
                price=price
            )
        elif order_type == 'sell':
            order = await client.order_limit_sell(
                symbol=symbol,
                quantity=quantity,
                price=price
            )
        else:
            raise ValueError("Invalid order type specified. Must be 'buy' or 'sell'.")

        return order
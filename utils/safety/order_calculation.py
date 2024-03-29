from binance.client import Client
from dotenv import load_dotenv
import os
import pandas as pd
import time
import uuid
# Load environment variables
load_dotenv()
api_key = os.getenv ('BINANCE_API_KEY')
api_secret = os.getenv ('BINANCE_API_SECRET')

client = Client(api_key, api_secret, tld='us')

class TradeConfig:
    """
A class for storing and managing the configuration parameters for a trading strategy.

Instantiate the class by creating an instance of TradeConfig:
    config = TradeConfig(rsi_oversold=30, rsi_overbought=70, max_risk_per_trade=0.015, total_capital=5000)

Args:
    rsi_oversold (int): The RSI level below which an asset is considered oversold. Default is 25.
    rsi_overbought (int): The RSI level above which an asset is considered overbought. Default is 75.
    max_risk_per_trade (float): The maximum percentage of total capital to risk per trade. Default is 0.02 (2%).
    total_capital (float): The total capital available for trading. Default is 1000.

The `TradeConfig` class provides a convenient way to store and access the configuration parameters for a trading strategy.
It allows you to specify the following parameters:

- RSI oversold level: The RSI level below which an asset is considered oversold and a potential buy signal is generated.
- RSI overbought level: The RSI level above which an asset is considered overbought and a potential sell signal is generated.
- Maximum risk per trade: The maximum percentage of the total capital that can be risked on a single trade.
- Total capital: The total amount of capital available for trading.

By creating an instance of the `TradeConfig` class with the desired parameter values, you can easily manage and access
these configuration settings throughout your trading strategy.

Example usage:
    # Create a TradeConfig instance
    config = TradeConfig(rsi_oversold=30, rsi_overbought=70, max_risk_per_trade=0.015, total_capital=5000)
    
    # Access the configuration parameters
    oversold_level = config.rsi_oversold
    overbought_level = config.rsi_overbought
    max_risk = config.max_risk_per_trade
    capital = config.total_capital
"""
    def __init__(self, rsi_oversold=25, rsi_overbought=75, max_risk_per_trade=0.02, total_capital=1000):
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.max_risk_per_trade = max_risk_per_trade
        self.total_capital = total_capital

class OrderCalculator:
    """
A class for calculating order sizes and managing asset purchases based on a specified risk percentage.

Instantiate the class by creating an instance of OrderCalculator:
    calculator = OrderCalculator(initial_usdt_balance=1000, risk_per_trade=0.01)

Args:
    initial_usdt_balance (float): The initial USDT balance to be used for placing orders.
    risk_per_trade (float): The percentage of the USDT balance to risk per trade. Default is 0.01 (1%).

The class provides methods to calculate the appropriate order size based on the entry price and stop loss price,
track purchased assets, and place buy or sell orders.

To calculate the order size:
    order_size = calculator.calculate_order_size(entry_price, stop_loss_price)

The `calculate_order_size` method returns the quantity of shares to buy based on the specified risk percentage.

To record a purchased asset:
    calculator.purchased_asset(symbol, entry_price, quantity)

The `purchased_asset` method stores the details of a purchased asset, including the symbol, entry price, and quantity.

To place an order:
    order = calculator.place_order(symbol, order_type, quantity, price)

The `place_order` method attempts to place a buy or sell order using the Binance client API.
It takes the following arguments:
    - symbol (str): The trading pair symbol.
    - order_type (str): The type of order ('buy' or 'sell').
    - quantity (float): The quantity of the asset to buy or sell.
    - price (float): The price at which to place the order.

Note: The `place_order` method requires a properly configured Binance client API and handles exceptions.
      Proper error handling and logging should be implemented for production use.
"""
    def __init__(self, initial_usdt_balance, risk_per_trade=0.01):
        self.usdt_balance = initial_usdt_balance # needs to get the actual usdt balance from the account since the algo will only use usdt to place orders
        self.risk_per_trade = risk_per_trade
        self.active_orders = {}
    # Calculate the size of the order to place for added safety
    def calculate_order_size(self, entry_price, stop_loss_price):
        risk_per_trade_amt = self.usdt_balance * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share <= 0:
            return 0
        num_of_shares_to_buy = risk_per_trade_amt / risk_per_share
        return round(num_of_shares_to_buy, 2)  # Assuming the exchange allows for fractional quantities
    
    def place_order(self, symbol, order_type, quantity, price):  # should use calculate order size to get the quantity
        try:
            # Generate a unique order ID
            order_id = f"{int(time.time() * 1000)}_{symbol}_{uuid.uuid4().hex}"

            if order_type == 'buy': # import tiggers and set a variable to check if the signal is true
                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity,
                    newClientOrderId=order_id
                )
                # need to update place order method to place the order, then update the active orders dict with the order details
                # create logic to check the active order dict 

                print(order)
            elif order_type == 'sell':
                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity, # should use the active order dict to get time of purchase and calculate the quantity to sell
                    newClientOrderId=order_id
                )
                print(order)

            # Store the order details in the in-memory dictionary
            self.active_orders[order_id] = {
                'timestamp': int(time.time() * 1000),
                'symbol': symbol,
                'type': order_type,
                'price': price,
                'quantity': quantity,
                'status': 'NEW'
            }

            return order_id

        except Exception as e:
            print(e)
            return None
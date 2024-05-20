# decided a better way to make use of this class is to create a new method 'long_order' 
# long order would combine buy/sell and order manager into one method that can be called in the check_signal method or in the trigger class itself
# this provides a more modular approach to the code and makes it easier to manage the order logic


from binance.client import Client
from dotenv import load_dotenv
import os
import pandas as pd
import time
import uuid
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()
api_key = os.getenv ('BINANCE_API_KEY')
api_secret = os.getenv ('BINANCE_API_SECRET')

client = Client(api_key, api_secret, tld='us')

class TradeConfig:
    """
    A class to store trading configuration parameters.

    Attributes:
        rsi_oversold (int): The RSI value that indicates an oversold condition.
        rsi_overbought (int): The RSI value that indicates an overbought condition.
        max_risk_per_trade (float): The maximum risk percentage allowed per trade.
        total_capital (float): The total capital available for trading.

    Methods:
        __init__(self, rsi_oversold=25, rsi_overbought=75, max_risk_per_trade=0.02, total_capital=1000):
            Initializes the TradeConfig object with the given parameters.

            Args:
                rsi_oversold (int, optional): The RSI value that indicates an oversold condition. Default is 25.
                rsi_overbought (int, optional): The RSI value that indicates an overbought condition. Default is 75.
                max_risk_per_trade (float, optional): The maximum risk percentage allowed per trade. Default is 0.02 (2%).
                total_capital (float, optional): The total capital available for trading. Default is 1000.
    """
    def __init__(self, rsi_oversold=25, rsi_overbought=75, max_risk_per_trade=0.02, total_capital=1000): #total capital should be the amount of usdt in the account, this is just a placeholder
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.max_risk_per_trade = max_risk_per_trade
        self.total_capital = total_capital

class OrderCalculator:
    """
    A class for calculating and managing orders based on a given trading strategy.

    This class provides methods to calculate the order size, place buy and sell orders,
    and manage active orders based on the current market price. It also keeps track of
    the USDT balance and the risk per trade.

    Attributes:
        usdt_balance (float): The initial USDT balance for placing orders.
        risk_per_trade (float): The percentage of the balance to risk per trade.
        active_orders (dict): A dictionary to store active orders.
    """
    def __init__(self, initial_usdt_balance, risk_per_trade=0.01):
        self.usdt_balance = initial_usdt_balance # needs to get the actual usdt balance from the account since the algo will only use usdt to place orders
        self.risk_per_trade = risk_per_trade
        self.active_orders = {}
    # Calculate the size of the order to place for added safety
    def calculate_order_size(self, entry_price, middle_band):
        """
        Calculate the size of the order to place based on the entry price and middle band.

        Args:
            entry_price (float): The entry price for the order.
            middle_band (float): The middle band price used for calculating the take profit.

        Returns:
            tuple: A tuple containing the rounded number of shares to buy,
                   the stop loss price, and the take profit price.
        """
        stop_loss_percentage = 0.02
        stop_loss = entry_price * (1 - stop_loss_percentage)
        take_profit = middle_band * 0.999  # Adjust the multiplier as needed

        risk_per_trade_amt = self.usdt_balance * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share <= 0:
            return 0, 0, 0
        num_of_shares_to_buy = risk_per_trade_amt / risk_per_share
        rounded_shares = round(num_of_shares_to_buy, 2)  # round to 2 decimal places

        return rounded_shares, stop_loss, take_profit
    
    def buy_order(self, symbol, quantity, entry_price, take_profit, stop_loss):
        """
        Place a buy order for the specified symbol and quantity.

        Args:
            symbol (str): The trading symbol for the order.
            quantity (float): The quantity of shares to buy.
            entry_price (float): The entry price for the order.
            take_profit (float): The take profit price for the order.
            stop_loss (float): The stop loss price for the order.

        Returns:
            str or None: The unique order ID if the order is placed successfully,
                         or None if an error occurs.
        """
        try:
            # Generate a unique order ID
            order_id = f"{int(time.time() * 1000)}_{symbol}_{uuid.uuid4().hex}"
            order = client.create_test_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity,
                newClientOrderId=order_id
            )
            if order:
                # Store the order details in the active_order dictionary
                self.active_order = {
                    'order_id': order_id,
                    'timestamp': int(time.time() * 1000),
                    'symbol': symbol,
                    'type': 'buy',
                    'entry_price': entry_price,
                    'take_profit': take_profit,
                    'stop_loss': stop_loss,
                    'quantity': quantity,
                    'status': 'NEW'
                }
                logger.info(f'Buy order placed: {self.active_order}')
            return order_id # maybe update to return the dict instead of the order_id 
        except Exception as e:
            logger.error(f"Error placing buy order: {str(e)}")
            return None

    def sell_order(self, current_price):
        """
        Place a sell order for the active order based on the current market price.

        This method retrieves the active order details, places a sell order, updates the
        order status, calculates the profit or loss, and writes the order details to a
        CSV file.

        Args:
            current_price (float): The current market price.

        Returns:
            None
        """
        try:
            order = self.active_order
            sell_order = client.create_test_order(
                symbol=order['symbol'],
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=order['quantity'],
                newClientOrderId=f"{order['order_id']}_SELL"
            )
            if sell_order:
                # Update the status and timestamp of the sold order
                order['status'] = 'SOLD'
                order['sell_timestamp'] = int(time.time() * 1000)
                order['sell_price'] = current_price
                # Calculate the profit or loss
                profit_loss = (current_price - order['entry_price']) * order['quantity']
                order['profit_loss'] = profit_loss
                # Label the order as 'GAIN' or 'LOSS'
                if profit_loss > 0:
                    order['outcome'] = 'GAIN'
                else:
                    order['outcome'] = 'LOSS'
                logger.info(f'Sell order placed: {order}')    
                # Convert the order dictionary to a DataFrame
                order_df = pd.DataFrame([order])
                # Write the DataFrame to a CSV file
                order_df.to_csv('order_history.csv', mode='a', header=not os.path.exists('order_history.csv'), index=False)
                # Reset the active_order to None
                self.active_order = None
        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
    # compares the tp/sl to the current price and sells the order if the price is reached
    def manage_orders(self, current_price):
        """
        Manage active orders based on the current market price.

        This method compares the current price with the take profit and stop loss prices
        of active orders. If the current price reaches either the take profit or stop loss
        price, it triggers a sell order for the corresponding order.

        Args:
            current_price (float): The current market price.

        Returns:
            None
        """
        if not self.active_orders:
            return  # If there are no active orders, return early

        for order_id, order in list(self.active_orders.items()):
            if order['status'] == 'NEW':
                if current_price <= order['stop_loss']:
                    # ...
                    self.sell_order(order_id, current_price)
                elif current_price >= order['take_profit']:
                    # ...
                    self.sell_order(order_id, current_price)
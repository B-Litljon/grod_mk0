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
    def __init__(self, rsi_oversold=25, rsi_overbought=75, max_risk_per_trade=0.02, total_capital=1000):
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.max_risk_per_trade = max_risk_per_trade
        self.total_capital = total_capital

class OrderCalculator:
    def __init__(self, initial_usdt_balance, risk_per_trade=0.01):
        self.usdt_balance = initial_usdt_balance # needs to get the actual usdt balance from the account since the algo will only use usdt to place orders
        self.risk_per_trade = risk_per_trade
        self.active_orders = {}
    # Calculate the size of the order to place for added safety
    def calculate_order_size(self, entry_price, middle_band):
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
        if self.active_order:
            order = self.active_order
            if order['status'] == 'NEW':
                if current_price <= order['stop_loss']:
                    logger.info(f"Stop loss triggered for order {order['order_id']}")
                    self.sell_order(current_price)
                elif current_price >= order['take_profit']:
                    logger.info(f"Take profit triggered for order {order['order_id']}")
                    self.sell_order(current_price)
# Define thresholds for RSI
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Define a function to make trade decisions
def make_trade_decision(rsi_value, close_price, support, resistance):
    if rsi_value is not None:
        # Check if RSI indicates oversold and price is near support level
        if rsi_value < RSI_OVERSOLD and close_price <= support:
            print("Buy signal triggered: RSI oversold and price near support level.")
            # Place buy order logic here
            # client.order_market_buy(...)
        # Check if RSI indicates overbought and price is near resistance level
        elif rsi_value > RSI_OVERBOUGHT and close_price >= resistance:
            print("Sell signal triggered: RSI overbought and price near resistance level.")
            # Place sell order logic here
            # client.order_market_sell(...)
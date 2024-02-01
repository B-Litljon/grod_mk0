# Define thresholds for RSI
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Define your risk parameters
MAX_RISK_PER_TRADE = 0.02  # 2% of total capital at risk per trade
TOTAL_CAPITAL = 1000  # Total trading capital

# Define a function to calculate trade size based on risk and stop distance
def calculate_trade_size(entry_price, stop_loss_price, total_capital, max_risk_per_trade, position='long'):
    risk_per_share = entry_price - stop_loss_price if position == 'long' else stop_loss_price - entry_price
    shares_to_buy = (total_capital * max_risk_per_trade) / risk_per_share
    return shares_to_buy

# Update the make_trade_decision function to include Bollinger Band width for determining 'power'
def make_trade_decision(rsi_value, close_price, lower_band, middle_band, upper_band, total_capital, max_risk_per_trade, volume, moving_average):
    # Calculate Bollinger Band width
    band_width = upper_band - lower_band

    # Define stop loss and take profit levels based on Bollinger Bands and market conditions
    stop_loss_long = lower_band * 0.98  # 2% below the lower band for long positions
    stop_loss_short = upper_band * 1.02  # 2% above the upper band for short positions
    take_profit_long = middle_band * 0.99  # Slightly below the middle band for long positions
    take_profit_short = middle_band * 1.01  # Slightly above the middle band for short positions

    # Adjust stop-loss and take-profit levels based on Bollinger Band width
    if band_width > moving_average:  # Wide bands indicate high volatility
        stop_loss_long *= 1.02  # Loosen stop loss in high volatility
        take_profit_long *= 1.02  # Increase take profit in high volatility
    elif band_width < moving_average:  # Narrow bands indicate low volatility
        stop_loss_short *= 0.98  # Tighten stop loss in low volatility
        take_profit_short *= 0.98  # Decrease take profit in low volatility

    # Check if RSI indicates oversold and price is near the lower Bollinger Band
    if rsi_value < RSI_OVERSOLD and close_price <= lower_band:
        print("Buy signal triggered: RSI oversold and price near lower Bollinger Band.")
        # Calculate the number of shares to buy
        shares_to_buy = calculate_trade_size(close_price, stop_loss_long, total_capital, max_risk_per_trade, position='long')
        # Place buy order logic here
        # client.create_order(symbol='BTCUSDT', side='BUY', type='LIMIT', quantity=shares_to_buy, price=close_price)

    # Check if RSI indicates overbought and price is near the upper Bollinger Band
    elif rsi_value > RSI_OVERBOUGHT and close_price >= upper_band:
        print("Sell signal triggered: RSI overbought and price near upper Bollinger Band.")
        # Calculate the number of shares to sell
        shares_to_sell = calculate_trade_size(close_price, stop_loss_short, total_capital, max_risk_per_trade, position='short')
        # Place sell order logic here
        # client.create_order(symbol='BTCUSDT', side='SELL', type='LIMIT', quantity=shares_to_sell, price=close_price)

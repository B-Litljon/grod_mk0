import pandas as pd
class RSI:
    """
A class for calculating and updating the Relative Strength Index (RSI) and checking for divergences.

Instantiate the class by creating an instance of RSI:
    rsi = RSI(period=14)

Args:
    period (int): The number of periods to consider for RSI calculation. Default is 13.

The class provides methods to update the RSI with new price data and check for bullish or bearish divergences.

To update the RSI with a new price and the previous price:
    current_rsi = rsi.update(new_price, previous_price)

The `update` method returns the current RSI value.

To check for divergences:
    divergence = rsi.check_divergence(current_price)

The `check_divergence` method takes the current price as an argument and returns:
    - 'bullish divergence' if the price is increasing but RSI is decreasing.
    - 'bearish divergence' if the price is decreasing but RSI is increasing.
    - None if no divergence is detected or there is insufficient data.

Note: The RSI is calculated using the specified period, and the class maintains a history of gains and losses.
      At least two price data points are required for divergence checking.
"""
    def __init__(self, period=13):
        self.period = period
        self.gains = []
        self.losses = []

    def update(self, new_price, previous_price):
        delta = new_price - previous_price
        gain = max(delta, 0)
        loss = abs(min(delta, 0))
        
        self.gains.append(gain)
        self.losses.append(loss)
        
        if len(self.gains) > self.period:
            self.gains.pop(0)
            self.losses.pop(0)
        
        avg_gain = sum(self.gains) / self.period
        avg_loss = sum(self.losses) / self.period
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def check_divergence(self, price):
        if len(self.prices) < 2:
            return None
        
        current_price = price
        previous_price = self.prices[-1]
        current_rsi = self.rsi_values[-1]
        previous_rsi = self.rsi_values[-2]

        if current_price > previous_price and current_rsi < previous_rsi:
            return 'bullish divergence' # signals the price is not following the rsi and is likely to reverse away from the bull trend short term
        elif current_price < previous_price and current_rsi > previous_rsi:
            return 'bearish divergence' 
        else:
            return None

# add logic to calculate divergence between the rsi and the price
# rsi crossover generate signals if the rsi crosses over the 30 or 70 line
# rsi trend eg: if the rsi is consistently above 50 for a while that could mean bullish trend or vice versa
# rsi smoothing, common smoothing teks include sma or exponential moving average    

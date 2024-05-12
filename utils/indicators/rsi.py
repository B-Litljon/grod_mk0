
import numpy as np

class RSI:
    def __init__(self, period=13):
        self.period = period
        self.gains = np.array([])
        self.losses = np.array([])
        self.prices = np.array([])
        self.values = np.array([])

    def update(self, new_price, previous_price):
        delta = new_price - previous_price
        gain = max(delta, 0)
        loss = abs(min(delta, 0))
        
        self.gains = np.append(self.gains, gain)
        self.losses = np.append(self.losses, loss)
        self.prices = np.append(self.prices, new_price)
        
        if len(self.gains) > self.period:
            self.gains = self.gains[-self.period:]
            self.losses = self.losses[-self.period:]
        
        avg_gain = np.mean(self.gains)
        avg_loss = np.mean(self.losses)
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        self.values = np.append(self.values, rsi)

        return rsi
    
    def check_divergence(self, price):
        if len(self.prices) < 2:
            return None

        current_price = price
        previous_price = self.prices[-2]
        current_rsi = self.values[-1]
        previous_rsi = self.values[-2]

        if current_price > previous_price and current_rsi < previous_rsi:
            return 'bullish divergence'
        elif current_price < previous_price and current_rsi > previous_rsi:
            return 'bearish divergence'
        else:
            return None

# add logic to calculate divergence between the rsi and the price
# rsi crossover generate signals if the rsi crosses over the 30 or 70 line
# rsi trend eg: if the rsi is consistently above 50 for a while that could mean bullish trend or vice versa
# rsi smoothing, common smoothing teks include sma or exponential moving average    

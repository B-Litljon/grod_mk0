
class RSI:
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

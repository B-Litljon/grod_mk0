import numpy as np
import pandas as pd


class RSI:
    def __init__(self, period=14):
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






# def calculate_rsi(prices, period=14):
#     """
#     Calculate the Relative Strength Index (RSI) for a given set of prices.
    
#     :param prices: A pandas Series of prices.
#     :param period: The period over which to calculate RSI.
#     :return: A pandas Series representing the RSI.
#     """
#     delta = prices.diff(1)
#     gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi
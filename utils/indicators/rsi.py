import numpy as np
import pandas as pd

def calculate_rsi(prices, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a given set of prices.
    
    :param prices: A pandas Series of prices.
    :param period: The period over which to calculate RSI.
    :return: A pandas Series representing the RSI.
    """
    delta = prices.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
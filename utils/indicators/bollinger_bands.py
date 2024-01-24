import numpy as np
import pandas as pd

def calculate_bollinger_bands(prices, window=20, num_of_std=2):
    """
    Calculate Bollinger Bands for a given set of prices.
    
    :param prices: A pandas Series of prices.
    :param window: The moving average window size.
    :param num_of_std: Number of standard deviations for the bands.
    :return: A DataFrame with Bollinger Bands (upper_band, lower_band, middle_band).
    """
    middle_band = prices.rolling(window=window).mean()
    std_dev = prices.rolling(window=window).std()
    
    upper_band = middle_band + (std_dev * num_of_std)
    lower_band = middle_band - (std_dev * num_of_std)
    
    return pd.DataFrame({'upper_band': upper_band, 'middle_band': middle_band, 'lower_band': lower_band})
import numpy as np
import pandas as pd

def find_support_resistance(prices, window=14):
    """
    Identify potential support and resistance levels by finding local minima and maxima.
    
    :param prices: A pandas DataFrame with 'high' and 'low' price columns.
    :param window: The window size to identify local minima and maxima.
    :return: A DataFrame with potential support and resistance levels.
    """
    # Use shift to compare against future and past values within the window
    minima = prices['low'].rolling(window=window, center=True).apply(lambda x: np.nan if np.nanmin(x) != x[int(window/2)] else np.nanmin(x), raw=True)
    maxima = prices['high'].rolling(window=window, center=True).apply(lambda x: np.nan if np.nanmax(x) != x[int(window/2)] else np.nanmax(x), raw=True)
    
    # Drop NaN values to clean up the DataFrame
    support = minima.dropna()
    resistance = maxima.dropna()
    
    return pd.DataFrame({'support': support, 'resistance': resistance})


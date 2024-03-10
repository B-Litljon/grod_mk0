
import pandas as pd


class BollingerBands:
    def __init__(self, window=30, num_of_std=2):
        self.window = window
        self.num_of_std = num_of_std
        self.prices = []
        self.mean = 0
        self.std_dev = 0

    def update(self, new_price):
        self.prices.append(new_price)
        if len(self.prices) > self.window:
            self.prices.pop(0)
        
        prices_series = pd.Series(self.prices)
        self.mean = prices_series.mean()
        self.std_dev = prices_series.std()
        
        upper_band = self.mean + (self.std_dev * self.num_of_std)
        lower_band = self.mean - (self.std_dev * self.num_of_std)
        band_width = upper_band - lower_band

        self.upper_bands.append(upper_band)
        self.middle_bands.append(self.mean)
        self.lower_bands.append(lower_band)
        self.band_widths.append(band_width)
        
        return upper_band, self.mean, lower_band
    
    def calculate_rolling_average_bandwidth(self, rolling_window=5):
        if len(self.bandwidths) < rolling_window:
            return None 
        rolling_avg = pd.Series(self.bandwidths).rolling(window=rolling_window).mean().iloc[-1]
        return rolling_avg

import pandas as pd


class BollingerBands:
    def __init__(self, window=30, num_of_std=2):
        self.window = window
        self.num_of_std = num_of_std
        self.prices = []
        self.mean = 0
        self.std_dev = 0
    # this method is good for testing, but in the real world we will need to implement logic to request enough data from the api to calculate the bollinger bands in the first place
        # as it stands now the bollinger bands will not be calculated until the window is filled with data, which is not ideal for trading, it would take like 20-30 minutes to get the first bollinger band
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
    # note: you can utilize this method using different periods to make a mini bollinger band for the upper and lower bands to aid in spotting trends in the data 
    # basically using it to determine areas of support and resistance in your upper and lower bands # 
    
    # gets the averge of the band width over a period of time
    def calculate_rolling_average_bandwidth(self, rolling_window=5):
        if len(self.bandwidths) < rolling_window:
            return None 
        rolling_avg = pd.Series(self.bandwidths).rolling(window=rolling_window).mean().iloc[-1]
        return rolling_avg
    # gets the rate of change of the bandwidth 
    def calculate_bandwidth_roc(self, period=2):  # rate of change of the bandwidth, checks the last two data points for the calculation
        if len(self.bandwidths) >= period:
            return (self.bandwidths[-1] - self.bandwidths[-period]) / self.bandwidths[-period]
        else:
            return None
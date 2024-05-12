
import numpy as np

class BollingerBands:
    def __init__(self, window=30, num_of_std=2):
       self.window = window
       self.num_of_std = num_of_std
       self.prices = np.array([])
       self.upper_band = np.array([])
       self.middle_band = np.array([])
       self.lower_band = np.array([])
       self.band_width = np.array([])

    def update(self, new_price):
        # Append the new price
        self.prices = np.append(self.prices, new_price)

        # Ensure we have enough price data to perform calculations
        if len(self.prices) >= self.window:
            # Calculate mean and standard deviation over the window
            self.middle_band = np.append(self.middle_band, np.mean(self.prices[-self.window:]))
            std_dev = np.std(self.prices[-self.window:])

            # Calculate upper and lower bands
            self.upper_band = np.append(self.upper_band, self.middle_band[-1] + (std_dev * self.num_of_std))
            self.lower_band = np.append(self.lower_band, self.middle_band[-1] - (std_dev * self.num_of_std))

            # Calculate band width
            self.band_width = np.append(self.band_width, self.upper_band[-1] - self.lower_band[-1])

            # Return the latest Bollinger Bands
            return self.upper_band[-1], self.middle_band[-1], self.lower_band[-1]
        else:
            return None, None, None

    def calculate_bandwidth_roc(self, rolling_window=5, period=2):
        if len(self.band_width) >= rolling_window + period - 1:
            # Calculate the rolling average of bandwidths
            rolling_avg_bandwidths = np.convolve(self.band_width, np.ones(rolling_window) / rolling_window, mode='valid')

            # Calculate ROC using the specified period
            roc = (rolling_avg_bandwidths[-1] - rolling_avg_bandwidths[-period]) / rolling_avg_bandwidths[-period]
            return roc
        else:
            return None


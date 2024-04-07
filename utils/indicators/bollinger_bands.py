
import numpy as np

class BollingerBands:
    def __init__(self, window=30, num_of_std=2):
       self.window = window
       self.num_of_std = num_of_std
       self.prices = np.array([])
       self.upper_band = np.array([])
       self.middle_band = np.array([])
       self.lower_band = np.array([])

    def update(self, new_price):
        # Append the new price
        new_row = {'price': new_price}
        self.data = self.data.append(new_row, ignore_index=True)

        # Ensure we have enough data to perform calculations
        if len(self.data) >= self.window:
            # Calculate mean and standard deviation over the window
            self.data['middle_band'] = self.data['price'].rolling(window=self.window).mean()
            std_dev = self.data['price'].rolling(window=self.window).std()

            # Calculate upper and lower bands
            self.data['upper_band'] = self.data['middle_band'] + (std_dev * self.num_of_std)
            self.data['lower_band'] = self.data['middle_band'] - (std_dev * self.num_of_std)

            # Calculate band width
            self.data['band_width'] = self.data['upper_band'] - self.data['lower_band']

        # Return the latest Bollinger Bands if available
        if self.data.iloc[-1].isnull().any():
            return None  # Not enough data yet
        else:
            return self.data.iloc[-1][['upper_band', 'middle_band', 'lower_band']]

    def calculate_bandwidth_roc(self, rolling_window=5, period=2):
        if len(self.data) >= rolling_window + period - 1:
            # Calculate the rolling average of bandwidths
            rolling_avg_bandwidths = self.data['band_width'].rolling(window=rolling_window).mean()

            # Calculate ROC using the specified period
            roc = (rolling_avg_bandwidths.iloc[-1] - rolling_avg_bandwidths.iloc[-period]) / rolling_avg_bandwidths.iloc[-period]
            return roc
        else:
            return None



import pandas as pd


class BollingerBands:
    """
    A class for calculating and updating Bollinger Bands.

    Instantiate the class by creating an instance of BollingerBands:
        bollinger_bands = BollingerBands(window=20, num_of_std=2)

    Args:
        window (int): The rolling window size for calculating the moving average and standard deviation. Default is 30.
        num_of_std (int): The number of standard deviations to use for the upper and lower bands. Default is 2.

    The class provides methods to update the Bollinger Bands with new price data and calculate the rate of change (ROC) of the average bandwidth.

    To update the Bollinger Bands with a new price:
        upper_band, middle_band, lower_band = bollinger_bands.update(new_price)

    To calculate the ROC of the average bandwidth:
        roc = bollinger_bands.calculate_bandwidth_roc(rolling_window=5, period=2)

    Note: The class requires a sufficient amount of price data to calculate the Bollinger Bands accurately. The bands will not be calculated until the window is filled with data.
    """
    def __init__(self, window=30, num_of_std=2):
        self.window = window
        self.num_of_std = num_of_std
        # Initialize a DataFrame to store price data and Bollinger Bands calculations
        self.data = pd.DataFrame(columns=['price', 'upper_band', 'middle_band', 'lower_band', 'band_width'])

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

class BollingerBands:
    def __init__(self, window=30, num_of_std=2):
        self.window = window
        self.num_of_std = num_of_std
        self.prices = []
        self.mean = 0
        self.std_dev = 0
        self.upper_band = []
        self.middle_band = []
        self.lower_band = []
        self.band_width = []
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

        self.upper_band.append(upper_band)
        self.middle_band.append(self.mean)
        self.lower_band.append(lower_band)
        self.band_width.append(band_width)
        
        return upper_band, self.mean, lower_band
    # note: you can utilize this method using different periods to make a mini bollinger band for the upper and lower bands to aid in spotting trends in the data 
    # basically using it to determine areas of support and resistance in your upper and lower bands # 
    
    
    # gets the rate of change of the average bandwidth 
    def calculate_bandwidth_roc(self, rolling_window=5, period=2):
        # First, ensure there's enough data to calculate the rolling average and ROC
        if len(self.band_widths) >= rolling_window + period - 1:
            # Calculate the rolling average of bandwidths up to the point of interest
            rolling_avg_bandwidths = pd.Series(self.band_widths).rolling(window=rolling_window).mean()
            # Calculate ROC based on the last two rolling average values
            current_rolling_avg_bandwidth = rolling_avg_bandwidths.iloc[-1]
            previous_rolling_avg_bandwidth = rolling_avg_bandwidths.iloc[-period]
            roc = (current_rolling_avg_bandwidth - previous_rolling_avg_bandwidth) / previous_rolling_avg_bandwidth
            return roc
        else:
            return None

        


   
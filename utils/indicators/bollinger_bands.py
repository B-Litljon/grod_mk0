
import numpy as np

class BollingerBands:
    """
    A class for calculating and updating Bollinger Bands.

    Bollinger Bands are a technical analysis tool that consists of three lines:
    the middle band (a simple moving average), the upper band (middle band + a
    number of standard deviations), and the lower band (middle band - a number
    of standard deviations). The bands adapt to volatility changes in the
    underlying price series.

    Attributes:
        window (int): The window size for calculating the middle band (default: 30).
        num_of_std (int): The number of standard deviations for the upper and lower bands (default: 2).
        prices (numpy.ndarray): An array to store the price data.
        upper_band (numpy.ndarray): An array to store the calculated upper band values.
        middle_band (numpy.ndarray): An array to store the calculated middle band values.
        lower_band (numpy.ndarray): An array to store the calculated lower band values.
        band_width (numpy.ndarray): An array to store the calculated band width values.
    """
    def __init__(self, window=30, num_of_std=2):
       self.window = window
       self.num_of_std = num_of_std
       self.prices = np.array([])
       self.upper_band = np.array([])
       self.middle_band = np.array([])
       self.lower_band = np.array([])
       self.band_width = np.array([])

    def update(self, new_price):
        """
        Update the Bollinger Bands with a new price data point.

        This method appends the new price to the prices array and calculates the updated
        Bollinger Bands (upper band, middle band, lower band) based on the window size and
        the number of standard deviations. It also calculates the band width.

        Args:
            new_price (float): The new price data point.

        Returns:
            tuple: A tuple containing the latest values of the upper band, middle band,
                   and lower band. If there is not enough price data to perform the
                   calculations, it returns (None, None, None).
        """
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
        """
        Calculate the rate of change (ROC) of the bandwidth.

        This method calculates the rate of change of the bandwidth over a specified period,
        using a rolling average of bandwidths. The ROC measures the percentage change in
        the bandwidth compared to a previous point in time.

        Args:
            rolling_window (int): The window size for calculating the rolling average of bandwidths (default: 5).
            period (int): The number of periods to use for calculating the ROC (default: 2).

        Returns:
            float or None: The calculated rate of change (ROC) of the bandwidth. If there
                           is not enough data to perform the calculation, it returns None.
        """
        if len(self.band_width) >= rolling_window + period - 1:
            # Calculate the rolling average of bandwidths
            rolling_avg_bandwidths = np.convolve(self.band_width, np.ones(rolling_window) / rolling_window, mode='valid')

            # Calculate ROC using the specified period
            roc = (rolling_avg_bandwidths[-1] - rolling_avg_bandwidths[-period]) / rolling_avg_bandwidths[-period]
            return roc
        else:
            return None


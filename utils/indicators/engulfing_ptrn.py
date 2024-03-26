
class EngulfingPatternDetector:
    """
A class for detecting bullish and bearish engulfing candlestick patterns in a given DataFrame.

Instantiate the class by creating an instance of EngulfingPatternDetector:
    detector = EngulfingPatternDetector(dataframe)

Args:
    dataframe (pandas.DataFrame): A DataFrame containing candlestick data with columns 'Open' and 'Close'.

The class provides methods to check for the presence of bullish and bearish engulfing patterns in the last two candles of the DataFrame.

To check for a bullish engulfing pattern:
    is_bullish = detector.is_bullish_engulfing()

To check for a bearish engulfing pattern:
    is_bearish = detector.is_bearish_engulfing()

The methods return a boolean value indicating whether the respective engulfing pattern is present (True) or not (False).

Note: The DataFrame must contain at least two rows of data for the engulfing pattern detection to work.
"""
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def is_bullish_engulfing(self):
        if len(self.dataframe) < 2:
            return False

        # Access the last two candles
        last_candle = self.dataframe.iloc[-1]
        prev_candle = self.dataframe.iloc[-2]

        # Bullish Engulfing Criteria
        is_bearish_prev_candle = prev_candle['Close'] < prev_candle['Open']
        is_bullish_last_candle = last_candle['Close'] > last_candle['Open']
        engulfing_condition = last_candle['Open'] < prev_candle['Close'] and last_candle['Close'] > prev_candle['Open']

        return is_bearish_prev_candle and is_bullish_last_candle and engulfing_condition

    def is_bearish_engulfing(self):
        if len(self.dataframe) < 2:
            return False

        # Access the last two candles
        last_candle = self.dataframe.iloc[-1]
        prev_candle = self.dataframe.iloc[-2]

        # Bearish Engulfing Criteria
        is_bullish_prev_candle = prev_candle['Close'] > prev_candle['Open']
        is_bearish_last_candle = last_candle['Close'] < last_candle['Open']
        engulfing_condition = last_candle['Open'] > prev_candle['Close'] and last_candle['Close'] < prev_candle['Open']

        return is_bullish_prev_candle and is_bearish_last_candle and engulfing_condition

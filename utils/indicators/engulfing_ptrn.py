
class EngulfingPatternDetector:
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

from bollinger_bands import BollingerBands
from rsi import RSI

class Triggers:
    """
    The Triggers class is designed to implement trading strategies based on technical analysis indicators such as Bollinger Bands and RSI (Relative Strength Index).
    It provides methods to check for specific market conditions like RSI divergence, bullish engulfing patterns, and a combined strategy involving RSI and Bollinger Band expansion.

    Attributes:
        bollinger_bands (BollingerBands): An instance of a BollingerBands class containing the upper, middle, and lower bands.
        rsi_values (list): A list of RSI values.
        price_data (list): A list of dictionaries containing price data with keys 'open', 'close', 'high', and 'low'.
        stage_one_triggered (bool): A flag to indicate if the first stage of the rsi_and_bb_expansion_strategy has been triggered.

    Methods:
        rsi_divergence_strategy: To be implemented for RSI divergence strategy.
        is_bullish_engulfing: Checks for a bullish engulfing pattern in the latest two candles.
        rsi_and_bb_expansion_strategy: Checks for a trading signal based on RSI values, Bollinger Band expansion, and bullish engulfing pattern.

    To properly instantiate this class, provide it with the current Bollinger Bands, RSI values, and price data like so:
    triggers_instance = Triggers(bollinger_bands_instance, rsi_values_list, price_data_list)
    """
    def __init__(self, bollinger_bands, rsi_values, price_data):
        self.bollinger_bands = bollinger_bands
        self.rsi_values = rsi_values
        self.price_data = price_data
        self.stage_one_triggered = False

    def rsi_divergence_strategy(self):
        # Implement logic for RSI divergence strategy
        pass

    def is_bullish_engulfing(self):
        if len(self.price_data) < 2:
            return False

        current_candle = self.price_data[-1]
        previous_candle = self.price_data[-2]

        if current_candle['close'] > previous_candle['open'] and current_candle['open'] < previous_candle['close']:
            return True
        else:
            return False

    def rsi_and_bb_expansion_strategy(self):
        if not self.stage_one_triggered:
            # Stage 1: Check if price is below the lower Bollinger Band and RSI is oversold
            current_price = self.price_data[-1]['close']
            lower_band = self.bollinger_bands.lower_bands[-1]
            if current_price < lower_band and self.rsi_values[-1] <= 25:
                self.stage_one_triggered = True
            else:
                return False

        # Stage 2: Check if RSI is back in the normal range, Bollinger Bands are expanding, and bullish engulfing pattern
        if self.stage_one_triggered:
            if 30 <= self.rsi_values[-1] < 35:
                # Utilize the calculate_bandwidth_roc method to check for Bollinger Bands expansion
                # Assuming a positive ROC indicates expansion. Adjust the threshold as needed.
                bandwidth_roc = self.bollinger_bands.calculate_bandwidth_roc()
                if bandwidth_roc is not None and bandwidth_roc > 0.15:  # Example threshold for ROC
                    if self.is_bullish_engulfing():
                        self.stage_one_triggered = False  # Reset stage one trigger
                        return True

        return False
    

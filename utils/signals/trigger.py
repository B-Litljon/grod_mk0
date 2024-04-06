from utils.indicators.bollinger_bands import BollingerBands
from utils.indicators.rsi import RSI
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Triggers:
    """
A class for implementing trading strategies based on technical analysis indicators such as Bollinger Bands and RSI.

Instantiate the class by creating an instance of Triggers:
    triggers = Triggers(bollinger_bands, rsi_values, price_data)

Args:
    bollinger_bands (BollingerBands): An instance of the BollingerBands class containing the upper, middle, and lower bands.
    rsi_values (list): A list of RSI values.
    price_data (list): A list of dictionaries containing price data with keys 'open', 'close', 'high', and 'low'.

The `Triggers` class provides methods to check for specific market conditions and generate trading signals based on
various strategies involving RSI, Bollinger Bands, and candlestick patterns.

Available methods:
    - `rsi_divergence_strategy()`: To be implemented for RSI divergence strategy.
    - `is_bullish_engulfing()`: Checks for a bullish engulfing pattern in the latest two candles.
    - `rsi_and_bb_expansion_strategy()`: Checks for a trading signal based on RSI values, Bollinger Band expansion, and
                                         bullish engulfing pattern.

The `rsi_and_bb_expansion_strategy()` method implements a two-stage strategy:
    1. Stage 1: Checks if the price is below the lower Bollinger Band and RSI is oversold (below 25).
    2. Stage 2: If Stage 1 is triggered, checks if RSI is back in the normal range (between 30 and 35),
                Bollinger Bands are expanding (based on the ROC of the bandwidth), and a bullish engulfing pattern is present.

If both stages are satisfied, the method returns True, indicating a potential trading signal.

Example usage:
    # Create instances of BollingerBands and Triggers
    bollinger_bands = BollingerBands(window=20, num_of_std=2)
    triggers = Triggers(bollinger_bands, rsi_values, price_data)
    
    # Check for trading signals
    if triggers.rsi_and_bb_expansion_strategy():
        # Execute trade based on the signal
        pass

Note: The `rsi_divergence_strategy()` method is not yet implemented and needs to be defined based on the specific
      requirements of the RSI divergence strategy.
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

    def rsi_and_bb_expansion_strategy(self, bbands, rsi, dataframe):
        if not self.stage_one_triggered:
            # Stage 1: Check if price is below the lower Bollinger Band and RSI is oversold
            current_price = self.price_data[-1]['close']
            lower_band = self.bollinger_bands.lower_bands[-1]
            if current_price < lower_band and self.rsi_values[-1] <= 25:
                self.stage_one_triggered = True
                logger.info(f"Stage 1 triggered: Price ({current_price}) below lower band ({lower_band}) and RSI ({self.rsi_values[-1]}) oversold")
            else:
                logger.debug(f"Stage 1 not triggered: Price ({current_price}) above lower band ({lower_band}) or RSI ({self.rsi_values[-1]}) not oversold")
                return False

        # Stage 2: Check if RSI is back in the normal range, Bollinger Bands are expanding, and bullish engulfing pattern            
        if self.stage_one_triggered:
            if 30 <= self.rsi_values[-1] < 35:
                # Utilize the calculate_bandwidth_roc method to check for Bollinger Bands expansion
                # Assuming a positive ROC indicates expansion. Adjust the threshold as needed.
                bandwidth_roc = self.bollinger_bands.calculate_bandwidth_roc()
                if bandwidth_roc is not None and bandwidth_roc > 0.15:  # Example threshold for ROC
                    logger.info(f"Bollinger Bands expanding: Bandwidth ROC ({bandwidth_roc}) above threshold (0.15)")
                    if self.is_bullish_engulfing():
                        logger.info("Bullish engulfing pattern detected")
                        self.stage_one_triggered = False  # Reset stage one trigger
                        logger.info("RSI and Bollinger Bands expansion strategy triggered")
                        return True
                    else:
                        logger.debug("Bullish engulfing pattern not detected")
                else:
                    logger.debug(f"Bollinger Bands not expanding: Bandwidth ROC ({bandwidth_roc}) below threshold (0.15)")
            else:
                logger.debug(f"RSI ({self.rsi_values[-1]}) not in the normal range (30-35)")
        return False
    
# dev note: you may need to incorporate some logic to limit the window of time stage two has to trigger, 
            # it is very possible that stage two will trigger even if it shouldn't in this current implementation
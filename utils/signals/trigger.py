from utils.indicators.bollinger_bands import BollingerBands
from utils.indicators.rsi import RSI
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Triggers:
    def __init__(self, bollinger_bands, rsi_values, price_data):
        self.bollinger_bands = bollinger_bands
        self.rsi_values = rsi_values
        self.price_data = price_data
        self.stage_one_triggered = False

    def rsi_divergence_strategy(self):
        # Implement logic for RSI divergence strategy
        pass

    def is_bullish_engulfing(self, dataframe):
        if len(dataframe) < 2:
            return False

        current_candle = dataframe.iloc[-1]
        previous_candle = dataframe.iloc[-2]    

        if current_candle['close'] > previous_candle['open'] and current_candle['open'] < previous_candle['close']:
            return True
        else:
            return False

    def rsi_and_bb_expansion_strategy(self, bbands, rsi, dataframe):
        if not self.stage_one_triggered:
            # Stage 1: Check if price is below the lower Bollinger Band and RSI is oversold
            current_price = dataframe['close'].iloc[-1]
            lower_band = bbands.lower_bands[-1]
            if current_price < lower_band and rsi.values[-1] <= 25:
                self.stage_one_triggered = True
                logger.info(f"Stage 1 triggered: Price ({current_price}) below lower band ({lower_band}) and RSI ({rsi.values[-1]}) oversold")
            else:
                logger.debug(f"Stage 1 not triggered: Price ({current_price}) above lower band ({lower_band}) or RSI ({rsi.values[-1]}) not oversold")
                return False

        # Stage 2: Check if RSI is back in the normal range, Bollinger Bands are expanding, and bullish engulfing pattern            
        if self.stage_one_triggered:
            if 30 <= rsi.values[-1] < 35:
                # Utilize the calculate_bandwidth_roc method to check for Bollinger Bands expansion
                # Assuming a positive ROC indicates expansion. Adjust the threshold as needed.
                bandwidth_roc = bbands.calculate_bandwidth_roc()
                if bandwidth_roc is not None and bandwidth_roc > 0.15:  # Example threshold for ROC
                    logger.info(f"Bollinger Bands expanding: Bandwidth ROC ({bandwidth_roc}) above threshold (0.15)")
                    if self.is_bullish_engulfing(dataframe):
                        logger.info("Bullish engulfing pattern detected")
                        self.stage_one_triggered = False  # Reset stage one trigger
                        logger.info("RSI and Bollinger Bands expansion strategy triggered")
                        return True
                    else:
                        logger.debug("Bullish engulfing pattern not detected")
                else:
                    logger.debug(f"Bollinger Bands not expanding: Bandwidth ROC ({bandwidth_roc}) below threshold (0.15)")
            else:
                logger.debug(f"RSI ({rsi.values[-1]}) not in the normal range (30-35)")
        return False
    
# dev note: you may need to incorporate some logic to limit the window of time stage two has to trigger, 
            # it is very possible that stage two will trigger even if it shouldn't in this current implementation
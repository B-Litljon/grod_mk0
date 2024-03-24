class Triggers:
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
            if self.rsi_values[-1] >= 30 and self.rsi_values[-1] < 35:
                current_bandwidth = self.bollinger_bands.band_widths[-1]
                rolling_avg_bandwidth = self.bollinger_bands.calculate_rolling_average_bandwidth()
                if current_bandwidth > rolling_avg_bandwidth * 1.15:  # Example of 15% expansion
                    if self.is_bullish_engulfing():
                        self.stage_one_triggered = False  # Reset stage one trigger
                        return True

        return False
    

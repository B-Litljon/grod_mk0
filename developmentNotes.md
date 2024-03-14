# Trading Strategy

## Indicators

- [ ] Bollinger Bands (Energy powering price movements)
  - [ ] Calculate upper, middle, and lower bands based on price data
  - [ ] Implement methods to calculate rolling average bandwidth and rate of change of bandwidth
  - [ ] Use different periods to create mini Bollinger Bands for upper and lower bands to identify support/resistance levels

- [ ] RSI (Direction of the firearm)
  - [ ] Use RSI to determine the direction of price movement
  - [ ] Wait for RSI to return to normal range (e.g., 35-40) after being oversold (e.g., below 25)

## Buy Signal

- [ ] Generate buy signal when:
  - [ ] RSI is back within the normal range
  - [ ] Bollinger Bands are expanding significantly based on defined criteria

## Order Placement

- [ ] Use `OrderCalculator` class to calculate order size based on risk management parameters
- [ ] Call `place_order` method to execute buy order on the exchange

## Risk Management

- [ ] Use `TradeConfig` class to hold trading strategy configuration
  - [ ] Define RSI oversold/overbought levels
  - [ ] Set maximum risk per trade
  - [ ] Set total capital

- [ ] Use `OrderCalculator` class to calculate order size based on risk per trade and entry/stop-loss prices
- [ ] Implement `purchased_asset` method to keep track of purchased assets

## Code Organization

- [ ] Separate concerns:
  - [ ] Keep indicator calculations (Bollinger Bands, RSI) in separate classes or modules
  - [ ] Create a separate class or module for trading logic and signal generation
  - [ ] Use `OrderCalculator` class for risk management and order placement

- [ ] Data management:
  - [ ] Implement reliable methods to fetch and store historical price data
  - [ ] Ensure efficient data handling and storage mechanisms

- [ ] Backtesting and optimization:
  - [ ] Perform backtesting on historical data to validate strategy performance
  - [ ] Optimize indicator parameters and trading rules based on backtesting results

- [ ] Error handling and logging:
  - [ ] Implement robust error handling to handle exceptions and unexpected situations
  - [ ] Use logging to track algorithm behavior, decisions, and errors

- [ ] Modular and reusable code:
  - [ ] Break down code into smaller, reusable functions and classes
  - [ ] Ensure each component has a clear responsibility and is easily testable

- [ ] Documentation and comments:
  - [ ] Provide clear documentation for code, explaining purpose and functionality
  - [ ] Use comments to clarify complex logic or algorithms

## Deployment and Monitoring

- [ ] Test code thoroughly before deploying
- [ ] Start with small amounts of capital in live trading environment
- [ ] Continuously monitor algorithm performance and make adjustments as needed

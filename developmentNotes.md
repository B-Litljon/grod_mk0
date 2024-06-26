# Trading Bot Development Checklist

## Integrate Trigger Conditions

- Import the Triggers class [X]
- Create an instance of the Triggers class [X]
- Modify the `check_signal` method to use the `rsi_and_bb_expansion_strategy` [X]

## Update Order Placement

- Modify the `place_order` method to generate unique order IDs [X]
- Update the `place_order` method to store order details in a dictionary [X]

## Implement Data Persistence

- add methods to store price data to csv after it fills the websocket dataframe [X]
- add method to store order information into order calculation [X]

## Update Order Management
- Modify the `sell_order` method to retrieve order details [X]
- Calculate profit/loss and duration based on stored order details [X]
- Update order status in the dictionary to "complete" [X]
- Call `DatabaseHandler` method to store completed order details [X]

# Create higher level 'BOT' class.
- import websocket class [x]
 

## Error Handling and Logging
- Import the logging module [x]
- Set up a logger with appropriate levels [x]
- Add log statements throughout your code []
- Implement error handling using try-except blocks []


## Integration and Testing
- implement 'live tuning' []
    ### live tuning:
        live tuning will allow you to tweak parameters while the bot is running
        and test the results to make for a smoother debugging experience.
        will also help making the bot profitable faster... 
        maybe machine learning would make more sense in this case? idk, we'll see 

- Integrate all updated components into your `BinanceWebsocketStream` class [x]
- Test your bot with a small amount of capital or in paper trading []
- Monitor logs and database to verify order functionality []

## Multiple Currency Support (Future Enhancement)

- Refactor code to allow multiple `BinanceWebsocketStream` instances []
- Modify the `start` method to accept currency pair parameters []
- Create instances for each desired currency pair and start them simultaneously []

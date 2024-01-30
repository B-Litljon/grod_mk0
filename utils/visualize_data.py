# # Global DataFrame to accumulate data
# data_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'RSI', 'UpperBB', 'MiddleBB', 'LowerBB', 'Support', 'Resistance'])

# # Initialize Plotly figure
# fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, subplot_titles=('Candlesticks with Bollinger Bands', 'RSI'))
# fig.add_trace(go.Candlestick(x=[], open=[], high=[], low=[], close=[], name='Candlesticks'), row=1, col=1)
# fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Upper Band'), row=1, col=1)
# fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Middle Band'), row=1, col=1)
# fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Lower Band'), row=1, col=1)
# fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='RSI'), row=2, col=1)
# fig.update_layout(xaxis_rangeslider_visible=False, height=800)

# def update_plot():
#     fig.data[0].x = data_df['Time']
#     fig.data[0].open = data_df['Open']
#     fig.data[0].high = data_df['High']
#     fig.data[0].low = data_df['Low']
#     fig.data[0].close = data_df['Close']

#     fig.data[1].x = data_df['Time']
#     fig.data[1].y = data_df['UpperBB']

#     fig.data[2].x = data_df['Time']
#     fig.data[2].y = data_df['MiddleBB']

#     fig.data[3].x = data_df['Time']
#     fig.data[3].y = data_df['LowerBB']

#     fig.data[4].x = data_df['Time']
#     fig.data[4].y = data_df['RSI']

#     fig.show()
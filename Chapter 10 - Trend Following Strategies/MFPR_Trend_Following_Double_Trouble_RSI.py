
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'
lookback = 10
lookback_rsi = 14

# Importing the asset as an array
my_data = mass_import(pair, horizon)

# Calculating the ATR
my_data = atr(my_data, lookback, 1, 2, 3, 4)
my_data = rsi(my_data, lookback_rsi, 3, 5)


# Creating the signal function
def signal(data, open_column, high_column, low_column, close_column, atr_column, rsi_column, buy_column, sell_column):

    data = add_column(data, 5)    
    
    for i in range(len(data)):  
        
       try:
           
           # Bullish pattern
           if data[i, close_column] > data[i, open_column] and \
              data[i, close_column] > data[i - 1, close_column] and \
              data[i - 1, close_column] > data[i - 1, open_column] and \
              data[i, high_column] - data[i, low_column] > (2 * data[i - 1, atr_column]) and \
              data[i, close_column] - data[i, open_column] > data[i - 1, close_column] - data[i - 1, open_column] and \
              data[i, buy_column] == 0 and \
              data[i, rsi_column] > 50:
                  
                    data[i + 1, buy_column] = 1 
                    
           # Bearish pattern
           elif data[i, close_column] < data[i, open_column] and \
              data[i, close_column] < data[i - 1, close_column] and \
              data[i - 1, close_column] < data[i - 1, open_column] and \
              data[i, high_column] - data[i, low_column] > (2 * data[i - 1, atr_column]) and \
              data[i, open_column] - data[i, close_column] > data[i - 1, open_column] - data[i - 1, close_column] and \
              data[i, sell_column] == 0 and \
              data[i, rsi_column] < 50:
                  
                    data[i + 1, sell_column] = -1 
                    
       except IndexError:
            
            pass
        
    return data

# Calling the signal function
my_data = signal(my_data, 0, 1, 2, 3, 4, 5, 6, 7)

# Charting the latest signals
signal_chart_indicator_plot_candles(my_data, 
                                    0, 
                                    5, 
                                    6, 
                                    7, 
                                    barriers = False,  
                                    window = 250)
plt.axhline(y = 50, color = 'black', linewidth = 1, linestyle = 'dashed')

# Performance
my_data = performance(my_data, 0, 6, 7, 8, 9, 10)

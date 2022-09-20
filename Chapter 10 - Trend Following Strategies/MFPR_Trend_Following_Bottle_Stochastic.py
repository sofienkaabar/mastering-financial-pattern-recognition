
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'
lookback = 14

# Importing the asset as an array
my_data = mass_import(pair, horizon)

my_data = stochastic_oscillator(my_data, 
                             lookback, 
                             1, 
                             2, 
                             3, 
                             4, 
                             slowing = True, 
                             smoothing = True, 
                             slowing_period = 3, 
                             smoothing_period = 3)

my_data = delete_column(my_data, 4, 1)

# Creating the signal function
def signal(data, open_column, high_column, low_column, close_column, 
            stochastic_column, signal_column, buy_column, sell_column):

    data = add_column(data, 5)    
    
    for i in range(len(data)):  
        
       try:
           
           # Bullish pattern
           if data[i, close_column] > data[i, open_column] and \
              data[i, open_column] == data[i, low_column] and \
              data[i - 1, close_column] > data[i - 1, open_column] and \
              data[i, open_column] < data[i - 1, close_column] and \
              data[i, stochastic_column] > data[i, signal_column] and \
              data[i, buy_column] == 0:
                  
                    data[i + 1, buy_column] = 1 
                    
           # Bearish pattern
           elif data[i, close_column] < data[i, open_column] and \
                data[i, open_column] == data[i, high_column] and \
                data[i - 1, close_column] < data[i - 1, open_column] and \
                data[i, open_column] > data[i - 1, close_column] and \
                data[i, stochastic_column] > data[i, signal_column] and \
                data[i, sell_column] == 0:
                  
                    data[i + 1, sell_column] = -1 
                    
       except IndexError:
            
            pass
        
    return data

# Calling the signal function
my_data = signal(my_data, 0, 1, 2, 3, 4, 5, 6, 7)

# Charting the latest signals
signal_chart_indicator_plot_candles(my_data, 
                                    0, 
                                    4, 
                                    6, 
                                    7, 
                                    barriers = False,  
                                    window = 250)
plt.plot(my_data[-250:, 5], color = 'orange')

# Performance
my_data = performance(my_data, 0, 6, 7, 8, 9, 10)
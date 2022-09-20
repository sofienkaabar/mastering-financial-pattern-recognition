
# Choosing the asset
pair = 8

# Time Frame
horizon = 'H1'
lookback = 3

# Importing the asset as an array
my_data = mass_import(pair, horizon)

my_data = k_candlesticks(my_data, 0, 1, 2, 3, lookback, 4)

# Creating the signal function
def signal(data, open_column, close_column, buy_column, sell_column):

    data = add_column(data, 5)
    
    for i in range(len(data)):
        
       try:
           
           # Bullish pattern
           if data[i, close_column] < data[i, open_column] and \
              data[i, close_column] < data[i - 1, open_column] and \
              data[i, close_column] > data[i - 2, close_column] and \
              data[i - 1, close_column] > data[i - 1, open_column] and \
              data[i - 1, open_column] > data[i - 2, close_column] and \
              data[i - 2, close_column] > data[i - 2, open_column]:
                  
                    data[i + 1, buy_column] = 1
                    
           # Bearish pattern
           elif data[i, close_column] > data[i, open_column] and \
                data[i, close_column] > data[i - 1, open_column] and \
                data[i, close_column] < data[i - 2, close_column] and \
                data[i - 1, close_column] < data[i - 1, open_column] and \
                data[i - 1, open_column] < data[i - 2, close_column] and \
                data[i - 2, close_column] < data[i - 2, open_column]:
                  
                    data[i + 1, sell_column] = -1
                    
       except IndexError:
            
            pass
        
    return data

my_data = signal(my_data, 4, 7, 8, 9)

k_candlestick_double_plot(my_data, 8, 9, window = 200)

# Performance
my_data = performance(my_data, 0, 8, 9, 10, 11, 12)

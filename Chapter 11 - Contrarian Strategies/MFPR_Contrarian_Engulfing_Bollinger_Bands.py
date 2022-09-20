
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'
lookback = 20
standard_deviation = 1

# Importing the asset as an array
my_data = mass_import(pair, horizon)

my_data = bollinger_bands(my_data, lookback, standard_deviation, 3, 4)

# Creating the signal function
def signal(data, open_column, close_column, upper_band_column, lower_band_column, buy_column, sell_column):

    data = add_column(data, 5)    
    
    for i in range(len(data)):  
        
       try:
           
           # Bullish setup
           if data[i, close_column] > data[i, open_column] and \
              data[i, open_column] < data[i - 1, close_column] and \
              data[i, close_column] > data[i - 1, open_column] and \
              data[i - 1, close_column] < data[i - 1, open_column] and \
              data[i - 2, close_column] < data[i - 2, open_column] and \
              data[i, close_column] < data[i, lower_band_column]:
                  
                    data[i + 1, buy_column] = 1 
                    
           # Bearish setup
           elif data[i, close_column] < data[i, open_column] and \
                data[i, open_column] > data[i - 1, close_column] and \
                data[i, close_column] < data[i - 1, open_column] and \
                data[i - 1, close_column] > data[i - 1, open_column] and \
                data[i - 2, close_column] > data[i - 2, open_column] and \
                data[i, close_column] > data[i, upper_band_column]:
                 
                    data[i + 1, sell_column] = -1 
                    
       except IndexError:
            
            pass
        
    return data

my_data = delete_column(my_data, 4, 1)

# Calling the signal function
my_data = signal(my_data, 0, 3, 4, 5, 6, 7)

# Charting the latest signals
signal_chart(my_data, 0, 6, 7, genre = 'candles', window = 250)
plt.plot(my_data[-250:, 4], color = 'blue')
plt.plot(my_data[-250:, 5], color = 'orange')

# Performance
my_data = performance(my_data, 0, 6, 7, 8, 9, 10)

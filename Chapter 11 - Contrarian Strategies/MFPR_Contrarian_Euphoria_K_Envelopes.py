
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'
lookback = 800

# Importing the asset as an array
my_data = mass_import(pair, horizon)

my_data = k_envelopes(my_data, lookback, 1, 2, 4)

# Creating the signal function
def signal(data, open_column, close_column, upper_k_envelope, lower_k_envelope, buy_column, sell_column):

    data = add_column(data, 5)  
    
    data = rounding(data, 4) # Put 0 instead of 4 as of pair 4
    
    for i in range(len(data)):  
        
       try:
           
           # Bullish setup
           if data[i, open_column] > data[i, close_column] and \
              data[i - 1, open_column] > data[i - 1, close_column] and \
              data[i - 2, open_column] > data[i - 2, close_column] and \
              data[i, close_column] < data[i - 1, close_column] and \
              data[i - 1, close_column] < data[i - 2, close_column] and \
              (data[i, open_column] - data[i, close_column]) > (data[i - 1, open_column] - data[i - 1, close_column]) and \
              (data[i - 1, open_column] - data[i - 1, close_column]) > (data[i - 2, open_column] - data[i - 2, close_column]) and \
              data[i, close_column] > data[i, lower_k_envelope] and data[i, close_column] < data[i, upper_k_envelope]: 
                  
                    data[i + 1, buy_column] = 1 
                    
           # Bearish setup
           elif data[i, open_column] < data[i, close_column] and \
                data[i - 1, open_column] < data[i - 1, close_column] and \
                data[i - 2, open_column] < data[i - 2, close_column] and \
                data[i, close_column] > data[i - 1, close_column] and \
                data[i - 1, close_column] > data[i - 2, close_column] and \
                (data[i, open_column] - data[i, close_column]) > (data[i - 1, open_column] - data[i - 1, close_column]) and \
                (data[i - 1, open_column] - data[i - 1, close_column]) > (data[i - 2, open_column] - data[i - 2, close_column]) and \
                data[i, close_column] > data[i, lower_k_envelope] and data[i, close_column] < data[i, upper_k_envelope]: 
                 
                    data[i + 1, sell_column] = -1 
                    
       except IndexError:
            
            pass
        
    return data

# Calling the signal function
my_data = signal(my_data, 0, 3, 4, 5, 6, 7)

# Charting the latest signals
signal_chart(my_data, 0, 6, 7, genre = 'candles', window = 110)
plt.plot(my_data[-110:, 4])
plt.plot(my_data[-110:, 5])

# Performance
my_data = performance(my_data, 0, 5, 6, 7, 8, 9)

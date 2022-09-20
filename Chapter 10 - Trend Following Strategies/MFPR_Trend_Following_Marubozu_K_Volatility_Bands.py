
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'
lookback = 20
multiplier = 2

# Importing the asset as an array
my_data = mass_import(pair, horizon)

'''
Use my_data = rounding(my_data, 4) for EURUSD, USDCHF, GBPUSD, USDCAD
Use my_data = rounding(my_data, 0) for BTCUSD, ETHUSD, XAUUSD, SP500m, UK100

'''

my_data = k_volatility_band(my_data, lookback, multiplier, 1, 2, 3, 4)

# Rounding
my_data = rounding(my_data, 4)

# Creating the signal function
def signal(data, open_column, high_column, low_column, close_column, 
            middle_band, buy_column, sell_column):

    data = add_column(data, 5)    
    
    for i in range(len(data)):  
        
       try:
           
           # Bullish pattern
           if data[i, close_column] > data[i, open_column] and \
              data[i, high_column] == data[i, close_column] and \
              data[i, low_column] == data[i, open_column] and \
              data[i, close_column] < data[i, middle_band] and \
              data[i, buy_column] == 0:
                  
                    data[i + 1, buy_column] = 1 
                    
           # Bearish pattern
           elif data[i, close_column] < data[i, open_column] and \
                data[i, high_column] == data[i, open_column] and \
                data[i, low_column] == data[i, close_column] and \
                data[i, close_column] > data[i, middle_band] and \
                data[i, sell_column] == 0:
                  
                    data[i + 1, sell_column] = -1 
                    
       except IndexError:
            
            pass
        
    return data

# Calling the signal function
my_data = signal(my_data, 0, 1, 2, 3, 4, 7, 8)

# Charting the latest signals
signal_chart(my_data, 0, 7, 8, genre = 'candles', window = 250)
plt.plot(my_data[-250:, 4], color = 'blue', linestyle = 'dashed')
plt.plot(my_data[-250:, 5], color = 'orange')
plt.plot(my_data[-250:, 6], color = 'purple')

# Performance
my_data = performance(my_data, 0, 7, 8, 9, 10, 11)



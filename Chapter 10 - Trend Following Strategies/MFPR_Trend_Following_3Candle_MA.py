
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'
lookback = 100

# Importing the asset as an array
my_data = mass_import(pair, horizon)

# Calculating the MA
my_data = ma(my_data, lookback, 3, 4)

'''
Use body = 0.0005 for EURUSD, USDCHF, GBPUSD, USDCAD
Use body = 50 for BTCUSD
Use body = 10 for ETHUSD
Use body = 2 for XAUUSD
Use body = 10 for SP500m, UK100

'''

body = 0.0005

# Creating the signal function
def signal(data, open_column, close_column, ma_column, buy_column, sell_column):

    data = add_column(data, 10)
    
    for i in range(len(data)):
        
       try:
           
           # Bullish pattern
           if data[i, close_column] - data[i, open_column] > body and \
              data[i - 1, close_column] - data[i - 1, open_column] > body and \
              data[i - 2, close_column] - data[i - 2, open_column] > body and \
              data[i, close_column] > data[i - 1, close_column] and \
              data[i - 1, close_column] > data[i - 2, close_column] and \
              data[i - 2, close_column] > data[i - 3, close_column] and \
              data[i, close_column] > data[i, ma_column] and \
              data[i, buy_column] == 0:
                  
                    data[i + 1, buy_column] = 1
                    
           # Bearish pattern
           elif data[i, open_column] - data[i, close_column] > body and \
                data[i - 1, open_column] - data[i - 1, close_column] > body and \
                data[i - 2, open_column] - data[i - 2, close_column] > body and \
                data[i, close_column] < data[i - 1, close_column] and \
                data[i - 1, close_column] < data[i - 2, close_column] and \
                data[i - 2, close_column] < data[i - 3, close_column] and \
                data[i, close_column] < data[i, ma_column] and \
                data[i, sell_column] == 0:
                  
                    data[i + 1, sell_column] = -1
                    
       except IndexError:
            
            pass
        
    return data

# Calling the signal function
my_data = signal(my_data, 0, 3, 4, 5, 6)

# Charting the latest signals
signal_chart(my_data, 0, 5, 6, genre = 'candles', window = 250)
plt.plot(my_data[-250:, 4])

# Performance
my_data = performance(my_data, 0, 5, 6, 7, 8, 9)

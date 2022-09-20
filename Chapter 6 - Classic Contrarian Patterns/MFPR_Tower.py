
# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'

'''
Use body = 0.0005 for EURUSD, USDCHF, GBPUSD, USDCAD
Use body = 50 for BTCUSD
Use body = 10 for ETHUSD
Use body = 2 for XAUUSD
Use body = 10 for SP500m, UK100

'''

body = 0.0005

# Importing the asset as an array
my_data = mass_import(pair, horizon)

# Creating the signal function
def signal(data, open_column, high_column, low_column, close_column, buy_column, sell_column):

    data = add_column(data, 5)    
    
    for i in range(len(data)):  
        
       try:
           
           # Bullish pattern
           if data[i, close_column] > data[i, open_column] and \
              data[i, close_column] - data[i, open_column] > body and \
              data[i - 2, low_column] < data[i - 1, low_column] and \
              data[i - 2, low_column] < data[i - 3, low_column] and \
              data[i - 4, close_column] < data[i - 4, open_column] and \
              data[i - 4, open_column] - data[i, close_column] > body:
                  
                    data[i + 1, buy_column] = 1 
                    
           # Bearish pattern
           elif data[i, close_column] < data[i, open_column] and \
                data[i, open_column] - data[i, close_column] > body and \
                data[i - 2, high_column] > data[i - 1, high_column] and \
                data[i - 2, high_column] > data[i - 3, high_column] and \
                data[i - 4, close_column] > data[i - 4, open_column] and \
                data[i - 4, close_column] - data[i, open_column] > body:
                 
                    data[i + 1, sell_column] = -1 
                    
       except IndexError:
            
            pass
        
    return data

# Calling the signal function
my_data = signal(my_data, 0, 1, 2, 3, 4, 5)

# Charting the latest signals
signal_chart(my_data, 0, 4, 5, genre = 'candles', window = 100)

# Performance
my_data = performance(my_data, 0, 4, 5, 6, 7, 8)


# Choosing the asset
pair = 0

# Time Frame
horizon = 'H1'

# Importing the asset as an array
my_data = mass_import(pair, horizon)

# Creating the signal function
def signal(data):

    data = add_column(data, 5)    
    
    for i in range(len(data)):    

       try:
        
           # Bullish Alpha
           if data[i, 2] < data[i - 5, 2] and data[i, 2] < data[i - 13, 2] and data[i, 2] > data[i - 21, 2] and \
              data[i, 3] > data[i - 1, 3] and data[i, 4] == 0:
                  
                    data[i + 1, 4] = 1 
                    
           # Bearish Alpha
           elif data[i, 1] > data[i - 5, 1] and data[i, 1] > data[i - 13, 1] and data[i, 1] < data[i - 21, 1] and \
                data[i, 3] < data[i - 1, 3] and data[i, 5] == 0:
                  
                    data[i + 1, 5] = -1 

       except IndexError:
            
            pass
              
    return data

# Calling the signal function
my_data = signal(my_data)

# Charting the latest signals
signal_chart(my_data, 0, 4, 5, genre = 'bars', window = 150)

# Performance
my_data = performance(my_data, 0, 4, 5, 6, 7, 8)



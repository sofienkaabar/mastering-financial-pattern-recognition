
# Choosing the asset
pair = 8

# Time Frame
horizon = 'H1'
lookback = 3

# Importing the asset as an array
my_data = mass_import(pair, horizon)

my_data = heikin_ashi(my_data, 0, 1, 2, 3, 4)

k_signal_chart(my_data, 0, 4, 5, window = 150)

k_candlestick_double_plot(my_data, window = 150)

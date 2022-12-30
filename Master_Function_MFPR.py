# IMPORTANT: MUST EXECUTE THIS FILE AS A WHOLE 
# SO THAT THE REST OF THE CODE WORKS PROPERLY



import datetime
import pytz
import pandas                    as pd
import MetaTrader5               as mt5
import matplotlib.pyplot         as plt
import numpy                     as np

frame_H1   = mt5.TIMEFRAME_H1
frame_D1   = mt5.TIMEFRAME_D1

now = datetime.datetime.now()

assets = ['EURUSD', 'USDCHF', 'GBPUSD', 'USDCAD', 'BTCUSD', 'ETHUSD', 'XAUUSD', 'SP500m', 'UK100'] 
     
def mass_import(asset, time_frame):
                
    if time_frame == 'H1':
        data = get_quotes(frame_H1, 2013, 1, 1, asset = assets[asset])
        data = data.iloc[:, 1:5].values
        data = data.round(decimals = 5)        
        
    if time_frame == 'D1':
        data = get_quotes(frame_D1, 2000, 1, 1, asset = assets[asset])
        data = data.iloc[:, 1:5].values
        data = data.round(decimals = 5)        
          
    return data 

def get_quotes(time_frame, year = 2005, month = 1, day = 1, asset = "EURUSD"):
        
    if not mt5.initialize():
        
        print("initialize() failed, error code =", mt5.last_error())
        
        quit()
    
    timezone = pytz.timezone("Europe/Paris")
    
    time_from = datetime.datetime(year, month, day, tzinfo = timezone)
    
    time_to = datetime.datetime.now(timezone) + datetime.timedelta(days=1)
    
    rates = mt5.copy_rates_range(asset, time_frame, time_from, time_to)
    
    rates_frame = pd.DataFrame(rates)

    return rates_frame

def performance(data, 
                 open_price, 
                 buy_column, 
                 sell_column, 
                 long_result_col, 
                 short_result_col, 
                 total_result_col):
    
    # Variable holding period
    for i in range(len(data)):
        
        try:
            
            if data[i, buy_column] == 1:
                
                for a in range(i + 1, i + 1000):
                    
                    if data[a, buy_column] == 1 or data[a, sell_column] == -1:
                        
                        data[a, long_result_col] = data[a, open_price] - data[i, open_price]
                        
                        break
                    
                    else:
                        
                        continue                
                    
            else:
                
                continue
            
        except IndexError:
            
            pass
                    
    for i in range(len(data)):
        
        try:
            
            if data[i, sell_column] == -1:
                
                for a in range(i + 1, i + 1000):
                                        
                    if data[a, buy_column] == 1 or data[a, sell_column] == -1:
                        
                        data[a, short_result_col] = data[i, open_price] - data[a, open_price]
                        
                        break   
                     
                    else:
                        
                        continue
                    
            else:
                continue
            
        except IndexError:
            
            pass   
        
    # Aggregating the long & short results into one column
    data[:, total_result_col] = data[:, long_result_col] + data[:, short_result_col]  
    
    # Profit factor    
    total_net_profits = data[data[:, total_result_col] > 0, total_result_col]
    total_net_losses  = data[data[:, total_result_col] < 0, total_result_col] 
    total_net_losses  = abs(total_net_losses)
    profit_factor     = round(np.sum(total_net_profits) / np.sum(total_net_losses), 2)

    # Hit ratio    
    hit_ratio         = len(total_net_profits) / (len(total_net_losses) + len(total_net_profits))
    hit_ratio         = hit_ratio * 100
    
    # Risk reward ratio
    average_gain            = total_net_profits.mean()
    average_loss            = total_net_losses.mean()
    realized_risk_reward    = average_gain / average_loss

    # Number of trades
    trades = len(total_net_losses) + len(total_net_profits)
        
    print('Hit Ratio         = ', hit_ratio)
    print('Profit factor     = ', profit_factor) 
    print('Realized RR       = ', round(realized_risk_reward, 3))
    print('Number of Trades  = ', trades)    
   
    return data

def add_column(data, times):
    
    for i in range(1, times + 1):
    
        new = np.zeros((len(data), 1), dtype = float)
        
        data = np.append(data, new, axis = 1)

    return data

def delete_column(data, index, times):
    
    for i in range(1, times + 1):
    
        data = np.delete(data, index, axis = 1)

    return data

def delete_row(data, number):
    
    data = data[number:, ]
    
    return data

def rounding(data, how_far):
    
    data = data.round(decimals = how_far)
    
    return data

def ma(data, lookback, close, position): 
    
    data = add_column(data, 1)
    
    for i in range(len(data)):
           
            try:
                
                data[i, position] = (data[i - lookback + 1:i + 1, close].mean())
            
            except IndexError:
                
                pass
            
    data = delete_row(data, lookback)
    
    return data

def ema(data, alpha, lookback, close, position):
    
    alpha = alpha / (lookback + 1.0)
    
    beta  = 1 - alpha
    
    data = ma(data, lookback, close, position)

    data[lookback + 1, position] = (data[lookback + 1, close] * alpha) + (data[lookback, position] * beta)

    for i in range(lookback + 2, len(data)):
        
            try:
                
                data[i, position] = (data[i, close] * alpha) + (data[i - 1, position] * beta)
        
            except IndexError:
                
                pass
            
    return data 

def smoothed_ma(data, alpha, lookback, close, position):
    
    lookback = (2 * lookback) - 1
    
    alpha = alpha / (lookback + 1.0)
    
    beta  = 1 - alpha
    
    data = ma(data, lookback, close, position)

    data[lookback + 1, position] = (data[lookback + 1, close] * alpha) + (data[lookback, position] * beta)

    for i in range(lookback + 2, len(data)):
        
            try:
                
                data[i, position] = (data[i, close] * alpha) + (data[i - 1, position] * beta)
        
            except IndexError:
                
                pass
            
    return data

def volatility(data, lookback, close, position):
    
    data = add_column(data, 1)
    
    for i in range(len(data)):
        
        try:
            
            data[i, position] = (data[i - lookback + 1:i + 1, close].std())
    
        except IndexError:
            
            pass
     
    data = delete_row(data, lookback)    
     
    return data

def atr(data, lookback, high_column, low_column, close_column, position):
    
    data = add_column(data, 1)
      
    for i in range(len(data)):
        
        try:
            
            data[i, position] = max(data[i, high_column] - data[i, low_column], abs(data[i, high_column] - data[i - 1, close_column]), abs(data[i, low_column]  - data[i - 1, close_column]))
            
        except ValueError:
            
            pass
        
    data[0, position] = 0   
      
    data = smoothed_ma(data, 2, lookback, position, position + 1)

    data = delete_column(data, position, 1)
    
    data = delete_row(data, lookback)
    
    return data

def ohlc_plot_bars(data, window):
     
    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        plt.vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'black', linewidth = 1)  

        if sample[i, 3] < sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'black', linewidth = 1)  
            
        if sample[i, 3] == sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0] + 0.00005, color = 'black', linewidth = 1.00)  
            
    plt.grid()
    
def ohlc_plot_bars_interval(data, first_interval, second_interval):
     
    sample = data[-first_interval:-second_interval, ]
    
    for i in range(len(sample)):
        
        plt.vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'mediumseagreen', linewidth = 3)  

        if sample[i, 3] < sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'maroon', linewidth = 3)  
            
        if sample[i, 3] == sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0] + 0.00001, color = 'black', linewidth = 1.75)  
            
    plt.grid()   
    
def ohlc_plot_candles(data, window):
      
    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        plt.vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'mediumseagreen', linewidth = 3)  

        if sample[i, 3] < sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'maroon', linewidth = 3)  
            
        if sample[i, 3] == sample[i, 0]:
            
            plt.vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0] + 0.00001, color = 'black', linewidth = 1.75)  
            
    plt.grid()   

def signal_chart(data, position, buy_column, sell_column, genre = 'bars', window = 500):   
 
    sample = data[-window:, ]
    
    if genre == 'bars':

        fig, ax = plt.subplots(figsize = (10, 5))
        
        ohlc_plot_bars(data, window)    
    
        for i in range(len(sample)):
            
            if sample[i, buy_column] == 1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
            
            elif sample[i, sell_column] == -1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

    if genre == 'candles':

        fig, ax = plt.subplots(figsize = (10, 5))
        
        ohlc_plot_candles(data, window)    
    
        for i in range(len(sample)):
            
            if sample[i, buy_column] == 1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
            
            elif sample[i, sell_column] == -1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

def indicator_plot(data, second_panel, window = 250):

    fig, ax = plt.subplots(2, figsize = (10, 5))

    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        ax[0].vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:

            ax[0].vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'black', linewidth = 1.5)  

        if sample[i, 3] < sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'black', linewidth = 1.5)  
            
        if sample[i, 3] == sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'black', linewidth = 1.5)  
   
    ax[0].grid() 
     
    ax[1].plot(sample[:, second_panel], color = 'royalblue', linewidth = 1)
    ax[1].grid()

def signal_chart_indicator_plot(data, 
                                    position, 
                                    second_panel, 
                                    buy_column, 
                                    sell_column, 
                                    barriers = False,  
                                    window = 250):   
 
    fig, ax = plt.subplots(2, figsize = (10, 5))

    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        ax[0].vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'black', linewidth = 1)  

        if sample[i, 3] < sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'black', linewidth = 1)  
            
        if sample[i, 3] == sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0] + 0.00003, color = 'black', linewidth = 1.00)  
            
    ax[0].grid() 

    for i in range(len(sample)):
        
        if sample[i, buy_column] == 1:
            
            x = i
            y = sample[i, position]
        
            ax[0].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
        
        elif sample[i, sell_column] == -1:
            
            x = i
            y = sample[i, position]
        
            ax[0].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

    ax[1].plot(sample[:, second_panel], color = 'royalblue', linewidth = 1)
    ax[1].grid()
    
    if barriers == True:
        
        plt.axhline(y = lower_barrier, color = 'black', linestyle = 'dashed', linewidth = 1)
        plt.axhline(y = upper_barrier, color = 'black', linestyle = 'dashed', linewidth = 1)

def signal_chart_indicator_plot_candles(data, 
                                    position, 
                                    second_panel, 
                                    buy_column, 
                                    sell_column, 
                                    barriers = False,  
                                    window = 250):   
 
    fig, ax = plt.subplots(2, figsize = (10, 5))

    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        ax[0].vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'mediumseagreen', linewidth = 3)  

        if sample[i, 3] < sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'maroon', linewidth = 3)  
            
        if sample[i, 3] == sample[i, 0]:
            
            ax[0].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0] + 0.00001, color = 'black', linewidth = 1.75)  
            
    ax[0].grid()   

    for i in range(len(sample)):
        
        if sample[i, buy_column] == 1:
            
            x = i
            y = sample[i, position]
        
            ax[0].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
        
        elif sample[i, sell_column] == -1:
            
            x = i
            y = sample[i, position]
        
            ax[0].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

    ax[1].plot(sample[:, second_panel], color = 'royalblue', linewidth = 1)
    ax[1].grid()
    
    if barriers == True:
        
        plt.axhline(y = lower_barrier, color = 'black', linestyle = 'dashed', linewidth = 1)
        plt.axhline(y = upper_barrier, color = 'black', linestyle = 'dashed', linewidth = 1)
        
def rsi(data, lookback, close, position):
    
    data = add_column(data, 5)
    
    for i in range(len(data)):
        
        data[i, position] = data[i, close] - data[i - 1, close]
     
    for i in range(len(data)):
        
        if data[i, position] > 0:
            
            data[i, position + 1] = data[i, position]
            
        elif data[i, position] < 0:
            
            data[i, position + 2] = abs(data[i, position])
            
    data = smoothed_ma(data, 2, lookback, position + 1, position + 3)
    data = smoothed_ma(data, 2, lookback, position + 2, position + 4)

    data[:, position + 5] = data[:, position + 3] / data[:, position + 4]
    
    data[:, position + 6] = (100 - (100 / (1 + data[:, position + 5])))

    data = delete_column(data, position, 6)
    data = delete_row(data, lookback)

    return data
    
def stochastic_oscillator(data, 
                             lookback, 
                             high, 
                             low, 
                             close, 
                             position, 
                             slowing = False, 
                             smoothing = False, 
                             slowing_period = 1, 
                             smoothing_period = 1):
            
    data = add_column(data, 1)
        
    for i in range(len(data)):
            
        try:
            
            data[i, position] = (data[i, close] - min(data[i - lookback + 1:i + 1, low])) / (max(data[i - lookback + 1:i + 1, high]) - min(data[i - lookback + 1:i + 1, low]))
            
        except ValueError:
            
            pass
        
    data[:, position] = data[:, position] * 100  
            
    if slowing == True and smoothing == False:
        
        data = ma(data, slowing_period, position, position + 1)
    
    if smoothing == True and slowing == False:
        
        data = ma(data, smoothing_period, position, position + 1)
        
    if smoothing == True and slowing == True:
    
        data = ma(data, slowing_period, position,   position + 1)
        
        data = ma(data, smoothing_period, position + 1, position + 2)        
       
    data = delete_row(data, lookback)

    return data

def normalized_index(data, lookback, close, position):
            
    data = add_column(data, 1)
        
    for i in range(len(data)):
            
        try:
            
            data[i, position] = (data[i, close] - min(data[i - lookback + 1:i + 1, close])) / (max(data[i - lookback + 1:i + 1, close]) - min(data[i - lookback + 1:i + 1, close]))
            
        except ValueError:
            
            pass
        
    data[:, position] = data[:, position] * 100  
            
    data = delete_row(data, lookback)

    return data

def bollinger_bands(data, lookback, standard_deviation, close, position):
       
    data = add_column(data, 2)
    
    # Calculating means
    data = ma(data, lookback, close, position)

    data = volatility(data, lookback, close, position + 1)
    
    data[:, position + 2] = data[:, position] + (standard_deviation * data[:, position + 1])
    data[:, position + 3] = data[:, position] - (standard_deviation * data[:, position + 1])
    
    data = delete_row(data, lookback)
    
    data = delete_column(data, position + 1, 1)
        
    return data

def k_envelopes(data, lookback, high, low, position):
    
    # Calculating the upper moving average
    data = ma(data, lookback, high, position)
    
    # Calculating the lower moving average
    data = ma(data, lookback, low, position + 1)    
    
    return data

def k_volatility_band(data, lookback, multiplier, high, low, close, position):
    
    data = add_column(data, 6)
    
    # Calculating the median line
    for i in range(len(data)):
        
        try:
            
            data[i, position] = max(data[i - lookback + 1:i + 1, high]) 
            data[i, position + 1] = min(data[i - lookback + 1:i + 1, low]) 
            data[i, position + 2] = (data[i, position] + data[i, position + 1]) / 2
            
        except ValueError:
            
            pass

    # Cleaning
    data = delete_column(data, position, 2)

    # Calculating maximum volatility
    data = volatility(data, lookback, close, position + 1)
    
    for i in range(len(data)):
        
        try:
            
            data[i, position + 2] = max(data[i - lookback + 1:i + 1, position + 1]) 
            
        except ValueError:
            
            pass   
        
    # Cleaning
    data = delete_column(data, position + 1, 1)
    
    # Calculating the bands
    data[:, position + 2] = data[:, position] + (multiplier * data[:, position + 1])    
    data[:, position + 3] = data[:, position] - (multiplier * data[:, position + 1])

    # Cleaning
    data = delete_column(data, position + 1, 1)    
        
    return data

def rsi_atr(data, lookback_rsi, lookback_atr, lookback_rsi_atr, high, low, close, position):
    
    data = rsi(data, lookback_rsi, close, position)
    
    data = atr(data, lookback_atr, high, low, close, position + 1)
    
    data = add_column(data, 1)
    
    data[:, position + 2] = data[:, position] / data[:, position + 1]
    
    data = rsi(data, lookback_rsi_atr, position + 2, position + 3)
    
    data = delete_column(data, position, 3)
    
    return data

def signal_chart_interval(data, position, buy_column, sell_column, 
                             first_interval, second_interval, genre = 'bars'):   
 
    sample = data[-first_interval:-second_interval, ]
    
    if genre == 'bars':

        fig, ax = plt.subplots(figsize = (10, 5))
        
        ohlc_plot_bars_interval(data, first_interval, second_interval)    
    
        for i in range(len(sample)):
            
            if sample[i, buy_column] == 1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
            
            elif sample[i, sell_column] == -1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

    if genre == 'candles':

        fig, ax = plt.subplots(figsize = (10, 5))
        
        ohlc_plot_bars_interval(data, first_interval, second_interval)
        
        for i in range(len(sample)):
            
            if sample[i, buy_column] == 1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
            
            elif sample[i, sell_column] == -1:
                
                x = i
                y = sample[i, position]
            
                ax.annotate(' ', xy = (x, y), 
                            arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  
            
def k_candlesticks(data, open_column, high_column, low_column, close_column, lookback, position):
    
    data = add_column(data, 4)
    
    # Averaging the open price
    data = ma(data, lookback, open_column, position)
     
    # Averaging the high price
    data = ma(data, lookback, high_column, position + 1)
       
    # Averaging the low price
    data = ma(data, lookback, low_column, position + 2)
       
    # Averaging the close price
    data = ma(data, lookback, close_column, position + 3)
    
    return data 

def k_ohlc_plot_candles(data, window):
     
    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        plt.vlines(x = i, ymin = sample[i, 6], ymax = sample[i, 5], color = 'black', linewidth = 1)  
        
        if sample[i, 7] > sample[i, 4]:
            
            plt.vlines(x = i, ymin = sample[i, 4], ymax = sample[i, 7], color = 'mediumseagreen', linewidth = 3)  

        if sample[i, 7] < sample[i, 4]:
            
            plt.vlines(x = i, ymin = sample[i, 7], ymax = sample[i, 4], color = 'maroon', linewidth = 3)  
            
        if sample[i, 7] == sample[i, 4]:
            
            plt.vlines(x = i, ymin = sample[i, 7], ymax = sample[i, 4] + 0.00005, color = 'black', linewidth = 1.00)  
            
    plt.grid()
    
def k_signal_chart(data, position, buy_column, sell_column, window = 500):   
 
    sample = data[-window:, ]

    fig, ax = plt.subplots(figsize = (10, 5))
    
    k_ohlc_plot_candles(data, window)    

    for i in range(len(sample)):
        
        if sample[i, buy_column] == 1:
            
            x = i
            y = sample[i, position]
        
            ax.annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
        
        elif sample[i, sell_column] == -1:
            
            x = i
            y = sample[i, position]
        
            ax.annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  
           
def k_candlestick_double_plot(data, buy_column, sell_column, window = 250):   
 
    fig, ax = plt.subplots(2, figsize = (10, 5))

    sample = data[-window:, ]
    
    for i in range(len(sample)):
        
        ax[0].vlines(x = i, ymin = sample[i, 6], ymax = sample[i, 5], color = 'black', linewidth = 1)  
        
        if sample[i, 7] > sample[i, 4]:
            
            ax[0].vlines(x = i, ymin = sample[i, 4], ymax = sample[i, 7], color = 'mediumseagreen', linewidth = 3)  

        if sample[i, 7] < sample[i, 4]:
            
            ax[0].vlines(x = i, ymin = sample[i, 7], ymax = sample[i, 4], color = 'maroon', linewidth = 3)  
            
        if sample[i, 7] == sample[i, 4]:
            
            ax[0].vlines(x = i, ymin = sample[i, 7], ymax = sample[i, 4] + 0.00005, color = 'black', linewidth = 1.00)  
            
        if sample[i, buy_column] == 1:
            
            x = i
            y = sample[i, 0]
        
            ax[0].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
        
        elif sample[i, sell_column] == -1:
            
            x = i
            y = sample[i, 0]
        
            ax[0].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

    ax[0].grid()

    for i in range(len(sample)):
        
        ax[1].vlines(x = i, ymin = sample[i, 2], ymax = sample[i, 1], color = 'black', linewidth = 1)  
        
        if sample[i, 3] > sample[i, 0]:
            
            ax[1].vlines(x = i, ymin = sample[i, 0], ymax = sample[i, 3], color = 'mediumseagreen', linewidth = 3)  

        if sample[i, 3] < sample[i, 0]:
            
            ax[1].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0], color = 'maroon', linewidth = 3)  
            
        if sample[i, 3] == sample[i, 0]:
            
            ax[1].vlines(x = i, ymin = sample[i, 3], ymax = sample[i, 0] + 0.00005, color = 'black', linewidth = 1.00)  
 
        if sample[i, buy_column] == 1:
            
            x = i
            y = sample[i, 0]
        
            ax[1].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = 11, headwidth = 11, facecolor = 'green', color = 'green'))
        
        elif sample[i, sell_column] == -1:
            
            x = i
            y = sample[i, 0]
        
            ax[1].annotate(' ', xy = (x, y), 
                        arrowprops = dict(width = 9, headlength = -11, headwidth = -11, facecolor = 'red', color = 'red'))  

            
    ax[1].grid()
    
def heikin_ashi(data, open_column, high_column, low_column, close_column, position):
    
    data = add_column(data, 4)
    
    # Heikin-Ashi Open
    try:
        for i in range(len(data)):
            data[i, position] = (data[i - 1, open_column] + data[i - 1, close_column]) / 2
    except:
        pass
    
    # Heikin-Ashi Close
    for i in range(len(data)):
        data[i, position + 3] = (data[i, open_column] + data[i, high_column] + data[i, low_column] + data[i, close_column]) / 4
    
    # Heikin-Ashi High
    for i in range(len(data)):    
        data[i, position + 1] = max(data[i, position], data[i, position + 3], data[i, high_column])
    
    # Heikin-Ashi Low    
    for i in range(len(data)):    
        data[i, position + 2] = min(data[i, position], data[i, position + 3], data[i, low_column])      
    
    return data
            
def trend_intensity_indicator(data, lookback, close_column, position):

    data = add_column(data, 5)
    
    # Calculating the Moving Average
    data = ma(data, lookback, close_column, position)

    # Deviations
    for i in range(len(data)):
        
        if data[i, close_column] > data[i, position]:
            data[i, position + 1] = data[i, close_column] - data[i, position]
        
        if data[i, close_column] < data[i, position]:
            data[i, position + 2] = data[i, position] - data[i, close_column]
              
    # Trend Intensity Index
    for i in range(len(data)):
            
        data[i, position + 3] = np.count_nonzero(data[i - lookback + 1:i + 1, position + 1])
            
    for i in range(len(data)):
            
        data[i, position + 4] = np.count_nonzero(data[i - lookback + 1:i + 1, position + 2])
        
    for i in range(len(data)):
        
        data[i, position + 5] = ((data[i, position + 3]) / (data[i, position + 3] + data[i, position + 4])) * 100
        
    data = delete_column(data, position, 5)
     
    return data

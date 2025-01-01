# import libraries
import alpaca_trade_api as tradeapi
import requests, json

# authentication and connection details
api_key = 'SECRET'
api_secret = 'SECRET'
base_url = 'https://paper-api.alpaca.markets'

# instantiate REST API
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

# ticker list
tickers = ["AAPL", "ADBE", "BA", "GE", "GOOG", "HD", "MSFT", "NKE", "TSLA", "WMT"]

# First data pull NOTE: Only run this on new tickers being added to the list.
def first_data_pull(tickers):
    
    # loop through tickers
    for ticker in tickers:
        url = "http://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+ticker+"&outputsize=full&apikey=SECRET"
        
        # request data
        request_dict = json.loads(requests.get(url).text)
        
        # variables to locate correct data
        time_key = "Time Series (Daily)"
        close_key = "4. close"
        
        # store data as csv
        with open("/home/ubuntu/environment/final_project/data/"+ticker+".csv", "w") as file:
            write_lines = []
            
            # write individual lines to the csv file
            for date in request_dict[time_key]:
                write_lines.append(date + "," + request_dict[time_key][date][close_key] + "\n")
            
            # sort data from oldest to newest
            write_lines.reverse()
            file.writelines(write_lines)

# Append Data Function
def append_data(tickers):
    
    # loop through tickers
    for ticker in tickers:
        url = "http://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+ticker+"&outputsize=full&apikey=SECRET"
        
        # request data
        request_dict = json.loads(requests.get(url).text)
        
        # variables to locate correct data
        time_key = "Time Series (Daily)"
        close_key = "4. close"
        
        # store data as csv
        with open("/home/ubuntu/environment/final_project/data/"+ticker+".csv", "r") as csv_file:
            
            # read csv and split on commas
            csv_lines = csv_file.readlines()
            last_date = csv_lines[-1].split(",")[0]
            
            # get new data
            new_lines = []
            for date in request_dict[time_key]:
                
                # only get new dates
                if date == last_date:
                    break
                
                # write data to csv
                print(date + "," + request_dict[time_key][date][close_key])
                new_lines.append(date + "," + request_dict[time_key][date][close_key] + "\n")
                
            # reverse lines for oldest to newest
            new_lines.reverse()
            csv_file = open("/home/ubuntu/environment/final_project/data/"+ticker+".csv", "a")
            csv_file.writelines(new_lines)

# Mean Reversion Strategy Function
def meanReversionStrategy(prices, ticker):
    
    # pre-define variables
    i            = 0
    total_profit = 0
    # selling variables
    buy          = 0
    last_buy     = 0
    last_sell    = 0
    # short selling variables
    short_price  = 0
    last_short   = 0
    last_cover   = 0
    
    # loop through each price
    for price in prices:
        
        event = False # only permits one event to take place each day
        
        # calculate 5 day moving avg on 6th day
        if i > 4:
            
            # 5 day moving average
            average = sum(prices[i-5:i]) / 5
            
            # buy condition
            if buy == 0 and short_price == 0 and event == False and price < average * 0.98:
                
                # buy
                buy = price # update buy variable to current price
                # print("buying at:   ", buy) # output buying price
                last_buy = i + 1 # save line number of last buy
                event = True
            
            # sell condition
            elif buy != 0 and short_price == 0 and event == False and price > average * 1.02:
                total_profit += (price - buy) # add profit to total_profit variable
                # print("selling at:  ", price) # output selling price
                # print("trade profit:", round(price - buy, 2)) # output trade profit
                buy = 0 # set buy back to 0 to allow another purchase
                last_sell = i + 1 # save line number of the last sell
                event = True
                
            # short selling condition
            if short_price == 0 and buy == 0 and event == False and price > average * 1.02:
                
                # short sell
                short_price = price # short sell
                # print("shorting at: ", short_price) # output price
                last_short = i + 1 # save line of last short
                event = True
                
            elif short_price != 0 and buy == 0 and event == False and price < average * 0.98:
                total_profit += (short_price - price) # add profit to total profit
                # print("covering at: ", price)
                # print("trade profit:", round(short_price - price, 2))
                short_price = 0 # set back to 0 to allow another short sell
                last_cover = i + 1 # save line of last cover
                event = True
            
        i += 1 # move 5 day moving average
        
    # output to console
    # print("---------------------")
    # print(ticker, "Mean Reversion")
    # print("---------------------")
    # print("Total profit:", round(total_profit, 2))
    # print()
    
    # try except for day trading errors because 3 strategies are running at once
    try:
    
        # output strategy and if you should buy or sell
        if len(prices) == last_buy:
            print(ticker + " Mean Reversion Strategy Output:")
            print("You should buy this stock today.")
            print()
            
        # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='buy', 
        		time_in_force='gtc', 
        		type='market')
    		
        if len(prices) == last_sell:
            print(ticker + " Mean Reversion Strategy Output:")
            print("You should sell this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='sell', 
        		time_in_force='gtc', 
        		type='market')
            
        if len(prices) == last_short:
            print(ticker + " Mean Reversion Strategy Output:")
            print("You should short sell this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='sell', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_cover:
            print(ticker + " Mean Reversion Strategy Output:")
            print("You should cover your short today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='buy', 
        		time_in_force='gtc', 
        		type='market')
    		
    except:
        print("Order cannot be executed because 3 strategies are being ran and you may have already ordered with a different strategy today.")
        print()
        
    # return total profit
    return round(total_profit, 2)

# Moving Average Crossover Strategy Function
def movingAverageCrossoverStrategy(prices, ticker):
      
    # pre-define variables
    i            = 0
    total_profit = 0
    # selling variables
    buy          = 0
    last_buy     = 0
    last_sell    = 0
    # short selling variables
    short_price  = 0
    last_short   = 0
    last_cover   = 0
    
    # loop through each price
    for price in prices:
        
        event = False # only permits one event to take place each day
        
        # calculate 20 and 5 day moving avg on 21st day
        if i > 19:
            
            # 5 and 20 day moving averages
            average5p  = sum(prices[i-5:i]) / 5 # past 5 days average
            average5t  = sum(prices[i-4:i+1]) / 5 # today and past 4 days average
            average20p = sum(prices[i-20:i]) / 20 # past 20 days average
            average20t = sum(prices[i-19:i+1]) / 20 # today and past 19 days average
            
            # buy condition
            if buy == 0 and short_price == 0 and event == False and average5p <= average20p and average5t > average20t:
                
                # buy
                buy = price # update buy variable to current price
                # print("buying at:   ", buy) # output buying price
                last_buy = i + 1 # save line number of last buy
                event = True
            
            # sell condition
            elif buy != 0 and short_price == 0 and event == False and average5p >= average20p and average5t < average20t:
                total_profit += (price - buy) # add profit to total_profit variable
                # print("selling at:  ", price) # output selling price
                # print("trade profit:", round(price - buy, 2)) # output trade profit
                buy = 0 # set buy back to 0 to allow another purchase
                last_sell = i + 1 # save line number of the last sell
                event = True
                
            # short selling condition
            if short_price == 0 and buy == 0 and event == False and average5p >= average20p and average5t < average20t:
                
                # short sell
                short_price = price # short sell
                # print("shorting at: ", short_price) # output price
                last_short = i + 1 # save line of last short
                event = True
                
            elif short_price != 0 and buy == 0 and event == False and average5p <= average20p and average5t > average20t:
                total_profit += (short_price - price) # add profit to total profit
                # print("covering at: ", price)
                # print("trade profit:", round(short_price - price, 2))
                short_price = 0 # set back to 0 to allow another short sell
                last_cover = i + 1 # save line of last cover
                event = True
            
        i += 1 # move forward a day
        
    # output to console
    # print("---------------------")
    # print(ticker, "Moving Average")
    # print("---------------------")
    # print("Total profit:", round(total_profit, 2))
    # print()
    
    # try except for day trading errors because 3 strategies are running at once
    try:
    
        # output strategy and if you should buy or sell
        if len(prices) == last_buy:
            print(ticker + " Moving Average Crossover Strategy Output:")
            print("You should buy this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='buy', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_sell:
            print(ticker + " Moving Average Crossover Strategy Output:")
            print("You should sell this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='sell', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_short:
            print(ticker + " Moving Average Crossover Strategy Output:")
            print("You should short sell this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='sell', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_cover:
            print(ticker + " Moving Average Crossover Strategy Output:")
            print("You should cover your short today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='buy', 
        		time_in_force='gtc', 
        		type='market')
        		
    except:
        print("Order cannot be executed because 3 strategies are being ran and you may have already ordered with a different strategy today.")
        print()
        
    # return total profit
    return round(total_profit, 2)

# Momentum Strategy Function
def momentumStrategy(prices, ticker):
    
    # pre-define variables
    i            = 0
    total_profit = 0
    # selling variables
    buy          = 0
    last_buy     = 0
    last_sell    = 0
    # short selling variables
    short_price  = 0
    last_short   = 0
    last_cover   = 0
    
    # loop through each price
    for price in prices:
        
        event = False # only permits one event to take place each day
        
        # start looking back 5 days on day 6
        if i > 4:
                
            # price 5 days ago
            past_price = prices[i-5]
            
            # buy condition
            if buy == 0 and short_price == 0 and event == False and price < past_price * 0.98:
                
                # buy
                buy = price # update buy variable to current price
                # print("buying at:   ", buy) # output buying price
                last_buy = i + 1 # save line number of last buy
                event = True
            
            # sell condition
            elif buy != 0 and short_price == 0 and event == False and price > past_price * 1.02:
                total_profit += (price - buy) # add profit to total_profit variable
                # print("selling at:  ", price) # output selling price
                # print("trade profit:", round(price - buy, 2)) # output trade profit
                buy = 0 # set buy back to 0 to allow another purchase
                last_sell = i + 1 # save line number of the last sell
                event = True
                
            # short selling condition
            if short_price == 0 and buy == 0 and event == False and price > past_price * 1.02:
                
                # short sell
                short_price = price # short sell
                # print("shorting at: ", short_price) # output price
                last_short = i + 1 # save line of last short
                event = True
                
            elif short_price != 0 and buy == 0 and event == False and price < past_price * 0.98:
                total_profit += (short_price - price) # add profit to total profit
                # print("covering at: ", price)
                # print("trade profit:", round(short_price - price, 2))
                short_price = 0 # set back to 0 to allow another short sell
                last_cover = i + 1 # save line of last cover
                event = True
            
        i += 1 # move day ahead
            
    # output to console
    # print("---------------------")
    # print(ticker, "Momentum")
    # print("---------------------")
    # print("Total profit:", round(total_profit, 2))
    # print()
    
    # try except for day trading errors because 3 strategies are running at once 
    try:
    
        # output strategy and if you should buy or sell
        if len(prices) == last_buy:
            print(ticker + " Momentum Strategy Output:")
            print("You should buy this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='buy', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_sell:
            print(ticker + " Momentum Strategy Output:")
            print("You should sell this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='sell', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_short:
            print(ticker + " Momentum Strategy Output:")
            print("You should short sell this stock today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='sell', 
        		time_in_force='gtc', 
        		type='market')
        		
        if len(prices) == last_cover:
            print(ticker + " Momentum Strategy Output:")
            print("You should cover your short today.")
            print()
            
            # submit order to alpaca trading api
            api.submit_order(symbol=ticker, 
        		qty=1, 
        		side='buy', 
        		time_in_force='gtc', 
        		type='market')
    		
    except:
        print("Order cannot be executed because 3 strategies are being ran and you may have already ordered with a different strategy today.")
        print()
        
    # return total profit
    return round(total_profit, 2)

# Save results
def saveResults(results, filename):
    with open(filename, 'w') as file:
        json.dump(results, file)
        
# Pass tickers through the functions
def runStrategies():
    
    # update tickers
    append_data(tickers)
    
    # create results dictionary
    results = {}
    first_profit = True
    highest_profit = 0
    best_ticker = ""
    best_strat = ""
    
    # loop through tickers
    for ticker in tickers:
        with open("/home/ubuntu/environment/final_project/data/"+ticker+".csv") as ticker_file:
            # put the prices in a list
            prices = [round(float(line.split(",")[1]), 2) for line in ticker_file.readlines()]
            
        # save prices in results
        results[ticker + "_prices"] = prices
        
        # save meanReversionStrategy output in results
        mr_output = meanReversionStrategy(prices, ticker)
        results[ticker + '_profit_mr'] = mr_output
        
        # save movingAverageCrossoverStrategy output in results
        mac_output = movingAverageCrossoverStrategy(prices, ticker)
        results[ticker + '_profit_mac'] = mac_output
        
        # save momentumStrategy output in results
        mo_output = momentumStrategy(prices, ticker)
        results[ticker + '_profit_mo'] = mo_output
        
        # set default highest profit to be overwritten
        if first_profit == True:
            highest_profit = mr_output
            best_ticker = ticker
            best_strat = "Mean Reversion"
            first_profit = False
            
        # find stock and strategy with highest profit
        if mr_output > highest_profit:
            highest_profit = mr_output
            best_ticker = ticker
            best_strat = "Mean Reversion"
        if mac_output > highest_profit:
            highest_profit = mac_output
            best_ticker = ticker
            best_strat = "Moving Average Crossover"
        if mo_output > highest_profit:
            highest_profit = mo_output
            best_ticker = ticker
            best_strat = "Momentum"
            
    # print stock and strategy with highest profit to console
    print("The", best_ticker, "stock performed the best with a total profit of", highest_profit, "using the", best_strat, "Strategy.")
    
    # save results to a json file
    saveResults(results, "/home/ubuntu/environment/final_project/results.json")
            
# Call the run strategies function 
runStrategies()

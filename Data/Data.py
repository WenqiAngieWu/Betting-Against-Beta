# -*- coding: utf-8 -*-
"""
Fetch data
"""



import pandas as pd
import bs4 as bs
import datetime as dt
#import os
#import pandas_datareader.data as web
import pickle
import requests
import pandas_datareader as pdr
from pandas_datareader._utils import RemoteDataError
import winsound

def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    with open("sp500tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
    return tickers


tickers = save_sp500_tickers()

with open('sp500_symbols.txt', 'w') as f:
    for item in tickers:
        f.write("%s" % item)




##########################
##########################
##########################
# start date, end date, data type: High/Low/...
start = dt.datetime(2006, 1, 1)
end = dt.datetime(2020, 2, 1)
data_type = 'Adj Close'

##########################
# SP500 Index Data
df = pdr.DataReader('^GSPC', 'yahoo', start, end)[data_type] 
df = pd.DataFrame(df)
df.columns = ['SP500']
df.index.names = ['Date']    
df.to_csv("SP500.csv") 
  
##########################

names = pd.read_csv('sp500_symbols.csv')
tickers = names['Symbol'].values.tolist()

count = 0
while count < len(tickers):
    if not isinstance(tickers[count], str):
        tickers.remove(tickers[count])
    if tickers[count].find('.') == -1:
        count += 1
    else:
        tickers.remove(tickers[count])

print("Extracting Data...")



df = pdr.DataReader(tickers[0], 'yahoo', start, end)[data_type]
print(tickers[0])


# try extracting data from Yahoo, throw exception if no data
count = 1
while count < len(tickers):
    try:
        df = pd.concat([df, pdr.DataReader(tickers[count], 'yahoo', start, end)[data_type]], axis=1)
        print(tickers[count])
        count += 1
    except KeyError:
        print("No information for ticker", tickers[count])
        tickers.remove(tickers[count])
        continue
    except RemoteDataError:
        print("No information for ticker", tickers[count])
        tickers.remove(tickers[count])
        continue

# filtered symbols which have data available on Yahoo
appended_symbols = pd.DataFrame(tickers)


# some of these will not work due to the symbol naming system employed by Yahoo Finance
appended_symbols.to_csv('SP500SymbolsThatHaveData.csv')


df.columns = tickers
df.to_csv("SP500_AdjCloseData.csv")
frequency = 500  # Set Frequency To 2500 Hertz
duration = 800 # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)


#def get_data_from_yahoo(reload_sp500=False):
#    if reload_sp500:
#        tickers = save_sp500_tickers()
#    else:
#        with open("sp500tickers.pickle", "rb") as f:
#            tickers = pickle.load(f)
#            tickers = tickers[1:]
#    if not os.path.exists('stock_dfs'):
#        os.makedirs('stock_dfs')
#
#    start = dt.datetime(2008, 1, 1)
#    end = dt.datetime(2019, 1, 1)
#    
#    for ticker in tickers:
#        # just in case your connection breaks, we'd like to save our progress!
#        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
#            df = web.DataReader(ticker, 'yahoo', start, end)
#            df.reset_index(inplace=True)
#            df.set_index("Date", inplace=True)
#            df = df.drop("Symbol", axis=1)
#            df.to_csv('stock_dfs/{}.csv'.format(ticker))
#        else:
#            print('Already have {}'.format(ticker))
#    
#
#
#get_data_from_yahoo()

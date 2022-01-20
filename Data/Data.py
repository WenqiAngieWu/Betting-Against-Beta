# -*- coding: utf-8 -*-
"""
Fetch data
"""


from ftplib import FTP
import pandas as pd
import bs4 as bs
import datetime as dt
#import pickle
import requests
import pandas_datareader as pdr
from pandas_datareader._utils import RemoteDataError
import winsound

#### get symbols of stocks on NASDAQ & NYSE from nasdaqtrader.com ####
def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
        
#    with open("sp500tickers.pickle", "wb") as f:
#        pickle.dump(tickers, f)
    
    # write to txt
    with open('SP500_symbols.txt', 'w') as f:
        for item in tickers:
            f.write("%s" % item)
    
    sp500_info = pd.read_csv('SP500_symbols.txt', '\n', header = None)
    
    # write to csv
    sp500_info.to_csv('SP500_symbols.csv', index = False, header = ['Symbol'])


#### get symbols of stocks on NASDAQ & NYSE from nasdaqtrader.com ####
def save_nasdaq_nyse_tickers():
    
    directory = 'symboldirectory'
    filenames = ('otherlisted.txt', 'nasdaqlisted.txt')
    
    ftp = FTP('ftp.nasdaqtrader.com')
    ftp.login()
    ftp.cwd(directory)
    
    for item in filenames:
        ftp.retrbinary('RETR {0}'.format(item), open(item, 'wb').write)
        
    ftp.quit()
    
    
    #### reader symbols, export to csv ####
    # delete last row: empty row
    nasdaq_exchange_info = pd.read_csv('nasdaqlisted.txt', '|').iloc[:-1]
    other_exchange_info = pd.read_csv('otherlisted.txt', '|').iloc[:-1]
    
    # to csv
    nasdaq_exchange_info['Symbol'].to_csv('NASDAQ_symbols.csv', index = False, header = ['Symbol'])
    other_exchange_info['ACT Symbol'].to_csv('NYSE_symbols.csv', index = False, header = ['Symbol'])



    

#### get data according to tickers ####
def get_data(name, data_type, start, end):
    
    csvName = name + '_symbols.csv'
    names = pd.read_csv(csvName)
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
    
#    frequency = 500  # Set Frequency To 2500 Hertz
#    duration = 800 # Set Duration To 1000 ms == 1 second
#    winsound.Beep(frequency, duration)
    
    outputName = name + '_AdjCloseData.csv'
    df.columns = tickers
    df.to_csv(outputName)





#### get the market index ####
def get_index(name, data_type, start, end):
    if name == 'SP500': ticker = '^GSPC'
    elif name == 'TSX': ticker = '^GSPTSE'
    elif name == 'NASDAQ': ticker = '^IXIC'
    elif name == 'NYSE': ticker = '^NYA'
    
    
    df = pdr.DataReader(ticker, 'yahoo', start, end)[data_type] 
    df = pd.DataFrame(df)
    df.columns = [name]
    df.index.names = ['Date']   
    outputName = name + '.csv'
    df.to_csv(outputName) 
  
####################################################
####################################################



save_sp500_tickers()
save_nasdaq_nyse_tickers()

start = dt.datetime(2006, 1, 1)
end = dt.datetime(2020, 2, 1)
data_type = 'Adj Close'



get_data('SP500', data_type, start, end)
get_data('NASDAQ', data_type, start, end)
get_data('NYSE', data_type, start, end)
get_data('TSX', data_type, start, end)


get_index('SP500', data_type, start, end)
get_index('NASDAQ', data_type, start, end)
get_index('NYSE', data_type, start, end)
get_index('TSX', data_type, start, end)


# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 02:41:06 2020

@author: wuwen
"""

import pandas_datareader as pdr
import pandas as pd
import datetime as dt
from pandas_datareader._utils import RemoteDataError
import winsound


def grab_data(start_year, start_month, start_day, end_year, end_month, end_day, data_type):
    # data_type can be Open, High, Low, Close, Adj Close, etc.
    # Usually want Adj Close

    # csv_name should include '.csv' at the end.
    # it is the name of the file the data will be saved under

    print("Starting data grabbing process...")

    data_type = str(data_type)

    print("Appending .TO to symbol names...")
    start = dt.datetime(start_year, start_month, start_day)
    end = dt.datetime(end_year, end_month, end_day)

    names = pd.read_csv('tsx_symbols.csv')
    tickers = names['Symbol'].values.tolist()

    count = 0
    while count < len(tickers):
        if not isinstance(tickers[count], str):
            tickers.remove(tickers[count])
        if tickers[count].find('.') == -1:
            tickers[count] += '.TO'
            count += 1
        else:
            tickers.remove(tickers[count])

    print("Extracting Data...")

    df = pdr.DataReader(tickers[0], 'yahoo', start, end)[data_type]
    print(tickers[0])

    # try extracting data from Yahoo, throw exception if no data

    # POSSIBLE IMPROVEMENT:
    # multi-thread this long process
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
    appended_symbols.to_csv('TSXSymbolsThatHaveData.csv')

    df.columns = tickers
    df.to_csv("UnprocessedData.csv")


def main():
    grab_data(2006, 1, 1, 2020, 2, 1, "Adj Close")

    # delete rows which contain delayed data manually

#    df = pd.read_csv("UnprocessedData.csv")
#    df = df.dropna(how='any', axis=1)
#    df.to_csv("AdjCloseData.csv")
    
    frequency = 500  # Set Frequency To 2500 Hertz
    duration = 800 # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    
    
    
    # S&P/TSX Composite Index
    start = dt.datetime(2006,1,1)
    end = dt.datetime(2020,1,1)
    TSX = pdr.DataReader('^GSPTSE', 'yahoo', start, end)['Adj Close'] 
    
    TSX = pd.DataFrame(TSX)
    TSX.columns = ['TSX']
    TSX.index.names = ['Date']    
    TSX.to_csv("TSX.csv") 
if __name__ == '__main__':
    main()

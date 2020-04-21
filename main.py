# -*- coding: utf-8 -*-

#### library ####
import pandas as pd
import numpy as np
import datetime as dt
from pathlib import Path





#### parameter ####
rf = 0 # risk-free rate, future development: using T-bills rate data

#### path ####
dataPath = Path("Data/")
resultPath = Path("Output/")


#### read data ####
def read_data(name):
    """
    
    """
    dataPath = Path("Data/")
    
    nameDF = name + '_AdjCloseData.csv'
    tmpDF = pd.read_csv(dataPath / nameDF, index_col=0) # asset data
    
    nameMarket = name + '.csv'
    tmpMarket = pd.read_csv(dataPath / nameMarket, index_col=0) # market data
    
    tickers = list(tmpDF.columns[1:])
    tickers.insert(0, name)
    dates = [dt for dt in tmpDF.index if dt in tmpMarket.index] 
    
    df = tmpDF.loc[dates[0]:dates[-1], :] # asset df
    market = tmpMarket.loc[dates[0]:dates[-1], :] # market df
    
    del tmpDF
    del tmpMarket
    
    # to datetime
    df.index = pd.to_datetime(df.index)
    market.index = pd.to_datetime(market.index)
    
    return (df, market, tickers, dates)

############################################
############################################



#### deal with missing data ####
def missing_data(df, market):
    """
    TSX one observation fewer than df
    """
    if set(market.index) - set(df.index):
        missDate = list(set(market.index) - set(df.index)) # find the missing data in df
        market = market.drop(missDate, axis = 0) # delete the corresponding data in market data, otherwise, cant compute the correlation between them

    else:
        missDate = list(set(df.index) - set(market.index)) # find the missing data in df or in market
        df = df.drop(missDate, axis = 0)
    
    return (df, market)

############################################
############################################
def daily_returns(df):
    """
    daily returns
    """
    dailyReturn = lambda series:series.pct_change()
    dailyReturnDF = df.apply(dailyReturn, axis = 0)
    
    return dailyReturnDF
    

def monthly_returns(df):
    """
    monthly returns
    """
    total_return_from_returns = lambda returns:(returns + 1).prod() - 1 # Returns the return between the first and last value of the DataFrame
    monthlyReturn = lambda series:series.pct_change().groupby([series.pct_change().index.year, series.pct_change().index.month])\
    .apply(total_return_from_returns)

    monthlyReturnDF = df.apply(monthlyReturn, axis = 0)
    
    return monthlyReturnDF

#######


#### estimate beta ###
def estimate_beta(name, df, market):
    """
    estimate beta
    """
    # log return
    log_returns = lambda series:np.diff(np.log(series)) # log return function
    returnDF = df.apply(log_returns, axis = 0).fillna(0, axis=1) # too many zeros
    returnDF.index = df.index[1:] # assign date to index
    returnMarket = market.apply(log_returns, axis = 0).fillna(0, axis=1)
    returnMarket.index = market.index[1:]
    
    # three day log return
    three_day_log_returns = lambda series:np.log(series).shift(-2) - np.log(series).shift(1)# three day log return function
    threeDayReturnDF = df.apply(three_day_log_returns, axis = 0).iloc[1:,].fillna(0, axis=1)
    threeDayReturnMarket = market.apply(three_day_log_returns, axis = 0).iloc[1:,].fillna(0, axis=1)
    
    # volatility
    volatility = lambda series:series.rolling(250).std()
    volatilityDF = returnDF.apply(volatility, axis = 0)
    volatilityMarket = returnMarket.apply(volatility, axis = 0)
    
    # correlation 
    corr = lambda series:series.rolling(250*5).corr(threeDayReturnMarket[name])
    corrDF = threeDayReturnDF.apply(corr, axis = 0)
    
    # drop invalid values 
    idx = volatilityDF.index & volatilityMarket.index & corrDF.index
    volatilityDF = volatilityDF.loc[idx, :]
    volatilityMarket= volatilityMarket.loc[idx, :]
    corrDF = corrDF.loc[idx, :]
    
    # beta
    beta = .6 * corrDF.mul(volatilityDF, axis = 0).apply(lambda x:x.div(volatilityMarket[name]), axis = 0) + .4
    
    return (beta, idx)


############################
############################



#### BaB portfolio (daily rebalancing) ####
def portfolio_daily(idx, beta, dailyReturnDF):
    """
    daily rebalancing
    """
    betaRank = beta.rank(axis = 1) # same value: average their rank
    median = betaRank.mean(axis = 1) # average rank on each day
    k = 2 / abs(betaRank.subtract(median, axis = 0)).sum(axis = 1) # normalizing constant on each day
    w = betaRank.subtract(median, axis = 0).mul(k, axis = 0) # weight (+: high beta, -: low beta)
    
    # BaB factor
    wH = w.applymap(lambda x:x if x > 0 else 0) # relative weight assigned to high beta 
    wL = w.applymap(lambda x:-x if x < 0 else 0) # relative weight assigned to low beta
    
    
    returnDFBaB = dailyReturnDF.loc[idx, ].shift(-1, axis = 0)
    portfolioDailyL = (returnDFBaB.mul(wL, axis = 1).sum(axis = 1) - rf) / (beta.mul(wL, axis = 1).sum(axis = 1))
    portfolioDailyH = (returnDFBaB.mul(wH, axis = 1).sum(axis = 1) - rf) / (beta.mul(wH, axis = 1).sum(axis = 1))
    portfolioDaily = portfolioDailyL - portfolioDailyH
    
    # adjust index
    newIdx = pd.Index(list(portfolioDaily.index)[1:])
    portfolioDaily = portfolioDaily[:-1,]

    portfolioDaily.index = newIdx
    return portfolioDaily




#### BaB portfolio (monthly rebalancing) ####
def portfolio_monthly(idx, beta, monthlyReturnDF):
    betaRank = beta.rank(axis = 1) # same value: average their rank
    median = betaRank.mean(axis = 1) # average rank on each day
    k = 2 / abs(betaRank.subtract(median, axis = 0)).sum(axis = 1) # normalizing constant on each day
    w = betaRank.subtract(median, axis = 0).mul(k, axis = 0) # weight (+: high beta, -: low beta)
    
    tail = lambda x:x.tail(1)
    monthly = lambda x:x.groupby([x.index.year, x.index.month]).apply(tail)
    wMonthly = w.apply(monthly, axis = 0)
    betaMonthly = beta.apply(monthly, axis = 0)

    wMonthlyL = wMonthly.applymap(lambda x:-x if x < 0 else 0) # relative weight assigned to low beta
    wMonthlyH = wMonthly.applymap(lambda x:x if x > 0 else 0) # relative weight assigned to high beta


    monthlyIdx = wMonthly.index & betaMonthly.index
    monthlyReturnDFBaB = monthlyReturnDF.loc[monthlyIdx, ].shift(-1, axis = 0)


    portfolioMonthlyL = (monthlyReturnDFBaB.mul(wMonthlyL, axis = 1).sum(axis = 1) - rf) / (betaMonthly.mul(wMonthlyL, axis = 1).sum(axis = 1))
    portfolioMonthlyH = (monthlyReturnDFBaB.mul(wMonthlyH, axis = 1).sum(axis = 1) - rf) / (betaMonthly.mul(wMonthlyH, axis = 1).sum(axis = 1))
    portfolioMonthly = portfolioMonthlyL - portfolioMonthlyH
    
    # adjust index
    newIdx = pd.Index(list(portfolioMonthly.index)[1:])
    portfolioMonthly = portfolioMonthly[:-1,]

    portfolioMonthly.index = newIdx
    
    # reset index ( to datetime)
    portfolioMonthly.index = portfolioMonthly.index.droplevel([0,1]) 
    
    return portfolioMonthly

#### Equal-weighted BaB portfolio (monthly rebalancing) ####
def portfolio_monthly_equal_weighted(idx, beta, monthlyReturnDF):
    beta = beta.dropna(how = 'all', axis = 0)
    median = beta.mean(axis = 1) # average rank on each day
    
    # assign weight to those whose beta larger than mean
    compare_1 = lambda x: 1 if x else 0
    assign_1 = lambda x: (x > median).apply(compare_1)
    tmp_w = beta.apply(assign_1, axis = 0)
    
    avg = lambda x: x.divide(tmp_w.sum(axis = 1))
    wH = tmp_w.apply(avg, axis = 0)
    
    
    # assign weight to those whose beta lower than mean
    compare_2 = lambda x: 1 if x else 0
    assign_2 = lambda x: (x <= median).apply(compare_2)
    tmp_w = beta.apply(assign_2, axis = 0)
    
    avg_2 = lambda x: x.divide(tmp_w.sum(axis = 1))
    wL = tmp_w.apply(avg_2, axis = 0)
    
    w = wL - wH
    
    # monthly
    tail = lambda x:x.tail(1)
    
    monthly = lambda x:x.groupby([x.index.year, x.index.month]).apply(tail)
    wMonthly = w.apply(monthly, axis = 0)
    betaMonthly = beta.apply(monthly, axis = 0)

    # pick monthly return
    monthlyIdx = wMonthly.index & betaMonthly.index
    monthlyReturnDFBaB = monthlyReturnDF.loc[monthlyIdx, ].shift(-1, axis = 0)
    
    portfolioMonthly = (monthlyReturnDFBaB * wMonthly).sum(axis = 1)

    
    # adjust index
    newIdx = pd.Index(list(portfolioMonthly.index)[1:])
    portfolioMonthly = portfolioMonthly[:-1,]

    portfolioMonthly.index = newIdx
    
    # reset index ( to datetime)
    portfolioMonthly.index = portfolioMonthly.index.droplevel([0,1]) 
    
    return portfolioMonthly


#### hedge the short position with equal weighted portfolio ####
def portfolio_monthly_hegding_EW(idx, beta, monthlyReturnDF):
    
    tail = lambda x:x.tail(1)
    monthly = lambda x:x.groupby([x.index.year, x.index.month]).apply(tail)
    
    ## long position
    beta = beta.dropna(how = 'all', axis = 0)
    median = beta.mean(axis = 1) # average rank on each day
    
    # assign weight to those whose beta larger than median
    compare = lambda x: 1 if x else 0
    assign = lambda x: (x < median).apply(compare)
    tmp_w = beta.apply(assign, axis = 0)
    
    avg = lambda x: x.divide(tmp_w.sum(axis = 1))
    wL = tmp_w.apply(avg, axis = 0)
    
    wMonthlyL = wL.apply(monthly, axis = 0)
    
    ## short position
    betaRank = beta.rank(axis = 1) # same value: average their rank
    median = betaRank.mean(axis = 1) # average rank on each day
    k = 2 / abs(betaRank.subtract(median, axis = 0)).sum(axis = 1) # normalizing constant on each day
    w = betaRank.subtract(median, axis = 0).mul(k, axis = 0) # weight (+: high beta, -: low beta)
    

    wMonthly = w.apply(monthly, axis = 0)
    betaMonthly = beta.apply(monthly, axis = 0)

    wMonthlyH = wMonthly.applymap(lambda x:x if x > 0 else 0) # relative weight assigned to high beta


    monthlyIdx = wMonthly.index & betaMonthly.index
    monthlyReturnDFBaB = monthlyReturnDF.loc[monthlyIdx, ].shift(-1, axis = 0)


    portfolioMonthlyL = (monthlyReturnDFBaB * wMonthlyL).sum(axis = 1)
    portfolioMonthlyH = (monthlyReturnDFBaB.mul(wMonthlyH, axis = 1).sum(axis = 1) - rf) / (betaMonthly.mul(wMonthlyH, axis = 1).sum(axis = 1))
    portfolioMonthly = portfolioMonthlyL - portfolioMonthlyH
    
    # adjust index
    newIdx = pd.Index(list(portfolioMonthly.index)[1:])
    portfolioMonthly = portfolioMonthly[:-1,]

    portfolioMonthly.index = newIdx
    
    # reset index ( to datetime)
    portfolioMonthly.index = portfolioMonthly.index.droplevel([0,1]) 
    
    return portfolioMonthly
    
    
    
    

#### Monthly cumulative return between specified start and end date ####
def portfolio_monthly_cum_ret(portfolioMonthly, start, end):
    portfolioMonthly = portfolioMonthly.drop(index = portfolioMonthly.idxmin())  # after dropping the downside outlier
    portfolioMonthly = portfolioMonthly.drop(index = portfolioMonthly.idxmax())  # after dropping the downside outlier
    
    # filter date
    portfolioMonthly = portfolioMonthly.loc[(portfolioMonthly.index > start) & (portfolioMonthly.index < end)]
    
    # cumulative return
    portfolioMonthlyCum = (1 + portfolioMonthly).cumprod()
    # add 1 (initial investment) to the first row
    firstDate = portfolioMonthlyCum.index[0] - pd.Timedelta(days = portfolioMonthly.index[0].day - 1)
    first = pd.Series([initialInvest], index = [firstDate])
    portfolioMonthlyCum = pd.concat([first, portfolioMonthlyCum])
    
    return pd.DataFrame(portfolioMonthlyCum)

#### to csv #####
def to_csv_cum_ret(resultPath, name, data, method):
    resultName = name + '_' +  method + '.csv'
    data.index.name = 'Date'
    data.columns = [name]
    data.to_csv(resultPath / resultName)



###############################################
###############################################
#################################################
name = 'NYSE' #SP500/TSX
start = dt.datetime(2011, 12, 31)
end = dt.datetime(2020, 1, 1)
initialInvest = 1

df, market, tickers, dates = read_data(name)
df, market = missing_data(df, market)

dailyReturnDF = daily_returns(df)
monthlyReturnDF = monthly_returns(df)
beta, idx = estimate_beta(name, df, market)


portfolioMonthly = portfolio_monthly(idx, beta, monthlyReturnDF)
portfolioMonthlyCum = portfolio_monthly_cum_ret(portfolioMonthly, start, end)


## compare with equal weighted
portfolioMonthly_equal_weighted = portfolio_monthly_equal_weighted(idx, beta, monthlyReturnDF)
portfolioMonthlyCum_equal_weighted = portfolio_monthly_cum_ret(portfolioMonthly_equal_weighted, start, end)


## compare with hedging the short position by equal-weighted long position
portfolioMonthly_hedging_EW = portfolio_monthly_hegding_EW(idx, beta, monthlyReturnDF)
portfolioMonthlyCum_hedging_EW = portfolio_monthly_cum_ret(portfolioMonthly_hedging_EW, start, end)

## to csv
to_csv_cum_ret(resultPath, name, portfolioMonthlyCum, 'CumRet')
to_csv_cum_ret(resultPath, name, portfolioMonthlyCum_equal_weighted, 'CumRet_EqualWeighted')
to_csv_cum_ret(resultPath, name, portfolioMonthlyCum_hedging_EW, 'CumRet_Hedging_EqualWeighted')

##################################

    









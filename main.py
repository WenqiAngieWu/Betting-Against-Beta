# -*- coding: utf-8 -*-

#### library ####
import pandas as pd
import numpy as np
from pathlib import Path
#import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib
from IPython.display import set_matplotlib_formats


#### prettify the figure ####
plt.style.use(['seaborn-white', 'seaborn-paper'])
matplotlib.rc('font', family='Times New Roman', size=15)
set_matplotlib_formats('png', 'png', quality=90)
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['figure.autolayout'] = False
plt.rcParams['figure.figsize'] = 8, 5
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['font.size'] = 12
plt.rcParams['lines.linewidth'] = 1.0
plt.rcParams['lines.markersize'] = 8
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['ytick.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.serif'] = 'cm'
plt.rcParams['axes.grid'] = True

kw_save = dict(bbox_iches='tight', transparent=True)




#### parameter ####
rf = 0 # risk-free rate

#### read data ####

dataPath = Path("Data/")
tmpDF = pd.read_csv(dataPath / "TSX_AdjCloseData.csv", index_col=0)
tmpTSX = pd.read_csv(dataPath / "TSX.csv", index_col=0) # S&P/TSX Composite Index


# =============================================================================
dataPath = Path("Data/")
tmpDF = pd.read_csv(dataPath / "SP500_AdjCloseData.csv", index_col=0)
tmpTSX = pd.read_csv(dataPath / "SP500.csv", index_col=0) # S&P/TSX Composite Index
# =============================================================================


tickers = list(tmpDF.columns[1:])
tickers.insert(0, "TSX")
dates = [dt for dt in tmpDF.index if dt in tmpTSX.index] 
df = tmpDF.loc[dates[0]:dates[-1], :] # stock df
TSX = tmpTSX.loc[dates[0]:dates[-1], :] # TSX Index df
del tmpDF
del tmpTSX

# TSX one observation fewer than df
missDate = list(set(TSX.index) - set(df.index)) # find the missing data in df
TSX = TSX.drop(missDate, axis = 0) # delete the corresponding data in TSX

# to datetime
df.index = pd.to_datetime(df.index)
TSX.index = pd.to_datetime(TSX.index)


#### monthly returns ####
total_return_from_returns = lambda returns:(returns + 1).prod() - 1 # Retuns the return between the first and last value of the DataFrame
monthlyReturn = lambda series:series.pct_change().groupby([series.pct_change().index.year, series.pct_change().index.month])\
.apply(total_return_from_returns)

monthlyReturnDF = df.apply(monthlyReturn, axis = 0)



#### estimate beta ###
# log return
log_returns = lambda series:np.diff(np.log(series)) # log return function
returnDF = df.apply(log_returns, axis = 0) # too many zeros
returnDF.index = df.index[1:] # assign date to index
returnTSX = TSX.apply(log_returns, axis = 0)
returnTSX.index = TSX.index[1:]

# three day log return
three_day_log_returns = lambda series:np.log(series).shift(-2) - np.log(series).shift(1)# three day log return function
threeDayReturnDF = df.apply(three_day_log_returns, axis = 0).iloc[1:,]
threeDayReturnTSX = TSX.apply(three_day_log_returns, axis = 0).iloc[1:,]

# volatility
volatility = lambda series:series.rolling(250).std()
volatilityDF = returnDF.apply(volatility, axis = 0).dropna(how='all')
volatilityTSX = returnTSX.apply(volatility, axis = 0).dropna(how='all')

# correlation 
corr = lambda series:series.rolling(250*5).corr(threeDayReturnTSX["TSX"])
corrDF = threeDayReturnDF.apply(corr, axis = 0).dropna(how='all')  


# =============================================================================
corr = lambda series:series.rolling(250*5).corr(threeDayReturnTSX["SP500"])
corrDF = threeDayReturnDF.apply(corr, axis = 0).dropna(how='all')  
# =============================================================================

# drop invalid values 
idx = volatilityDF.index & volatilityTSX.index & corrDF.index
volatilityDF = volatilityDF.loc[idx, :]
volatilityTSX = volatilityTSX.loc[idx, :]
corrDF = corrDF.loc[idx, :]

# beta
beta = .6 * corrDF.mul(volatilityDF, axis = 0).apply(lambda x:x.div(volatilityTSX["TSX"]), axis = 0) + .4

# =============================================================================
beta = .6 * corrDF.mul(volatilityDF, axis = 0).apply(lambda x:x.div(volatilityTSX["SP500"]), axis = 0) + .4
# =============================================================================



#### BaB portfolio (daily rebalancing) ####
betaRank = beta.rank(axis = 1) # same value: average their rank
median = betaRank.mean(axis = 1) # average rank on each day
k = 2 / abs(betaRank.subtract(median, axis = 0)).sum(axis = 1) # normalizing constant on each day
w = betaRank.subtract(median, axis = 0).mul(k, axis = 0) # weight (+: high beta, -: low beta)

# BaB factor
wH = w.applymap(lambda x:x if x > 0 else 0) # relative weight assigned to high beta 
wL = w.applymap(lambda x:-x if x < 0 else 0) # relative weight assigned to low beta


returnDFBaB = returnDF.loc[idx, ].shift(-1, axis = 0)
portfolioDailyL = (returnDFBaB.mul(wL, axis = 1).sum(axis = 1) - rf) / (beta.mul(wL, axis = 1).sum(axis = 1))
portfolioDailyH = (returnDFBaB.mul(wH, axis = 1).sum(axis = 1) - rf) / (beta.mul(wH, axis = 1).sum(axis = 1))
portfolioDaily = portfolioDailyL - portfolioDailyH
portfolioDaily.plot()



#### BaB portfolio (monthly rebalancing) ####
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
portfolioMonthly.plot() # one downside outlier, so drop it

portfolioMonthly = portfolioMonthly.drop(index = portfolioMonthly.idxmin())  # after dropping the downside outlier

portfolioMonthly.index = portfolioMonthly.index.droplevel([0,1]) # reset index (datetime)
portfolioMonthly.plot()




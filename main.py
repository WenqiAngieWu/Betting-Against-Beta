# -*- coding: utf-8 -*-
"""

"""
### library ###
import pandas as pd
import numpy as np
from pathlib import Path


### read data ###
# TSX 比 df 少一个obs
dataPath = Path("Data/")
tmpDF = pd.read_csv(dataPath / "AdjCloseData.csv", index_col=0)
tmpTSX = pd.read_csv(dataPath / "TSX.csv", index_col=0)
tickers = list(tmpDF.columns[1:])
tickers.insert(0, "TSX")
dates = [dt for dt in tmpDF.index if dt in tmpTSX.index] 
df = tmpDF.loc[dates[0]:dates[-1], ]
del tmpDF
del tmpTSX




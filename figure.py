# -*- coding: utf-8 -*-
"""
Create figure for slides
"""


import matplotlib
from IPython.display import set_matplotlib_formats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import datetime as dt


####################
dataPath = Path("Data/")
resultPath = Path("Output/")
####################


####################
#### rank weighted vs equal weighted
x = np.arange(0, 1.05, 0.05)
y = 8*(x - 0.5)
func = lambda x:-3 if x<1/3 else 3
x2 = np.arange(0, 1/3, 1/30)
z2 = list(map(func, x2))

x3 = np.arange(2/3, 1, 1/30)
z3 = list(map(func, x3))

fig, ax = plt.subplots()
ax.plot(x, y, label = 'Rank-weighted')
ax.plot(x2, z2, label = 'Equal-weighted')
ax.plot(x3, z3, label = 'Equal-weighted')

ax.set_xlim(0, 1)
ax.set_ylim(-4, 4)

plt.xlabel('Sorting Variable Rank r')
plt.ylabel('Portfolio Weight')
plt.legend()
plt.grid(True)

plt.savefig(resultPath / 'rankWvsEqualW.png')
plt.show()




####################
###################
#### BAB in US and CAN
start = dt.datetime(2012,1,1)
end = dt.datetime(2020,1,1)

equityCANCumRet = pd.read_csv(resultPath / "TSX_CumRet.csv", index_col = 0)
equityCANCumRet.columns = ['CAN']

equityUSCumRet = pd.read_csv(resultPath / "SP500_CumRet.csv", index_col = 0)
equityUSCumRet.columns = ['US']

SMBCAN = pd.read_csv(dataPath / "SMBCAN.csv", index_col = 0)
SMBUS = pd.read_csv(dataPath / "SMBUS.csv", index_col = 0)
HMLCAN = pd.read_csv(dataPath / "HMLCAN.csv", index_col = 0)
HMLUS = pd.read_csv(dataPath / "HMLUS.csv", index_col = 0)


equityCANCumRet.index = pd.to_datetime(equityCANCumRet.index)
equityUSCumRet.index = pd.to_datetime(equityUSCumRet.index)
SMBCAN.index = pd.to_datetime(SMBCAN.index)
SMBUS.index = pd.to_datetime(SMBUS.index)
HMLCAN.index =  pd.to_datetime(HMLCAN.index)
HMLUS.index= pd.to_datetime(HMLUS.index)

equityCANCumRet = equityCANCumRet.loc[start:end, ]
equityUSCumRet  = equityUSCumRet.loc[start:end, ]
SMBCAN = SMBCAN.loc[start:end, ]
SMBUS = SMBUS.loc[start:end, ]
HMLCAN = HMLCAN.loc[start:end, ]
HMLUS = HMLUS.loc[start:end, ]


## Cumulative return
SMBCANCumRet = (1 + SMBCAN['CAN']).cumprod()
HMLCANCumRet = (1 + HMLCAN['CAN']).cumprod()


SMBUSCumRet = (1 + SMBUS['US']).cumprod()
HMLUSCumRet = (1 + HMLUS['US']).cumprod()



# add 1 (initial investment) to the first row
initialInvest = 1
firstDate = SMBCANCumRet.index[0] - pd.Timedelta(days = SMBCAN.index[0].day - 1)
first = pd.Series([initialInvest], index = [firstDate])
SMBCANCumRet = pd.concat([first, SMBCANCumRet])
HMLCANCumRet = pd.concat([first, HMLCANCumRet])
SMBUSCumRet = pd.concat([first, SMBUSCumRet])
HMLUSCumRet = pd.concat([first, HMLUSCumRet])


## plot
#appendS = lambda x:'$' + x # append dollar sign $ to the values
#equityCANCumRet = equityCANCumRet.astype(str).apply(appendS)
#SMBCANCumRet = SMBCANCumRet.astype(str).apply(appendS)
#HMLCANCumRet = HMLCANCumRet.astype(str).apply(appendS)



plt.ylabel('Cumulative Return')
equityCANCumRet.plot(color='blue', grid=True, label='BAB')
SMBCANCumRet.plot(color='red', grid=True, label='SMB')
HMLCANCumRet.plot(color='green', grid=True, label='HML')
plt.legend()
plt.xticks(rotation = 0)
plt.savefig(resultPath / 'CAN.png')
plt.show()



equityUSCumRet.plot(color='blue', grid=True, label='BAB')
SMBUSCumRet.plot(color='red', grid=True, label='SMB')
HMLUSCumRet.plot(color='green', grid=True, label='HML')
plt.legend()
plt.xticks(rotation = 0)
plt.savefig(resultPath / 'US.png')
plt.show()



################
################


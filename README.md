# Betting-Against-Beta

This project is based upon the paper: Frazzini, A. \& Pedersen, L. (2014). *Betting against beta*. (referred to as "the paper" in the following content)

## Data
- `Data` folder stores the fetched data and `Data.py`.

- `Data.py` consists of 2 parts: save tickers, get data. Tickers are processed through website information, data are fetched using 'pandas-datareader'.


## Implementation
- `main.py` contains all the functions.

- `figure.py` is for drawing plots.


## Results

The strategy was back-tested on SP500 stocks and TSX (Toronto Stock Exchange) stocks and compared with two other similar factors presented in the Fama French 3-factor model: one is the SMB (small minus big), the other is the HML (high minus low).
![US](Output/US.png)
Figure 1: *Cumulative Return with $1 invested in the beginning in the SP500 (shown as US) equity market (in comparison with the SMB and HML factors)*

![CAN](Output/CAN.png)
Figure 2: *Cumulative Return with $1 invested in the beginning in the TSX (shown as CAN) equity market (in comparison with the SMB and HML factors)*

## Evaluation
- Portfolio construction
![US Equal W](Output/SP500EqualW.png)

- Hedging
![US Hedge](Output/SP500Hedge.png)

- Trading cost




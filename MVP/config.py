CONFIG = {
    "data": {
        "ticker": "BTC-USD",            #Type of Stock
        "period": "1y",                 #Timeframe of Data
        "interval": "1h"                #Tick-Duration
    },
    "backtest": {
        "initial_capital": 1_000_000,   #Initial Capital
        "verbose": False                #Extra Console Output every 20 Ticks
    },
    "strategy": {
        "window_size": 15,              #How many past Ticks are taken into account
        "threshold_buy": 0.0001,        #Buy Signal Brake
        "threshold_sell": 0.0001        #Sell Signal Brake
    },
    "metrics": {
        "trading_days_per_year": 365,   #Infos regarding the specified Stock
        "hours_per_day": 24,               
        "interval_hours": 1                
    }
}
CONFIG = {
    "data": {
        "ticker": "BTC-USD",            #Type of Stock
        "period": "2y",                 #Timeframe of Data
        "interval": "1h"                #Tick-Duration
    },
    "backtest": {
        "initial_capital": 1_000_000,   #Initial Capital
    },
    "strategies": {
        "buy_and_hold": {
            "enabled": True
        },
        "moving_average": {
            "enabled": True,
            "window_size": 20,
            "threshold_buy": 0.01,
            "threshold_sell": 0.01
        },
        "rsi": {
            "enabled": True,
            "window_size": 14,
            "oversold": 30,
            "overbought": 70
        },
        "dual_ma": {
            "enabled": True,
            "window_short": 10,
            "window_long": 50
        },
        "bollinger": {
            "enabled": True,
            "window_size": 20,
            "num_std": 2
        }
    },
    "metrics": {
        "trading_days_per_year": 365,   #Infos regarding the specified Stock
        "hours_per_day": 24,               
        "interval_hours": 1                
    }
}
import pandas as pd
import numpy as np
from load_data import get_yahoo_data
from pathlib import Path
from backtest import backtest
from strategy import mov_avg_strat


def main():
    print("\n" + "="*60)
    print("BACKTESTER STARTER")
    print("="*60)

    get_yahoo_data(ticker="BTC-USD", period="1y", interval="1h")


    # Initialize backtest
    backtest_runner = backtest(
        charts_file='MVP/data/BTC-USD_live.csv',
        strategy=mov_avg_strat(window_size=15),
        initial_capital = 1000000
    )
    
    backtest_runner.load_data()
    backtest_runner.run_backtest(verbose=False)
    backtest_runner.show_results()

if __name__ == '__main__':
    main()
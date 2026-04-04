import pandas as pd
import numpy as np
from load_data import get_yahoo_data
from pathlib import Path
from backtest import backtest
from strategy import mov_avg_strat
from config import CONFIG


def main():
    print("\n" + "="*60)
    print("BACKTESTER STARTER")
    print("="*60)

    # Loading data
    get_yahoo_data(
        ticker=CONFIG["data"]["ticker"],
        period=CONFIG["data"]["period"],
        interval=CONFIG["data"]["interval"]
    )

    # Initialize strategy
    strategy = mov_avg_strat(
        window_size=CONFIG["strategy"]["window_size"],
        threshold_buy=CONFIG["strategy"]["threshold_buy"],
        threshold_sell=CONFIG["strategy"]["threshold_sell"]
    )

    # Initialize backtest
    backtest_runner = backtest(
        charts_file=f'MVP/data/{CONFIG["data"]["ticker"]}_live.csv',
        strategy=strategy,
        initial_capital=CONFIG["backtest"]["initial_capital"]
    )
    
    # Run backtest
    backtest_runner.load_data()
    backtest_runner.run_backtest(verbose=CONFIG["backtest"]["verbose"])
    backtest_runner.show_results()

if __name__ == '__main__':
    main()
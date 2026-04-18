import pandas as pd
import numpy as np
from load_data import get_yahoo_data
from backtest import backtest
from strategy import mov_avg_strat, rsi_strat, dual_ma_strat, bollinger_strat, buy_and_hold_strat
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

    # Nur enabled Strategien initialisieren
    strategies = []

    if CONFIG["strategies"]["moving_average"]["enabled"]:
        strategies.append(mov_avg_strat(
            window_size=CONFIG["strategies"]["moving_average"]["window_size"],
            threshold_buy=CONFIG["strategies"]["moving_average"]["threshold_buy"],
            threshold_sell=CONFIG["strategies"]["moving_average"]["threshold_sell"]
        ))

    if CONFIG["strategies"]["rsi"]["enabled"]:
        strategies.append(rsi_strat(
            window_size=CONFIG["strategies"]["rsi"]["window_size"],
            oversold=CONFIG["strategies"]["rsi"]["oversold"],
            overbought=CONFIG["strategies"]["rsi"]["overbought"]
        ))

    if CONFIG["strategies"]["dual_ma"]["enabled"]:
        strategies.append(dual_ma_strat(
            window_short=CONFIG["strategies"]["dual_ma"]["window_short"],
            window_long=CONFIG["strategies"]["dual_ma"]["window_long"]
        ))

    if CONFIG["strategies"]["bollinger"]["enabled"]:
        strategies.append(bollinger_strat(
            window_size=CONFIG["strategies"]["bollinger"]["window_size"],
            num_std=CONFIG["strategies"]["bollinger"]["num_std"]
        ))

    if CONFIG["strategies"]["buy_and_hold"]["enabled"]:
        strategies.append(buy_and_hold_strat(
        ))

    # Initialize backtest
    backtest_runner = backtest(
        charts_file=f'MVP/data/{CONFIG["data"]["ticker"]}_live.csv',
        strategies=strategies,
        initial_capital=CONFIG["backtest"]["initial_capital"]
    )

    # Run backtest
    backtest_runner.load_data()
    backtest_runner.run_backtest()
    backtest_runner.show_results()


if __name__ == '__main__':
    main()
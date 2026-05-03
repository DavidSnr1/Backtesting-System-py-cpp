import pandas as pd
import numpy as np
import subprocess
import sys
import time
import os
from load_data import get_yahoo_data
from backtest import backtest
from strategy import mov_avg_strat, rsi_strat, dual_ma_strat, bollinger_strat, buy_and_hold_strat
from config import CONFIG


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def run_cpp_backtest(csv_path):
    # Binary name depends on the OS
    binary_name = "backtest.exe" if sys.platform == "win32" else "backtest"
    binary = os.path.join(PROJECT_ROOT, "data", "cpp", binary_name)

    if not os.path.exists(binary):
        print("\nC++ binary not found at:")
        print(binary)
        print("Compile from repository root with:")
        if sys.platform == "win32":
            print("  g++ -O2 -std=c++17 -o data/cpp/backtest.exe data/cpp/backtest.cpp")
        else:
            print("  g++ -O2 -std=c++17 -o data/cpp/backtest data/cpp/backtest.cpp")
        return None

    cpp_args = [
        binary,
        os.path.abspath(csv_path),
        "all",
        str(CONFIG["backtest"]["initial_capital"]),
        str(CONFIG["backtest"]["fraction_position"]),
        str(CONFIG["transaction_cost"]),
        str(CONFIG["metrics"]["trading_days_per_year"]),
        str(CONFIG["metrics"]["hours_per_day"]),
        str(CONFIG["metrics"]["interval_hours"]),
        str(CONFIG["strategies"]["moving_average"]["window_size"]),
        str(CONFIG["strategies"]["moving_average"]["threshold_buy"]),
        str(CONFIG["strategies"]["moving_average"]["threshold_sell"]),
        str(CONFIG["strategies"]["rsi"]["window_size"]),
        str(CONFIG["strategies"]["rsi"]["oversold"]),
        str(CONFIG["strategies"]["rsi"]["overbought"]),
        str(CONFIG["strategies"]["dual_ma"]["window_short"]),
        str(CONFIG["strategies"]["dual_ma"]["window_long"]),
        str(CONFIG["strategies"]["bollinger"]["window_size"]),
        str(CONFIG["strategies"]["bollinger"]["num_std"]),
    ]

    result = subprocess.run(
        cpp_args,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"\nC++ error: {result.stderr}")
        return None

    # parsing output: every strategy is separated by "---"
    all_results = []
    current = {}
    for line in result.stdout.strip().split('\n'):
        if line == "---":
            if current:
                all_results.append(current)
                current = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            try:
                current[key] = float(value)
            except ValueError:
                current[key] = value
    if current:
        all_results.append(current)

    return all_results


def print_cpp_comparison(python_ms, cpp_results):
    if not cpp_results:
        return

    total_cpp_ms = sum(r.get("runtime_ms", 0.0) for r in cpp_results)
    speedup = (python_ms / total_cpp_ms) if total_cpp_ms > 0 else float("inf")

    print("\n" + "="*60)
    print("PYTHON vs C++ PERFORMANCE")
    print("="*60)
    print(f"Python:  {python_ms:.1f}ms")
    print(f"C++:     {total_cpp_ms:.1f}ms")
    if speedup == float("inf"):
        print("Speedup: n/a (C++ runtime not reported)")
    else:
        print(f"Speedup: {speedup:.0f}x faster")
    print("="*60)


def main():
    print("\n" + "="*60)
    print("BACKTESTER STARTER")
    print("="*60)

    csv_path = os.path.join(PROJECT_ROOT, "data", f"{CONFIG['data']['ticker']}_live.csv")

    # Loading data
    get_yahoo_data(
        ticker=CONFIG["data"]["ticker"],
        period=CONFIG["data"]["period"],
        interval=CONFIG["data"]["interval"]
    )

    # only initialize enabled strategies
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
        strategies.append(buy_and_hold_strat())

    # Initialize backtest
    backtest_runner = backtest(
        charts_file=csv_path,
        strategies=strategies,
        initial_capital=CONFIG["backtest"]["initial_capital"],
        fraction_position=CONFIG["backtest"]["fraction_position"]
    )

    # Python backtest timer
    start = time.time()
    backtest_runner.load_data()
    backtest_runner.run_backtest()
    python_ms = (time.time() - start) * 1000

    backtest_runner.show_results()

    # C++ backtest comparison
    cpp_results = run_cpp_backtest(csv_path)
    print_cpp_comparison(python_ms, cpp_results)


if __name__ == '__main__':
    main()
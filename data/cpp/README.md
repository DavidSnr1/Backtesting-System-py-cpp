# C++ Backtest Engine Technical Documentation

This document explains the C++ engine in detail.

File in scope: backtest.cpp
Purpose: execute the same strategy logic and portfolio math as the Python engine, with lower runtime overhead for benchmarking and production-style compute speed.

## 1. What This Binary Does

The C++ program:

1. Reads market prices from a CSV file.
2. Reads runtime parameters from a key=value config file.
3. Selects strategies based on runtime config (or optional CLI override).
4. Runs each strategy through the same core backtest loop.
5. Prints a machine-parseable result block per strategy.

It is designed so Python can call it via subprocess and parse deterministic text output.

## 2. Build and Run

### Build (from data/cpp)

Using Makefile:

```bash
make
```

Direct compile:

```bash
g++ -O2 -std=c++17 -o backtest backtest.cpp
```

Windows direct compile from repository root:

```bash
g++ -O2 -std=c++17 -o data/cpp/backtest.exe data/cpp/backtest.cpp
```

### Run

CLI signature:

```text
backtest[.exe] <csv_file> <runtime_config_file> [strategy]
```

Examples:

```bash
./backtest ../../data/BTC-USD_live.csv runtime_config.txt
./backtest ../../data/BTC-USD_live.csv runtime_config.txt rsi
```

On Windows from repository root:

```bash
data/cpp/backtest.exe data/BTC-USD_live.csv data/cpp/runtime_config.txt
```

## 3. Input Contracts

### 3.1 CSV contract

The loader expects:

1. First line is a header.
2. Each following line contains at least one comma.
3. Price is parsed from substring after the first comma.

Implication:

1. Compatible with current generated format: tick,price.
2. The first column is ignored by the C++ parser.
3. Malformed numeric rows are skipped silently.

### 3.2 Runtime config contract

File format is line-based key=value.

Rules:

1. Empty lines are ignored.
2. Lines starting with # are comments.
3. Unknown keys are ignored.
4. Conversion errors fail fast with a descriptive message.

Required operational key:

1. enabled_strategies must resolve to a non-empty list, otherwise the program exits with error.

Supported keys:

1. initial_capital
2. fraction_position
3. transaction_cost
4. trading_days
5. hours_per_day
6. interval_hours
7. mov_avg_window
8. mov_avg_threshold_buy
9. mov_avg_threshold_sell
10. rsi_window
11. rsi_oversold
12. rsi_overbought
13. dual_ma_window_short
14. dual_ma_window_long
15. bollinger_window
16. bollinger_num_std
17. enabled_strategies (comma-separated)

## 4. Core Data Structures

### RuntimeConfig

Stores all tunable numeric parameters used by signal generation and metrics annualization.

### Portfolio

State:

1. cash
2. shares
3. initial_capital
4. fees
5. transaction_cost
6. buy_history (prices)
7. sell_history (prices)

Methods:

1. check_buy(size, price)
2. buy(size, price)
3. check_sell(size)
4. sell(size, price)
5. total(current_price)
6. profit_loss(current_price)
7. roi(current_price)
8. max_dd(total_history)
9. sharpe_ratio(total_history, trading_days, hours_per_day, interval_hours)
10. calculate_win_rate()

### BacktestResult

Per-strategy output payload:

1. final_value
2. roi
3. profit_loss
4. max_dd
5. sharpe
6. win_rate
7. total_fees
8. total_trades
9. runtime_ms
10. strategy_name

## 5. Strategy Implementations

Implemented signal functions:

1. mov_avg_signal
2. buy_and_hold_signal
3. rsi_signal
4. dual_ma_signal
5. bollinger_signal

Each returns one of three strings: buy, sell, hold.

### 5.1 Moving Average

1. Uses lookback window ending at idx-1.
2. buy when current_price > avg * (1 + threshold_buy).
3. sell when current_price < avg * (1 - threshold_sell).

### 5.2 Buy and Hold

1. buy only at idx == 0.
2. hold forever after initial buy.

### 5.3 RSI

1. Computes gains/losses over lookback window.
2. RSI is 100 when losses == 0.
3. buy when RSI < oversold.
4. sell when RSI > overbought.

### 5.4 Dual MA

1. Computes short and long moving averages.
2. buy when short_avg > long_avg.
3. sell when short_avg < long_avg.

### 5.5 Bollinger Bands

1. Computes mean and standard deviation on lookback window.
2. upper = mean + num_std * std_dev.
3. lower = mean - num_std * std_dev.
4. sell above upper, buy below lower.

## 6. Backtest Execution Flow

Function: run_backtest(charts, strategy_name, cfg)

Execution sequence:

1. Start high-resolution timer.
2. Create Portfolio with initial capital and transaction_cost.
3. Iterate over all ticks.
4. Dispatch signal function by strategy_name.
5. Execute buy/sell policy.
6. Append total portfolio value to total_history.
7. Stop timer.
8. Compute metrics and build BacktestResult.

Trade sizing policy:

1. On buy: size = int(cash * fraction_position / price).
2. Buy only when size > 0 and check_buy passes.
3. On sell signal: liquidate all current shares.

This means each sell is full position exit, while buys are fractional capital entries.

## 7. Metric Formulas

Given final price p_last:

1. total = cash + shares * p_last
2. profit_loss = total - initial_capital
3. roi = (profit_loss / initial_capital) * 100

Max drawdown:

1. Track running peak in total_history.
2. drawdown = (peak - value) / peak
3. max_dd = max(drawdown) * 100

Sharpe ratio:

1. returns_t = (V_t - V_{t-1}) / V_{t-1}
2. mean = average(returns)
3. std_dev = standard deviation(returns) using population divisor n
4. periods_per_year = trading_days * hours_per_day / interval_hours
5. sharpe = (mean / std_dev) * sqrt(periods_per_year)

Win rate:

1. closed_trades = min(len(buy_history), len(sell_history))
2. win if sell_price_i > buy_price_i
3. win_rate = wins / closed_trades * 100

## 8. Strategy Selection Semantics

Main behavior:

1. If optional [strategy] argument is provided, run only that strategy.
2. If not provided, run all strategies listed in enabled_strategies from runtime config.
3. If enabled_strategies is empty, exit with error.

This enforces alignment with Python-side strategy enable flags and prevents silent fallback to defaults.

## 9. Output Protocol (for Python Parser)

For each strategy, stdout emits key:value lines followed by separator line ---.

Output keys in order:

1. strategy
2. final_value
3. roi
4. profit_loss
5. max_dd
6. sharpe
7. win_rate
8. total_fees
9. total_trades
10. runtime_ms
11. ---

Example:

```text
strategy:rsi
final_value:10234567.89
roi:2.34568
profit_loss:234567.89
max_dd:4.12
sharpe:1.03
win_rate:48.0
total_fees:1234.5
total_trades:25
runtime_ms:0.87
---
```

Python parser assumptions:

1. Colon separates key/value at first occurrence.
2. Numeric values are parsed as float when possible.
3. Strategy blocks are delimited by ---.

## 10. Error Handling and Exit Codes

Program returns non-zero on hard failures:

1. Missing required arguments.
2. Runtime config file cannot be opened.
3. Runtime config parse conversion error.
4. enabled_strategies empty.
5. Price list empty or CSV unreadable.

Soft behavior:

1. Malformed CSV data lines are skipped.
2. Unknown config keys are ignored.

## 11. Performance Characteristics

Complexity per strategy:

1. Time: O(N * W) in current implementation for window-based signals, where N is tick count and W is lookback size.
2. Space: O(N) for total_history plus O(T) for trade histories.

Why fast in practice:

1. Native compiled loops.
2. Low allocation pressure in hot path.
3. No DataFrame overhead.
4. Simple contiguous vector usage.

## 12. Known Implementation Notes

1. A Trade struct exists but is currently unused.
2. CSV parser is intentionally minimal and expects stable input format.
3. Unknown strategy names result in hold-only behavior in run_backtest.
4. Signal and metric implementations are intentionally mirrored to Python semantics.

## 13. Verification Checklist

Use this checklist when validating changes:

1. Build succeeds with C++17.
2. Binary runs with generated runtime_config.txt.
3. Empty enabled_strategies triggers explicit error.
4. Per-strategy output contains all expected keys and separators.
5. Python parser can read C++ output without modification.
6. Runtime benchmark prints plausible x-speedup and relative speedup percentage versus Python.

## 14. Extension Guide

To add a new strategy:

1. Add parameters to RuntimeConfig.
2. Parse new keys in load_runtime_config.
3. Implement signal function.
4. Add dispatch branch in run_backtest.
5. Add strategy name to Python-to-C++ mapping in main.py.
6. Ensure enabled_strategies includes the new key when enabled.

To add a new metric:

1. Add field to BacktestResult.
2. Compute value in run_backtest.
3. Emit key:value output line in main loop.
4. Update Python parser expectations if needed.

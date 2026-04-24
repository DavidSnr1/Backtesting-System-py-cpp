# Backtesting-System-py-cpp

Python-first trading strategy backtester with a matching C++ engine for performance comparison.

## What This Project Does

- Downloads market data from Yahoo Finance.
- Runs multiple trading strategies against the same price series.
- Reports core metrics (P&L, ROI, Max Drawdown, Sharpe, Win Rate, Fees, Trade count).
- Saves a chart image and prints a tabular performance summary.
- Runs the same logic in Python and C++ to compare runtime.

## Project Structure

```text
.
|- main.py                 # Main entry point
|- backtest.py             # Python backtest engine
|- portfolio.py            # Portfolio accounting and metrics
|- strategy.py             # Strategy implementations
|- load_data.py            # Yahoo data download and CSV export
|- config.py               # Backtest and strategy configuration
|- data/
|  |- BTC-USD_live.csv     # Example generated data file
|  |- sample_data.csv      # Sample input file
|  |- cpp/
|     |- backtest.cpp      # C++ backtest engine
|     |- MakeFile          # C++ build file
|- requirements.txt
```

## Requirements

### Python

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

### C++

- A C++17-capable compiler (g++ or clang++)
- The C++ engine uses structured bindings, so C++17 is required.

Windows (MSYS2 example):

```bash
winget install MSYS2.MSYS2
# In MSYS2 terminal:
pacman -S mingw-w64-x86_64-gcc
```

macOS:

```bash
xcode-select --install
```

Linux:

```bash
sudo apt install g++
```

## Quick Start

Run the full Python workflow (download data, run backtests, show metrics, save chart, compare with C++ if binary exists):

```bash
python main.py
```

## Build and Run C++ Engine

From the repository root:

Windows:

```bash
g++ -O2 -std=c++17 -o data/cpp/backtest.exe data/cpp/backtest.cpp
data/cpp/backtest.exe data/BTC-USD_live.csv all
```

macOS/Linux:

```bash
g++ -O2 -std=c++17 -o data/cpp/backtest data/cpp/backtest.cpp
./data/cpp/backtest data/BTC-USD_live.csv all
```

Or use Make from the C++ folder:

```bash
cd data/cpp
make
```

## Configuration

Edit values in `config.py`:

- Data source: `ticker`, `period`, `interval`
- Initial capital and transaction cost
- Strategy enable/disable switches
- Strategy parameters (windows, thresholds, RSI bounds, Bollinger settings)
- Annualization settings for metrics

## Output

- Console summary table with per-strategy metrics
- Saved chart image: `backtest_ergebnis.png`
- Optional Python vs C++ runtime comparison in console

## Runtime Benchmark

| Engine  | Runtime |
|---------|---------|
| Python  | ~580ms  |
| C++     | ~2ms    |
| Speedup | ~284x   |

*Measured on 8,760 ticks (BTC-USD, 1h, 1 year)*

## Performance Metrics

### P&L (Profit and Loss)

```text
P&L = End Capital - Start Capital
```

### ROI (Return on Investment)

```text
ROI = (P&L / Start Capital) * 100
```

### Max Drawdown

```text
Max DD = max((peak - trough) / peak) * 100
```

### Sharpe Ratio

```text
Sharpe = (mean return / std return) * sqrt(periods per year)
```

### Win Rate

```text
Win Rate = (profitable trades / completed trades) * 100
```

## Implemented Strategies

- Buy and Hold
- Moving Average
- RSI
- Dual Moving Average
- Bollinger Bands

All strategy toggles and parameters are managed in `config.py`.

## Troubleshooting

- `cc1plus.exe: fatal error: cpp/backtest.cpp: No such file or directory`
Use the correct path from repo root:

```bash
g++ -O2 -std=c++17 -o data/cpp/backtest.exe data/cpp/backtest.cpp
```

- `structured bindings requires compiler flag '/std:c++17'`
Compile with C++17 enabled (`-std=c++17` for g++, `/std:c++17` for MSVC)


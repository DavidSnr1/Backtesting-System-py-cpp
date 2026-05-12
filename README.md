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
|     |- Makefile          # C++ build file
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

If `g++` is not found in PowerShell/Command Prompt after installation, either:

1. Build from the **MSYS2 MinGW x64** shell, or
2. Add `C:\msys64\mingw64\bin` to your Windows PATH.

Temporary (current PowerShell session only):

```powershell
$env:Path = "C:\msys64\mingw64\bin;$env:Path"
```

Verify compiler availability before building:

```bash
g++ --version
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
python main.py  # generates data/cpp/runtime_config.txt and runs C++ automatically
```

macOS/Linux:

```bash
g++ -O2 -std=c++17 -o data/cpp/backtest data/cpp/backtest.cpp
python main.py  # generates data/cpp/runtime_config.txt and runs C++ automatically
```

Manual C++ run with generated config file:

```bash
data/cpp/backtest.exe data/BTC-USD_live.csv data/cpp/runtime_config.txt  # Windows
./data/cpp/backtest data/BTC-USD_live.csv data/cpp/runtime_config.txt    # macOS/Linux
```

Or use Make from the C++ folder:

```bash
cd data/cpp
make
```

Note: Runtime file paths are resolved from the repository root (via each module's file location), so running from a different current working directory still reads/writes `data/`, finds `data/cpp/backtest(.exe)`, and saves outputs in the project folder.

## Configuration

Edit values in `config.py`:

- Data source: `ticker`, `period`, `interval`
- Initial capital and transaction cost
- Strategy enable/disable switches
- Strategy parameters (windows, thresholds, RSI bounds, Bollinger settings)
- Annualization settings for metrics

## Output

- Console summary table with per-strategy metrics
- Saved chart image: `backtest_ergebnis.png` in the repository root
- Optional Python vs C++ runtime comparison in console

## Runtime Benchmark

| Engine  | Runtime |
| ------- | ------- |
| Python  | ~580ms  |
| C++     | ~2ms    |
| Speedup | ~284x   |

_Measured on 8,760 ticks (BTC-USD, 1h, 1 year)_

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

## Pipeline Handout

### General Workflow (main method)

1. Before execution, set your parameters in `config.py` and compile `data/cpp/backtest.cpp` to create the C++ binary.
2. `get_yahoo_data(...)` from `load_data.py` runs with the configured data settings and creates the runtime CSV in `data/`.
3. `main.py` initializes only the strategies that are enabled in `CONFIG["strategies"]`.
4. A `backtest` object (`backtest_runner`) is created with CSV path, strategy list, initial capital, and `fraction_position`.
5. Python runtime timer starts.
6. `load_data()` reads the CSV and stores prices in the backtest object.
7. `run_backtest()` simulates trades using strategy signals (`buy/sell/hold`) and updates portfolio state.
8. `show_results()` prints Python results and saves the chart.
9. Python timer stops.
10. `run_cpp_backtest(...)` is called: it writes runtime settings to `data/cpp/runtime_config.txt`, starts the C++ executable via subprocess, and captures C++ output.
11. `print_cpp_comparison(...)` compares Python and C++ runtime.

### What each part does in more detail

#### The Config file (`config.py`)

`CONFIG` is a nested dictionary of settings (data source, costs, backtest settings, strategy switches/parameters, and metric assumptions). The nested structure allows direct access to specific values, for example strategy parameters and enable flags.

Example:

```python
CONFIG = {
	"data": {
		"ticker": "BTC-USD",
		"period": "1mo",
		"interval": "15m"
	},
	"transaction_cost": 0.001,
	"backtest": {
		"initial_capital": 10000000,
		"fraction_position": 0.1
	},
	"strategies": {
		"buy_and_hold": {"enabled": True},
		"moving_average": {"enabled": True, "window_size": 20}
	}
}
```

#### The main file (`main.py`)

`main.py` orchestrates the full pipeline and contains the Python-to-C++ handoff.

#### `write_cpp_runtime_config(config_path)`

This method:

1. Maps Python strategy names to C++ strategy IDs.
2. Collects only enabled strategies.
3. Writes all required numeric settings and `enabled_strategies` to `runtime_config.txt`.

#### `run_cpp_backtest(csv_path)`

This method:

1. Selects the binary name by OS (`backtest.exe` on Windows, `backtest` otherwise).
2. Verifies that the binary exists and prints compile guidance if missing.
3. Writes runtime config via `write_cpp_runtime_config(...)`.
4. Executes C++ as subprocess with:
   1. binary path
   2. absolute CSV path
   3. runtime config path
5. Checks subprocess return code.
6. Parses C++ stdout (`key:value` blocks separated by `---`) into structured Python dictionaries.

Key code path:

```python
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
```

Subprocess call (using runtime config, no extra strategy argument needed):

```python
cpp_args = [
	binary,
	os.path.abspath(csv_path),
	runtime_config_path,
]

result = subprocess.run(
	cpp_args,
	capture_output=True,
	text=True
)
```

Parsing C++ output:

```python
if result.returncode != 0:
	print(f"\nC++ error: {result.stderr}")
	return None

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
```

Note: The Python call no longer passes `all`. C++ uses `enabled_strategies` from `runtime_config.txt` by default. This keeps Python and C++ strategy selection aligned.

#### `print_cpp_comparison(python_ms, cpp_results)`

This method sums `runtime_ms` values reported by C++ and prints:

1. total Python runtime
2. total C++ runtime
3. average runtime per strategy on both sides
4. speedup factor (x-times)
5. relative speedup percentage

Code example:

```python
total_cpp_ms = sum(r.get("runtime_ms", 0.0) for r in cpp_results)
strategy_count = len(cpp_results)
avg_python_ms = (python_ms / strategy_count) if strategy_count > 0 else python_ms
avg_cpp_ms = (total_cpp_ms / strategy_count) if strategy_count > 0 else total_cpp_ms
speedup = (python_ms / total_cpp_ms) if total_cpp_ms > 0 else float("inf")
relative_speedup_pct = (
	((python_ms - total_cpp_ms) / python_ms) * 100.0
	if python_ms > 0
	else 0.0
)

print("\n" + "="*60)
print("PYTHON vs C++ PERFORMANCE")
print("="*60)
print(f"Python:  {python_ms:.1f}ms")
print(f"C++:     {total_cpp_ms:.1f}ms")
print(f"Avg/strategy (Python): {avg_python_ms:.1f}ms")
print(f"Avg/strategy (C++):    {avg_cpp_ms:.1f}ms")
print(f"Relative speedup: {relative_speedup_pct:.1f}%")
```

So the final output shows both strategy metrics (business result) and performance difference (engineering result).

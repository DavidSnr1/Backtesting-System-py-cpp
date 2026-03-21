import pandas as pd
import numpy as np
from pathlib import Path
from backtest import backtest
from strategy import mov_avg_strat

def gen_sample_data():
    data = pd.DataFrame({
        'date': pd.date_range('2020-01-01', periods=100),
        'price': [100 + np.sin(i/10)*10 + np.random.randn()*2 for i in range(100)]
    })
    data.to_csv('MVP/data/sample_data.csv', index=False)


def main():
    print("\n" + "="*60)
    print("BACKTESTER STARTER")
    print("="*60)
    
    # Generate sample data if it doesn't exist
    gen_sample_data()
    
    # Initialize backtest
    backtest_runner = backtest(
        charts_file='MVP/data/sample_data.csv',
        strategy=mov_avg_strat(window_size=10),
        initial_capital = 10000
    )
    
    backtest_runner.load_data()
    backtest_runner.run_backtest(verbose=True)
    backtest_runner.show_results()

if __name__ == '__main__':
    main()
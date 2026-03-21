import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from portfolio import portfolio

class backtest:
    # This class is responsible for running the backtest. It takes the charts file, the strategy, and the initial capital as input. It loads the data, runs the backtest by iterating through each day and executing trades based on the strategy's signals, and finally shows the results of the backtest.
    def __init__(self, charts_file, strategy, initial_capital):
        self.charts_file = charts_file
        self.strategy = strategy
        self.initial_capital = initial_capital

        self.charts = None
        self.portfolio = None
        self.total_history = []
        self.signal_history = []

    # The load_data method reads the charts data from a CSV file and stores it in the charts attribute. It uses pandas to read the CSV file and extracts the 'charts' column as a numpy array.
    def load_data(self):
        df = pd.read_csv(self.charts_file)
        price_column = 'price' if 'price' in df.columns else 'charts'
        self.charts = df[price_column].values
        return self.charts
    
    # The run_backtest method runs the backtest by iterating through each day in the charts data. For each day, it generates a signal using the strategy's signal method, executes trades based on the signal, and records the total value of the portfolio. It also prints out the progress of the backtest every 20 days if verbose is set to True.
    def run_backtest(self, verbose=True):
        self.portfolio = portfolio(self.initial_capital)

        print(f"Starting backtest with strategy: {self.strategy}")
        print(f"Initial capital: {self.initial_capital}")
        print(f"Data points: {len(self.charts)}")
        print("="*60)

        for day in range(len(self.charts)):
            chart_today = self.charts[day]

            # Signal generation
            signal = self.strategy.signal(self.charts, day)
            self.signal_history.append(signal)

            # Execute trades based on signal
            if signal == 'buy' and self.portfolio.cash > 0:
                size = int(self.portfolio.cash / chart_today)
                if size > 0:
                    self.portfolio.buy(size, chart_today)
            elif signal == 'sell' and self.portfolio.shares > 0:
                self.portfolio.sell(self.portfolio.shares, chart_today)
            
            # Record total value of the portfolio
            total = self.portfolio.total(chart_today)
            self.total_history.append(total)  
            if verbose and day % 20 == 0:
                print(f"Tag {day:3d} | Kurs: ${chart_today:7.2f} | "
                      f"Wert: ${total:10.2f} | "
                      f"Aktien: {self.portfolio.shares:4d} | "
                      f"Signal: {signal}")
        
        print("="*60)

    def show_results(self):
        final_value = self.total_history[-1]
        final_chart = self.charts[-1]
        profit_loss = self.portfolio.profit_loss(final_chart)
        roi = self.portfolio.roi(final_chart)

        print("\n" + "="*60)
        print("FINAL STATISTIC")
        print("="*60)
        print(f"Start Capital:      ${self.initial_capital:>12,.2f}")
        print(f"End Capital:        ${final_value:>12,.2f}")
        print(f"Profit/Loss:        ${profit_loss:>12,.2f}")
        print(f"ROI:                {roi:>12.2f}%")
        print(f"\nFinal Shares:       {self.portfolio.shares:>12}")
        print(f"Final Cash:         ${self.portfolio.cash:>12,.2f}")
        print(f"Final Price:        ${final_chart:>12,.2f}")
        print("="*60)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
        # Graph 1: Chart
        ax1.plot(self.charts, label='Stock Price', color='blue', linewidth=2)
        ax1.set_title(f'{self.strategy.name} - Backtest Result')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Graph 2: Portfolio Value
        ax2.plot(self.total_history, label='Your Portfolio', color='green', linewidth=2)
        ax2.axhline(y=self.initial_capital, color='red', linestyle='--', 
                    label=f'Start Capital (${self.initial_capital:,.0f})')
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Value ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('backtest_ergebnis.png', dpi=150)

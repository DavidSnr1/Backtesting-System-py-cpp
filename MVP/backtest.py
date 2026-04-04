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
        self.charts = df['price'].values
        return self.charts
    
    # The run_backtest method runs the backtest by iterating through each day in the charts data. For each day, it generates a signal using the strategy's signal method, executes trades based on the signal, and records the total value of the portfolio. It also prints out the progress of the backtest every 20 days if verbose is set to True.
    def run_backtest(self, verbose=True):
        self.portfolio = portfolio(self.initial_capital)

        print(f"Starting backtest with strategy: {self.strategy}")
        print(f"Initial capital: {self.initial_capital}")
        print(f"Data points: {len(self.charts)}")
        print("="*60)

        for tick in range(len(self.charts)):
            chart_today = self.charts[tick]

            # Signal generation
            signal = self.strategy.signal(self.charts, tick)
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
            if verbose and tick % 20 == 0:
                print(f"Tick {tick:3d} | Price: ${chart_today:7.2f} | "
                      f"Total: ${total:10.2f} | "
                      f"Shares: {self.portfolio.shares:4d} | "
                      f"Signal: {signal}")
        
        print("="*60)

    # The calc_bandh_roi_benchmark method calculates the return on investment (ROI) of a buy-and-hold strategy as a benchmark for comparison. It calculates how many shares could be bought with the initial capital at the first price, and then calculates the value of those shares at the last price. It returns the ROI as a percentage.
    def calc_bandh_roi_benchmark(self):
        bh_shares_bought = int(self.initial_capital / self.charts[0])
        bh_rest_cash = self.initial_capital - bh_shares_bought * self.charts[0]
        return (bh_rest_cash + bh_shares_bought * self.charts[-1] - self.initial_capital) / self.initial_capital * 100
    
    # The calc_bandh_history method calculates the total value of a buy-and-hold strategy over time. It calculates how many shares could be bought with the initial capital at the first price, and then calculates the value of those shares at each price in the charts data. It returns a list of the total value of the buy-and-hold strategy at each time point.
    def calc_bandh_history(self):
        bh_shares = int(self.initial_capital / self.charts[0])
        bh_cash = self.initial_capital - bh_shares * self.charts[0]
        return [bh_cash + bh_shares * price for price in self.charts]

    # The show_results method calculates and displays the final results of the backtest, including the final capital, profit/loss, ROI, total trades, win rate, max drawdown, Sharpe Ratio, and a comparison to a buy-and-hold benchmark. It also generates two graphs: one showing the stock price over time and another showing the portfolio value over time compared to the buy-and-hold strategy. The results are printed in a formatted manner, and the graphs are saved as an image file.
    def show_results(self):
        final_value = self.total_history[-1]
        final_chart = self.charts[-1]
        profit_loss = self.portfolio.profit_loss(final_chart)
        roi = self.portfolio.roi(final_chart)
        max_dd = self.portfolio.max_dd(self.total_history)
        sharpe = self.portfolio.sharpe_ratio(self.total_history)
        win_rate, total_trades = self.portfolio.calculate_win_rate()
        bandh_roi = self.calc_bandh_roi_benchmark()


        print("\n" + "="*60)
        print("FINAL STATISTIC")
        print("="*60)
        print(f"Start Capital:      ${self.initial_capital:>12,.2f}")
        print(f"End Capital:        ${final_value:>12,.2f}")
        print(f"Profit/Loss:        ${profit_loss:>12,.2f}")
        print(f"\nROI:                {roi:>12.2f}%")
        print(f"Total Trades:        {total_trades:>12}")
        print(f"Win Rate:           {win_rate:>12,.2f}%")
        print(f"Max Drawdown:       {max_dd:>12.2f}%")
        print(f"Sharpe Ratio:        {sharpe:>12.2f}")
        print(f"B&H Benchmark:      {bandh_roi:>12,.2f}%")
        print(f"\nFinal Shares:        {self.portfolio.shares:>12}")
        print(f"Final Cash:         ${self.portfolio.cash:>12,.2f}")
        print(f"Final Price:        ${final_chart:>12,.2f}")
        print("="*60)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
        # Graph 1: Chart
        ax1.plot(self.charts, label='Stock Price', color='blue', linewidth=2)
        ax1.set_title('Backtest Result')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Graph 2: Portfolio Value
        bnh_history = self.calc_bandh_history()
        bnh_roi = self.calc_bandh_roi_benchmark()

        ax2.plot(self.total_history, label=f'Strategy (ROI: {roi:.2f}%)', color='green', linewidth=1)
        ax2.plot(bnh_history, label=f'Buy & Hold (ROI: {bandh_roi:.2f}%)', color='orange', linewidth=1)
        ax2.axhline(y=self.initial_capital, color='red', linestyle='--',
                    label=f'Start Capital (${self.initial_capital:,.0f})')
        ax2.set_xlabel('Ticks')
        ax2.set_ylabel('Value ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('backtest_ergebnis.png', dpi=150)

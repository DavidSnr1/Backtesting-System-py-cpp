import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from portfolio import portfolio
from tabulate import tabulate


class backtest:
    def __init__(self, charts_file, strategies, initial_capital):
        self.charts_file = charts_file
        self.strategies = strategies
        self.initial_capital = initial_capital
        self.charts = None
        self.results = {}

    def load_data(self):
        df = pd.read_csv(self.charts_file)
        self.charts = df['price'].values
        return self.charts

    def run_backtest(self):
        print(f"\nData points: {len(self.charts)}")
        print(f"Initial capital: ${self.initial_capital:,.2f}")
        print(f"Running {len(self.strategies)} strategies...\n")

        for strategy in self.strategies:
            print(f"Backtesting: {strategy.name}")

            p = portfolio(self.initial_capital)
            total_history = []
            signal_history = []

            for tick in range(len(self.charts)):
                chart_today = self.charts[tick]

                signal = strategy.signal(self.charts, tick)
                signal_history.append(signal)

                if signal == 'buy' and p.cash > 0:
                    size = int(p.cash / chart_today)
                    if size > 0:
                        p.buy(size, chart_today)
                elif signal == 'sell' and p.shares > 0:
                    p.sell(p.shares, chart_today)

                total_history.append(p.total(chart_today))

            win_rate, total_trades = p.calculate_win_rate()

            self.results[strategy.name] = {
                "portfolio":      p,
                "total_history":  total_history,
                "signal_history": signal_history,
                "roi":            p.roi(self.charts[-1]),
                "profit_loss":    p.profit_loss(self.charts[-1]),
                "max_dd":         p.max_dd(total_history),
                "sharpe":         p.sharpe_ratio(total_history),
                "win_rate":       win_rate,
                "total_trades":   total_trades,
                "final_value":    total_history[-1]
            }

    def calc_bandh_roi_benchmark(self):
        bh_shares = int(self.initial_capital / self.charts[0])
        bh_cash = self.initial_capital - bh_shares * self.charts[0]
        return (bh_cash + bh_shares * self.charts[-1] - self.initial_capital) / self.initial_capital * 100

    def calc_bandh_history(self):
        bh_shares = int(self.initial_capital / self.charts[0])
        bh_cash = self.initial_capital - bh_shares * self.charts[0]
        return [bh_cash + bh_shares * price for price in self.charts]

    def show_results(self):
        bandh_roi = self.calc_bandh_roi_benchmark()
        bandh_history = self.calc_bandh_history()
        bandh_max_dd = portfolio(self.initial_capital).max_dd(bandh_history)

        # Summary Tabelle
        headers = ["Strategy", "End Capital", "P&L", "ROI", "Max DD", "Sharpe", "Win Rate", "Trades"]
        rows = []

        for name, r in self.results.items():
            rows.append([
                name,
                f"${r['final_value']:,.2f}",
                f"${r['profit_loss']:,.2f}",
                f"{r['roi']:+.2f}%",
                f"{r['max_dd']:.2f}%",
                f"{r['sharpe']:.2f}",
                f"{r['win_rate']:.2f}%",
                r['total_trades']
            ])

        print("\n" + "="*90)
        print("BACKTEST SUMMARY")
        print("="*90)
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
        print("="*90)

        # Chart
        colors = ['green', 'royalblue', 'purple', 'crimson', 'darkorange']
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9))

        # Graph 1: Kursverlauf
        ax1.plot(self.charts, label='Price', color='blue', linewidth=2)
        ax1.set_title(f'Backtest Result')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Graph 2: Portfolio Value pro Strategie
        for i, (name, r) in enumerate(self.results.items()):
            color = colors[i % len(colors)]
            ax2.plot(
                r['total_history'],
                label=f"{name} (ROI: {r['roi']:+.2f}%)",
                color=color,
                linewidth=1
            )

        ax2.plot(bandh_history, label=f'Buy & Hold (ROI: {bandh_roi:+.2f}%)', color='orange', linewidth=1, linestyle='--')
        ax2.axhline(y=self.initial_capital, color='red', linestyle='--', label=f'Start Capital (${self.initial_capital:,.0f})')
        ax2.set_xlabel('Ticks')
        ax2.set_ylabel('Value ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('backtest_ergebnis.png', dpi=150)
        print("\nChart saved as backtest_ergebnis.png")

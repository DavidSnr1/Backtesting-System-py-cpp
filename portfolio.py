import pandas as pd
import numpy as np
from config import CONFIG


class portfolio:

# This class is used to keep track of the portfolio's cash and shares, as well as the buy and sell history.

    # The __init__ method initializes the portfolio with the initial capital, sets the cash and shares to 0, and creates empty lists for the buy and sell history.
    def __init__(self, initial_capital):
        self.cash = initial_capital
        self.shares = 0
        self.initial_capital = initial_capital
        self.fees = 0

        self.buy_history = []
        self.sell_history = []

    # The check_buy method checks if the portfolio has enough cash to buy a certain number of shares at a given price. It calculates the total cost of the purchase and compares it to the available cash.
    def check_buy(self, size, price):
        costs = size * price
        return self.cash >= costs
    
    # The buy method attempts to buy a certain number of shares at a given price. It first checks if the purchase is possible using the check_buy method. If it is, it deducts the cost from the cash, adds the shares to the portfolio, and records the purchase in the buy history. If not, it prints an error message and returns False.
    def buy(self, size, price):
        costs = size * price
        fee = costs * CONFIG["transaction_cost"]
        costs += fee
        if self.check_buy(size,price):
            self.cash -= costs
            self.shares += size
            self.fees += fee
            self.buy_history.append((size, price))
            return True
        else: 
            print("Insufficient funds for this purchase")
            return False
    
    # The check_sell method checks if the portfolio has enough shares to sell a certain number of shares. It compares the number of shares in the portfolio to the size of the sale.
    def check_sell(self, size):
        return self.shares >= size
    
    # The sell method attempts to sell a certain number of shares at a given price. It first checks if the sale is possible using the check_sell method. If it is, it calculates the revenue from the sale, adds it to the cash, deducts the shares from the portfolio, and records the sale in the sell history. If not, it prints an error message and returns False.
    def sell(self, size, price):

        revenue = size * price
        fee = revenue * CONFIG["transaction_cost"]
        revenue -= fee
        if self.check_sell(size):
            self.cash += revenue
            self.shares -= size
            self.fees += fee
            self.sell_history.append((size, price))
            return True
        else:
            print("Not enough shares to sell")
            return False
    
    # The total method calculates the total value of the portfolio by adding the cash and the value of the shares at the current price.
    def total(self, current_price):
        return self.cash + self.shares * current_price
    
    # The profit_loss method calculates the profit or loss of the portfolio by subtracting the initial capital from the total value of the portfolio at the current price.
    def profit_loss(self, current_price):
        return self.total(current_price) - self.initial_capital
    
    # The roi method calculates the return on investment (ROI) of the portfolio by dividing the profit or loss by the initial capital and multiplying by 100 to get a percentage.
    def roi(self, current_price):
        return (self.profit_loss(current_price) / self.initial_capital) * 100

    # The max_dd method calculates the maximum drowdown by identifying the lowest value after every peak.
    def max_dd(self, total_history):
        peak = total_history[0]
        max_drawdown = 0
    
        for total in total_history:
            if total > peak:
                peak = total

            drawdown = (peak - total) / peak 

            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown * 100
    
    # The sharpe_ratio method calculates the Sharpe Ratio of the portfolio by first calculating the returns from the total history, then calculating the mean and standard deviation of the returns.
    #  It annualizes the Sharpe Ratio based on the number of trading periods per year defined in the CONFIG. If the standard deviation of returns is zero, it returns a Sharpe Ratio of 0 to avoid division by zero.
    def sharpe_ratio(self, total_history):
        returns = pd.Series(total_history).pct_change().dropna()
    
        if returns.std() == 0:
            return 0
    
        # Annualization from config
        periods_per_year = (
            CONFIG["metrics"]["trading_days_per_year"] *
            CONFIG["metrics"]["hours_per_day"] /
            CONFIG["metrics"]["interval_hours"]
        )

        annualization = np.sqrt(periods_per_year)
    
        sharpe = (returns.mean() / returns.std()) * annualization
        return sharpe
    # The calculate_win_rate method calculates the win rate of the trades by comparing the buy and sell prices. 
    # It zips the buy and sell history together, checks if each sell price is greater than the corresponding buy price, and calculates the win rate as a percentage.
    # It also returns the total number of trades. If there are no trades, it returns a win rate of 0 and a total trade count of 0.
    def calculate_win_rate(self):
        trades = zip(self.buy_history, self.sell_history)
        
        results = [sell[1] > buy[1] for buy, sell in trades]
        
        if not results:
            return 0, 0
        
        win_rate = sum(results) / len(results) * 100
        return win_rate, len(results)
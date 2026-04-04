import pandas as pd
import numpy as np

class portfolio:

# This class is used to keep track of the portfolio's cash and shares, as well as the buy and sell history.

    # The __init__ method initializes the portfolio with the initial capital, sets the cash and shares to 0, and creates empty lists for the buy and sell history.
    def __init__(self, initial_capital):
        self.cash = initial_capital
        self.shares = 0
        self.initial_capital = initial_capital

        self.buy_history = []
        self.sell_history = []

    # The check_buy method checks if the portfolio has enough cash to buy a certain number of shares at a given price. It calculates the total cost of the purchase and compares it to the available cash.
    def check_buy(self, size, price):
        kosten = size * price
        return self.cash >= kosten
    
    # The buy method attempts to buy a certain number of shares at a given price. It first checks if the purchase is possible using the check_buy method. If it is, it deducts the cost from the cash, adds the shares to the portfolio, and records the purchase in the buy history. If not, it prints an error message and returns False.
    def buy(self, size, price):
        kosten = size * price
        if self.check_buy(size,price):
            self.cash -= kosten
            self.shares += size
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
        if self.check_sell(size):
            self.cash += revenue
            self.shares -= size
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
    
    def sharpe_ratio(self, total_history):
        returns = pd.Series(total_history).pct_change().dropna()
    
        if returns.std() == 0:
            return 0
    
        annualization = np.sqrt(252 * 390)
    
        sharpe = (returns.mean() / returns.std()) * annualization
        return sharpe
    
    def calculate_win_rate(self):
        trades = zip(self.buy_history, self.sell_history)
        
        results = [sell[1] > buy[1] for buy, sell in trades]
        
        if not results:
            return 0, 0
        
        win_rate = sum(results) / len(results) * 100
        return win_rate, len(results)
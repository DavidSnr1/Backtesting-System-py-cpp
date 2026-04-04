import numpy as np

class mov_avg_strat:
    # Initialising the Strategy
    def __init__(self, window_size, threshold_buy, threshold_sell):
        self.window = window_size
        self.name = f"Moving Average Strategy (window size: {window_size})"
        self.threshold_buy = threshold_buy
        self.threshold_sell = threshold_sell

    
    def signal(self, charts, current_index):
        # Check if we have enough data to calculate the moving average
        if current_index < self.window:
            return 'hold'
    
        # Calculate the moving average
        avg = np.mean(charts[current_index - self.window:current_index])
        current_price = charts[current_index]

        # Generate buy/sell/hold signal based on the current price and the moving average
        if current_price > avg * self.threshold_buy:
            return 'buy'
        elif current_price < avg * self.threshold_sell:
            return 'sell'
        else:
            return 'hold'
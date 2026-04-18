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
        if current_price > avg * (1 + self.threshold_buy):
            return 'buy'
        elif current_price < avg * (1 - self.threshold_sell):
            return 'sell'
        else:
            return 'hold'
        
class buy_and_hold_strat:
    def __init__(self):
        self.name = "Buy and Hold Strategy"
    
    def signal(self, charts, current_index):
        if current_index == 0:
            return 'buy'
        else:
            return 'hold'
        
class rsi_strat:
    def __init__(self, window_size, oversold, overbought):
        self.window = window_size
        self.name = f"RSI Strategy (window size: {window_size})"
        self.oversold = oversold
        self.overbought = overbought
    
    def signal(self, charts, current_index):
        if current_index < self.window:
            return 'hold'
        
        # Calculate RSI
        deltas = np.diff(charts[current_index - self.window:current_index + 1])
        gains = deltas[deltas > 0].sum()
        losses = -deltas[deltas < 0].sum()
        
        if losses == 0:
            rsi = 100
        else:
            rs = gains / losses
            rsi = 100 - (100 / (1 + rs))
        
        # Generate buy/sell/hold signal based on RSI
        if rsi < self.oversold:
            return 'buy'
        elif rsi > self.overbought:
            return 'sell'
        else:
            return 'hold'
        
class dual_ma_strat:
    def __init__(self, window_short, window_long):
        self.window_short = window_short
        self.window_long = window_long
        self.name = f"Dual Moving Average Strategy (short: {window_short}, long: {window_long})"
    
    def signal(self, charts, current_index):
        if current_index < self.window_long:
            return 'hold'
        
        short_avg = np.mean(charts[current_index - self.window_short:current_index])
        long_avg = np.mean(charts[current_index - self.window_long:current_index])
        
        if short_avg > long_avg:
            return 'buy'
        elif short_avg < long_avg:
            return 'sell'
        else:
            return 'hold'
        
class bollinger_strat:
    def __init__(self, window_size, num_std):
        self.window = window_size
        self.num_std = num_std
        self.name = f"Bollinger Bands Strategy (window size: {window_size}, num std: {num_std})"
    
    def signal(self, charts, current_index):
        if current_index < self.window:
            return 'hold'
        
        avg = np.mean(charts[current_index - self.window:current_index])
        std = np.std(charts[current_index - self.window:current_index])
        
        upper_band = avg + self.num_std * std
        lower_band = avg - self.num_std * std
        current_price = charts[current_index]
        
        if current_price > upper_band:
            return 'sell'
        elif current_price < lower_band:
            return 'buy'
        else:
            return 'hold'
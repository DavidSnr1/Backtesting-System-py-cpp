# Concept:

### Requirements.txt
Here I will store the libs I need for my MVP. They iclude:
- pandas (1.3.5)
- numpy (1.21.6)
- matplotlib (3.5.1)

### Data / sample.csv

To keep it simple i will generate a sample csv in my main with sample minimal made up data

### Portfolio Class

The portfolio class will need several methods I implement in the according file:
- init method
- checkbuy (check if the porfolio has the funds to make a transaction)
- buy (implements the actual transaction)
- check sell (check if the portfolio has the proclaimed shares it wants to sell)
- sell (implements the actual transaction)
- total (calculates the total of the portfolio)
- profit_and_loss (calculates p&l)
- roi (calculates the roi)

### Strategy 

In this file I will implement my strategies via classes. Each class will implement an init method and a signal method that specifies the signals to when to sell and buy

### Backtesting Class

The backtesting class will implement the following methods:
- init method
- load_data method (loads the data from the sample.csv)
- run backtest (initializes the portfolio and calculates different metrics after trading via the given strategy)
- show_result (print and visaulize the results from using this strategy)

### main

In the main I will create the sample dataset, select the strategy and run trough the backtest


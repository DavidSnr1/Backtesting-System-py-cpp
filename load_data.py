import yfinance as yf
import pandas as pd
import os

def get_yahoo_data(ticker="BTC-USD", period="1y", interval="1h"):
    
    # Download Data from Yahoo Finance
    data = yf.download(tickers=ticker, period=period, interval=interval)

    if data.empty:
        raise ValueError(
            f"No data downloaded for {ticker} (period={period}, interval={interval}). "
            "Please check internet connection, ticker symbol, or Yahoo interval limits."
        )
    
    # Making sure the data directory exists
    if not os.path.exists('MVP/data'):
        os.makedirs('MVP/data')
        
    # Extract relevant columns from both MultiIndex and flat-column formats.
    close_series = data['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    df = close_series.reset_index()
    df.columns = ['tick', 'price'] 

    if df.empty:
        raise ValueError(
            f"Downloaded dataset for {ticker} contains no rows after processing."
        )
    
    # Save to CSV
    df.to_csv(f'MVP/data/{ticker}_live.csv', index=False)
    return df

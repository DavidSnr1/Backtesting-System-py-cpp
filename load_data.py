import yfinance as yf
import pandas as pd
import os


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CPP_DIR = os.path.join(DATA_DIR, 'cpp')

def get_yahoo_data(ticker="BTC-USD", period="1y", interval="1h"):
    
    # Download Data from Yahoo Finance
    data = yf.download(tickers=ticker, period=period, interval=interval)

    if data.empty:
        raise ValueError(
            f"No data downloaded for {ticker} (period={period}, interval={interval}). "
            "Please check internet connection, ticker symbol, or Yahoo interval limits."
        )
    
    # Make sure runtime output folders exist under the project root.
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CPP_DIR, exist_ok=True)
        
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
    output_csv = os.path.join(DATA_DIR, f'{ticker}_live.csv')
    df.to_csv(output_csv, index=False)
    return df

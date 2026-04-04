import yfinance as yf
import pandas as pd
import os

def get_yahoo_data(ticker="BTC-USD", period="1y", interval="1h"):
    
    # Download Data from Yahoo Finance
    data = yf.download(tickers=ticker, period=period, interval=interval)
    
    # Making sure the data directory exists
    if not os.path.exists('MVP/data'):
        os.makedirs('MVP/data')
        
    # Extracting relevant columns and saving to CSV
    df = data[['Close']].droplevel(1, axis=1).reset_index()
    df.columns = ['tick', 'price'] 
    
    # Save to CSV
    df.to_csv(f'MVP/data/{ticker}_live.csv', index=False)
    return df

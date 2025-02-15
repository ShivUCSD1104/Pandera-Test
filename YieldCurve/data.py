import yfinance as yf
import pandas as pd
import numpy as np

def get_yield_data(start_date, end_date):
    tickers = {
        "^IRX": "3-Month",
        "^FVX": "5-Year",
        "^TNX": "10-Year",
        "^TYX": "30-Year",
    }

    data = {}
    for ticker, label in tickers.items():
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if not df.empty:
                # Ensure we get a Series (1D) even if yfinance returns DataFrame
                close_data = df["Close"].squeeze()  # Fix here
                if isinstance(close_data, pd.Series):
                    data[label] = close_data
                else:
                    print(f"Unexpected data format for {label} ({ticker})")
            else:
                print(f"No data for {label} ({ticker})")
        except Exception as e:
            print(f"Error fetching {label}: {e}")

    yield_data = pd.DataFrame(columns=['Date', 'Maturity', 'Yield'])
    for label, series in data.items():
        maturity = {
            "3-Month": 3,
            "5-Year": 60,
            "10-Year": 120,
            "30-Year": 360
        }[label]
        
        # Ensure all columns are 1D arrays
        temp_df = pd.DataFrame({
            'Date': series.index,         # 1D DatetimeIndex
            'Maturity': [maturity] * len(series),  # Explicit 1D list
            'Yield': series.values        # 1D array
        })
        yield_data = pd.concat([yield_data, temp_df])

    # Handle empty data edge case
    if yield_data.empty:
        return np.array([]), np.array([]), np.array([])  # Return empty arrays

    # Pivot and clean
    pivot_yield = yield_data.pivot(index='Date', columns='Maturity', values='Yield')
    pivot_yield = pivot_yield[[3, 60, 120, 360]]  # Ensure column order

    return (
        pivot_yield.columns.to_numpy(),  # Maturities (x)
        pivot_yield.index.to_numpy(),    # Dates (y)
        pivot_yield.to_numpy()           # Yields (z)
    )
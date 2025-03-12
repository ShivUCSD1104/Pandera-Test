import os
import pandas as pd
from datetime import datetime, date
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models import OptionChain

# Setup DB connection using DATABASE_URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def get_risk_free_rate():
    """
    For simplicity, we use a fixed risk-free rate.
    In production you might also cache a daily-fetched T-Bill yield.
    """
    return 0.042  # e.g., 4.2%


def get_option_data(ticker_str, contract_type="calls", start_date=None, end_date=None):
    """
    Retrieve cached option chain data from the Postgres DB.
    This function queries the OptionChain table for the latest fetched data
    for a given ticker and contract type and then groups by expiration date.
    
    Returns:
      - A list of tuples: [(DataFrame, T), ...] where DataFrame is built from the JSON stored.
      - Underlying spot price S (assumed to be present in the option data as "underlyingPrice").
    """
    # Get the most recent fetch timestamp for this ticker and contract_type
    latest_fetch = session.query(func.max(OptionChain.fetched_at)).filter(
        OptionChain.ticker == ticker_str,
        OptionChain.contract_type == contract_type
    ).scalar()
    
    if not latest_fetch:
        raise ValueError(f"No cached data in database for ticker {ticker_str} and contract type {contract_type}.")

    # Query all entries for that timestamp
    entries = session.query(OptionChain).filter(
        OptionChain.ticker == ticker_str,
        OptionChain.contract_type == contract_type,
        OptionChain.fetched_at == latest_fetch
    ).all()

    # Optionally filter by expiration date if provided
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        entries = [e for e in entries if start_dt <= e.expiration_date <= end_dt]
    
    # Sort entries by expiration date and select up to 12 groups
    entries.sort(key=lambda e: e.expiration_date)
    selected_entries = entries[:12]

    data_list = []
    S = None  # underlying spot price

    today = date.today()
    for entry in selected_entries:
        # Convert stored JSON data into a DataFrame
        df = pd.DataFrame(entry.data)
        # Assume each option record has an "underlyingPrice" field.
        if S is None and "underlyingPrice" in df.columns and not df.empty:
            S = df["underlyingPrice"].iloc[0]
        # Compute time-to-expiry T (in years)
        T = (entry.expiration_date - today).days / 365.0
        if T > 0:
            data_list.append((df, T))

    if S is None:
        raise ValueError("Underlying price not found in cached data.")

    return data_list, S

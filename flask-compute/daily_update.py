import os
import requests
import json
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from IVSurface.models import Base, OptionChain

# Ensure required environment variables are set
DATABASE_URL = os.environ.get("DATABASE_URL")
FMP_API_KEY = os.environ.get("FMP_API_KEY")
if not DATABASE_URL or not FMP_API_KEY:
    raise ValueError("DATABASE_URL and FMP_API_KEY must be set as environment variables.")


# Create DB engine and session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

TICKERS = ["AAPL", "GOOGL", "MSFT"]

def fetch_and_store_options(ticker):
    """
    Fetch option chain data from Financial Modeling Prep and store it in the DB.
    """
    url = f"https://financialmodelingprep.com/api/v3/options/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")
        return
    data = response.json()
    if not data:
        print(f"No data returned for {ticker}.")
        return

    # Group the option contracts by contract type and expiration date
    options_grouped = {}
    for contract in data:
        # Use "call" and "put" fields – normalize to plural form
        contract_type = contract.get("type", "").lower()
        if contract_type == "call":
            ct = "calls"
        elif contract_type == "put":
            ct = "puts"
        else:
            continue
        
        expiration = contract.get("expirationDate")
        if not expiration:
            continue
        exp_date = date.fromisoformat(expiration)
        key = (ct, exp_date)
        options_grouped.setdefault(key, []).append(contract)
    
    # Insert a new record for each (contract_type, expiration_date) group
    for (ct, exp_date), options_data in options_grouped.items():
        option_chain = OptionChain(
            ticker=ticker,
            contract_type=ct,
            expiration_date=exp_date,
            data=options_data
        )
        session.add(option_chain)
    
    session.commit()
    print(f"Stored option data for {ticker}.")


def run_daily_update():
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    for ticker in TICKERS:
        fetch_and_store_options(ticker)


if __name__ == "__main__":
    run_daily_update()

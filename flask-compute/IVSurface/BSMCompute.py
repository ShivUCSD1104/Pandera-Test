import numpy as np
from math import log, sqrt, exp
from scipy.stats import norm
from .datasourcing import get_risk_free_rate, get_option_data

#Black–Scholes Formulas
def black_scholes_call(S, K, T, r, sigma):
    """
    Black-Scholes price of a European Call.
    
    S: Current underlying price
    K: Strike price
    T: Time to maturity (in years)
    r: Risk-free interest rate (annualized, decimal form)
    sigma: Volatility (annualized, decimal form)

    """
    if T <= 0 or sigma <= 0:
        # Extremely rough edge case
        return max(0.0, S - K)
    
    d1 = (log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * sqrt(T))
    d2 = d1 - sigma*sqrt(T)
    
    call_price = S * norm.cdf(d1) - K * exp(-r*T) * norm.cdf(d2)
    return call_price


def black_scholes_put(S, K, T, r, sigma):
    """
    Black-Scholes price of a European Put.
    
    S: Current underlying price
    K: Strike price
    T: Time to maturity (in years)
    r: Risk-free interest rate (annualized, decimal form)
    sigma: Volatility (annualized, decimal form)
    """
    if T <= 0 or sigma <= 0:
        # Extremely rough edge case
        return max(0.0, K - S)
    
    d1 = (log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * sqrt(T))
    d2 = d1 - sigma*sqrt(T)
    
    put_price = K * exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price


#Implied Volatility Calculation using Newton-Raphson method
def implied_vol_call(market_price, S, K, T, r=0.0, tol=0.001, max_iter=100):
    """
    Newton-Raphson to find implied volatility for a European Call.
    market_price: Observed market price (bid/ask mid or last)
    S, K, T, r: Underlying price, strike, time-to-expiry, risk-free rate
    """
    # Intrinsic value for a call is max(0, S - K*exp(-r*T))
    intrinsic_value = max(0.0, S - K*exp(-r*T))
    if market_price < intrinsic_value:
        return np.nan  # Impossible if below intrinsic
    
    sigma = 0.3  # initial guess
    for _ in range(max_iter):
        price_guess = black_scholes_call(S, K, T, r, sigma)
        diff = price_guess - market_price
        
        if abs(diff) < tol:
            return sigma
        
        # Vega: partial derivative wrt sigma
        d1 = (log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * sqrt(T))
        vega = S * norm.pdf(d1) * sqrt(T)
        
        if vega < 1e-8:  # avoid division by near-zero
            break
        
        sigma -= diff / vega
        if sigma < 1e-8:
            sigma = 1e-8
    
    return sigma


def implied_vol_put(market_price, S, K, T, r=0.0, tol=0.01, max_iter=100):
    """
    Newton-Raphson to find implied volatility for a European Put.
    market_price: Observed market price (bid/ask mid or last)
    S, K, T, r: Underlying price, strike, time-to-expiry, risk-free rate
    """
    # Intrinsic value for a put is max(0, K*exp(-r*T) - S)
    intrinsic_value = max(0.0, K*exp(-r*T) - S)
    if market_price < intrinsic_value:
        return np.nan
    
    sigma = 0.3  # initial guess
    for _ in range(max_iter):
        price_guess = black_scholes_put(S, K, T, r, sigma)
        diff = price_guess - market_price
        
        if abs(diff) < tol:
            return sigma
        
        d1 = (log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * sqrt(T))
        vega = S * norm.pdf(d1) * sqrt(T)
        
        if vega < 1e-8:
            break
        
        sigma -= diff / vega
        if sigma < 1e-8:
            sigma = 1e-8
    
    return sigma

def compute_implied_vols(ticker_str, contract_type="calls", start_date=None, end_date=None):
    """
    Main function to:
      1. Get the risk-free rate from T-Bill yield.
      2. Retrieve up to 3 earliest expiration DataFrames (calls or puts).
      3. Compute implied volatility for each contract.
      4. Switch the moneyness formula:
         - For calls: moneyness = S / K
         - For puts:  moneyness = K / S
      5. Filter out any contracts that return NaN IV.
      6. Return arrays for implied vol, moneyness, and time-to-expiry.
    """
    # Step 1: Risk-free rate from T-Bill
    r = get_risk_free_rate()
    
    # Step 2: Get up to 3 option data sets
    data_list, S = get_option_data(ticker_str, contract_type=contract_type, start_date=start_date, end_date=end_date)
    print(data_list, 'haha')
    ivs = []
    mny = []
    ttes = []
    
    # Step 3: Loop over each (DataFrame, time-to-expiry) pair
    for options_df, T in data_list:
        for _, row in options_df.iterrows():
            K = row["strike"]
            
            # Mid-price from bid/ask if possible
            bid = row.get("bid", np.nan)
            ask = row.get("ask", np.nan)
            if not np.isnan(bid) and not np.isnan(ask):
                market_price = 0.5 * (bid + ask)
            else:
                market_price = row.get("lastPrice", np.nan)
            
            if np.isnan(market_price):
                continue  # skip if we have no usable price
            
            # Compute implied vol for call or put
            if contract_type == "calls":
                iv = implied_vol_call(market_price, S, K, T, r=r)
                money = S / K  # Moneyness for calls
            else:
                iv = implied_vol_put(market_price, S, K, T, r=r)
                money = K / S  # Moneyness for puts
            
            # Filter out any NaN implied vol
            if np.isnan(iv):
                continue
            
            ivs.append(iv)
            mny.append(money)
            ttes.append(T)
    
    return ivs, mny, ttes
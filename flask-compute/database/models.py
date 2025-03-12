from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = {'schema': 'finance'}

class OptionContract(Base):
    __tablename__ = 'option_contracts'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, index=True)
    expiration_date = Column(Date, nullable=False, index=True)
    strike = Column(Float, nullable=False)
    contract_type = Column(String, nullable=False)  # 'call' or 'put'
    bid = Column(Float)
    ask = Column(Float)
    last_price = Column(Float)
    volume = Column(Integer)
    open_interest = Column(Integer)
    implied_volatility = Column(Float)
    fetch_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = {'schema': 'finance'}

class YieldData(Base):
    __tablename__ = 'yield_data'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, index=True)
    label = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    maturity_months = Column(Integer, nullable=False)
    yield_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = {'schema': 'finance'}

class RiskFreeRate(Base):
    __tablename__ = 'risk_free_rates'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    rate = Column(Float, nullable=False)  # Decimal form (e.g., 0.045 for 4.5%)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = {'schema': 'finance'}
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database
from .models import Base
import os

DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "finance_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    engine = create_engine(DATABASE_URL)
    
    # Create database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)
        
    return engine

def init_db():
    engine = get_engine()
    
    # Create schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS finance;")
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(engine)
    
    return engine

engine = init_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
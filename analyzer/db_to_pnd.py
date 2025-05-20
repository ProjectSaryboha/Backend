from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine
import pandas as pd

def get_connection_string():
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def create_dataframe(connection_string, market_name, category):
    engine = create_engine(connection_string)
    
    query = """
        SELECT * 
        FROM groceries 
        WHERE url ILIKE %s AND category = %s 
        ORDER BY timestamp;
    """
    
    params = (f"%{market_name}%", category)
    
    df = pd.read_sql(query, engine, params=params)
    
    return df
from dotenv import load_dotenv
load_dotenv()
import os
import psycopg2


def create_table_if_not_exists():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    cur = conn.cursor()


    cur.execute("""
            CREATE TABLE IF NOT EXISTS groceries (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                currency VARCHAR(10),
                url TEXT,
                category TEXT,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
    """)




    conn.commit()
    cur.close()
    conn.close()
    
def insert_item_if_not_exists(name, price, currency, url, category):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO groceries (name, price, currency, url, category)
            SELECT %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM groceries WHERE url = %s
            );
        """, (name, price, currency, url, category, url))
        
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"❌ Помилка при вставці в базу: {e}")
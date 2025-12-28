import os
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor 
from dotenv import load_dotenv

load_dotenv()

# Global threaded pool (safe for your async threads)
connection_pool = None

def init_connection_pool():
    global connection_pool
    try:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            raise ValueError("DATABASE_URL not set in .env")
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,          # Min connections
            maxconn=10,         # Max (free tier safe)
            dsn=dsn,
            cursor_factory=DictCursor
        )
        print("PostgreSQL pool initialized")
    except Exception as e:
        print(f"Pool init error: {e}")
        raise

@contextmanager
def get_db_connection():
    conn = None
    try:
        if connection_pool is None:
            raise ValueError("Connection pool not initialized")
        conn = connection_pool.getconn()
        conn.autocommit = False  # Transactions
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"DB error: {e}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)
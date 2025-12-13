import sqlite3
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'student_management.db')

@contextmanager
def get_db_connection():
    
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        
        yield conn
        conn.commit()
    
    except sqlite3.Error as e:
        
        if conn:
            conn.rollback()
        print(f" Database Error: {e}") 
        raise e

    except Exception as e:
        if conn:
            conn.rollback()
        raise e 
    finally:
        if conn:
            conn.close()
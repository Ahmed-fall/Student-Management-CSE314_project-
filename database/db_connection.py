import sqlite3
import os

def get_db_connection():
    # Helper to get the full path to the database file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Database file is created in the project root, one level up from /database
    DB_PATH = os.path.join(BASE_DIR, '..', 'student_management.db')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn
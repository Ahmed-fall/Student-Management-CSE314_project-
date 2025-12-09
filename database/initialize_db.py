import sqlite3
import os

def create_tables():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'student_management.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking database tables...")

    # --- TEAM MEMBER 4 (AUTH/LEAD): USERS TABLE ---
    # [cite: 10] Schema from Page 5/10
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL -- "student", "instructor", "admin"
    );
    """)

    # --- TEAM MEMBER 1: STUDENTS ---
    # Paste your schema here...

    # --- TEAM MEMBER 2: INSTRUCTORS ---
    # Paste your schema here...

    # --- TEAM MEMBER 3: COURSES ---
    # Paste your schema here...

    # --- TEAM MEMBER 5: ASSIGNMENTS ---
    # Paste your schema here...

    # --- TEAM MEMBER 6: ANNOUNCEMENTS ---
    # Paste your schema here...

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    create_tables()
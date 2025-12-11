import sqlite3
import os

def create_tables():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'student_management.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking database tables...")

    # --- TEAM MEMBER 4 (AUTH/LEAD): USERS TABLE ---

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        level TEXT,
        birthdate TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # --- TEAM MEMBER 2: INSTRUCTORS ---
    # Paste your schema here...
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instructors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        specialty TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    # --- TEAM MEMBER 3: COURSES --- We need Instructors table first to be able to excute this (due to the forign key (instructor_id))
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        instructor_id INTEGER,
        FOREIGN KEY (instructor_id) REFERENCES instructors(id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        date_enrolled TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
    """)

    # --- TEAM MEMBER 5: ASSIGNMENTS ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        type TEXT NOT NULL, -- "quiz" or "project"
        due_date TEXT,
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        content TEXT,
        submitted_at TEXT,
        FOREIGN KEY (assignment_id) REFERENCES assignments(id),
        FOREIGN KEY (student_id) REFERENCES students(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL,
        grade_value REAL NOT NULL,
        FOREIGN KEY (submission_id) REFERENCES submissions(id)
    );
    """)

    # --- TEAM MEMBER 6: ANNOUNCEMENTS ---
    # Paste your schema here...

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    create_tables()
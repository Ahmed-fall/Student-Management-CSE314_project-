import os
import psycopg2
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

def create_tables():
    # 2. Get the URL from .env (just like your pool does)
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("Error: DATABASE_URL not found in .env file.")
        return

    try:
        # 3. Connect using the URL string
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        print("Connected to PostgreSQL. Checking tables...")

        # --- 1. USERS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            gender VARCHAR(20),
            password TEXT NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'instructor', 'admin'))
        );
        """)

        # --- 2. STUDENTS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            level INTEGER,
            birthdate DATE,
            major VARCHAR(100)
        );
        """)

        # --- 3. INSTRUCTORS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            department VARCHAR(100)
        );
        """)

        # --- 4. COURSES ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            code VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            credits INTEGER NOT NULL DEFAULT 3,
            semester VARCHAR(20) NOT NULL,
            max_students INTEGER NOT NULL DEFAULT 30,
            instructor_id INTEGER REFERENCES instructors(id) ON DELETE SET NULL
        );
        """)

        # --- 5. ENROLLMENTS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            date_enrolled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL DEFAULT 'enrolled'
        );
        """)

        # --- 6. ASSIGNMENTS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id SERIAL PRIMARY KEY,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            type VARCHAR(20) NOT NULL,
            due_date TIMESTAMP,
            max_score INTEGER NOT NULL DEFAULT 100
        );
        """)

        # --- 7. SUBMISSIONS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            content TEXT,
            submitted_at TIMESTAMP
        );
        """)

        # --- 8. GRADES ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id SERIAL PRIMARY KEY,
            submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
            grade_value DECIMAL(5, 2) NOT NULL,
            feedback TEXT
        );
        """)

        # --- 9. ANNOUNCEMENTS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # --- 10. NOTIFICATIONS ---
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            announcement_id INTEGER NOT NULL REFERENCES announcements(id) ON DELETE CASCADE,
            read_flag INTEGER DEFAULT 0,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully using .env config!")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    create_tables()
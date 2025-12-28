from core.base_repository import BaseRepository
from models.student import Student
from datetime import datetime

class StudentRepository(BaseRepository):
    """
    Handles interactions for Students.
    Manages the 'users' AND 'students' tables together.
    """

    def create(self, item: Student) -> Student:
        """
        ATOMIC CREATE: Saves User first, then Student.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql_user = """
        INSERT INTO users (username, name, email, gender, password, role)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql_student = """
        INSERT INTO students (user_id, level, birthdate, major)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        
        # Prepare User Data
        user_vals = (item.username, item.name, item.email, item.gender, item.password_hash, item.role)

        b_date = item.birthdate if item.birthdate else None

        with self.get_connection() as conn:
            cur = conn.cursor() # CHANGED
            
            # 1. Insert into Users
            cur.execute(sql_user, user_vals)
            new_id = cur.fetchone()[0] # CHANGED: Fetch returned ID
            
            # 2. Update Object with the new ID
            item.id = new_id
            item.user_id = new_id
            
            # 3. Insert into Students using that ID
            student_vals = (new_id, item.level, b_date, item.major)
            cur.execute(sql_student, student_vals)
            
            # CAPTURE THE STUDENT PROFILE ID
            item.student_profile_id = cur.fetchone()[0] # CHANGED: Fetch returned ID

            return item

    def update(self, item: Student):
        """
        ATOMIC UPDATE: Updates both tables at once.
        """
        # CHANGED: ? -> %s
        sql_user = """
        UPDATE users SET username=%s, name=%s, email=%s, gender=%s WHERE id=%s
        """
        # CHANGED: ? -> %s
        sql_student = """
        UPDATE students SET level=%s, birthdate=%s, major=%s WHERE user_id=%s
        """
        
        b_date = item.birthdate if item.birthdate else None
        user_vals = (item.username, item.name, item.email, item.gender, item.id)
        student_vals = (item.level, b_date, item.major, item.id)
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql_user, user_vals)
            cur.execute(sql_student, student_vals)

    def get_all(self):
        sql = """
        SELECT 
            users.*, 
            students.user_id, 
            students.id as student_profile_id, 
            students.level, 
            students.birthdate, 
            students.major
        FROM users
        JOIN students ON users.id = students.user_id
        WHERE users.role = 'student'
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Student.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id):
        # CHANGED: ? -> %s
        sql = """
        SELECT 
            users.*, 
            students.user_id, 
            students.id as student_profile_id, 
            students.level, 
            students.birthdate, 
            students.major
        FROM users
        JOIN students ON users.id = students.user_id
        WHERE users.id = %s
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            return Student.from_row(row) if row else None

    def delete(self, id):
        # Deleting the User triggers a cascade delete in SQL usually.
        # If not, we delete manually. Assuming CASCADE or Parent delete:
        # CHANGED: ? -> %s
        sql = "DELETE FROM users WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
    
    def add_enrollment(self, user_id: int, course_id: int):
        """Links a student to a course using their profile ID."""
        # CHANGED: ? -> %s
        sql_get_profile = "SELECT id FROM students WHERE user_id = %s"
        sql_insert = "INSERT INTO enrollments (student_id, course_id, status, date_enrolled) VALUES (%s, %s, 'enrolled', %s)"
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Find the student's internal ID first
            cur.execute(sql_get_profile, (user_id,))
            res = cur.fetchone()
            if not res:
                return False
            
            student_profile_id = res[0]
            # Register them
            cur.execute(sql_insert, (student_profile_id, course_id, datetime.now()))
            return True

    def get_profile_id_by_user_id(self, user_id: int):
        """
        Helper: Resolves the Auth User ID to the internal Student Profile ID.
        Required by AssignmentService.
        """
        # CHANGED: ? -> %s
        sql = "SELECT id FROM students WHERE user_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            res = cur.fetchone()
            return res[0] if res else None
        
    def _fetch_all(self, sql, params=()):
        """
        Helper to ensure results can be accessed by column name (like s.name).
        Adapted for PostgreSQL since psycopg2 returns tuples by default.
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            
            # Manually map column names to values to create a dict
            if cur.description:
                colnames = [desc[0] for desc in cur.description]
                return [dict(zip(colnames, row)) for row in rows]
            return []

    def get_students_by_course(self, course_id: int):
        """Fetches students using the correct table name."""
        # CHANGED: ? -> %s
        sql = """
            SELECT u.name, s.major, s.level 
            FROM users u
            JOIN students s ON u.id = s.user_id
            JOIN enrollments e ON s.id = e.student_id
            WHERE e.course_id = %s
        """
        return self._fetch_all(sql, (course_id,))
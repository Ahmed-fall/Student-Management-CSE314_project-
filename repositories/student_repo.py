from core.base_repository import BaseRepository
from models.student import Student

class StudentRepository(BaseRepository):
    """
    Handles interactions for Students.
    Manages the 'users' AND 'students' tables together.
    """

    def create(self, item: Student) -> Student:
        """
        ATOMIC CREATE: Saves User first, then Student.
        """
        sql_user = """
        INSERT INTO users (username, name, email, gender, password, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        sql_student = """
        INSERT INTO students (user_id, level, birthdate, major)
        VALUES (?, ?, ?, ?)
        """
        
        # Prepare User Data
        user_vals = (item.username, item.name, item.email, item.gender, item.password_hash, item.role)

        with self.get_connection() as conn:
            # 1. Insert into Users
            cursor = conn.execute(sql_user, user_vals)
            new_id = cursor.lastrowid
            
            # 2. Update Object with the new ID
            item.id = new_id
            item.user_id = new_id
            
            # 3. Insert into Students using that ID
            student_vals = (new_id, item.level, item.birthdate, item.major)
            cursor_stud = conn.execute(sql_student, student_vals)
            
            # CAPTURE THE STUDENT PROFILE ID
            item.student_profile_id = cursor_stud.lastrowid

            return item

    def update(self, item: Student):
        """
        ATOMIC UPDATE: Updates both tables at once.
        """
        sql_user = """
        UPDATE users SET username=?, name=?, email=?, gender=? WHERE id=?
        """
        sql_student = """
        UPDATE students SET level=?, birthdate=?, major=? WHERE user_id=?
        """
        
        user_vals = (item.username, item.name, item.email, item.gender, item.id)
        student_vals = (item.level, item.birthdate, item.major, item.id)
        
        with self.get_connection() as conn:
            conn.execute(sql_user, user_vals)
            conn.execute(sql_student, student_vals)

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
            cursor = conn.execute(sql)
            return [Student.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id):
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
        WHERE users.id = ?
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return Student.from_row(cursor.fetchone())

    def delete(self, id):
        # Deleting the User triggers a cascade delete in SQL usually.
        # If not, we delete manually. Assuming CASCADE or Parent delete:
        sql = "DELETE FROM users WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
    
    def add_enrollment(self, user_id: int, course_id: int):
        """Links a student to a course using their profile ID."""
        sql_get_profile = "SELECT id FROM students WHERE user_id = ?"
        sql_insert = "INSERT INTO enrollments (student_id, course_id, status, date_enrolled) VALUES (?, ?, 'enrolled', ?)"
        
        with self.get_connection() as conn:
            # Find the student's internal ID first
            res = conn.execute(sql_get_profile, (user_id,)).fetchone()
            if not res:
                return False
            
            student_profile_id = res[0]
            # Register them
            from datetime import datetime
            conn.execute(sql_insert, (student_profile_id, course_id, datetime.now().isoformat()))
            return True
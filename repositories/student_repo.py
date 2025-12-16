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
            conn.execute(sql_student, student_vals)
            
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
        SELECT users.*, students.user_id, students.level, students.birthdate, students.major
        FROM users
        JOIN students ON users.id = students.user_id
        WHERE users.role = 'student'
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Student.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id):
        sql = """
        SELECT users.*, students.user_id, students.level, students.birthdate, students.major
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
from core.base_repository import BaseRepository
from models.course import Course

class CourseRepository(BaseRepository):
    """
    Handles strict database interactions for the 'courses' table.

    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:'.
    - Data Safety: Returns strict 'Course' objects via 'from_row'.
    - Security: Parameterized queries to prevent SQL injection.
    """

    def create(self, code: str, name: str, description: str, credits: int, semester: str, max_students: int, instructor_id: int):
        """
        Inserts a new course into the database.
        """
        sql = """
        INSERT INTO courses (code, name, description, credits, semester, max_students, instructor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(sql, (code, name, description, credits, semester, max_students, instructor_id))

    def get_all(self):
        """
        Fetches all courses.
        """
        sql = "SELECT * FROM courses"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Course.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single course by its unique ID.
        """
        sql = "SELECT * FROM courses WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return Course.from_row(cursor.fetchone())

    def get_by_instructor_id(self, instructor_id: int):
        """
        Fetches all courses taught by a specific instructor.
        """
        sql = "SELECT * FROM courses WHERE instructor_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (instructor_id,))
            return [Course.from_row(row) for row in cursor.fetchall()]

    def update(self, id: int, code: str, name: str, description: str, credits: int, semester: str, max_students: int, instructor_id: int):
        """
        Updates an existing course's details.
        """
        sql = """
        UPDATE courses
        SET code = ?, name = ?, description = ?, credits = ?, semester = ?, max_students = ?, instructor_id = ?
        WHERE id = ?
        """
        with self.get_connection() as conn:
            conn.execute(sql, (code, name, description, credits, semester, max_students, instructor_id, id))

    def delete(self, id: int):
        """
        Hard deletes a course by ID.
        """
        sql = "DELETE FROM courses WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

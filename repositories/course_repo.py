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

    def create(self, item: Course) -> Course:
        """
        Inserts a new course into the database.
        """
        sql = """
        INSERT INTO courses (code, name, description, credits, semester, max_students, instructor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            item.code, item.name, item.description, 
            item.credits, item.semester, item.max_students, item.instructor_id
        )
        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid 
            return item 
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

    def update(self, item: Course):
        """
        Updates an existing course's details.
        """
        sql = """
        UPDATE courses
        SET code = ?, name = ?, description = ?, credits = ?, semester = ?, max_students = ?, instructor_id = ?
        WHERE id = ?
        """
        values = (
            item.code, item.name, item.description, item.credits, 
            item.semester, item.max_students, item.instructor_id, item.id
        )
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes a course by ID.
        """
        sql = "DELETE FROM courses WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

    def get_by_code(self, code: str):
        """
        Fetches a course by its unique code (e.g. 'CS101').
        Used for validation to prevent duplicates.
        """
        sql = "SELECT * FROM courses WHERE code = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (code,))
            return Course.from_row(cursor.fetchone())
    
    def get_enrollment_count(self, course_id: int) -> int:
        """Calculates how many students are currently in the course."""
        sql = "SELECT COUNT(*) FROM enrollments WHERE course_id = ? AND status = 'enrolled'"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        
def unassign_instructor(self, course_id: int):
        """Sets the instructor_id of a course to NULL in the database."""
        sql = "UPDATE courses SET instructor_id = NULL WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (course_id,))
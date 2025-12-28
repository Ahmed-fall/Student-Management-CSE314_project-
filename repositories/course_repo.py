from core.base_repository import BaseRepository
from models.course import Course

class CourseRepository(BaseRepository):
    """
    Handles strict database interactions for the 'courses' table.
    """

    def create(self, item: Course) -> Course:
        """
        Inserts a new course into the database.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql = """
        INSERT INTO courses (code, name, description, credits, semester, max_students, instructor_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        values = (
            item.code, item.name, item.description, 
            item.credits, item.semester, item.max_students, item.instructor_id
        )
        with self.get_connection() as conn:
            cur = conn.cursor()          # CHANGED
            cur.execute(sql, values)     # CHANGED
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item 

    def get_all(self):
        """
        Fetches all courses.
        """
        sql = "SELECT * FROM courses"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Course.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single course by its unique ID.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM courses WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            return Course.from_row(row) if row else None

    def get_by_instructor_id(self, instructor_id: int):
        """
        Fetches all courses taught by a specific instructor.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM courses WHERE instructor_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (instructor_id,))
            return [Course.from_row(row) for row in cur.fetchall()]

    def update(self, item: Course):
        """
        Updates an existing course's details.
        """
        # CHANGED: ? -> %s
        sql = """
        UPDATE courses
        SET code = %s, name = %s, description = %s, credits = %s, semester = %s, max_students = %s, instructor_id = %s
        WHERE id = %s
        """
        values = (
            item.code, item.name, item.description, item.credits, 
            item.semester, item.max_students, item.instructor_id, item.id
        )
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes a course by ID.
        """
        # CHANGED: ? -> %s
        sql = "DELETE FROM courses WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))

    def get_by_code(self, code: str):
        """
        Fetches a course by its unique code (e.g. 'CS101').
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM courses WHERE code = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (code,))
            row = cur.fetchone()
            return Course.from_row(row) if row else None
    
    def get_enrollment_count(self, course_id: int) -> int:
        """Calculates how many students are currently in the course."""
        # CHANGED: ? -> %s
        sql = "SELECT COUNT(*) FROM enrollments WHERE course_id = %s AND status = 'enrolled'"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            result = cur.fetchone()
            return result[0] if result else 0

    def get_enrolled_students_details(self, course_id: int):
        """
        Fetches details (Name, Major) for the Roster Popup.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT u.name, u.email, s.major 
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_profile_id
        JOIN users u ON s.user_id = u.id
        WHERE e.course_id = %s
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            return cur.fetchall()
        
    def unassign_instructor(self, course_id: int):
        """Sets the instructor_id of a course to NULL in the database."""
        # CHANGED: ? -> %s
        sql = "UPDATE courses SET instructor_id = NULL WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
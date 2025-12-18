from core.base_repository import BaseRepository
from models.enrollment import Enrollment
from models.course import Course

class EnrollmentRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'enrollments' table.

    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    - Data Safety: Returns strict 'Enrollment' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, item: Enrollment) -> Enrollment:
        """
        Inserts a new enrollment into the database.
        If date_enrolled is None, uses current date.
        """
        
        sql = """
        INSERT INTO enrollments (student_id, course_id, date_enrolled, status)
        VALUES (?, ?, ?, ?)
        """
        values = (item.student_id, item.course_id, item.date_enrolled, item.status)
        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid
            return item

    def get_all(self):
        """
        Fetches all enrollments.
        """
        sql = "SELECT * FROM enrollments"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Enrollment.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetch a single enrollment by unique ID.
        """
        sql = "SELECT * FROM enrollments WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return Enrollment.from_row(cursor.fetchone())

    def get_by_student_id(self, student_id: int):
        """
        Fetch all enrollments for a specific student.
        """
        sql = "SELECT * FROM enrollments WHERE student_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id,))
            return [Enrollment.from_row(row) for row in cursor.fetchall()]

    def get_by_course_id(self, course_id: int):
        """
        Fetch all enrollments for a specific course.
        """
        sql = "SELECT * FROM enrollments WHERE course_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            return [Enrollment.from_row(row) for row in cursor.fetchall()]

    def update(self, item: Enrollment):
        """
        Update an enrollment's status.
        """
        sql = "UPDATE enrollments SET status = ? WHERE id = ?"
        values = (item.status, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes an enrollment by ID.
        """
        sql = "DELETE FROM enrollments WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

    def is_enrolled(self, user_id: int, course_id: int) -> bool:
        """
        Checks if a User (via user_id) is enrolled in a course.
        Bridges the gap between User ID and Student Profile ID.
        """
        sql = """
        SELECT 1 FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE s.user_id = ? AND e.course_id = ? AND e.status = 'enrolled'
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (user_id, course_id))
            return cursor.fetchone() is not None
        
    def get_courses_by_student(self, student_profile_id: int):
        """
        Joins Enrollments with Courses to return the actual Course objects
        that a student is enrolled in.
        """
        sql = """
        SELECT c.* FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.student_id = ? AND e.status = 'enrolled'
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_profile_id,))
            # We reuse the Course model's factory to return standard objects
            return [Course.from_row(row) for row in cursor.fetchall()]
    
    def get_enrolled_user_ids(self, course_id: int):
        """
        Returns a list of User IDs (from users table) for all active students in a course.
        Essential for sending Notifications to the correct Account.
        """
        sql = """
        SELECT s.user_id 
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE e.course_id = ? AND e.status = 'enrolled'
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            return [row[0] for row in cursor.fetchall()]

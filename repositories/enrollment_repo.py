from core.base_repository import BaseRepository
from models.enrollment import Enrollment
from models.course import Course

class EnrollmentRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'enrollments' table.
    """

    def create(self, item: Enrollment) -> Enrollment:
        """
        Inserts a new enrollment into the database.
        If date_enrolled is None, uses current date.
        """
        
        # CHANGED: ? -> %s and added RETURNING id
        sql = """
        INSERT INTO enrollments (student_id, course_id, date_enrolled, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        values = (item.student_id, item.course_id, item.date_enrolled, item.status)
        with self.get_connection() as conn:
            cur = conn.cursor()          # CHANGED
            cur.execute(sql, values)     # CHANGED
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item

    def get_all(self):
        """
        Fetches all enrollments.
        """
        sql = "SELECT * FROM enrollments"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Enrollment.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetch a single enrollment by unique ID.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM enrollments WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            return Enrollment.from_row(row) if row else None

    def get_by_student_id(self, student_id: int):
        """
        Fetch all enrollments for a specific student.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM enrollments WHERE student_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_id,))
            return [Enrollment.from_row(row) for row in cur.fetchall()]

    def get_by_course_id(self, course_id: int):
        """
        Fetch all enrollments for a specific course.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM enrollments WHERE course_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            return [Enrollment.from_row(row) for row in cur.fetchall()]

    def update(self, item: Enrollment):
        """
        Update an enrollment's status.
        """
        # CHANGED: ? -> %s
        sql = "UPDATE enrollments SET status = %s WHERE id = %s"
        values = (item.status, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes an enrollment by ID.
        """
        # CHANGED: ? -> %s
        sql = "DELETE FROM enrollments WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))

    def is_enrolled(self, user_id: int, course_id: int) -> bool:
        """
        Checks if a User (via user_id) is enrolled in a course.
        Bridges the gap between User ID and Student Profile ID.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT 1 FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE s.user_id = %s AND e.course_id = %s AND e.status = 'enrolled'
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id, course_id))
            return cur.fetchone() is not None
        
    def get_courses_by_student(self, student_profile_id: int):
        """
        Joins Enrollments with Courses to return the actual Course objects
        that a student is enrolled in.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT c.* FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.student_id = %s AND e.status = 'enrolled'
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_profile_id,))
            # We reuse the Course model's factory to return standard objects
            return [Course.from_row(row) for row in cur.fetchall()]
        
    def delete_enrollment(self, student_id: int, course_id: int) -> bool:
        """Permanently removes the enrollment record from the database."""
        # CHANGED: ? -> %s
        sql = "DELETE FROM enrollments WHERE student_id = %s AND course_id = %s"
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, (student_id, course_id))
                # Return True if a row was actually deleted
                return cur.rowcount > 0
        except Exception:
            return False
    
    def get_enrolled_user_ids(self, course_id: int):
        """
        Returns a list of User IDs (from users table) for all active students in a course.
        Essential for sending Notifications to the correct Account.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT s.user_id 
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE e.course_id = %s AND e.status = 'enrolled'
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            return [row[0] for row in cur.fetchall()]
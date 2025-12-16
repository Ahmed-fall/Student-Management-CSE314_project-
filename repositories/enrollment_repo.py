from core.base_repository import BaseRepository
from models.enrollment import Enrollment

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
        values = (item.status, item.date_enrolled, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes an enrollment by ID.
        """
        sql = "DELETE FROM enrollments WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

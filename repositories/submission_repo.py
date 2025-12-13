from core.base_repository import BaseRepository
from database.db_connection import get_db_connection

class SubmissionRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'submissions' table.
    
    Implementation details:
    - Connection Safety: Uses 'with get_db_connection()' for automatic cleanup.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, assignment_id: int, student_id: int, content: str, submitted_at: str):
        """
        Inserts a new submission into the database.
        """
        sql = """
        INSERT INTO submissions (assignment_id, student_id, content, submitted_at)
        VALUES (?, ?, ?, ?)
        """
        with get_db_connection() as conn:
            conn.execute(sql, (assignment_id, student_id, content, submitted_at))

    def get_all(self):
        """
        Fetches all submissions.
        """
        sql = "SELECT * FROM submissions"
        with get_db_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()

    def get_by_id(self, id: int):
        """
        Fetches a single submission by unique ID.
        """
        sql = "SELECT * FROM submissions WHERE id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return cursor.fetchone()

    def get_by_assignment_id(self, assignment_id: int):
        """
        Fetches all submissions for a specific assignment.
        Useful for teachers grading a specific task.
        """
        sql = "SELECT * FROM submissions WHERE assignment_id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (assignment_id,))
            return cursor.fetchall()

    def get_by_student_id(self, student_id: int):
        """
        Fetches all submissions made by a specific student.
        Useful for student history views.
        """
        sql = "SELECT * FROM submissions WHERE student_id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (student_id,))
            return cursor.fetchall()

    def update(self, id: int, content: str, submitted_at: str):
        """
        Updates an existing submission's content and timestamp.
        Note: We do not update assignment_id or student_id as ownership shouldn't change.
        """
        sql = """
        UPDATE submissions 
        SET content = ?, submitted_at = ?
        WHERE id = ?
        """
        with get_db_connection() as conn:
            conn.execute(sql, (content, submitted_at, id))

    def delete(self, id: int):
        """
        Hard deletes a submission by ID.
        """
        sql = "DELETE FROM submissions WHERE id = ?"
        with get_db_connection() as conn:
            conn.execute(sql, (id,))
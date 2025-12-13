from core.base_repository import BaseRepository
from database.db_connection import get_db_connection

class GradeRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'grades' table.
    
    Implementation details:
    - Connection Safety: Uses 'with get_db_connection()' for automatic cleanup.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, submission_id: int, grade_value: float, feedback: str):
        """
        Inserts a new grade into the database.
        """
        sql = """
        INSERT INTO grades (submission_id, grade_value, feedback)
        VALUES (?, ?, ?)
        """
        with get_db_connection() as conn:
            conn.execute(sql, (submission_id, grade_value, feedback))

    def get_all(self):
        """
        Fetches all grades.
        """
        sql = "SELECT * FROM grades"
        with get_db_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()

    def get_by_id(self, id: int):
        """
        Fetches a single grade by unique ID.
        """
        sql = "SELECT * FROM grades WHERE id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return cursor.fetchone()

    def get_by_submission_id(self, submission_id: int):
        """
        Fetches the grade associated with a specific submission.
        """
        sql = "SELECT * FROM grades WHERE submission_id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (submission_id,))
            return cursor.fetchone()

    def update(self, id: int, grade_value: float, feedback: str):
        """
        Updates an existing grade's value and feedback.
        """
        sql = """
        UPDATE grades 
        SET grade_value = ?, feedback = ?
        WHERE id = ?
        """
        with get_db_connection() as conn:
            conn.execute(sql, (grade_value, feedback, id))

    def delete(self, id: int):
        """
        Hard deletes a grade by ID.
        """
        sql = "DELETE FROM grades WHERE id = ?"
        with get_db_connection() as conn:
            conn.execute(sql, (id,))
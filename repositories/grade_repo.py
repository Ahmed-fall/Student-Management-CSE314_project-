from core.base_repository import BaseRepository
from models.grade import Grade

class GradeRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'grades' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection()' (Inherited from Base).
    - Data Safety: Returns strict 'Grade' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, item: Grade) -> Grade:
        """
        Inserts a new grade into the database.
        """
        sql = """
        INSERT INTO grades (submission_id, grade_value, feedback)
        VALUES (?, ?, ?)
        """
        values = (item.submission_id, item.grade_value, item.feedback)

        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid
            return item

    def get_all(self):
        """
        Fetches all grades and converts them to Grade objects.
        """
        sql = "SELECT * FROM grades"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Grade.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single grade by unique ID.
        """
        sql = "SELECT * FROM grades WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            # CRITICAL UPDATE: Convert single row to Object
            return Grade.from_row(cursor.fetchone())

    def get_by_submission_id(self, submission_id: int):
        """
        Fetches the grade associated with a specific submission.
        """
        sql = "SELECT * FROM grades WHERE submission_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (submission_id,))
            return Grade.from_row(cursor.fetchone())

    def update(self, item: Grade):
        """
        Updates an existing grade's value and feedback.
        """
        sql = """
        UPDATE grades 
        SET grade_value = ?, feedback = ?
        WHERE id = ?
        """
        values = (item.grade_value, item.feedback, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes a grade by ID.
        """
        sql = "DELETE FROM grades WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
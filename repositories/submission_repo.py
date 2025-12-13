from core.base_repository import BaseRepository
from models.submission import Submission

class SubmissionRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'submissions' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection()' (Inherited from Base).
    - Data Safety: Returns strict 'Submission' objects via 'from_row', not raw tuples.
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
        with self.get_connection() as conn:
            conn.execute(sql, (assignment_id, student_id, content, submitted_at))

    def get_all(self):
        """
        Fetches all submissions and converts them to Submission objects.
        """
        sql = "SELECT * FROM submissions"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Submission.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single submission by unique ID.
        """
        sql = "SELECT * FROM submissions WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return Submission.from_row(cursor.fetchone())

    def get_by_assignment_id(self, assignment_id: int):
        """
        Fetches all submissions for a specific assignment.
        Useful for teachers grading a specific task.
        """
        sql = "SELECT * FROM submissions WHERE assignment_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (assignment_id,))
            return [Submission.from_row(row) for row in cursor.fetchall()]

    def get_by_student_id(self, student_id: int):
        """
        Fetches all submissions made by a specific student.
        Useful for student history views.
        """
        sql = "SELECT * FROM submissions WHERE student_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id,))
            return [Submission.from_row(row) for row in cursor.fetchall()]

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
        with self.get_connection() as conn:
            conn.execute(sql, (content, submitted_at, id))

    def delete(self, id: int):
        """
        Hard deletes a submission by ID.
        """
        sql = "DELETE FROM submissions WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
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

    def create(self, item: Submission) -> Submission:
        """
        Inserts a new submission into the database.
        """
        sql = """
        INSERT INTO submissions (assignment_id, student_id, content, submitted_at)
        VALUES (?, ?, ?, ?)
        """
        values = (item.assignment_id, item.student_id, item.content, item.submitted_at)

        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid
            return item

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

    def update(self, item: Submission):
        """
        Updates an existing submission's content and timestamp.
        Note: We do not update assignment_id or student_id as ownership shouldn't change.
        """
        sql = """
        UPDATE submissions 
        SET content = ?, submitted_at = ?
        WHERE id = ?
        """
        values = (item.content, item.submitted_at, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes a submission by ID.
        """
        sql = "DELETE FROM submissions WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
    
    def get_by_student_and_course(self, student_id: int, course_id: int):
        sql = """
        SELECT s.* FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.student_id = ? AND a.course_id = ?
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id, course_id))
            return [Submission.from_row(row) for row in cursor.fetchall()]
    
    def get_by_student_and_assignment(self, student_id: int, assignment_id: int):
        sql = "SELECT * FROM submissions WHERE student_id = ? AND assignment_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id, assignment_id))
            return Submission.from_row(cursor.fetchone())
            
    def get_grading_queue(self, assignment_id: int):
            """
            Fetches all submissions for a specific assignment, including Student Name and Grade.
            Used by the Instructor Grading View.
            """
            sql = """
            SELECT 
                s.id as submission_id,
                u.name as student_name,
                s.submitted_at,
                g.grade_value,
                g.feedback
            FROM submissions s
            JOIN students st ON s.student_id = st.id
            JOIN users u ON st.user_id = u.id
            LEFT JOIN grades g ON s.id = g.submission_id
            WHERE s.assignment_id = ?
            ORDER BY s.submitted_at DESC
            """
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (assignment_id,))
                return [dict(row) for row in cursor.fetchall()]
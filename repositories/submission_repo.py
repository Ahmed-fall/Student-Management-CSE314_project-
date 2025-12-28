from core.base_repository import BaseRepository
from models.submission import Submission

class SubmissionRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'submissions' table.
    """

    def create(self, item: Submission) -> Submission:
        """
        Inserts a new submission into the database.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql = """
        INSERT INTO submissions (assignment_id, student_id, content, submitted_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        values = (item.assignment_id, item.student_id, item.content, item.submitted_at)

        with self.get_connection() as conn:
            cur = conn.cursor()          # CHANGED
            cur.execute(sql, values)     # CHANGED
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item

    def get_all(self):
        """
        Fetches all submissions and converts them to Submission objects.
        """
        sql = "SELECT * FROM submissions"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Submission.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single submission by unique ID.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM submissions WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            return Submission.from_row(row) if row else None

    def get_by_assignment_id(self, assignment_id: int):
        """
        Fetches all submissions for a specific assignment.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM submissions WHERE assignment_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (assignment_id,))
            return [Submission.from_row(row) for row in cur.fetchall()]

    def get_by_student_id(self, student_id: int):
        """
        Fetches all submissions made by a specific student.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM submissions WHERE student_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_id,))
            return [Submission.from_row(row) for row in cur.fetchall()]

    def update(self, item: Submission):
        """
        Updates an existing submission's content and timestamp.
        """
        # CHANGED: ? -> %s
        sql = """
        UPDATE submissions 
        SET content = %s, submitted_at = %s
        WHERE id = %s
        """
        values = (item.content, item.submitted_at, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes a submission by ID.
        """
        # CHANGED: ? -> %s
        sql = "DELETE FROM submissions WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
    
    def get_by_student_and_course(self, student_id: int, course_id: int):
        # CHANGED: ? -> %s
        sql = """
        SELECT s.* FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.student_id = %s AND a.course_id = %s
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_id, course_id))
            return [Submission.from_row(row) for row in cur.fetchall()]
    
    def get_by_student_and_assignment(self, student_id: int, assignment_id: int):
        # CHANGED: ? -> %s
        sql = "SELECT * FROM submissions WHERE student_id = %s AND assignment_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_id, assignment_id))
            row = cur.fetchone()
            return Submission.from_row(row) if row else None
            
    def get_grading_queue(self, assignment_id: int):
        """
        Fetches all submissions for a specific assignment, including the Content.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT 
            s.id as submission_id,
            u.name as student_name,
            s.submitted_at,
            s.content as submission_content, 
            g.grade_value,
            g.feedback
        FROM submissions s
        JOIN students st ON s.student_id = st.id
        JOIN users u ON st.user_id = u.id
        LEFT JOIN grades g ON s.id = g.submission_id
        WHERE s.assignment_id = %s
        ORDER BY s.submitted_at DESC
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (assignment_id,))
            rows = cur.fetchall()
            
            # Manual dictionary mapping because psycopg2 rows are tuples
            results = []
            for row in rows:
                results.append({
                    "submission_id": row[0],
                    "student_name": row[1],
                    "submitted_at": row[2],
                    "submission_content": row[3],
                    "grade_value": row[4],
                    "feedback": row[5]
                })
            return results
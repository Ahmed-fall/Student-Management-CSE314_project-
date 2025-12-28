from core.base_repository import BaseRepository
from models.grade import Grade

class GradeRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'grades' table.
    """

    def create(self, item: Grade) -> Grade:
        """
        Inserts a new grade into the database.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql = """
        INSERT INTO grades (submission_id, grade_value, feedback)
        VALUES (%s, %s, %s)
        RETURNING id
        """
        values = (item.submission_id, item.grade_value, item.feedback)

        with self.get_connection() as conn:
            cur = conn.cursor()          # CHANGED
            cur.execute(sql, values)     # CHANGED
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item

    def get_all(self):
        """
        Fetches all grades and converts them to Grade objects.
        """
        sql = "SELECT * FROM grades"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Grade.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single grade by unique ID.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM grades WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            return Grade.from_row(row) if row else None

    def get_by_submission_id(self, submission_id: int):
        """
        Fetches the grade associated with a specific submission.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM grades WHERE submission_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (submission_id,))
            row = cur.fetchone()
            return Grade.from_row(row) if row else None

    def update(self, item: Grade):
        """
        Updates an existing grade's value and feedback.
        """
        # CHANGED: ? -> %s
        sql = """
        UPDATE grades 
        SET grade_value = %s, feedback = %s
        WHERE id = %s
        """
        values = (item.grade_value, item.feedback, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes a grade by ID.
        """
        # CHANGED: ? -> %s
        sql = "DELETE FROM grades WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
    
    def get_student_total_score(self, student_id: int, course_id: int) -> float:
        """
        Calculates total points earned by a student in a specific course.
        Joins Grades -> Submissions -> Assignments.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT SUM(g.grade_value)
        FROM grades g
        JOIN submissions s ON g.submission_id = s.id
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.student_id = %s AND a.course_id = %s
        """
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_id, course_id))
            result = cur.fetchone()[0]
            return result if result else 0.0
    
    def get_transcript_data(self, student_id: int):
        """
        Complex Reporting Query updated for tuple row access.
        """
        # CHANGED: ? -> %s
        sql = """
        SELECT 
            c.code, 
            c.name as course_name, 
            AVG(g.grade_value) as average_score
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        LEFT JOIN assignments a ON c.id = a.course_id
        LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = e.student_id
        LEFT JOIN grades g ON s.id = g.submission_id
        WHERE e.student_id = %s AND e.status = 'enrolled'
        GROUP BY c.id, c.code, c.name
        """
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (student_id,))
            rows = cur.fetchall()
            
            transcript = []
            for row in rows:
                # IMPORTANT: PostgreSQL returns tuples, not dicts.
                # Access by index: 0=code, 1=course_name, 2=average_score
                avg = row[2] if row[2] is not None else 0.0
                
                transcript.append({
                    "course_code": row[0],
                    "course_name": row[1],
                    "total_score": round(avg, 2) 
                })
            return transcript
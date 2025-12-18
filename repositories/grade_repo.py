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
    
    def get_student_total_score(self, student_id: int, course_id: int) -> float:
        """
        Calculates total points earned by a student in a specific course.
        Joins Grades -> Submissions -> Assignments.
        """
        sql = """
        SELECT SUM(g.grade_value)
        FROM grades g
        JOIN submissions s ON g.submission_id = s.id
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.student_id = ? AND a.course_id = ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id, course_id))
            result = cursor.fetchone()[0]
            return result if result else 0.0
    
    def get_transcript_data(self, student_id: int):
        """
        Complex Reporting Query updated for named row access.
        """
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
        WHERE e.student_id = ? AND e.status = 'enrolled'
        GROUP BY c.id, c.code, c.name
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id,))
            rows = cursor.fetchall()
            
            transcript = []
            for row in rows:
                # Use NAMED access since row_factory is sqlite3.Row
                avg = row["average_score"] if row["average_score"] is not None else 0.0
                
                transcript.append({
                    "course_code": row["code"],
                    "course_name": row["course_name"],
                    "total_score": round(avg, 2) 
                })
            return transcript
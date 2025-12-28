from core.base_repository import BaseRepository
from models.assignment import Assignment

class AssignmentRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'assignments' table.
    """

    def create(self, item: Assignment) -> Assignment:
        """
        Inserts a new assignment into the database.
        """
        sql = """
        INSERT INTO assignments (course_id, title, description, type, due_date, max_score)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        values = (item.course_id, item.title, item.description, item.type, item.due_date, item.max_score)
        
        with self.get_connection() as conn:
            cur = conn.cursor()          
            cur.execute(sql, values)     
            item.id = cur.fetchone()[0]  
            return item

    def get_all(self):
        """
        Fetches all assignments.
        """
        sql = "SELECT * FROM assignments"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Assignment.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single assignment by unique ID.
        """
        sql = "SELECT * FROM assignments WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            if row:
                return Assignment.from_row(row)
            return None

    def get_by_course_id(self, course_id: int):
        """
        Fetches all assignments belonging to a specific course.
        """
        sql = "SELECT * FROM assignments WHERE course_id = %s ORDER BY due_date ASC"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            return [Assignment.from_row(row) for row in cur.fetchall()]

    def update(self, item: Assignment):
        """
        Updates an existing assignment's details.
        """
        sql = """
        UPDATE assignments 
        SET title = %s, description = %s, type = %s, due_date = %s, max_score = %s
        WHERE id = %s
        """
        values = (item.title, item.description, item.type, item.due_date, item.max_score, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes an assignment by ID.
        """
        sql = "DELETE FROM assignments WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
    
    def get_course_max_score(self, course_id: int) -> float:
        """
        Calculates the total possible points for a course (Sum of all assignments).
        """
        sql = "SELECT SUM(max_score) FROM assignments WHERE course_id = %s"
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            result = cur.fetchone()[0]
            return result if result else 0.0
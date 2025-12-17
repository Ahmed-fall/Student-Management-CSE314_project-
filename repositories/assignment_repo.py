from core.base_repository import BaseRepository
from models.assignment import Assignment

class AssignmentRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'assignments' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    -Data Safety: Returns strict 'Assignment' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, item: Assignment) -> Assignment:
        """
        Inserts a new assignment into the database.
        """
        sql = """
        INSERT INTO assignments (course_id, title, description, type, due_date, max_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        # We extract values from the Validated Object, not raw arguments
        values = (item.course_id, item.title, item.description, item.type, item.due_date, item.max_score)
        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid
            return item

    def get_all(self):
        """
        Fetches all assignments.
        """
        sql = "SELECT * FROM assignments"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Assignment.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        """
        Fetches a single assignment by unique ID.
        """
        sql = "SELECT * FROM assignments WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return Assignment.from_row(cursor.fetchone())

    def get_by_course_id(self, course_id: int):
        """
        Fetches all assignments belonging to a specific course.
        """
        sql = "SELECT * FROM assignments WHERE course_id = ? ORDER BY due_date ASC"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            return [Assignment.from_row(row) for row in cursor.fetchall()]

    def update(self, item: Assignment):
        """
        Updates an existing assignment's details.
        """
        sql = """
        UPDATE assignments 
        SET title = ?, description = ?, type = ?, due_date = ?, max_score = ?
        WHERE id = ?
        """
        values = (item.title, item.description, item.type, item.due_date, item.max_score, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id: int):
        """
        Hard deletes an assignment by ID.
        """
        sql = "DELETE FROM assignments WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
    
    def get_course_max_score(self, course_id: int) -> float:
        """
        Calculates the total possible points for a course (Sum of all assignments).
        """
        sql = "SELECT SUM(max_score) FROM assignments WHERE course_id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            result = cursor.fetchone()[0]
            # If result is None (no assignments), return 0.0
            return result if result else 0.0
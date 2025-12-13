from core.base_repository import BaseRepository
from database.db_connection import get_db_connection

class AssignmentRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'assignments' table.
    
    Implementation details:
    - Connection Safety: Uses 'with get_db_connection()' for automatic cleanup.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    - Consistency: Enforces foreign keys and transaction commits automatically.
    """

    def create(self, course_id: int, title: str, description: str, type: str, due_date: str, max_score: int):
        """
        Inserts a new assignment into the database.
        """
        sql = """
        INSERT INTO assignments (course_id, title, description, type, due_date, max_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with get_db_connection() as conn:
            conn.execute(sql, (course_id, title, description, type, due_date, max_score))

    def get_all(self):
        """
        Fetches all assignments.
        """
        sql = "SELECT * FROM assignments"
        with get_db_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()

    def get_by_id(self, id: int):
        """
        Fetches a single assignment by unique ID.
        """
        sql = "SELECT * FROM assignments WHERE id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return cursor.fetchone()

    def get_by_course_id(self, course_id: int):
        """
        Fetches all assignments belonging to a specific course.
        """
        sql = "SELECT * FROM assignments WHERE course_id = ?"
        with get_db_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            return cursor.fetchall()

    def update(self, id: int, title: str, description: str, type: str, due_date: str, max_score: int):
        """
        Updates an existing assignment's details.
        """
        sql = """
        UPDATE assignments 
        SET title = ?, description = ?, type = ?, due_date = ?, max_score = ?
        WHERE id = ?
        """
        with get_db_connection() as conn:
            conn.execute(sql, (title, description, type, due_date, max_score, id))

    def delete(self, id: int):
        """
        Hard deletes an assignment by ID.
        """
        sql = "DELETE FROM assignments WHERE id = ?"
        with get_db_connection() as conn:
            conn.execute(sql, (id,))
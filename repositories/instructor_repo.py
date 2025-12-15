from .base_repo import BaseRepository
from ..models.instructor import Instructor 

class InstructorRepository(BaseRepository):
    
    def __init__(self):
        super().__init__()
        self.table_name = 'instructors'

    def create(self, user_id: int, department: str) -> int:
        """Inserts a new instructor profile record, returning the new profile ID."""
        query = f"""
            INSERT INTO {self.table_name} 
            (user_id, department) 
            VALUES (?, ?)
        """
        params = (user_id, department)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid 

    def get_full_profile(self, user_id: int) -> Instructor:
        """
        Fetches the complete Instructor object by joining the users and instructors tables.
        """
        query = f"""
            SELECT 
                u.id, u.username, u.name, u.email, u.gender, u.password, u.role,
                i.id AS instructor_profile_id, i.user_id, i.department
            FROM users u
            INNER JOIN {self.table_name} i ON u.id = i.user_id
            WHERE u.id = ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            return Instructor.from_row(row)

    def update(self, user_id: int, updates: dict) -> int:
        """Updates specific fields for an instructor profile record, using the user_id FK."""
        if not updates:
            return 0
        
        set_clauses = [f"{key} = ?" for key in updates.keys()]
        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE user_id = ?"
        params = list(updates.values()) + [user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def delete(self, user_id: int) -> int:
        """Deletes the instructor profile record (not the base user record)."""
        query = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            return cursor.rowcount

    def get_all(self) -> list[Instructor]:
        """Fetches all Instructor objects."""
        query = f"""
            SELECT 
                u.id, u.username, u.name, u.email, u.gender, u.password, u.role,
                i.id AS instructor_profile_id, i.user_id, i.department
            FROM users u
            INNER JOIN {self.table_name} i ON u.id = i.user_id
            WHERE u.role = 'instructor'
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [Instructor.from_row(row) for row in rows]
from core.base_repository import BaseRepository
from models.instructor import Instructor 

class InstructorRepository(BaseRepository):
    
    """
    Handles interactions for Instructors. 
    Manages the complexities of the 'users' AND 'instructors' tables.
    """

    def create(self, item: Instructor) -> Instructor:
        """
        Saves the Instructor atomically.
        1. Inserts into 'users'.
        2. Gets the new user_id.
        3. Inserts into 'instructors' using that ID.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql_user = """
        INSERT INTO users (username, name, email, gender, password, role) 
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql_instructor = """
        INSERT INTO instructors (user_id, department) 
        VALUES (%s, %s)
        RETURNING id
        """
        
        # User Data
        user_values = (item.username, item.name, item.email, item.gender, item.password_hash, item.role)
        
        with self.get_connection() as conn:
            cur = conn.cursor() # CHANGED
            
            # 1. Save User Part
            cur.execute(sql_user, user_values)
            new_user_id = cur.fetchone()[0] # CHANGED: Fetch returned ID
            
            # Update Object with ID
            item.id = new_user_id
            item.user_id_fk = new_user_id
            
            # 2. Save Instructor Part
            cur.execute(sql_instructor, (new_user_id, item.department))
            item.instructor_profile_id = cur.fetchone()[0] # CHANGED: Fetch returned ID
            
            return item

    def update(self, item: Instructor):
        """
        Updates BOTH the User details and Instructor details.
        """
        # CHANGED: ? -> %s
        sql_user = """
        UPDATE users SET username=%s, name=%s, email=%s, gender=%s, role=%s WHERE id=%s
        """
        # CHANGED: ? -> %s
        sql_instructor = """
        UPDATE instructors SET department=%s WHERE user_id=%s
        """
        
        user_values = (item.username, item.name, item.email, item.gender, item.role, item.id)
        instructor_values = (item.department, item.id)
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql_user, user_values)
            cur.execute(sql_instructor, instructor_values)

    def get_all(self):
        # We JOIN to get the full object
        sql = """
            SELECT u.*, i.user_id, i.id as instructor_profile_id, i.department 
            FROM users u
            JOIN instructors i ON u.id = i.user_id
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Instructor.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id: int):
        # CHANGED: ? -> %s
        sql = """
            SELECT u.*, i.user_id, i.id as instructor_profile_id, i.department 
            FROM users u
            JOIN instructors i ON u.id = i.user_id
            WHERE u.id = %s
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            return Instructor.from_row(row) if row else None
            
    def delete(self, id: int):
        # If DB has CASCADE DELETE, deleting User deletes Instructor.
        # Otherwise, delete Instructor first, then User.
        # CHANGED: ? -> %s
        sql = "DELETE FROM users WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
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
        sql_user = """
        INSERT INTO users (username, name, email, gender, password, role) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        sql_instructor = """
        INSERT INTO instructors (user_id, department) 
        VALUES (?, ?)
        """
        
        # User Data
        user_values = (item.username, item.name, item.email, item.gender, item.password_hash, item.role)
        
        with self.get_connection() as conn:
            # 1. Save User Part
            cursor = conn.execute(sql_user, user_values)
            new_user_id = cursor.lastrowid
            
            # Update Object with ID
            item.id = new_user_id
            item.user_id_fk = new_user_id
            
            # 2. Save Instructor Part
            cursor_inst= conn.execute(sql_instructor, (new_user_id, item.department))

            item.instructor_profile_id = cursor_inst.lastrowid
            
           
            return item

    def update(self, item: Instructor):
        """
        Updates BOTH the User details and Instructor details.
        """
        sql_user = """
        UPDATE users SET username=?, name=?, email=?, gender=?, role=? WHERE id=?
        """
        sql_instructor = """
        UPDATE instructors SET department=? WHERE user_id=?
        """
        
        user_values = (item.username, item.name, item.email, item.gender, item.role, item.id)
        instructor_values = (item.department, item.id)
        
        with self.get_connection() as conn:
            conn.execute(sql_user, user_values)
            conn.execute(sql_instructor, instructor_values)

    def get_all(self):
        # We JOIN to get the full object
        sql = """
            SELECT u.*, i.user_id, i.id as instructor_profile_id, i.department 
            FROM users u
            JOIN instructors i ON u.id = i.user_id
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Instructor.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id: int):
        sql = """
            SELECT u.*, i.user_id, i.id as instructor_profile_id, i.department 
            FROM users u
            JOIN instructors i ON u.id = i.user_id
            WHERE u.id = ?
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return Instructor.from_row(cursor.fetchone())
            
    def delete(self, id: int):
        # If DB has CASCADE DELETE, deleting User deletes Instructor.
        # Otherwise, delete Instructor first, then User.
        # Assuming CASCADE is ON or we delete parent:
        sql = "DELETE FROM users WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
from core.base_repository import BaseRepository
from ..models.user import User 

class UserRepository(BaseRepository):
    
    def __init__(self):
        super().__init__()
        self.table_name = 'users'

    def create(self, username, name, email, gender, password_hash, role):
        query = f"""
            INSERT INTO {self.table_name} 
            (username, name, email, gender, password, role) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (username, name, email, gender, password_hash, role)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid 

    def get_by_username(self, username):
        query = f"SELECT id, username, name, email, gender, password, role FROM {self.table_name} WHERE username = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            return cursor.fetchone()

    def get_by_email(self, email):
        query = f"SELECT id, username, name, email, gender, password, role FROM {self.table_name} WHERE email = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            return cursor.fetchone()

    def get_by_id(self, user_id):
        query = f"SELECT id, username, name, email, gender, password, role FROM {self.table_name} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return User.from_row(row)

    def update(self, user_id, updates):
        if not updates:
            return 0
        
        set_clauses = [f"{key} = ?" for key in updates.keys()]
        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE id = ?"
        params = list(updates.values()) + [user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def update_password(self, user_id, password_hash):
        query = f"UPDATE {self.table_name} SET password = ? WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (password_hash, user_id))
            return cursor.rowcount

    def delete(self, user_id):
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            return cursor.rowcount

    def get_all(self):
        query = f"SELECT id, username, name, email, gender, password, role FROM {self.table_name}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [User.from_row(row) for row in rows]
from core.base_repository import BaseRepository
from models.user import User 

class UserRepository(BaseRepository):
    
    def __init__(self):
        super().__init__()
        self.table_name = 'users'

    def create(self, item: User) -> User:
        sql = """
            INSERT INTO {self.table_name} 
            (username, name, email, gender, password, role) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (item.username, item.name, item.email, item.gender, item.password_hash, item.role)
        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid 
            return item

    def get_by_username(self, username: str) -> User:
        sql = "SELECT * FROM users WHERE username = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (username,))
            return User.from_row(cursor.fetchone())

    def get_by_email(self, email):
        sql = "SELECT * FROM users WHERE email = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor = conn.execute(sql, (email,))
            return User.from_row(cursor.fetchone())

    def get_by_id(self, user_id):
        sql = "SELECT * FROM users WHERE id = ?"        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            return User.from_row(cursor.fetchone())

    def update(self, item: User):
        
        sql = """
        UPDATE users 
        SET username = ?, name = ?, email = ?, gender = ?, role = ?
        WHERE id = ?
        """
        values = (item.username, item.name, item.email, item.gender, item.role, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def update_password(self, user_id, new_password_hash):
       
        sql = "UPDATE users SET password = ? WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (new_password_hash, user_id))

    def delete(self, id: int):
        sql = "DELETE FROM users WHERE id = ?"
        
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

    def get_all(self):
        sql = "SELECT * FROM users"        
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [User.from_row(row) for row in cursor.fetchall()]
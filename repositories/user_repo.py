from core.base_repository import BaseRepository
from models.user import User 

class UserRepository(BaseRepository):
    
    def __init__(self):
        super().__init__()
        self.table_name = 'users'

    def create(self, item: User) -> User:
        # CHANGED: ? -> %s and added RETURNING id
        sql = f"""
            INSERT INTO {self.table_name} 
            (username, name, email, gender, password, role) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = (item.username, item.name, item.email, item.gender, item.password_hash, item.role)
        
        with self.get_connection() as conn:
            cur = conn.cursor()          # CHANGED
            cur.execute(sql, values)     # CHANGED
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item

    def get_by_username(self, username: str) -> User:
        # CHANGED: ? -> %s
        sql = "SELECT * FROM users WHERE username = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (username,))
            row = cur.fetchone()
            return User.from_row(row) if row else None

    def get_by_email(self, email):
        # CHANGED: ? -> %s
        sql = "SELECT * FROM users WHERE email = %s"
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (email,))
            row = cur.fetchone()
            return User.from_row(row) if row else None

    def get_by_id(self, user_id):
        # CHANGED: ? -> %s
        sql = "SELECT * FROM users WHERE id = %s"        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            row = cur.fetchone()
            return User.from_row(row) if row else None

    def update(self, item: User):
        # CHANGED: ? -> %s
        sql = """
        UPDATE users 
        SET username = %s, name = %s, email = %s, gender = %s, role = %s
        WHERE id = %s
        """
        values = (item.username, item.name, item.email, item.gender, item.role, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def update_password(self, user_id, new_password_hash):
        # CHANGED: ? -> %s
        sql = "UPDATE users SET password = %s WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (new_password_hash, user_id))

    def delete(self, id: int):
        # CHANGED: ? -> %s
        sql = "DELETE FROM users WHERE id = %s"
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))

    def get_all(self):
        sql = "SELECT * FROM users"        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [User.from_row(row) for row in cur.fetchall()]
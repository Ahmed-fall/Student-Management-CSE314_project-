from core.base_repository import BaseRepository
from models.announcement import Announcement


class AnnouncementRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'announcements' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    - Data Safety: Returns strict 'Announcement' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, item: Announcement) -> Announcement:
        """
        Inserts a new announcement into the database.
        """

        sql = """
        INSERT INTO announcements (course_id, title, message, created_at)
        VALUES (?, ?, ?, ?)
        """
        values = (item.course_id, item.title, item.message, item.created_at)
        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid
            return item

    def get_all(self):
        """
        Fetches all announcements.
        """
        sql = "SELECT * FROM announcements"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Announcement.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id):
        """
        Fetches a single announcement by unique ID.
        """
        sql = "SELECT * FROM announcements WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            row = cursor.fetchone()
            if row:
                return Announcement.from_row(row)
            return None

    def get_by_course_id(self, course_id):
        """
        Fetches all announcements belonging to a specific course.
        """
        sql = "SELECT * FROM announcements WHERE course_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            return [Announcement.from_row(row) for row in cursor.fetchall()]

    def get_global(self):
        """
        Fetches all global announcements (course_id is NULL).
        """
        sql = "SELECT * FROM announcements WHERE course_id IS NULL"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Announcement.from_row(row) for row in cursor.fetchall()]

    def update(self, item: Announcement):
        """
        Updates an existing announcement's details.
        """
        
        sql = """
        UPDATE announcements 
        SET course_id = ?, title = ?, message = ?
        WHERE id = ?
        """
        values = (item.course_id, item.title, item.message, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id):
        """
        Hard deletes an announcement by ID.
        """
        sql = "DELETE FROM announcements WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

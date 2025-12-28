from core.base_repository import BaseRepository
from models.announcement import Announcement


class AnnouncementRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'announcements' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    - Data Safety: Returns strict 'Announcement' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (%s) to prevent SQL Injection.
    """

    def create(self, item: Announcement) -> Announcement:
        """
        Inserts a new announcement into the database.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql = """
        INSERT INTO announcements (course_id, title, message, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        values = (item.course_id, item.title, item.message, item.created_at)
        with self.get_connection() as conn:
            cur = conn.cursor()       # CHANGED: Create cursor
            cur.execute(sql, values)  # CHANGED: Execute on cursor
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item

    def get_all(self):
        """
        Fetches all announcements.
        """
        sql = "SELECT * FROM announcements"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Announcement.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id):
        """
        Fetches a single announcement by unique ID.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM announcements WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            if row:
                return Announcement.from_row(row)
            return None

    def get_by_course_id(self, course_id):
        """
        Fetches all announcements belonging to a specific course.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM announcements WHERE course_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (course_id,))
            return [Announcement.from_row(row) for row in cur.fetchall()]

    def get_global(self):
        """
        Fetches all global announcements (course_id is NULL).
        """
        sql = "SELECT * FROM announcements WHERE course_id IS NULL"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Announcement.from_row(row) for row in cur.fetchall()]

    def update(self, item: Announcement):
        """
        Updates an existing announcement's details.
        """
        # CHANGED: ? -> %s
        sql = """
        UPDATE announcements 
        SET course_id = %s, title = %s, message = %s
        WHERE id = %s
        """
        values = (item.course_id, item.title, item.message, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id):
        """
        Hard deletes an announcement by ID.
        """
        # CHANGED: ? -> %s
        sql = "DELETE FROM announcements WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
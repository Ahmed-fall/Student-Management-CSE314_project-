# repositories/announcement_repo.py

from core.base_repository import BaseRepository
from models.announcement import Announcement
from datetime import datetime

class AnnouncementRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'announcements' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    - Data Safety: Returns strict 'Announcement' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, course_id, title, message, created_at=None):
        """
        Inserts a new announcement into the database.
        """
        created_at = created_at or datetime.now().isoformat()
        sql = """
        INSERT INTO announcements (course_id, title, message, created_at)
        VALUES (?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id, title, message, created_at))
            announcement_id = cursor.lastrowid
            return Announcement(
                id=announcement_id,
                course_id=course_id,
                title=title,
                message=message,
                created_at=created_at
            )

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

    def update(self, id, course_id, title, message, created_at=None):
        """
        Updates an existing announcement's details.
        """
        created_at = created_at or datetime.now().isoformat()
        sql = """
        UPDATE announcements 
        SET course_id = ?, title = ?, message = ?, created_at = ?
        WHERE id = ?
        """
        with self.get_connection() as conn:
            conn.execute(sql, (course_id, title, message, created_at, id))

    def delete(self, id):
        """
        Hard deletes an announcement by ID.
        """
        sql = "DELETE FROM announcements WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

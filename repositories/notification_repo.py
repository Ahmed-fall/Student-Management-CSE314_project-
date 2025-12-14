# repositories/notification_repo.py

from core.base_repository import BaseRepository
from models.notification import Notification
from datetime import datetime

class NotificationRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'notifications' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    - Data Safety: Returns strict 'Notification' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, user_id, announcement_id, read_flag=0, sent_at=None):
        """
        Inserts a new notification into the database.
        """
        sent_at = sent_at or datetime.now().isoformat()
        sql = """
        INSERT INTO notifications (user_id, announcement_id, read_flag, sent_at)
        VALUES (?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (user_id, announcement_id, read_flag, sent_at))
            notification_id = cursor.lastrowid
            return Notification(
                id=notification_id,
                user_id=user_id,
                announcement_id=announcement_id,
                read_flag=read_flag,
                sent_at=sent_at
            )

    def get_all(self):
        """
        Fetches all notifications.
        """
        sql = "SELECT * FROM notifications"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return [Notification.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, id):
        """
        Fetches a single notification by unique ID.
        """
        sql = "SELECT * FROM notifications WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (id,))
            row = cursor.fetchone()
            if row:
                return Notification.from_row(row)
            return None

    def get_by_user_id(self, user_id):
        """
        Fetches all notifications for a specific user.
        """
        sql = "SELECT * FROM notifications WHERE user_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (user_id,))
            return [Notification.from_row(row) for row in cursor.fetchall()]

    def get_by_announcement_id(self, announcement_id):
        """
        Fetches all notifications related to a specific announcement.
        """
        sql = "SELECT * FROM notifications WHERE announcement_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (announcement_id,))
            return [Notification.from_row(row) for row in cursor.fetchall()]

    def update(self, id, read_flag=None, sent_at=None):
        """
        Updates an existing notification's read_flag or sent_at.
        """
        sql = "UPDATE notifications SET read_flag = ?, sent_at = ? WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (read_flag, sent_at, id))

    def delete(self, id):
        """
        Hard deletes a notification by ID.
        """
        sql = "DELETE FROM notifications WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))

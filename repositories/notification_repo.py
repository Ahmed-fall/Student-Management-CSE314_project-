from typing import List
from core.base_repository import BaseRepository
from models.notification import Notification

class NotificationRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'notifications' table.
    
    Implementation details:
    - Connection Safety: Uses 'with self.get_connection() as conn:' for automatic cleanup.
    - Data Safety: Returns strict 'Notification' objects via 'from_row', not raw tuples.
    - Security: Uses parameterized queries (?) to prevent SQL Injection.
    """

    def create(self, item: Notification) -> Notification:
        """
        Inserts a new notification into the database.
        """
        
        sql = """
        INSERT INTO notifications (user_id, announcement_id, read_flag, sent_at)
        VALUES (?, ?, ?, ?)
        """
        values = (item.user_id, item.announcement_id, item.read_flag, item.sent_at)
        with self.get_connection() as conn:
            cursor = conn.execute(sql, values)
            item.id = cursor.lastrowid
            return item

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

    def update(self, item: Notification):
        """
        Updates an existing notification's read_flag
        """
        sql = "UPDATE notifications SET read_flag = ? WHERE id = ?"
        values = (item.read_flag, item.id)
        with self.get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id):
        """
        Hard deletes a notification by ID.
        """
        sql = "DELETE FROM notifications WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (id,))
    
    def create_many(self, items: List[Notification]):
        """
        OPTIMIZATION: Inserts multiple notifications in one transaction.
        Prevents opening 50 separate database connections for one announcement.
        """
        sql = """
        INSERT INTO notifications (user_id, announcement_id, read_flag, sent_at)
        VALUES (?, ?, ?, ?)
        """
        # Convert list of Objects to list of Tuples for SQLite
        values_list = [
            (item.user_id, item.announcement_id, item.read_flag, item.sent_at) 
            for item in items
        ]
        
        with self.get_connection() as conn:
            conn.executemany(sql, values_list)

    def count_unread(self, user_id: int) -> int:
        """Fast SQL count for the UI badge."""
        sql = "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND read_flag = 0"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (user_id,))
            return cursor.fetchone()[0]

    def delete_by_announcement(self, announcement_id: int):
        """Cleanup: When an announcement is deleted, clear its notifications."""
        sql = "DELETE FROM notifications WHERE announcement_id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (announcement_id,))

    def get_dashboard_notifications(self, user_id: int):
        """
        Complex Query: Joins Notifications with Announcements.
        Returns a dictionary for the UI, not a Model object.
        """
        sql = """
        SELECT 
            n.id as notification_id, 
            n.read_flag, 
            n.sent_at,
            a.id as announcement_id,
            a.title, 
            a.message, 
            a.course_id
        FROM notifications n
        JOIN announcements a ON n.announcement_id = a.id
        WHERE n.user_id = ?
        ORDER BY n.sent_at DESC
        """
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_old_read(self, cutoff_date: str):
        """System Cleanup job."""
        sql = "DELETE FROM notifications WHERE sent_at < ? AND read_flag = 1"
        with self.get_connection() as conn:
            conn.execute(sql, (cutoff_date,))
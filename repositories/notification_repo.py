from typing import List
from core.base_repository import BaseRepository
from models.notification import Notification

class NotificationRepository(BaseRepository):
    """
    Handles strict Database interactions for the 'notifications' table.
    """

    def create(self, item: Notification) -> Notification:
        """
        Inserts a new notification into the database.
        """
        # CHANGED: ? -> %s and added RETURNING id
        sql = """
        INSERT INTO notifications (user_id, announcement_id, read_flag, sent_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        values = (item.user_id, item.announcement_id, item.read_flag, item.sent_at)
        with self.get_connection() as conn:
            cur = conn.cursor()          # CHANGED
            cur.execute(sql, values)     # CHANGED
            item.id = cur.fetchone()[0]  # CHANGED: Fetch returned ID
            return item

    def get_all(self):
        """
        Fetches all notifications.
        """
        sql = "SELECT * FROM notifications"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return [Notification.from_row(row) for row in cur.fetchall()]

    def get_by_id(self, id):
        """
        Fetches a single notification by unique ID.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM notifications WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
            row = cur.fetchone()
            if row:
                return Notification.from_row(row)
            return None

    def get_by_user_id(self, user_id):
        """
        Fetches all notifications for a specific user.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM notifications WHERE user_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            return [Notification.from_row(row) for row in cur.fetchall()]

    def get_by_announcement_id(self, announcement_id):
        """
        Fetches all notifications related to a specific announcement.
        """
        # CHANGED: ? -> %s
        sql = "SELECT * FROM notifications WHERE announcement_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (announcement_id,))
            return [Notification.from_row(row) for row in cur.fetchall()]

    def update(self, item: Notification):
        """
        Updates an existing notification's read_flag
        """
        # CHANGED: ? -> %s
        sql = "UPDATE notifications SET read_flag = %s WHERE id = %s"
        values = (item.read_flag, item.id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, values)

    def delete(self, id):
        """
        Hard deletes a notification by ID.
        """
        # CHANGED: ? -> %s
        sql = "DELETE FROM notifications WHERE id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (id,))
    
    def create_many(self, items: List[Notification]):
        """
        OPTIMIZATION: Inserts multiple notifications in one transaction.
        """
        # CHANGED: ? -> %s
        sql = """
        INSERT INTO notifications (user_id, announcement_id, read_flag, sent_at)
        VALUES (%s, %s, %s, %s)
        """
        # Convert list of Objects to list of Tuples
        values_list = [
            (item.user_id, item.announcement_id, item.read_flag, item.sent_at) 
            for item in items
        ]
        
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.executemany(sql, values_list) # psycopg2 supports executemany

    def count_unread(self, user_id: int) -> int:
        """Fast SQL count for the UI badge."""
        # CHANGED: ? -> %s
        sql = "SELECT COUNT(*) FROM notifications WHERE user_id = %s AND read_flag = 0"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            return cur.fetchone()[0]

    def delete_by_announcement(self, announcement_id: int):
        """Cleanup: When an announcement is deleted, clear its notifications."""
        # CHANGED: ? -> %s
        sql = "DELETE FROM notifications WHERE announcement_id = %s"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (announcement_id,))

    def get_dashboard_notifications(self, user_id: int):
        """
        Complex Query: Joins Notifications with Announcements.
        Returns a dictionary for the UI, not a Model object.
        """
        # CHANGED: ? -> %s
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
        WHERE n.user_id = %s
        ORDER BY n.sent_at DESC
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()
            
            # Manual dictionary mapping because psycopg2 rows are tuples
            results = []
            for row in rows:
                results.append({
                    "notification_id": row[0],
                    "read_flag": row[1],
                    "sent_at": row[2],
                    "announcement_id": row[3],
                    "title": row[4],
                    "message": row[5],
                    "course_id": row[6]
                })
            return results
    
    def delete_old_read(self, cutoff_date: str):
        """System Cleanup job."""
        # CHANGED: ? -> %s
        sql = "DELETE FROM notifications WHERE sent_at < %s AND read_flag = 1"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (cutoff_date,))
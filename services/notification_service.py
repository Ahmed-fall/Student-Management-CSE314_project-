from typing import Optional
from datetime import datetime, timedelta
from core.base_service import BaseService
from models.notification import Notification

# Repositories
from repositories.notification_repo import NotificationRepository
from repositories.enrollment_repo import EnrollmentRepository
from repositories.course_repo import CourseRepository

class NotificationService(BaseService):
    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.course_repo = CourseRepository()

    def notify_course(self, course_id: int, related_id: int):
        """
        Bulk creates notifications for all ACTIVE students in a course.
        """
        try:
            # 1. Get Active User IDs (FIXED)
            # We now fetch the actual User IDs, not student profile IDs
            user_ids = self.enrollment_repo.get_enrolled_user_ids(course_id)

            if not user_ids:
                return # No one to notify

            # 2. Prepare Batch Data
            notifications_to_send = []
            now = datetime.now().isoformat()
            
            for uid in user_ids:
                notifications_to_send.append(Notification(
                    id=None,
                    user_id=uid, # Correct User ID
                    announcement_id=related_id,
                    read_flag=0,
                    sent_at=now
                ))

            # 3. Optimized Batch Insert
            self.notification_repo.create_many(notifications_to_send)
            
        except Exception as e:
            self.handle_db_error(e)

    def mark_as_read(self, user_id: int, notification_id: int):
        """Marks a notification as read safely."""
        try:
            notification = self.notification_repo.get_by_id(notification_id)
            if not notification:
                raise ValueError("Notification not found.")
            
            if notification.user_id != user_id:
                raise PermissionError("Access denied.")

            notification.read_flag = 1
            self.notification_repo.update(notification)
            return True
        except Exception as e:
            self.handle_db_error(e)

    def get_unread_count(self, user_id: int) -> int:
        """Returns the number of unread alerts."""
        try:
            return self.notification_repo.count_unread(user_id)
        except Exception as e:
            self.handle_db_error(e)
    
    def get_dashboard_notifications(self, user_id: int):
        """
        Pass-through for the complex dashboard query.
        Returns raw dictionaries (not Objects) for UI rendering.
        """
        try:
            return self.notification_repo.get_dashboard_notifications(user_id)
        except Exception as e:
            self.handle_db_error(e)
            return []
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
            # 1. Get Active Students
            # Ensure your EnrollmentRepo has 'get_by_course_id'
            enrollments = self.enrollment_repo.get_by_course_id(course_id)
            active_enrollments = [e for e in enrollments if e.status == 'enrolled']

            if not active_enrollments:
                return # No one to notify

            # 2. Prepare Batch Data
            notifications_to_send = []
            now = datetime.now().isoformat()
            
            for enrollment in active_enrollments:
                notifications_to_send.append(Notification(
                    id=None,
                    user_id=enrollment.student_id,
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
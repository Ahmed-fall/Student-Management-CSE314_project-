from datetime import datetime
from core.base_service import BaseService
from models.announcement import Announcement

# Import the new Service
from services.notification_service import NotificationService

# Repos
from repositories.announcement_repo import AnnouncementRepository
from repositories.course_repo import CourseRepository
from repositories.notification_repo import NotificationRepository # Still needed for the Feed view

class AnnouncementService(BaseService):
    def __init__(self):
        self.announcement_repo = AnnouncementRepository()
        self.course_repo = CourseRepository()
        self.notification_repo = NotificationRepository()
        
        # Inject Notification Service
        self.notification_service = NotificationService()

    def create_announcement(self, instructor_id: int, course_id: int, title: str, message: str):
        try:
            # 1. Validation
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")
            
            self.check_permission(course.instructor_id, instructor_id)

            if not title or not message:
                raise ValueError("Title/Message cannot be empty.")

            # 2. Create Announcement
            announcement = Announcement(
                id=None,
                course_id=course_id,
                title=title,
                message=message,
                created_at=datetime.now().isoformat()
            )
            saved_announcement = self.announcement_repo.create(announcement)

            # 3. DELEGATE: Trigger Bulk Notification via Service
            self.notification_service.notify_course(
                course_id=course_id,
                related_id=saved_announcement.id
            )

            return saved_announcement

        except Exception as e:
            self.handle_db_error(e)

    def get_student_announcements(self, student_id: int):
        """
        The Feed: Shows the message (Announcement) merged with the status (Notification)
        """
        try:
            # Uses the OPTIMIZED join method from the repo
            return self.notification_repo.get_dashboard_notifications(student_id)
        except Exception as e:
            self.handle_db_error(e)

    # ... Include get_course_announcements, update, delete as before ...
    # (I can provide the full file if you need the standard methods repeated)
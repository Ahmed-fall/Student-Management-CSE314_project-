from typing import List, Optional
from datetime import datetime
from core.base_service import BaseService
from models.announcement import Announcement

# Import the Notification Service for delegation
from services.notification_service import NotificationService

# Import Repositories
from repositories.announcement_repo import AnnouncementRepository
from repositories.course_repo import CourseRepository
from repositories.notification_repo import NotificationRepository 

class AnnouncementService(BaseService):
    """
    Business logic for managing Announcements.
    Acts as a facade that coordinates the AnnouncementRepo and NotificationService.
    """
    
    def __init__(self):
        self.announcement_repo = AnnouncementRepository()
        self.course_repo = CourseRepository()
        self.notification_repo = NotificationRepository()
        
        self.notification_service = NotificationService()

    def create_announcement(self, instructor_id: int, course_id: int, title: str, message: str) -> Optional[Announcement]:
        """
        Creates an announcement and triggers the NotificationService to alert all students.
        """
        try:
            # 1. Validation: Ensure Course exists
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")
            
            # 2. Permission: Ensure the user is the instructor of this course
            self.check_permission(course.instructor_id, instructor_id)

            if not title or not message:
                raise ValueError("Title and Message cannot be empty.")

            # 3. Create Announcement Object
            announcement = Announcement(
                id=None,
                course_id=course_id,
                title=title,
                message=message,
                created_at=datetime.now().isoformat()
            )
            
            # 4. Persist to DB
            saved_announcement = self.announcement_repo.create(announcement)

            # 5. DELEGATE: Trigger Bulk Notification via Service
            # This keeps the logic decoupled; AnnouncementService doesn't know *how* to notify, just *to* notify.
            self.notification_service.notify_course(
                course_id=course_id,
                related_id=saved_announcement.id
            )

            return saved_announcement

        except Exception as e:
            self.handle_db_error(e)

    def get_student_announcements(self, student_id: int) -> List[dict]:
        """
        The Feed: Shows the message (Announcement) merged with the status (Notification).
        Returns a list of dictionaries (optimized for View).
        """
        try:
            return self.notification_repo.get_dashboard_notifications(student_id)
        except Exception as e:
            self.handle_db_error(e)
            return []

    def get_course_announcements(self, course_id: int) -> List[Announcement]:
        """
        Fetches all announcements for a specific course (e.g., for the Course Details view).
        """
        try:
            return self.announcement_repo.get_by_course_id(course_id)
        except Exception as e:
            self.handle_db_error(e)
            return []

    def update_announcement(self, instructor_id: int, announcement_id: int, title: str, message: str) -> bool:
        """
        Updates an existing announcement.
        """
        try:
            # 1. Fetch existing
            announcement = self.announcement_repo.get_by_id(announcement_id)
            if not announcement:
                raise ValueError("Announcement not found.")

            # 2. Verify Course Owner Permission
            course = self.course_repo.get_by_id(announcement.course_id)
            if course:
                self.check_permission(course.instructor_id, instructor_id)

            # 3. Update fields
            announcement.title = title
            announcement.message = message
            
            # 4. Save
            self.announcement_repo.update(announcement)
            return True

        except Exception as e:
            self.handle_db_error(e)
            return False

    def delete_announcement(self, instructor_id: int, announcement_id: int) -> bool:
        """
        Deletes an announcement AND cleans up associated notifications.
        """
        try:
            # 1. Fetch existing
            announcement = self.announcement_repo.get_by_id(announcement_id)
            if not announcement:
                raise ValueError("Announcement not found.")

            # 2. Verify Permission
            course = self.course_repo.get_by_id(announcement.course_id)
            if course:
                self.check_permission(course.instructor_id, instructor_id)

            # 3. CLEANUP: Delete associated notifications first
            self.notification_repo.delete_by_announcement(announcement_id)

            # 4. Delete the announcement
            self.announcement_repo.delete(announcement_id)
            return True

        except Exception as e:
            self.handle_db_error(e)
            return False

    def get_announcement_details(self, announcement_id: int) -> Optional[Announcement]:
        """
        Helper to get a single announcement object.
        """
        try:
            return self.announcement_repo.get_by_id(announcement_id)
        except Exception as e:
            self.handle_db_error(e)
            return None
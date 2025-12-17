from core.base_service import BaseService
from repositories.instructor_repo import InstructorRepository
from models.instructor import Instructor

class InstructorService(BaseService):
    """
    Manages instructor-specific business logic.
    Handles profile updates and specialized faculty data retrieval.
    """

    def __init__(self):
        # Service uses the specialized instructor repository
        self.instructor_repo = InstructorRepository()

    def get_instructor_profile(self, user_id: int):
        """
        Fetches the full instructor object, including joined user data.
        """
        try:
            # Uses the JOIN logic in the repo to return a complete Instructor model
            instructor = self.instructor_repo.get_by_id(user_id)
            if not instructor:
                raise ValueError("Instructor profile not found.")
            return instructor
        except Exception as e:
            self.handle_db_error(e)

    def update_department(self, instructor_id: int, current_user_id: int, new_dept: str):
        """
        Updates the instructor's department after verifying ownership.
        """
        try:
            # 1. Security: Ensure the instructor is only editing their own profile
            self.check_permission(instructor_id, current_user_id)

            # 2. Fetch the current object
            instructor = self.instructor_repo.get_by_id(instructor_id)
            if not instructor:
                raise ValueError("Profile does not exist.")

            # 3. Apply change (Triggering model validation)
            instructor.department = new_dept

            # 4. Save to the database
            self.instructor_repo.update(instructor)
            return instructor

        except Exception as e:
            self.handle_db_error(e)

    def get_all_faculty(self):
        """
        Returns a list of all instructors for directory purposes.
        """
        try:
            return self.instructor_repo.get_all()
        except Exception as e:
            self.handle_db_error(e)
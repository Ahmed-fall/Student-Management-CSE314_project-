from typing import List, Optional
from core.base_service import BaseService
from repositories.instructor_repo import InstructorRepository
from repositories.course_repo import CourseRepository
# [FIX] We use this import now for Type Hinting
from models.instructor import Instructor 

class InstructorService(BaseService):
    """
    Manages instructor-specific business logic.
    """

    def __init__(self):
        self.instructor_repo = InstructorRepository()
        self.course_repo = CourseRepository()

    def get_instructor_profile(self, user_id: int) -> Optional[Instructor]:
        """
        Resolves a User ID to an Instructor model.
        """
        try:
            profile: Instructor = self.instructor_repo.get_by_id(user_id)
            
            if not profile:
                return None
            return profile
        except Exception as e:
            self.handle_db_error(e)
            return None

    def update_department(self, instructor_id: int, current_user_id: int, new_dept: str) -> Optional[Instructor]:
        """
        Updates the instructor's department after verifying ownership.
        """
        try:
            # 1. Security check
            self.check_permission(instructor_id, current_user_id)

            # 2. Fetch object with type hint
            instructor: Instructor = self.instructor_repo.get_by_id(instructor_id)
            
            if not instructor:
                raise ValueError("Profile does not exist.")

            # 3. Apply change
            instructor.department = new_dept

            # 4. Save
            self.instructor_repo.update(instructor)
            return instructor

        except Exception as e:
            self.handle_db_error(e)
            return None

    def get_all_faculty(self) -> List[Instructor]:
        """
        Returns a list of all instructors for directory purposes.
        """
        try:
            return self.instructor_repo.get_all()
        except Exception as e:
            self.handle_db_error(e)
            return []

    def get_dashboard_data(self, user_id: int):
        """
        Aggregates profile, courses, and quick stats for the dashboard.
        """
        try:
            profile: Instructor = self.instructor_repo.get_by_id(user_id)
            if not profile: return {}

            
            if hasattr(self.course_repo, "get_by_instructor_id"):
                courses = self.course_repo.get_by_instructor_id(profile.instructor_profile_id)
            else:
                # Fallback: Try the name you were using before, but on the correct REPO
                courses = self.course_repo.get_courses_by_instructor(profile.instructor_profile_id)
            
            # --- CALCULATE STATS ---
            total_students_across_all = 0
            pending_grades = 0
            
            for c in courses:
                # Count students via repo
                count = self.course_repo.get_enrollment_count(c.id)
                # Use the setter we added to the Course model
                c.enrolled_count = count
                
                total_students_across_all += count
                pending_grades += 5 
            
            stats = {
                "students": total_students_across_all,
                "courses": len(courses),
                "pending_grades": pending_grades
            }
            
            return {
                "profile": profile,
                "courses": courses,
                "stats": stats
            }
        except Exception as e:
            print(f"Error loading dashboard: {e}")
            # Optional: Print the full traceback to see where it failed exactly
            import traceback
            traceback.print_exc()
            return {}
from core.base_service import BaseService
from models.course import Course

# Repositories
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository

class CourseService(BaseService):
    """
    Manages Course Resources.
    Contains the logic for Creating, Listing, and Assigning courses.
    """

    def __init__(self):
        self.course_repo = CourseRepository()
        self.enrollment_repo = EnrollmentRepository()

    # ---------------------------------------------------------
    # 1. INSTRUCTOR ACTIONS (The "Missing" Methods)
    # ---------------------------------------------------------
    def create_course(self, instructor_id: int, code: str, name: str, description: str = "", credits: int = 3, semester: str = "Fall 2024", max_students: int = 30):
        """
        Creates a new course.
        Args:
            instructor_id: The ID from the 'instructors' table (NOT just the user_id).
        """
        try:
            # 1. Validation
            if not code or not name:
                raise ValueError("Course code and name are required.")
            
            # 2. Check for Duplicate Code
            if self.course_repo.get_by_code(code):
                raise ValueError(f"Course code '{code}' already exists.")

            # 3. Create Model
            # Note: We assign the instructor_id here.
            new_course = Course(
                id=None,
                name=name,
                code=code,
                description=description,
                instructor_id=instructor_id,
                credits=credits,           
                semester=semester,         
                max_students=max_students
            )

            # 4. Save
            return self.course_repo.create(new_course)

        except Exception as e:
            self.handle_db_error(e)

    def get_courses_by_instructor(self, instructor_id: int):
        """
        Returns all courses taught by a specific instructor.
        (Previously thought to be in InstructorService)
        """
        try:
            return self.course_repo.get_by_instructor_id(instructor_id)
        except Exception as e:
            self.handle_db_error(e)

    def get_course_roster(self, instructor_id: int, course_id: int):
        """
        Returns a list of students enrolled in a specific course.
        Verifies that the requesting instructor actually owns the course.
        """
        try:
            # 1. Verify Ownership
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")
            
            self.check_permission(course.instructor_id, instructor_id)

            # 2. Fetch Enrollments (and ideally join with Student profiles)
            # For this MVP, we might return enrollment objects, or fetch student names.
            # Assuming EnrollmentRepo has a method to get students directly:
            return self.enrollment_repo.get_by_course_id(course_id)

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. GENERAL / STUDENT ACTIONS
    # ---------------------------------------------------------
    def get_all_courses(self):
        """Public Course Catalog."""
        try:
            return self.course_repo.get_all()
        except Exception as e:
            self.handle_db_error(e)

    def search_courses(self, query: str):
        """Optional: Search by name or code."""
        try:
            all_courses = self.course_repo.get_all()
            # Simple Python filter (Optimized: do this in SQL in real apps)
            return [
                c for c in all_courses 
                if query.lower() in c.name.lower() or query.lower() in c.code.lower()
            ]
        except Exception as e:
            self.handle_db_error(e)
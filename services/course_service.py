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

    def drop_course(self, course_id: int) -> bool:
            """Logic to allow an instructor to stop teaching a course."""
            try:
                self.course_repo.unassign_instructor(course_id)
                return True
            except Exception as e:
                self.handle_db_error(e)
                return False
        
    # ---------------------------------------------------------
    # 1. INSTRUCTOR ACTIONS (The "Missing" Methods)
    # ---------------------------------------------------------
    def create_course(self, instructor_id: int, code: str, name: str, description: str = ""):
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
                credits=3, semester="Fall 2025", max_students=30 # Defaults
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
    
            return self.enrollment_repo.get_students_by_course(course_id)

        except Exception as e:
            self.handle_db_error(e)

    def assign_instructor(self, course_id: int, instructor_profile_id: int) -> bool:
        """
        Updates an existing course to set a specific instructor as the owner.
        """
        try:
            # 1. Fetch the course
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")
            
            # 2. Safety check: Ensure it's not already assigned
            if course.instructor_id is not None:
                raise ValueError("This course is already assigned to an instructor.")

            # 3. Update the model and save
            course.instructor_id = instructor_profile_id
            self.course_repo.update(course)
            return True
        except Exception as e:
            self.handle_db_error(e)
            return False

    def get_unassigned_courses(self):
        """Returns a list of Course objects where instructor_id is NULL."""
        try:
            # Fetch all courses from the repo
            all_courses = self.course_repo.get_all()
            # Filter for those with no instructor
            return [c for c in all_courses if c.instructor_id is None]
        except Exception as e:
            self.handle_db_error(e)
            return []
        
    def drop_course(self, course_id: int) -> bool:
        """Removes the instructor from the course so it becomes unassigned."""
        try:
            course = self.course_repo.get_by_id(course_id)
            if course:
                course.instructor_id = None 
                self.course_repo.update(course) # Save change
                return True
            return False
        except Exception as e:
            self.handle_db_error(e)
            return False

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
            return [
                c for c in all_courses 
                if query.lower() in c.name.lower() or query.lower() in c.code.lower()
            ]
        except Exception as e:
            self.handle_db_error(e)

    def get_course_by_id(self, course_id: int):
        """
        Fetches a single course by ID.
        """
        try:
            return self.course_repo.get_by_id(course_id)
        except Exception as e:
            self.handle_db_error(e)
    
    def get_all_courses_with_details(self):
        try:
            courses = self.get_all_courses()
            results = []
            for c in courses:
                d = c.to_dict() if hasattr(c, 'to_dict') else vars(c)
                with self.course_repo.get_connection() as conn:
                    res = conn.execute("""
                        SELECT u.name 
                        FROM instructors i 
                        JOIN users u ON i.user_id = u.id 
                        WHERE i.id = ?
                    """, (c.instructor_id,)).fetchone()
                    d['instructor_name'] = res[0] if res else "Unknown"
                results.append(d)
            return results
        except Exception as e:
            self.handle_db_error(e)
    
    def search_courses_with_details(self, query: str):
        try:
            courses = self.search_courses(query)
            results = []
            for c in courses:
                d = c.to_dict() if hasattr(c, 'to_dict') else vars(c)
                with self.course_repo.get_connection() as conn:
                    res = conn.execute("""
                        SELECT u.name 
                        FROM instructors i 
                        JOIN users u ON i.user_id = u.id 
                        WHERE i.id = ?
                    """, (c.instructor_id,)).fetchone()
                    d['instructor_name'] = res[0] if res else "Unknown"
                results.append(d)
            return results
        except Exception as e:
            self.handle_db_error(e)
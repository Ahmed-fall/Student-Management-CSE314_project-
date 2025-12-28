from core.base_service import BaseService
from models.course import Course
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository

class CourseService(BaseService):
    def __init__(self):
        self.course_repo = CourseRepository()
        self.enrollment_repo = EnrollmentRepository()

    def create_course(self, instructor_id: int, code: str, name: str, description: str = ""):
        try:
            if not code or not name:
                raise ValueError("Course code and name are required.")
            
            if self.course_repo.get_by_code(code):
                raise ValueError(f"Course code '{code}' already exists.")

            new_course = Course(
                id=None,
                name=name,
                code=code,
                description=description,
                instructor_id=instructor_id,
                credits=3, 
                semester="Fall 2025", 
                max_students=30
            )

            return self.course_repo.create(new_course)

        except Exception as e:
            self.handle_db_error(e)
    
    def update_course(self, course_id: int, data: dict) -> bool:
        try:
            course = self.course_repo.get_by_id(course_id)
            if not course:
                return False
            
            if 'description' in data:
                course.description = data['description']
            
            if 'max_students' in data:
                try:
                    course.max_students = int(data['max_students'])
                except ValueError:
                    pass 

            self.course_repo.update(course)
            return True
        except Exception as e:
            self.handle_db_error(e)
            return False

    def get_courses_by_instructor(self, instructor_id: int):
        try:
            return self.course_repo.get_by_instructor_id(instructor_id)
        except Exception as e:
            self.handle_db_error(e)

    def get_course_roster(self, instructor_id: int, course_id: int):
        try:
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")
            
            self.check_permission(course.instructor_id, instructor_id)
    
            return self.enrollment_repo.get_students_by_course(course_id)

        except Exception as e:
            self.handle_db_error(e)

    def assign_instructor(self, course_id: int, instructor_profile_id: int) -> bool:
        try:
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")
            
            if course.instructor_id is not None:
                raise ValueError("This course is already assigned to an instructor.")

            course.instructor_id = instructor_profile_id
            self.course_repo.update(course)
            return True
        except Exception as e:
            self.handle_db_error(e)
            return False

    def get_unassigned_courses(self):
        try:
            all_courses = self.course_repo.get_all()
            return [c for c in all_courses if c.instructor_id is None]
        except Exception as e:
            self.handle_db_error(e)
            return []
        
    def drop_course(self, course_id: int) -> bool:
        try:
            course = self.course_repo.get_by_id(course_id)
            if course:
                course.instructor_id = None 
                self.course_repo.update(course)
                return True
            return False
        except Exception as e:
            self.handle_db_error(e)
            return False

    def get_all_courses(self):
        try:
            return self.course_repo.get_all()
        except Exception as e:
            self.handle_db_error(e)

    def search_courses(self, query: str):
        try:
            all_courses = self.course_repo.get_all()
            return [
                c for c in all_courses 
                if query.lower() in c.name.lower() or query.lower() in c.code.lower()
            ]
        except Exception as e:
            self.handle_db_error(e)

    def get_course_by_id(self, course_id: int):
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
                
                # Fetch instructor name manually for the view
                with self.course_repo.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT u.name 
                        FROM instructors i 
                        JOIN users u ON i.user_id = u.id 
                        WHERE i.id = %s
                    """, (c.instructor_id,))
                    res = cur.fetchone()
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
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT u.name 
                        FROM instructors i 
                        JOIN users u ON i.user_id = u.id 
                        WHERE i.id = %s
                    """, (c.instructor_id,))
                    res = cur.fetchone()
                    d['instructor_name'] = res[0] if res else "Unknown"
                results.append(d)
            return results
        except Exception as e:
            self.handle_db_error(e)
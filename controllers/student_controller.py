from core.base_controller import BaseController
from core.session import Session
from services.student_service import StudentService
from services.course_service import CourseService
from services.assignment_service import AssignmentService

class StudentController(BaseController):
    
    
    
    # --- DASHBOARD & COURSES (Unchanged) ---
    def load_dashboard_data(self, update_view_callback):
        user = Session.current_user
        if not user: return self.navigate("login")
        self.run_async(lambda: self.get_service(StudentService).get_dashboard_overview(user.id), update_view_callback)

    def load_my_courses(self, update_view_callback):
        user = Session.current_user
        if user:
            self.run_async(lambda: self.get_service(StudentService).get_my_courses(user.id), update_view_callback)

    # --- CLASSROOM LOGIC (FIXED) ---
    
    def open_classroom(self, course_id):
        """
        Transfers the student to the Classroom View.
        Passes 'course_id' explicitly to the next view via kwargs.
        """
        # We pass course_id as a keyword argument to the router
        self.navigate("student_classroom", course_id=course_id)

    def load_classroom_data(self, course_id, update_view_callback):
        """
        Fetches data for the specific course_id passed from the View.
        """
        if not course_id:
            # If for some reason ID is missing, go back
            self.navigate("student_courses")
            return
        
        user = Session.current_user
        if not user: return

        def fetch_task():
            # 1. Get Course Info
            course_service = self.get_service(CourseService)
            course = course_service.get_course_by_id(course_id)
            
            # 2. Get Assignments
            assign_service = self.get_service(AssignmentService)
            assignments = assign_service.get_student_assignments(user.id, course_id)
            
            # 3. Get Announcements (Placeholder)
            announcements = [] 
            
            return {
                "course": course,
                "assignments": assignments,
                "announcements": announcements
            }

        self.run_async(fetch_task, update_view_callback)
    # --- ASSIGNMENT DETAILS & SUBMISSION ---

    def open_assignment_details(self, assignment_id):
        """
        Transfers the student to the Assignment Details View.
        Passes 'assignment_id' explicitly to the next view via kwargs.
        """
        self.navigate("student_assignment_details", assignment_id=assignment_id)

    def load_assignments(self, update_view_callback):
        """
        Fetches available assignments for the view.
        """
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(AssignmentService)
            return service.get_student_assignments(user.id)
            
        self.run_async(task, update_view_callback)
        
    def load_assignment_details(self, assignment_id, callback):
        """
        Fetches a single assignment by ID for the details view.
        """
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(AssignmentService)
            return service.get_assignment_detail_for_student(user.id, assignment_id)
            
        self.run_async(task, callback)
    
    def submit_assignment(self, assignment_id, content, callback):
        """
        Submits the student's work and notifies the view when done.
        """
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(AssignmentService)
            # Pass the 3 necessary arguments to the service
            return service.submit_assignment(user.id, assignment_id, content)
            
        # Run the task, then call 'callback' with the result
        self.run_async(task, callback)
    
    def navigate_to_assignments(self):
        """
        Clicked from Sidebar > Assignments.
        Shows the Global To-Do List (All assignments from all courses).
        """
        self.navigate("student_assignments") 

    def navigate_to_grades(self):
        """
        Clicked from Sidebar > Grades.
        Shows the Transcript.
        """
        self.navigate("student_grades")
    
    def load_grades(self, update_view_callback):
        """
        Fetches the grade report for the current user.
        """
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(StudentService)
            return service.get_student_grades(user.id)
            
        self.run_async(task, update_view_callback)

    def navigate_to_notifications(self):
        """
        Clicked from Sidebar > Notifications.
        Shows the Notifications View.
        """
        self.navigate("student_notifications")
    
    def navigate_to_catalog(self):
        """
        Clicked from Sidebar > Course Catalog.
        Shows the Course Catalog View.
        """
        self.navigate("student_catalog")
    
    def load_catalog_data(self, update_view_callback, query=None):
        user = Session.current_user
        if not user: return

        def task():
            course_service = self.get_service(CourseService)
            if query:
                courses = course_service.search_courses_with_details(query)
            else:
                courses = course_service.get_all_courses_with_details()
            
            student_service = self.get_service(StudentService)
            my_courses = student_service.get_my_courses(user.id)
            enrolled_ids = [mc['id'] for mc in my_courses] if my_courses else []
            
            return {
                "courses": courses,
                "enrolled_ids": enrolled_ids
            }

        self.run_async(task, update_view_callback)
    
    def enroll_course(self, course_id, callback):
        user = Session.current_user
        if not user: return

        def task():
            service = self.get_service(StudentService)
            return service.enroll_course(user.id, course_id)

        self.run_async(task, callback)
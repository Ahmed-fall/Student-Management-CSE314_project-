from core.base_controller import BaseController
from core.session import Session
# --- Service Imports ---
from services.student_service import StudentService
from services.course_service import CourseService
from services.assignment_service import AssignmentService
from services.announcement_service import AnnouncementService
from services.notification_service import NotificationService 

class StudentController(BaseController):
    
    # --- DASHBOARD & COURSES LOGIC ---
    def load_dashboard_data(self, update_view_callback):
        """
        Fetches all summary data for the dashboard view.
        Aggregates data from multiple services to fill the Dashboard widgets.
        """
        user = Session.current_user
        if not user: return self.navigate("login")

        def fetch_task():
            student_service = self.get_service(StudentService)
            notification_service = self.get_service(NotificationService)
            
            # 1. Get Student ID & Profile
            # Assuming get_student_by_user_id returns the student profile object
            student_obj = student_service.get_student_by_user_id(user.id)
            if not student_obj: return {}

            student_id = student_obj.student_id

            # 2. Get Stats (Courses, GPA, etc.)
            # If your service doesn't have these exact methods, return defaults (0 or [])
            try:
                courses = student_service.get_my_courses(user.id)
                gpa = student_service.calculate_gpa(student_id) 
                deadlines = student_service.get_upcoming_deadlines(student_id)
            except Exception:
                courses = []
                gpa = 0.0
                deadlines = []

            # 3. Get Notifications Count
            notifs = notification_service.get_dashboard_notifications(user.id)
            unread_count = len([n for n in notifs if n['read_flag'] == 0])

            return {
                "student": student_obj.to_dict(),
                "current_gpa_average": gpa,
                "enrolled_courses_count": len(courses),
                "unread_notifications": unread_count,
                "upcoming_deadlines": deadlines
            }

        self.run_async(fetch_task, update_view_callback)

    def load_my_courses(self, update_view_callback):
        user = Session.current_user
        if user:
            self.run_async(lambda: self.get_service(StudentService).get_my_courses(user.id), update_view_callback)

    # --- NOTIFICATIONS LOGIC 
    def load_notifications(self, callback):
        """Fetches list of notifications for the Notifications View."""
        user = Session.current_user
        if not user: return

        def task():
            return self.get_service(NotificationService).get_dashboard_notifications(user.id)
        
        self.run_async(task, callback)

    def mark_notification_read(self, notif_id, callback=None):
        """Marks a single notification as read."""
        user = Session.current_user
        if not user: return

        def task():
            self.get_service(NotificationService).mark_as_read(user.id, notif_id)
        
        def on_done(_):
            if callback: callback()

        self.run_async(task, on_done)

    def mark_all_notifications_read(self, callback=None):
        """Marks all notifications as read."""
        user = Session.current_user
        if not user: return

        def task():
            service = self.get_service(NotificationService)
            # Fetch all and loop through them (unless you have a mark_all SQL method)
            all_notifs = service.get_dashboard_notifications(user.id)
            for n in all_notifs:
                if n['read_flag'] == 0:
                    service.mark_as_read(user.id, n['notification_id'])

        def on_done(_):
            if callback: callback()

        self.run_async(task, on_done)

    # --- CLASSROOM LOGIC---
    def open_classroom(self, course_id):
        self.navigate("student_classroom", course_id=course_id)

    def load_classroom_data(self, course_id, update_view_callback):
        if not course_id:
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
            
            # 3. Get Announcements
            ann_service = self.get_service(AnnouncementService)
            raw_announcements = ann_service.get_course_announcements(course_id)

            announcements = [a.to_dict() for a in raw_announcements]
            announcements.sort(key=lambda x: x['id'], reverse=True)
            
            return {
                "course": course,
                "assignments": assignments,
                "announcements": announcements
            }

        self.run_async(fetch_task, update_view_callback)

    # --- ASSIGNMENT DETAILS & SUBMISSION ---
    def open_assignment_details(self, assignment_id):
        self.navigate("student_assignment_details", assignment_id=assignment_id)

    def load_assignments(self, update_view_callback):
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(AssignmentService)
            return service.get_student_assignments(user.id)
            
        self.run_async(task, update_view_callback)
        
    def load_assignment_details(self, assignment_id, callback):
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(AssignmentService)
            return service.get_assignment_detail_for_student(user.id, assignment_id)
            
        self.run_async(task, callback)
    
    def submit_assignment(self, assignment_id, content, callback):
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(AssignmentService)
            return service.submit_assignment(user.id, assignment_id, content)
            
        self.run_async(task, callback)
    
    # --- NAVIGATION HELPERS ---
    def navigate_to_assignments(self):
        self.navigate("student_assignments") 

    def navigate_to_grades(self):
        self.navigate("student_grades")
    
    def load_grades(self, update_view_callback):
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(StudentService)
            # Ensure this method exists in your StudentService
            return service.get_grades(user.id) 
            
        self.run_async(task, update_view_callback)

    def navigate_to_notifications(self):
        self.navigate("student_notifications")
    
    def navigate_to_catalog(self):
        self.navigate("student_catalog")
    
    # --- CATALOG & ENROLLMENT ---
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
    
    def drop_course(self, course_id, callback):
        user = Session.current_user
        if not user: return

        def task():
            service = self.get_service(StudentService)
            return service.drop_course(user.id, course_id)

        self.run_async(task, callback)
from core.base_controller import BaseController
from core.session import Session
# --- Service Imports ---
from services.student_service import StudentService
from services.course_service import CourseService
from services.assignment_service import AssignmentService
from services.announcement_service import AnnouncementService
from services.notification_service import NotificationService 

class StudentController(BaseController):
    
    # ------------------------------------------------------------------
    # DASHBOARD LOGIC
    # ------------------------------------------------------------------
    def load_dashboard_data(self, update_view_callback):
        user = Session.current_user
        if not user: return self.navigate("login")

        def fetch_task():
            student_service = self.get_service(StudentService)
            notification_service = self.get_service(NotificationService)
            
            # 1. Get Student Profile
            student_obj = student_service.get_student_by_user_id(user.id)
            if not student_obj: return {}

            student_id = student_obj.student_id

            # 2. Get Stats
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
            
            # --- FIX: ROBUST ACCESS (Handle Dict or Object) ---
            unread_count = 0
            for n in notifs:
                # Check if it's an object (hasattr) or dict (get)
                flag = n.read_flag if hasattr(n, 'read_flag') else n.get('read_flag')
                if flag == 0:
                    unread_count += 1

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

    # ------------------------------------------------------------------
    # NOTIFICATIONS LOGIC 
    # ------------------------------------------------------------------
    def load_notifications(self, callback):
        user = Session.current_user
        if not user: return

        def task():
            return self.get_service(NotificationService).get_dashboard_notifications(user.id)
        
        self.run_async(task, callback)

    def mark_notification_read(self, notif_id, callback=None):
        user = Session.current_user
        if not user: return

        def task():
            self.get_service(NotificationService).mark_as_read(user.id, int(notif_id))
        
        def on_done(_):
            if callback: callback()

        self.run_async(task, on_done)

    def mark_all_notifications_read(self, callback=None):
        user = Session.current_user
        if not user: return

        def task():
            service = self.get_service(NotificationService)
            all_notifs = service.get_dashboard_notifications(user.id)
            
            for n in all_notifs:
                # --- FIX: ROBUST ACCESS ---
                flag = n.read_flag if hasattr(n, 'read_flag') else n.get('read_flag')
                n_id = n.id if hasattr(n, 'id') else n.get('id')
                # Note: Some DB queries might return 'notification_id' instead of 'id'
                if not n_id: n_id = n.get('notification_id')

                if flag == 0 and n_id:
                    service.mark_as_read(user.id, int(n_id))

        def on_done(_):
            if callback: callback()

        self.run_async(task, on_done)

    # ------------------------------------------------------------------
    # CLASSROOM LOGIC
    # ------------------------------------------------------------------
    def open_classroom(self, course_id):
        self.navigate("student_classroom", course_id=course_id)

    def load_classroom_data(self, course_id, update_view_callback):
        if not course_id:
            self.navigate("student_courses")
            return
        
        user = Session.current_user
        if not user: return

        def fetch_task():
            c_id = int(course_id)

            course_service = self.get_service(CourseService)
            course = course_service.get_course_by_id(c_id)
            
            assign_service = self.get_service(AssignmentService)
            assignments = assign_service.get_student_assignments(user.id, c_id)
            
            ann_service = self.get_service(AnnouncementService)
            raw_announcements = ann_service.get_course_announcements(c_id)

            # Ensure announcements are dicts for the view
            announcements = []
            for a in raw_announcements:
                if hasattr(a, 'to_dict'):
                    announcements.append(a.to_dict())
                else:
                    announcements.append(a)

            announcements.sort(key=lambda x: x.get('id', 0), reverse=True)
            
            return {
                "course": course,
                "assignments": assignments,
                "announcements": announcements
            }

        self.run_async(fetch_task, update_view_callback)

    # ------------------------------------------------------------------
    # ASSIGNMENT DETAILS & SUBMISSION
    # ------------------------------------------------------------------
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
            return service.get_assignment_detail_for_student(user.id, int(assignment_id))
            
        self.run_async(task, callback)
    
    def submit_assignment(self, assignment_id, content, callback):
        user = Session.current_user
        if not user: return
        
        if not content or not content.strip():
             self.show_error("Error", "Submission content cannot be empty.")
             return

        def task():
            service = self.get_service(AssignmentService)
            return service.submit_assignment(user.id, int(assignment_id), content)
            
        self.run_async(task, callback)
    
    # ------------------------------------------------------------------
    # NAVIGATION HELPERS
    # ------------------------------------------------------------------
    def navigate_to_assignments(self):
        self.navigate("student_assignments") 

    def navigate_to_grades(self):
        self.navigate("student_grades")
    
    def load_grades(self, update_view_callback):
        user = Session.current_user
        if not user: return
        
        def task():
            service = self.get_service(StudentService)
            return service.get_grades(user.id) 
            
        self.run_async(task, update_view_callback)

    def navigate_to_notifications(self):
        self.navigate("student_notifications")
    
    def navigate_to_catalog(self):
        self.navigate("student_catalog")
    
    # ------------------------------------------------------------------
    # CATALOG & ENROLLMENT
    # ------------------------------------------------------------------
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
            
            # Handle both object and dict return types for courses
            enrolled_ids = []
            if my_courses:
                for mc in my_courses:
                    c_id = mc.id if hasattr(mc, 'id') else mc.get('id')
                    enrolled_ids.append(c_id)
            
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
            return service.enroll_course(user.id, int(course_id))

        self.run_async(task, callback)
    
    def drop_course(self, course_id, callback):
        user = Session.current_user
        if not user: return

        def task():
            service = self.get_service(StudentService)
            return service.drop_course(user.id, int(course_id))

        self.run_async(task, callback)
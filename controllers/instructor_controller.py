from core.base_controller import BaseController
from core.session import Session
from services.announcement_service import AnnouncementService
from services.instructor_service import InstructorService
from services.course_service import CourseService
from services.assignment_service import AssignmentService
from services.student_service import StudentService

class InstructorController(BaseController):
    """
    Orchestrates business logic for Instructor views.
    Includes sanitization to prevent UI strings from crashing strict Models.
    """

    # ------------------------------------------------------------------
    # DASHBOARD & LOADING
    # ------------------------------------------------------------------
    def load_dashboard_data(self, callback):
        user = Session.current_user
        if not user: return self.navigate("login")

        def task():
            return self.get_service(InstructorService).get_dashboard_data(user.id)

        self.run_async(task, callback)

    def load_course_editor_data(self, course_id, callback):
        def task():
            course_service = self.get_service(CourseService)
            assignment_service = self.get_service(AssignmentService)
            
            # Ensure ID is int
            c_id = int(course_id)
            
            return {
                "course": course_service.get_course_by_id(c_id),
                "assignments": assignment_service.get_assignments_by_course(c_id)
            }

        self.run_async(task, callback)

    # ------------------------------------------------------------------
    # ASSIGNMENT MANAGEMENT
    # ------------------------------------------------------------------
    def create_assignment(self, course_id, assignment_data, callback):
        """
        Orchestrates assignment creation.
        FIX: Sanitizes 'max_score' from String to Int/Float.
        """
        user = Session.current_user
        if not user: return

        # --- 1. Validation & Sanitization ---
        try:
            # UI sends strings; Model needs numbers.
            if 'max_score' in assignment_data:
                assignment_data['max_score'] = int(assignment_data['max_score'])
        except ValueError:
            self.show_error("Validation Error", "Max Score must be a valid number.")
            return

        def task():
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            if not profile: return False

            service = self.get_service(AssignmentService)
            return service.create_assignment(
                instructor_id=profile.instructor_profile_id,
                course_id=int(course_id),
                title=assignment_data['title'],
                description=assignment_data['description'],
                due_date=assignment_data['due_date'],
                max_score=assignment_data['max_score'],
                type=assignment_data['type']
            )

        self.run_async(task, callback)

    def delete_assignment(self, assignment_id, callback):
        user = Session.current_user
        if not user: return

        def task():
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            if not profile: raise ValueError("Profile not found")

            service = self.get_service(AssignmentService)
            return service.delete_assignment(profile.instructor_profile_id, int(assignment_id))

        self.run_async(task, callback)

    # ------------------------------------------------------------------
    # GRADING LOGIC
    # ------------------------------------------------------------------
    def load_assignment_submissions(self, assignment_id, callback):
        def task():
            service = self.get_service(AssignmentService)
            return service.submission_repo.get_grading_queue(int(assignment_id))
        self.run_async(task, callback)

    def submit_grade(self, submission_id, grade_value, feedback, callback):
        user = Session.current_user
        if not user: return

        # --- 1. Validation ---
        try:
            # Ensure grade is a number before hitting the DB
            g_val = float(grade_value)
        except ValueError:
            self.show_error("Validation Error", "Grade must be a number.")
            return

        def task():
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            if not profile: raise ValueError("Instructor profile not found.")

            service = self.get_service(AssignmentService)
            return service.grade_assignment(
                instructor_id=profile.instructor_profile_id,
                submission_id=int(submission_id),
                grade_value=g_val,
                feedback=feedback
            )

        self.run_async(task, callback)

    # ------------------------------------------------------------------
    # COURSE MANAGEMENT & EDITING
    # ------------------------------------------------------------------
    def get_course_details(self, course_id, callback):
        def task():
             return self.get_service(CourseService).get_course_by_id(int(course_id))
        self.run_async(task, callback)

    def update_course_details(self, course_id, data, callback):
        """
        Updates course info (e.g., Capacity).
        FIX: Sanitizes 'capacity' to Int.
        """
        # --- 1. Sanitization ---
        try:
            if 'capacity' in data:
                data['capacity'] = int(data['capacity'])
        except ValueError:
            self.show_error("Validation Error", "Capacity must be an integer.")
            return

        def task():
            service = self.get_service(CourseService)
            return service.update_course(int(course_id), data)
        
        self.run_async(task, callback)

    # ------------------------------------------------------------------
    # ANNOUNCEMENTS & MISC
    # ------------------------------------------------------------------
    def load_my_courses_for_selector(self, callback):
        user = Session.current_user
        if not user: return

        def task():
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            if not profile: return []
            
            course_service = self.get_service(CourseService)
            return course_service.get_courses_by_instructor(profile.instructor_profile_id)

        self.run_async(task, callback)

    def create_announcement(self, course_id, title, message, callback):
        user = Session.current_user
        if not user: return

        def task():
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            if not profile: return False

            ann_service = AnnouncementService() 
            return ann_service.create_announcement(
                instructor_id=profile.instructor_profile_id,
                course_id=int(course_id),
                title=title,
                message=message
            )

        self.run_async(task, callback)

    # ------------------------------------------------------------------
    # CAMPUS MANAGER & NAVIGATION
    # ------------------------------------------------------------------
    def load_unassigned_courses(self, callback):
        def task():
            return self.get_service(CourseService).get_unassigned_courses()
        self.run_async(task, callback)

    def claim_teaching_rights(self, course_id, callback):
        def task():
            inst_svc = self.get_service(InstructorService)
            profile = inst_svc.get_instructor_profile(Session.current_user.id)
            
            course_svc = self.get_service(CourseService)
            return course_svc.assign_instructor(int(course_id), profile.instructor_profile_id)
        
        self.run_async(task, callback)

    def drop_teaching_course(self, course_id, callback):
        def task():
            return self.get_service(CourseService).drop_course(int(course_id))
        self.run_async(task, callback)

    def create_new_course(self, code, name, callback):
        def task():
            return self.get_service(CourseService).create_course(instructor_id=None, code=code, name=name)
        self.run_async(task, callback)
    
    def get_course_students(self, course_id, callback):
        def task():
            return self.get_service(StudentService).get_students_by_course(int(course_id))
        self.run_async(task, callback)

    def open_course_editor(self, course_id):
        self.navigate("course_editor", course_id=course_id)